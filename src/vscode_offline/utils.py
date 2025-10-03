from __future__ import annotations

import os
import subprocess
from pathlib import Path
from vscode_offline.loggers import logger

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


def get_vscode_commit_from_installer(installer: os.PathLike[str]) -> str | None:
    directories = list(Path(installer).glob("cli-*"))
    if len(directories) == 1:
        return directories[0].name[len("cli-") :]
    return None


def get_vscode_commit_from_code_version() -> str | None:
    res = subprocess.run(["code", "--version"], stdout=subprocess.PIPE)
    if res.returncode != 0:
        return None
    lines = res.stdout.splitlines()
    if len(lines) < 2:
        return None  # Unexpected output

    # The commit hash is usually on the second line
    commit = lines[1].strip().decode("utf-8")
    logger.info(f"Getting commit from `code --version`: {commit}")

    return lines[1].strip().decode("utf-8")


def get_target_platform_from_installer(cli_installer: str) -> str | None:
    directories = list(Path(cli_installer).glob("vscode-server-*.tar.gz"))
    if len(directories) == 1:
        return directories[0].name[len("vscode-server-") : -len(".tar.gz")]
    return None
