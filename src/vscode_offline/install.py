from __future__ import annotations

import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from vscode_offline.loggers import logger
from vscode_offline.utils import get_cli_os_arch, get_vscode_server_home

# These extensions are excluded because they are not needed in a VSCode server.
EXCLUDE_EXTENSIONS = {
    "ms-vscode-remote.remote-ssh",
    "ms-vscode-remote.remote-ssh-edit",
    "ms-vscode-remote.remote-wsl",
    "ms-vscode-remote.remote-containers",
    "ms-vscode.remote-explorer",
    "ms-vscode-remote.vscode-remote-extensionpack",
    "ms-vscode.remote-server",
}


def get_extension_identifier(filename: str) -> str:
    filename = os.path.splitext(filename)[0]
    identifier_version = filename.rsplit("@", maxsplit=1)[0]
    extension_identifier = identifier_version.rsplit("-", maxsplit=1)[0]
    return extension_identifier


def install_vscode_extensions(vscode_bin: os.PathLike[str], vsix_dir: str) -> None:
    for vsix_file in Path(vsix_dir).glob("*.vsix"):
        extension_identifier = get_extension_identifier(vsix_file.name)
        if extension_identifier in EXCLUDE_EXTENSIONS:
            logger.info(f"Skipping excluded extension {extension_identifier}")
            continue
        logger.info(f"Installing {vsix_file}")
        subprocess.check_call([vscode_bin, "--install-extension", vsix_file, "--force"])
        logger.info(f"Installed {vsix_file}")


def install_vscode_server(
    commit: str,
    cli_installer: str,
    vscode_cli_bin: os.PathLike[str],
    platform: str,
) -> None:
    cli_os = get_cli_os_arch(platform)
    cli_os_ = cli_os.replace("-", "_")

    vscode_cli_tarball = Path(cli_installer) / f"vscode_cli_{cli_os_}_cli.tar.gz"
    with TemporaryDirectory() as tmpdir:
        subprocess.check_call(["tar", "-xzf", vscode_cli_tarball, "-C", tmpdir])
        tmpfile = Path(tmpdir) / "code"
        if os.path.exists(vscode_cli_bin):
            os.remove(vscode_cli_bin)
        os.makedirs(os.path.dirname(vscode_cli_bin), exist_ok=True)
        os.rename(tmpfile, vscode_cli_bin)
    logger.info(f"Extracted vscode_cli_{cli_os_}_cli.tar.gz to {vscode_cli_bin}")

    vscode_server_tarball = Path(cli_installer) / f"vscode-server-{platform}.tar.gz"
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
