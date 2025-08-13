# Imports are separated into those needed specifically for attach()
# For easier decoupling if that ever can be removed/simplified
import argparse
import asyncio
from contextlib import ExitStack, closing
import importlib
import importlib.metadata
from io import StringIO
from multiprocessing import Value
from pathlib import Path
import pdb
from subprocess import Popen, PIPE

## attach() imports
import os
import sys
import json
import stat
import atexit
import socket
import tempfile
import textwrap
import _colorize

from textual import log
from textual.app import App
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Input
from textual.worker import Worker, get_current_worker

from .attachedscreen import AttachedScreen
from .detachedscreen import DetachedScreen
from .messages import (
    PdbState,
    PdbMessageType,
    MessageFromRepl,
    MessageToRepl,
    StdoutMessageFromRepl,
)
from .debuginputarea import DebugInputWidget
from .debugresponsearea import DebugResponseArea
from .IOarea import IOArea
from .wrappedclient import WrappedClient


class Pdbsharp(App):
    MODES = {"detached": DetachedScreen, "attached": AttachedScreen}
    DEFAULT_MODE = "detached"

    pdbmode = reactive(PdbState.Unattached)
    process_name = reactive("")

    def __init__(self, *args, attach_to=None, capture_io=False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = "pdb#"
        self._client: WrappedClient | None = None
        self._server_pid: int | None = None
        self._exitstack = ExitStack()
        self.command_list: list[str] | None = None
        self._start_captured_io = capture_io
        self._remote_stdout = tempfile.NamedTemporaryFile("w+", delete=False)
        self._remote_stdin = tempfile.NamedTemporaryFile("r+", delete=False)

        atexit.register(self._exitstack.close)

        def _close_client():
            if self._client and self._client.server_socket:
                return self._client.server_socket.close
            else:
                return lambda *args, **kwargs: 0

        atexit.register(_close_client)

        self._attach_to = attach_to

        self._pdb_readline_worker: Worker | None = None
        self._stdout_worker: Worker | None = None
        self._quitting = False
        atexit.register(self.quit)

    def on_message_to_repl(self, message: MessageToRepl) -> None:
        if self._client:
            match message.type:
                case PdbMessageType.COMMAND:
                    self._client._send(reply=message.content)
                case PdbMessageType.INT:
                    self._client.send_interrupt()
                case _:
                    raise ValueError(f"Unknown message type {message.type.name}")

    def on_mount(self):
        if self._attach_to:
            self.attach(self._attach_to, capture_io=self._start_captured_io)

    def attach(self, pid, commands=(), capture_io=False):
        if self.pdbmode in (PdbState.Attached, PdbState.Attaching):
            raise ValueError(f"Already in state {self.pdbmode} and trying to attach()")
        """Attach to a running process with the given PID."""
        """Based on original PdbClient's attach method"""
        self.pdbmode = PdbState.Attaching
        server = self._exitstack.enter_context(
            closing(socket.create_server(("localhost", 0)))
        )

        port = server.getsockname()[1]

        connect_script = self._exitstack.enter_context(
            tempfile.NamedTemporaryFile("w", delete=False)
        )

        use_signal_thread = sys.platform == "win32"
        colorize = _colorize.can_colorize()

        connect_script.write(
            textwrap.dedent(
                f"""
                import pdb, sys
                pdb._connect(
                    host="localhost",
                    port={port},
                    frame=sys._getframe(1),
                    commands={json.dumps("\n".join(commands))},
                    version={pdb._PdbServer.protocol_version()},
                    signal_raising_thread={use_signal_thread!r},
                    colorize={colorize!r},
                )
                """
            )
        )
        connect_script.close()
        orig_mode = os.stat(connect_script.name).st_mode
        os.chmod(connect_script.name, orig_mode | stat.S_IROTH | stat.S_IRGRP)
        try:
            sys.remote_exec(pid, connect_script.name)
        except RuntimeError:
            # showwarning("Pid does not match python process")
            self.query_one(Input).value = ""
            self.query_one(
                Input
            ).placeholder = "PID does not match a valid python process"
            self._exitstack.close()
            self.pdbmode = PdbState.Unattached
            return

        self.query_one(Input).placeholder = "Remote Process PID"

        # TODO Add a timeout? Or don't bother since the user can ^C?
        client_sock, _ = server.accept()
        self._exitstack.enter_context(closing(client_sock))

        if use_signal_thread:
            interrupt_sock, _ = server.accept()
            self._exitstack.enter_context(closing(interrupt_sock))
            interrupt_sock.setblocking(False)
        else:
            interrupt_sock = None

        # Dropped the call to cmdloop() at the end of this
        self._client = WrappedClient(self, pid, client_sock, interrupt_sock)

        self._server_pid = pid
        self.pdbmode = PdbState.Attached
        self.switch_mode("attached")
        if capture_io:
            self.capture_io()
        self._pdb_readline_worker = self.run_worker(self.readline_from_pdb, thread=True)

        self._exitstack.push(self._detach_and_close)

    def _detach_and_close(self, *args):
        if not self.pdbmode in (PdbState.Attached,):
            raise ValueError(f"Tried to detach while in state {self.pdbmode}")
        if self._client:
            self._client._send(signal="INT")
        self._exitstack.close()

    def detach(self, *args):
        self._detach_and_close()
        if self._screen_stack:
            self.screen.query_one(DebugResponseArea).clear()
        self._client = None
        self.pdbmode = PdbState.Unattached
        self.switch_mode("detached")

    async def readline_from_pdb(self, prewait=0.25):
        if self._quitting:
            return

        while not self._client:
            if self._quitting:
                return
            await asyncio.sleep(0.25)

        await asyncio.sleep(prewait)
        log("About to _readline")
        while not get_current_worker().is_cancelled and not self._quitting:
            res = self._client._readline()
            if res:
                self.screen.post_message(MessageFromRepl(res.decode("utf-8")))

    def stdout_reader_factory(self, filepath: str | Path, pause=0.1):
        async def inner():
            """Read input in from a file (_remote_stdout) and send it to the capture output, if any"""
            if self._quitting or not self._client:
                return

            while not get_current_worker().is_cancelled and not self._quitting:
                with open(filepath, "r") as f:
                    data = f.read().lstrip("\x00")
                if data:
                    if not "\n" in data:
                        data = "\n" + data
                    try:
                        self.screen.query_one(IOArea).post_message(
                            StdoutMessageFromRepl(data)
                        )
                    except NoMatches:
                        pass
                    else:
                        open(filepath, "w").close()  # clear file
                await asyncio.sleep(pause)

        return inner

    def on_debug_input_widget_capture_message(self, _: DebugInputWidget.CaptureMessage):
        self.capture_io()

    def on_debug_input_widget_uncapture_message(
        self, _: DebugInputWidget.UncaptureMessage
    ):
        self.uncapture_io()

    def capture_io(self):
        if not (self._client and self._server_pid):
            return

        io_capture_script = self._exitstack.enter_context(
            tempfile.NamedTemporaryFile("w", delete=False)
        )

        src = textwrap.dedent(f"""
            import atexit
            from contextlib import ExitStack, closing
            import socket
            import os
            import sys

            class Unbuffered(object):
                def __init__(self, stream):
                    self.stream = stream
                def write(self, data):
                    self.stream.write(data)
                    self.stream.flush()
                def writelines(self, data):
                    self.stream.writelines(data)
                    self.stream.flush()
                def __getattr__(self, attr):
                    return getattr(self.stream, attr)

            os.environ['PYTHONUNBUFFERED'] = '1'

            _pdbsharp_orig_stdout = sys.stdout
            #_pdbsharp_orig_stdin = sys.stdin

            _exitstack = ExitStack()

            def _restore_sys_at_close():
                sys.stdout = _pdbsharp_orig_stdout
                #sys.stdin = _pdbsharp_orig_stdin
                _exitstack.close()

            sys._restore_sys_at_close = _restore_sys_at_close

            atexit.register(_restore_sys_at_close)

            print("Redirecting stdout to {self._remote_stdout.name} for pdb#")

            sys.stdout = _exitstack.enter_context(closing(open("{self._remote_stdout.name}", "w")))
            #sys.stdin = _exitstack.enter_context(closing(open("{self._remote_stdin.name}", "r")))

            sys.stdout = Unbuffered(sys.stdout)
            """)
        io_capture_script.write(src)
        io_capture_script.close()
        orig_mode = os.stat(io_capture_script.name).st_mode
        os.chmod(io_capture_script.name, orig_mode | stat.S_IROTH | stat.S_IRGRP)
        try:
            sys.remote_exec(self._server_pid, io_capture_script.name)
        except RuntimeError as err:
            raise err

        self._exitstack.callback(self.uncapture_io)
        self._stdout_worker = self.run_worker(
            self.stdout_reader_factory(self._remote_stdout.name), thread=True
        )

    def uncapture_io(self):
        # Kill the worker reading std from remote process from tempfile
        if not self._stdout_worker or not self._server_pid:
            return
        if not self._stdout_worker.is_cancelled:
            self._stdout_worker.cancel()

        io_release_script = self._exitstack.enter_context(
            tempfile.NamedTemporaryFile("w", delete=False)
        )
        # Try to call the earlier implemented
        src = textwrap.dedent(
            """
            import sys

            try:
                sys._restore_sys_at_close()
            except AttributeError as err:
                raise err
            """
        )
        io_release_script.write(src)
        io_release_script.close()
        orig_mode = os.stat(io_release_script.name).st_mode
        os.chmod(io_release_script.name, orig_mode | stat.S_IROTH | stat.S_IRGRP)
        try:
            sys.remote_exec(self._server_pid, io_release_script.name)
        except RuntimeError as err:
            raise err

    def action_quit(self):
        self.quit()
        self.exit()

    def quit(self):
        self._quitting = True
        if self._client:
            self._client._send(signal="INT")
        if self._pdb_readline_worker:
            self._pdb_readline_worker.cancel()
        if self._stdout_worker:
            self._stdout_worker.cancel()

        self.uncapture_io()

        # if self._loop: self._loop.shutdown_default_executor(1)

    def debug(self, msg: str):
        try:
            self.screen.query_one(DebugResponseArea).write(f"DEBUG: {msg}")
        except NoMatches as err:
            self.notify(msg)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version",
    )
    parser.add_argument(
        "-p",
        "--pid",
        type=int,
        help="The PID of a Python process to connect to",
    )
    parser.add_argument(
        "-m",
        type=str,
        metavar="module",
        dest="module",
    )
    parser.add_argument("-c", "--capture-io", action="store_true", dest="capture_io")

    try:
        idx = sys.argv.index("-m")
    except ValueError:
        args, _ = parser.parse_known_args()
    else:
        # If we're using the -m flag, everything after the module name should be passed to the module being run and not processed as an argument to pdbsharp
        args, _ = parser.parse_known_args(sys.argv[: idx + 2])

    # -c must have -p flag
    if args.capture_io and not args.pid:
        raise AttributeError("--capture-io flag can only be used with --pid")

    return args


def run(args, auto_pilot=None):
    if args.version:
        print(f"pdbsharp {importlib.metadata.version('pdbsharp')}")
        return

    exitstack = ExitStack()
    atexit.register(exitstack.close)
    _process = None

    # Check for flag compatibility
    if args.module and args.pid:
        raise AttributeError("-m and --pid options cannot be used together")
    if args.module:
        file = args.module
        # If we're using the -m flag, everything after the module name should be passed to the module being run
        idx = sys.argv.index("-m")
        module_args = sys.argv[idx + 2 :] if len(sys.argv) >= idx + 2 else []
        _process = Popen(
            [sys.executable, "-m", file] + module_args,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE,
            env={"PYTHONUNBUFFERED": "1"},
        )
        exitstack.callback(lambda *args: _process.terminate)
        args.pid = int(_process.pid)

    app = Pdbsharp(attach_to=args.pid, capture_io=args.capture_io)
    app.run(auto_pilot=auto_pilot)


def main(auto_pilot=None):
    args = parse_args()
    return run(args, auto_pilot)


if __name__ == "__main__":
    main()
