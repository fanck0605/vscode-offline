from __future__ import annotations

import os
import shutil
import subprocess
import sys
from argparse import ArgumentTypeError
from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from email.parser import HeaderParser
from pathlib import Path
from typing import Final

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


def get_vscode_version_from_server_installer(
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

    version = directories[0].parent.name[len("server-") :]
    logger.info(f"Getting version from {platform} installer: {version}")
    return version


def get_default_code_version() -> str | None:
    """Get the current VS Code version by running `code --version`.

    Returns:
        `None` if `code` is not found or the output is unexpected.
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
    version = f"commit:{commit}"
    logger.info(f"Getting version from `code --version`: {version}")

    return version


# Mapping from other platforms to VS Code client platform used in download URLs
_client_platform_mapping: Final[Mapping[str, str]] = {
    "linux-x64": "linux-x64",
    "alpine-x64": "linux-x64",
    "linux-deb-x64": "linux-deb-x64",
    "linux-rpm-x64": "linux-rpm-x64",
    "linux-arm64": "linux-arm64",
    "alpine-arm64": "linux-arm64",
    "linux-deb-arm64": "linux-deb-arm64",
    "linux-rpm-arm64": "linux-rpm-arm64",
    "linux-armhf": "linux-armhf",
    "linux-deb-armhf": "linux-deb-armhf",
    "linux-rpm-armhf": "linux-rpm-armhf",
    "win32-x64": "win32-x64",
    "win32-x64-user": "win32-x64-user",
    "win32-x64-archive": "win32-x64-archive",
    "win32-arm64": "win32-arm64",
    "win32-arm64-user": "win32-arm64-user",
    "win32-arm64-archive": "win32-arm64-archive",
    "darwin": "darwin",
    "darwin-x64": "darwin",
    "darwin-arm64": "darwin-arm64",
}

# Mapping from other platforms to VS Code server platform used in download URLs
_server_platform_mapping: Final[Mapping[str, str]] = {
    "linux-x64": "linux-x64",
    "alpine-x64": "linux-x64",
    "linux-deb-x64": "linux-x64",
    "linux-rpm-x64": "linux-x64",
    "linux-arm64": "linux-arm64",
    "alpine-arm64": "linux-arm64",
    "linux-deb-arm64": "linux-arm64",
    "linux-rpm-arm64": "linux-arm64",
    "linux-armhf": "linux-armhf",
    "linux-deb-armhf": "linux-armhf",
    "linux-rpm-armhf": "linux-armhf",
    "win32-x64": "win32-x64",
    "win32-x64-user": "win32-x64",
    "win32-x64-archive": "win32-x64",
    "win32-arm64": "win32-arm64",
    "win32-arm64-user": "win32-arm64",
    "win32-arm64-archive": "win32-arm64",
    "darwin": "darwin",
    "darwin-x64": "darwin",
    "darwin-arm64": "darwin-arm64",
}


# Mapping from other platforms to VS Code CLI platform used in download URLs
_cli_platform_mapping: Final[Mapping[str, str]] = {
    "linux-x64": "alpine-x64",
    "alpine-x64": "alpine-x64",
    "linux-deb-x64": "alpine-x64",
    "linux-rpm-x64": "alpine-x64",
    "linux-arm64": "alpine-arm64",
    "alpine-arm64": "alpine-arm64",
    "linux-deb-arm64": "alpine-arm64",
    "linux-rpm-arm64": "alpine-arm64",
    "linux-armhf": "linux-armhf",
    "linux-deb-armhf": "linux-armhf",
    "linux-rpm-armhf": "linux-armhf",
    "win32-x64": "win32-x64",
    "win32-x64-user": "win32-x64",
    "win32-x64-archive": "win32-x64",
    "win32-arm64": "win32-arm64",
    "win32-arm64-user": "win32-arm64",
    "win32-arm64-archive": "win32-arm64",
    "darwin": "darwin-x64",
    "darwin-x64": "darwin-x64",
    "darwin-arm64": "darwin-arm64",
}


# Mapping from other platforms to extension target platform used in download URLs
_extension_platform_mapping: Final[Mapping[str, str]] = {
    "linux-x64": "linux-x64",
    "alpine-x64": "linux-x64",
    "linux-deb-x64": "linux-x64",
    "linux-rpm-x64": "linux-x64",
    "linux-arm64": "linux-arm64",
    "alpine-arm64": "linux-arm64",
    "linux-deb-arm64": "linux-arm64",
    "linux-rpm-arm64": "linux-arm64",
    "linux-armhf": "linux-armhf",
    "linux-deb-armhf": "linux-armhf",
    "linux-rpm-armhf": "linux-armhf",
    "win32-x64": "win32-x64",
    "win32-x64-user": "win32-x64",
    "win32-x64-archive": "win32-x64",
    "win32-arm64": "win32-arm64",
    "win32-arm64-user": "win32-arm64",
    "win32-arm64-archive": "win32-arm64",
    "darwin": "darwin-x64",
    "darwin-x64": "darwin-x64",
    "darwin-arm64": "darwin-arm64",
}


def get_client_platform(platform: str) -> str:
    """Get the VS Code platform for the given platform."""
    return _client_platform_mapping.get(platform, platform)


def get_server_platform(platform: str) -> str:
    """Get the VS Code server platform for the given platform."""
    return _server_platform_mapping.get(platform, platform)


def get_cli_platform(platform: str) -> str:
    """Get the VS Code CLI platform for the given platform."""
    return _cli_platform_mapping.get(platform, platform)


def get_extension_platform(platform: str) -> str:
    """Get the VS Code extension target platform for the given platform."""
    return _extension_platform_mapping.get(platform, platform)


_all_platforms: Final[AbstractSet[str]] = {
    *_client_platform_mapping.keys(),
    *_client_platform_mapping.values(),
    *_server_platform_mapping.keys(),
    *_server_platform_mapping.values(),
    *_cli_platform_mapping.keys(),
    *_cli_platform_mapping.values(),
    *_extension_platform_mapping.keys(),
    *_extension_platform_mapping.values(),
}


assert (
    _client_platform_mapping.keys()
    == _server_platform_mapping.keys()
    == _cli_platform_mapping.keys()
    == _extension_platform_mapping.keys()
    == _all_platforms
)


def validate_platform(platform: str) -> str:
    """Check if the given platform is a valid VS Code platform."""
    if platform in _all_platforms:
        return platform
    raise ArgumentTypeError(f"Unsupported platform: {platform!r}")


def get_host_platform() -> str:
    """Get the host platform in the format used by VS Code install."""
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
        elif machine in ("armv7l", "armhf"):
            return "linux-armhf"
    raise ValueError(f"Unsupported host platform: {osname}-{machine}")


def extract_filename_from_headers(headers: Mapping[str, str]) -> str | None:
    """Get the filename from HTTP headers.

    Args:
        headers: The HTTP headers.
    """
    content_disposition = headers.get("Content-Disposition")
    header_str = ""
    if content_type := headers.get("Content-Type"):
        header_str += f"Content-Type: {content_type}\n"
    if content_disposition := headers.get("Content-Disposition"):
        header_str += f"Content-Disposition: {content_disposition}\n"
    if not header_str:
        return None
    header = HeaderParser().parsestr(header_str)
    return header.get_filename()
