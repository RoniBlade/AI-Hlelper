import logging
import subprocess
import sys
from typing import Sequence

log = logging.getLogger(__name__)


def _run(cmd: Sequence[str]) -> None:
    try:
        subprocess.Popen(list(cmd))
    except Exception:
        log.exception("Failed to run: %r", cmd)
        raise


def open_notepad() -> None:
    """
    Открыть текстовый редактор.
    """
    if sys.platform.startswith("win"):
        _run(["notepad.exe"])
    elif sys.platform == "darwin":
        _run(["open", "-a", "TextEdit"])
    else:
        # На Linux у всех по-разному, пробуем популярные варианты:
        for candidate in (["gedit"], ["kate"], ["nano"], ["xdg-open", "/tmp"]):
            try:
                _run(candidate)
                return
            except Exception:
                continue
        raise RuntimeError("No known editor found on this system")
