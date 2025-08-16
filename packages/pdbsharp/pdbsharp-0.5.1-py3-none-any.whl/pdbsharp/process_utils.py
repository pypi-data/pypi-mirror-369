from os import getpid
from textwrap import shorten
from typing import TypedDict

import psutil


class ProcessInfo(TypedDict):
    name: str
    pid: str
    cmdline: list[str] | None


def get_python_processes() -> list[ProcessInfo]:
    process_info: list[ProcessInfo] = []
    wanted = ("pid", "name", "cmdline")
    ignored_command_strings = (
        ".vscode/extensions",  # If developing in VS code, Pylance and the language server create a bunch of processes
        "pylance",
    )
    for p in psutil.process_iter():
        data: ProcessInfo = p.as_dict(attrs=wanted)
        # Heuristics for which processes to show are in this conditional
        if (
            (
                data["cmdline"] and any("python" in cmd for cmd in data["cmdline"])
            )  # 'python' in the command line invocation
            and not int(data["pid"]) == getpid()  # Don't list our own process
            and not any(
                s in cmd for cmd in data["cmdline"] for s in ignored_command_strings
            )  # Anything with a forbidden string is ignored
        ):
            process_info.append(data)
    return process_info


def get_process_name(pid: int) -> str:
    proc = psutil.Process(pid)
    p: ProcessInfo = proc.as_dict(attrs=("name", "cmdline"))
    return f"{shorten(p['name'], 10)}:{shorten(p['cmdline'][-1] if p['cmdline'] else '', 50)}"
