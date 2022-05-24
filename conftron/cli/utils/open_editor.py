import os
import subprocess
from pathlib import Path

from sys import platform


def open_editor(path: Path):
    editor = None

    if platform == "linux" or platform == "linux2" or platform == "darwin":
        if not os.environ.get("EDITOR", None):
            raise Exception(
                "Unable to open editor; please set your EDITOR "
                "environment variable to point to your preferred "
                'editor, e.g. "/usr/bin/vim" or simply "vim"'
            )

        editor = os.environ["EDITOR"]
    elif platform == "win32":
        editor = "notepad.exe"

    subprocess.call(f"{editor} {str(path)}", shell=True)
