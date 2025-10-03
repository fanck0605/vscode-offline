from __future__ import annotations

import os
from pathlib import Path

VSCODE_DATA = Path("~/.vscode").expanduser()
VSCODE_SERVER_DATA = Path("~/.vscode-server").expanduser()


def get_vscode_cli_bin(commit: str) -> os.PathLike[str]:
    return VSCODE_SERVER_DATA / f"code-{commit}"


def get_vscode_server_home(commit: str) -> os.PathLike[str]:
    return VSCODE_SERVER_DATA / f"cli/servers/Stable-{commit}/server"


def get_vscode_extensions_config() -> os.PathLike[str]:
    p = VSCODE_DATA / "extensions/extensions.json"
    if p.exists():
        return p
    s = VSCODE_SERVER_DATA / "extensions/extensions.json"
    if s.exists():
        return s
    return p  # default to this path
