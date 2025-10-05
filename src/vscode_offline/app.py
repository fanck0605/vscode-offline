from __future__ import annotations

import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from vscode_offline._version import __version__
from vscode_offline.download import (
    download_vscode_client,
    download_vscode_extensions,
    download_vscode_server,
)
from vscode_offline.install import (
    SERVER_EXCLUDE_EXTENSIONS,
    install_vscode_extensions,
    install_vscode_server,
)
from vscode_offline.utils import (
    get_client_platform,
    get_default_code_version,
    get_extension_platform,
    get_host_platform,
    get_server_platform,
    get_vscode_extensions_config,
    get_vscode_version_from_server_installer,
    validate_platform,
)


def cmd_download_server(args: Namespace) -> None:
    if args.code_version is None:
        args.code_version = get_default_code_version()
        if args.code_version is None:
            raise ValueError(
                "Cannot determine version from `code --version`, please specify `--version` when downloading."
            )

    download_vscode_server(
        args.code_version,
        output=args.installer / args.code_version.replace(":", "-"),
        platform=get_server_platform(args.platform),
    )
    extensions_config = Path(args.extensions_config).expanduser()
    download_vscode_extensions(
        extensions_config,
        target_platforms={
            get_extension_platform(args.platform),
        },
        output=args.installer / "extensions",
    )


def cmd_install_server(args: Namespace) -> None:
    host_platform = get_host_platform()
    if args.code_version is None:
        try:
            args.code_version = get_vscode_version_from_server_installer(
                args.installer, host_platform
            )
        except Exception as e:
            raise ValueError(
                f"{e}, please specify `--version` when installing."
            ) from None

    vscode_server_home = install_vscode_server(
        server_installer=args.installer / args.code_version.replace(":", "-"),
        platform=get_server_platform(host_platform),
    )
    install_vscode_extensions(
        Path(vscode_server_home) / "bin/code-server",
        vsix_dir=args.installer / "extensions",
        platform=get_extension_platform(host_platform),
        exclude=SERVER_EXCLUDE_EXTENSIONS,
    )


def cmd_download_extensions(args: Namespace) -> None:
    extensions_config = Path(args.extensions_config).expanduser()
    download_vscode_extensions(
        extensions_config,
        target_platforms={
            get_extension_platform(args.platform),
        },
        output=args.installer / "extensions",
    )


def cmd_install_extensions(args: Namespace) -> None:
    host_platform = get_host_platform()
    install_vscode_extensions(
        args.code,
        vsix_dir=args.installer / "extensions",
        platform=get_extension_platform(host_platform),
    )


def cmd_download_client(args: Namespace) -> None:
    if args.code_version is None:
        args.code_version = get_default_code_version()
        if args.code_version is None:
            raise ValueError(
                "Cannot determine version from `code --version`, please specify `--version` manually."
            )

    download_vscode_client(
        args.code_version,
        output=args.installer / args.code_version.replace(":", "-"),
        platform=get_client_platform(args.platform),
    )
    extensions_config = Path(args.extensions_config).expanduser()
    download_vscode_extensions(
        extensions_config,
        target_platforms={
            get_extension_platform(args.platform),
        },
        output=args.installer / "extensions",
    )


def cmd_download_all(args: Namespace) -> None:
    if args.code_version is None:
        args.code_version = get_default_code_version()
        if args.code_version is None:
            raise ValueError(
                "Cannot determine version from `code --version`, please specify `--version` manually."
            )

    download_vscode_server(
        args.code_version,
        output=args.installer / args.code_version.replace(":", "-"),
        platform=get_server_platform(args.server_platform),
    )
    download_vscode_client(
        args.code_version,
        output=args.installer / args.code_version.replace(":", "-"),
        platform=get_client_platform(args.client_platform),
    )
    extensions_config = Path(args.extensions_config).expanduser()
    download_vscode_extensions(
        extensions_config,
        target_platforms={
            get_extension_platform(args.server_platform),
            get_extension_platform(args.client_platform),
        },
        output=args.installer / "extensions",
    )


def cmd_version(args: Namespace) -> None:
    # print version instead of logging
    print(__version__)


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

    version_parser = subparsers.add_parser(
        "version",
        help="Show version information",
    )
    version_parser.set_defaults(func=cmd_version)

    download_server_parser = subparsers.add_parser(
        "download-server",
        help="Download VS Code Server and extensions",
        parents=[parent_parser],
    )
    download_server_parser.set_defaults(func=cmd_download_server)
    download_server_parser.add_argument(
        "--code-version",
        type=str,
        help="The version of the VS Code Server to download, must match the version of the VS Code Client.",
    )
    download_server_parser.add_argument(
        "--platform",
        type=validate_platform,
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
        "--code-version",
        type=str,
        help="The version of the VS Code Server to install.",
    )

    download_extensions_parser = subparsers.add_parser(
        "download-extensions",
        help="Download VS Code Server and extensions",
        parents=[parent_parser],
    )
    download_extensions_parser.set_defaults(func=cmd_download_extensions)
    download_extensions_parser.add_argument(
        "--platform",
        type=validate_platform,
        required=True,
        help="The target platform of the VS Code extensions to download.",
    )
    download_extensions_parser.add_argument(
        "--extensions-config",
        type=Path,
        default=get_vscode_extensions_config(),
        help="Path to the extensions configuration file. Will search for extensions to download.",
    )

    install_extensions_parser = subparsers.add_parser(
        "install-extensions",
        help="Install VS Code extensions",
        parents=[parent_parser],
    )
    install_extensions_parser.set_defaults(func=cmd_install_extensions)
    install_extensions_parser.add_argument(
        "--code",
        type=str,
        default="code",
        help="Path to the `code` binary.",
    )

    download_client_parser = subparsers.add_parser(
        "download-client",
        help="Download VS Code and extensions",
        parents=[parent_parser],
    )
    download_client_parser.set_defaults(func=cmd_download_client)
    download_client_parser.add_argument(
        "--code-version",
        type=str,
        help="The version of the VS Code to download, must match the version of the VS Code Client.",
    )
    download_client_parser.add_argument(
        "--platform",
        type=validate_platform,
        required=True,
        help="The target platform of the VS Code to download.",
    )
    download_client_parser.add_argument(
        "--extensions-config",
        type=Path,
        default=get_vscode_extensions_config(),
        help="Path to the extensions configuration file. Will search for extensions to download.",
    )

    download_all_parser = subparsers.add_parser(
        "download-all",
        help="Download VS Code server, client and extensions, all in one command",
        parents=[parent_parser],
    )
    download_all_parser.set_defaults(func=cmd_download_all)
    download_all_parser.add_argument(
        "--code-version",
        type=str,
        help="The version of the VS Code to download, defaults to `code --version` at current environment.",
    )
    download_all_parser.add_argument(
        "--server-platform",
        type=validate_platform,
        required=True,
        help="The target platform of the VS Code Server to download, defaults to linux-x64.",
    )
    download_all_parser.add_argument(
        "--client-platform",
        type=validate_platform,
        required=True,
        help="The target platform of the VS Code to download, defaults to win32-x64.",
    )
    download_all_parser.add_argument(
        "--extensions-config",
        type=Path,
        default=get_vscode_extensions_config(),
        help="Path to the extensions configuration file. Will search for extensions to download.",
    )

    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = make_argparser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
