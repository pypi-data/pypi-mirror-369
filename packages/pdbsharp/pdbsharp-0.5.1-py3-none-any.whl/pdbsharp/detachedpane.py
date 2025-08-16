from textwrap import shorten
from tkinter import Widget
from typing import TYPE_CHECKING, Callable, TypedDict, cast

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, OptionList, Static, TextArea
from textual.widgets.option_list import Option

from .messages import PdbState, TabAddMessage
from .process_utils import get_python_processes

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class DetachedPane(Static):
    CSS_PATH = "detachedscreen.tcss"

    def compose(self) -> ComposeResult:
        with Vertical(id="content"):
            yield Label(
                "Enter the PID of a running Python process to debug:",
                id="intro",
            )
            yield Input(
                "", placeholder="Remote Process PID", type="integer", id="remote-pid"
            )
            info = get_python_processes()

            # Sort by descending PID order, so that the newest processes are at the top of the list
            key: Callable[[Option], int] = lambda opt: int(opt.prompt.partition(" ")[0])
            options = sorted(
                [
                    Option(
                        f"{p['pid']: <10}{shorten(p['name'], 10): <11}{shorten(p['cmdline'][-1] if p['cmdline'] else '', self.app.size.width - 30)}"
                    )
                    for p in info
                ],
                key=key,
                reverse=True,
            )
            yield Label(
                "Or select an existing process:\n[grey][showing processes matching 'python3'][/grey]"
            )
            yield ProcessOptionList(
                *options, id="processlist", compact=(len(options) > 10)
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.value:
            value = event.input.value
            event.input.value = ""
            self.app.post_message(
                TabAddMessage(pid=int(value), capture_io=False, commands=None)
            )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        prompt = cast(str, event.option.prompt)
        pid, _, _ = prompt.partition(" ")
        self.app.post_message(
            TabAddMessage(pid=int(pid), capture_io=False, commands=None)
        )


class ProcessOptionList(OptionList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.highlighted = None

    def on_focus(self, event):
        self.highlighted = 0
