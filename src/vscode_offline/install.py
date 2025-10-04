from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections.abc import Set as AbstractSet
from pathlib import Path
from tempfile import TemporaryDirectory

from vscode_offline.loggers import logger
from vscode_offline.utils import (
    get_cli_platform,
    get_vscode_cli_bin,
    get_vscode_server_home,
)

# These extensions are excluded because they are not needed in a VS Code Server.
SERVER_EXCLUDE_EXTENSIONS = frozenset(
    [
        "ms-vscode-remote.remote-ssh",
        "ms-vscode-remote.remote-ssh-edit",
        "ms-vscode-remote.remote-wsl",
        "ms-vscode-remote.remote-containers",
        "ms-vscode.remote-explorer",
        "ms-vscode-remote.vscode-remote-extensionpack",
        "ms-vscode.remote-server",
    ]
)


def get_extension_identifier(filename: str) -> str:
    filename = os.path.splitext(filename)[0]
    identifier_version = filename.rsplit("@", maxsplit=1)[0]
    extension_identifier = identifier_version.rsplit("-", maxsplit=1)[0]
    return extension_identifier


def get_extension_target_platform(filename: str) -> str | None:
    filename = os.path.splitext(filename)[0]
    parts = filename.rsplit("@", maxsplit=1)
    if len(parts) != 2:
        return None
    return parts[1]


def install_vscode_extensions(
    code: str | os.PathLike[str],
    vsix_dir: str,
    platform: str,
    exclude: AbstractSet[str] = frozenset(),
) -> None:
    code_executable = shutil.which(code)
    for vsix_file in Path(vsix_dir).glob("*.vsix"):
        extension_identifier = get_extension_identifier(vsix_file.name)
        if extension_identifier in exclude:
            logger.info(f"Skipping excluded extension {extension_identifier}")
            continue
        # Skip extensions that are not for the current platform
        extension_target_platform = get_extension_target_platform(vsix_file.name)
        if (
            extension_target_platform is not None
            and extension_target_platform != platform
        ):
            logger.info(
                f"Skipping extension {extension_identifier} for platform {extension_target_platform}"
            )
            continue
        logger.info(f"Installing {vsix_file}")
        subprocess.check_call(
            [code, "--install-extension", vsix_file, "--force"],
            executable=code_executable,
        )
        logger.info(f"Installed {vsix_file}")


_code_version_output_pattern = re.compile(rb"\(commit ([0-9a-f]{40,})\)")


def _extract_commit_from_code_version_output(code_version_output: bytes) -> str:
    m = _code_version_output_pattern.search(code_version_output)
    if not m:
        raise ValueError("Cannot determine commit hash from code version")
    return m.group(1).decode("utf-8")


def install_vscode_server(
    server_installer: str,
    platform: str,
) -> os.PathLike[str]:
    cli_platform = get_cli_platform(platform)
    cli_platform_ = cli_platform.replace("-", "_")

    code_cli_tarball = Path(server_installer) / f"vscode_cli_{cli_platform_}_cli.tar.gz"
    with TemporaryDirectory() as tmpdir:
        subprocess.check_call(["tar", "-xzf", code_cli_tarball, "-C", tmpdir])
        tmp_code_cli = Path(tmpdir) / "code"
        version_output = subprocess.check_output(
            ["code", "--version"], executable=tmp_code_cli, cwd=tmpdir
        )
        commit = _extract_commit_from_code_version_output(version_output)
        logger.info(f"Extracted commit from `code --version`: {commit}")
        code_cli = get_vscode_cli_bin(commit)
        if os.path.exists(code_cli):
            os.remove(code_cli)
        os.makedirs(os.path.dirname(code_cli), exist_ok=True)
        os.rename(tmp_code_cli, code_cli)
    logger.info(f"Extracted vscode_cli_{cli_platform_}_cli.tar.gz to {code_cli}")

    vscode_server_tarball = Path(server_installer) / f"vscode-server-{platform}.tar.gz"
    vscode_server_home = get_vscode_server_home(commit)
    os.makedirs(vscode_server_home, exist_ok=True)
    subprocess.check_call(
        [
            "tar",
            "-xzf",
            vscode_server_tarball,
            "-C",
            vscode_server_home,
            "--strip-components=1",
        ]
    )
    logger.info(f"Extracted vscode-server-{platform}.tar.gz to {vscode_server_home}")
    return vscode_server_home
