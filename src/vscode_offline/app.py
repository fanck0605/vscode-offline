from __future__ import annotations

import logging
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from vscode_offline.download import (
    download_vscode_extensions,
    download_vscode_server,
)
from vscode_offline.install import (
    SERVER_EXCLUDE_EXTENSIONS,
    install_vscode_extensions,
    install_vscode_server,
)
from vscode_offline.loggers import logger
from vscode_offline.utils import (
    get_host_platform,
    get_vscode_cli_bin,
    get_vscode_commit_from_code_version,
    get_vscode_commit_from_installer,
    get_vscode_extensions_config,
    get_vscode_server_home,
)


def cmd_download_server(args: Namespace) -> None:
    if args.commit is None:
        args.commit = get_vscode_commit_from_code_version()
        if args.commit is None:
            logger.info(
                "Cannot determine commit from `code --version`, please specify --commit manually."
            )
            raise ValueError("Please specify --commit when installing.")

    download_vscode_server(
        args.commit,
        output=args.installer / f"cli-{args.commit}",
        target_platform=args.target_platform,
    )
    extensions_config = Path(args.extensions_config).expanduser()
    download_vscode_extensions(
        extensions_config, args.target_platform, args.installer / "extensions"
    )


def cmd_install_server(args: Namespace) -> None:
    host_platform = get_host_platform()
    if args.commit is None:
        try:
            args.commit = get_vscode_commit_from_installer(
                args.installer, host_platform
            )
        except Exception as e:
            raise ValueError(
                f"{e}, please specify `--commit` when installing."
            ) from None

    install_vscode_server(
        args.commit,
        cli_installer=args.installer / f"cli-{args.commit}",
        vscode_cli_bin=get_vscode_cli_bin(args.commit),
        platform=host_platform,
    )
    vscode_server_home = get_vscode_server_home(args.commit)
    install_vscode_extensions(
        Path(vscode_server_home) / "bin/code-server",
        vsix_dir=args.installer / "extensions",
        platform=host_platform,
        exclude=SERVER_EXCLUDE_EXTENSIONS,
    )


def cmd_download_extensions(args: Namespace) -> None:
    extensions_config = Path(args.extensions_config).expanduser()
    download_vscode_extensions(
        extensions_config, args.target_platform, args.installer / "extensions"
    )


def cmd_install_extensions(args: Namespace) -> None:
    host_platform = get_host_platform()
    install_vscode_extensions(
        os.fspath("code"),
        vsix_dir=args.installer / "extensions",
        platform=host_platform,
    )


def make_argparser() -> ArgumentParser:
    parent_parser = ArgumentParser(add_help=False)

    parent_parser.add_argument(
        "--installer",
        type=Path,
        default="./vscode-offline-installer",
        help="The output directory for downloaded files. Also used as the installer directory.",
    )

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    download_server_parser = subparsers.add_parser(
        "download-server",
        help="Download VS Code Server and extensions",
        parents=[parent_parser],
    )
    download_server_parser.set_defaults(func=cmd_download_server)
    download_server_parser.add_argument(
        "--commit",
        type=str,
        help="The commit hash of the VS Code Server to download, must match the version of the VSCode client.",
    )
    download_server_parser.add_argument(
        "--target-platform",
        type=str,
        required=True,
        help="The target platform of the VS Code Server to download.",
    )
    download_server_parser.add_argument(
        "--extensions-config",
        type=Path,
        default=get_vscode_extensions_config(),
        help="Path to the extensions configuration file. Will search for extensions to download.",
    )

    install_server_parser = subparsers.add_parser(
        "install-server",
        help="Install VS Code Server and extensions",
        parents=[parent_parser],
    )
    install_server_parser.set_defaults(func=cmd_install_server)
    install_server_parser.add_argument(
        "--commit",
        type=str,
        help="The commit hash of the VS Code Server to install.",
    )

    download_extensions_parser = subparsers.add_parser(
        "download-extensions",
        help="Download VS Code Server and extensions",
        parents=[parent_parser],
    )
    download_extensions_parser.set_defaults(func=cmd_download_extensions)
    download_extensions_parser.add_argument(
        "--target-platform",
        type=str,
        required=True,
        help="The target platform of the VSCode extensions to download.",
    )
    download_extensions_parser.add_argument(
        "--extensions-config",
        type=Path,
        default=get_vscode_extensions_config(),
        help="Path to the extensions configuration file. Will search for extensions to download.",
    )

    install_extensions_parser = subparsers.add_parser(
        "install-extensions",
        help="Install VSCode extensions",
        parents=[parent_parser],
    )
    install_extensions_parser.set_defaults(func=cmd_install_extensions)
    download_extensions_parser.add_argument(
        "--code",
        type=str,
        default="code",
        help="Path to the `code` binary.",
    )

    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = make_argparser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
