import subprocess
import sys
from pathlib import Path

import rich


def stop_rm_cs():
    rich.print("Terminating the service registry manager core service...")

    out = open(Path("~/.rm_cs.stop.out").expanduser(), "w")

    subprocess.Popen(
        [sys.executable, "-m", "egse.registry.server", "stop"],
        stdout=out,
        stderr=out,
        stdin=subprocess.DEVNULL,
        close_fds=True,
    )


def stop_log_cs():
    rich.print("Terminating the logging core service...")

    out = open(Path("~/.log_cs.stop.out").expanduser(), "w")

    subprocess.Popen(
        [sys.executable, "-m", "egse.logger.log_cs", "stop"],
        stdout=out,
        stderr=out,
        stdin=subprocess.DEVNULL,
        close_fds=True,
    )


def stop_sm_cs():
    rich.print("Terminating the storage manager core service...")

    out = open(Path("~/.sm_cs.stop.out").expanduser(), "w")

    subprocess.Popen(
        [sys.executable, "-m", "egse.storage.storage_cs", "stop"],
        stdout=out,
        stderr=out,
        stdin=subprocess.DEVNULL,
        close_fds=True,
    )


def stop_cm_cs():
    rich.print("Terminating the configuration manager core service...")

    out = open(Path("~/.cm_cs.stop.out").expanduser(), "w")

    subprocess.Popen(
        [sys.executable, "-m", "egse.confman.confman_cs", "stop"],
        stdout=out,
        stderr=out,
        stdin=subprocess.DEVNULL,
        close_fds=True,
    )


def stop_pm_cs():
    rich.print("Terminating the process manager core service...")

    out = open(Path("~/.pm_cs.stop.out").expanduser(), "w")

    subprocess.Popen(
        [sys.executable, "-m", "egse.procman.procman_cs", "stop"],
        stdout=out,
        stderr=out,
        stdin=subprocess.DEVNULL,
        close_fds=True,
    )
