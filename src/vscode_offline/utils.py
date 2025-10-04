from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from vscode_offline.loggers import logger

_vscode_data = Path("~/.vscode").expanduser()
_vscode_server_data = Path("~/.vscode-server").expanduser()


def get_vscode_cli_bin(commit: str) -> os.PathLike[str]:
    return _vscode_server_data / f"code-{commit}"


def get_vscode_server_home(commit: str) -> os.PathLike[str]:
    return _vscode_server_data / f"cli/servers/Stable-{commit}/server"


def get_vscode_extensions_config() -> os.PathLike[str]:
    p = _vscode_data / "extensions/extensions.json"
    if p.exists():
        return p
    s = _vscode_server_data / "extensions/extensions.json"
    if s.exists():
        return s
    return p  # default to this path


def get_vscode_commit_from_server_installer(
    installer: os.PathLike[str], platform: str
) -> str:
    directories = list(
        Path(installer).glob(f"server-*/vscode-server-{platform}.tar.gz")
    )
    if len(directories) > 1:
        raise ValueError(
            f"Multiple matching installers found in {installer} for platform {platform}"
        )
    elif len(directories) == 0:
        raise ValueError(
            f"No matching installer found in {installer} for platform {platform}"
        )

    commit = directories[0].parent.name[len("server-") :]
    logger.info(f"Getting commit from {platform} installer: {commit}")
    return commit


def get_vscode_commit_from_code_version() -> str | None:
    """Get the current VS Code commit hash by running `code --version`.
    Returns None if `code` is not found or the output is unexpected.
    """
    executable = shutil.which("code")
    if executable is None:
        return None
    proc = subprocess.run(
        ["code", "--version"],
        executable=executable,
        stdout=subprocess.PIPE,
    )
    if proc.returncode != 0:
        return None
    lines = proc.stdout.splitlines()
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


# Mapping from target platform to CLI OS and architecture used in download URLs
_cli_os_arch_mapping = {
    "linux-x64": "alpine-x64",
    "linux-arm64": "alpine-arm64",
}


def get_cli_os_arch(platform: str) -> str:
    """Get the CLI OS and architecture for the given target platform."""
    if platform not in _cli_os_arch_mapping:
        raise ValueError(f"Unsupported target platform: {platform}")
    return _cli_os_arch_mapping[platform]


def get_host_platform() -> str:
    """Get the host platform in the format used by VS Code Server install."""
    if os.name == "nt":
        if "amd64" in sys.version.lower():
            return "win32-x64"
        raise ValueError(f"Unsupported host platform: {os.name}-{sys.version}")

    (osname, _, _, _, machine) = os.uname()

    if osname.lower() == "linux":
        if machine in ("x86_64", "amd64"):
            return "linux-x64"
        elif machine in ("aarch64", "arm64"):
            return "linux-arm64"
    raise ValueError(f"Unsupported host platform: {osname}-{machine}")
