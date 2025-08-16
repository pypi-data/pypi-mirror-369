"""Tool Runner

Executes shell commands with timeouts, returning (exit_code, stdout, stderr).
This helper is sandbox-friendly and wrapped in telemetry spans.
"""

from __future__ import annotations

import subprocess
from typing import Sequence

from ..telemetry import start_span


def run_command(
    cmd: Sequence[str], cwd: str | None = None, timeout: int | None = None
) -> tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    with start_span("isaac.tools.exec", {"cmd": " ".join(cmd), "cwd": cwd or "."}):
        proc = subprocess.Popen(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            return 124, "", "timeout"
        return proc.returncode, out, err
