from __future__ import annotations

import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from vscode_offline.download import download_vscode_extensions, download_vscode_server
from vscode_offline.install import install_vscode_extensions, install_vscode_server
from vscode_offline.loggers import logger
from vscode_offline.utils import (
    get_host_platform,
    get_vscode_cli_bin,
    get_vscode_commit_from_code_version,
    get_vscode_commit_from_installer,
    get_vscode_extensions_config,
    get_vscode_server_home,
)


def download(args: Namespace) -> None:
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


def install(args: Namespace) -> None:
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

    download_parser = subparsers.add_parser(
        "download",
        help="Download VSCode server and extensions",
        parents=[parent_parser],
    )
    download_parser.set_defaults(func=download)
    download_parser.add_argument(
        "--commit",
        type=str,
        help="The commit hash of the VSCode server to download, must match the version of the VSCode client.",
    )
    download_parser.add_argument(
        "--target-platform",
        type=str,
        required=True,
        help="The target platform of the VSCode server to download.",
    )
    download_parser.add_argument(
        "--extensions-config",
        type=Path,
        default=get_vscode_extensions_config(),
        help="Path to the extensions configuration file. Will search for extensions to download.",
    )

    install_parser = subparsers.add_parser(
        "install",
        help="Install VSCode server and extensions",
        parents=[parent_parser],
    )
    install_parser.set_defaults(func=install)
    install_parser.add_argument(
        "--commit",
        type=str,
        help="The commit hash of the VSCode server to install.",
    )

    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = make_argparser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
