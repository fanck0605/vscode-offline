from __future__ import annotations

import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from vscode_offline.download import download_vscode_extensions, download_vscode_server
from vscode_offline.install import install_vscode_extensions, install_vscode_server
from vscode_offline.paths import (
    get_vscode_cli_bin,
    get_vscode_extensions_config,
    get_vscode_server_home,
)

cli_os_mapping = {
    "linux-x64": "cli-alpine-x64",
}


def download(args: Namespace) -> None:
    download_vscode_server(
        args.commit,
        output=args.installer / f"cli-{args.commit}",
        target_platform=args.target_platform,
        cli_os=cli_os_mapping[args.target_platform],
    )
    extensions_config = Path(args.extensions_config).expanduser()
    download_vscode_extensions(
        extensions_config, args.target_platform, args.installer / "extensions"
    )


def install(args: Namespace) -> None:
    install_vscode_server(
        args.commit,
        installer=args.installer / f"cli-{args.commit}",
        vscode_cli_bin=get_vscode_cli_bin(args.commit),
        target_platform=args.target_platform,
        cli_os=cli_os_mapping[args.target_platform],
    )
    vscode_server_home = get_vscode_server_home(args.commit)
    install_vscode_extensions(
        Path(vscode_server_home) / "bin/code-server",
        vsix_dir=args.installer / "extensions",
    )


def make_argparser() -> ArgumentParser:
    parent_parser = ArgumentParser(add_help=False)

    parent_parser.add_argument(
        "--commit",
        type=str,
        required=True,
        help="The commit hash of the VSCode server to download, must match the version of the VSCode client.",
    )
    parent_parser.add_argument(
        "--target-platform",
        type=str,
        default="linux-x64",
        help="The target platform for the VSCode server.",
    )
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
        "--extensions-config",
        type=Path,
        default=get_vscode_extensions_config(),
        help="Path to the extensions configuration file. Will search for extensions to download.",
    )

    install_parsers = subparsers.add_parser(
        "install",
        help="Install VSCode server and extensions",
        parents=[parent_parser],
    )
    install_parsers.set_defaults(func=install)

    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = make_argparser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
