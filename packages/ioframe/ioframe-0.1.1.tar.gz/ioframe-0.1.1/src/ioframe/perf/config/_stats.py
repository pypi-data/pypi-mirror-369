from __future__ import annotations

import os
import platform
import re
from multiprocessing import cpu_count
from subprocess import check_output
from typing import TypedDict

from psutil import virtual_memory


def _get_processor_name() -> str:
    system = platform.system()
    if system == "Windows":
        return platform.processor()
    elif system == "Darwin":
        env = os.environ.copy()
        env["PATH"] = env["PATH"] + os.pathsep + "/usr/sbin"
        command = ["sysctl", "-n", "machdep.cpu.brand_string"]
        return str(check_output(command, env=env).strip())  # noqa: S603
    elif platform.system() == "Linux":
        command = ["cat", "/proc/cpuinfo"]
        all_info = check_output(command).decode().strip()  # noqa: S603
        for line in all_info.split("\n"):
            if "model name" in line:
                return re.sub(".*model name.*: ", "", line, count=1)
    return ""


class MachineSpecDict(TypedDict, total=True):
    cpu_count: int | None
    total_memory: int
    system: str
    processor_name: str


def get_machine_spec() -> MachineSpecDict:
    return {
        "cpu_count": cpu_count(),
        "total_memory": virtual_memory().total,
        "system": platform.system(),
        "processor_name": _get_processor_name(),
    }
