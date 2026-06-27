from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


INSTALL_HELP = """The Tesseract backend requires the Tesseract OCR system binary.

Install it, then restart your terminal:

Windows:
  winget install UB-Mannheim.TesseractOCR

macOS:
  brew install tesseract

Ubuntu/Debian:
  sudo apt install tesseract-ocr

If Tesseract is already installed, set TESSERACT_CMD to the full tesseract
executable path.
"""


@dataclass(frozen=True)
class TesseractStatus:
    available: bool
    command: str | None
    version: str | None = None
    message: str = ""


class TesseractUnavailableError(RuntimeError):
    """Raised when the Tesseract executable is missing or unusable."""


def find_tesseract_command() -> str | None:
    for env_name in ("TESSERACT_CMD", "TESSERACT_PATH"):
        configured = os.environ.get(env_name)
        if configured and Path(configured).is_file():
            return configured

    from_path = shutil.which("tesseract")
    if from_path:
        return from_path

    candidates: list[Path] = []
    if platform.system() == "Windows":
        for root_name in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
            root = os.environ.get(root_name)
            if root:
                candidates.append(Path(root) / "Tesseract-OCR" / "tesseract.exe")

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    return None


def get_tesseract_status() -> TesseractStatus:
    command = find_tesseract_command()
    if command is None:
        return TesseractStatus(
            available=False,
            command=None,
            message=INSTALL_HELP,
        )

    try:
        completed = subprocess.run(
            [command, "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return TesseractStatus(
            available=False,
            command=command,
            message=f"Tesseract was found but could not run: {exc}\n\n{INSTALL_HELP}",
        )

    first_line = completed.stdout.splitlines()[0] if completed.stdout else "unknown"
    return TesseractStatus(
        available=True,
        command=command,
        version=first_line,
        message="Tesseract OCR is available.",
    )


def configure_pytesseract() -> str:
    command = find_tesseract_command()
    if command is None:
        raise TesseractUnavailableError(INSTALL_HELP)

    return command
