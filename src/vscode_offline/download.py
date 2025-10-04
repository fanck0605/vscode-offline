from __future__ import annotations

import json
import os
from gzip import GzipFile
from io import DEFAULT_BUFFER_SIZE
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from vscode_offline.loggers import logger
from vscode_offline.utils import get_cli_platform, get_filename_from_headers


def _download_file(
    url: str,
    directory: str | os.PathLike[str],
    filename: str | None = None,
) -> os.PathLike[str]:
    with urlopen(url) as resp:
        content_encoding = resp.headers.get("Content-Encoding")
        if content_encoding in {"gzip", "deflate"}:
            logger.info(f"Content-Encoding is {content_encoding}, using GzipFile")
            reader = GzipFile(fileobj=resp)
        elif not content_encoding:
            reader = resp
        else:
            raise ValueError(f"Unsupported Content-Encoding: {content_encoding}")

        if filename:
            file_path = Path(directory).joinpath(filename)
        else:
            filename = get_filename_from_headers(resp.headers)
            if not filename:
                raise ValueError(
                    "Cannot get filename from HTTP headers, please specify argument `filename`."
                )
            logger.info(f"Get filename `{filename}` from HTTP headers.")
            file_path = Path(directory).joinpath(filename)
            if file_path.exists():
                logger.info(f"File {file_path} already exists, skipping download.")
                return file_path

        tmp_file_path = Path(directory).joinpath(f"{filename}.tmp")
        with reader, tmp_file_path.open("wb") as fp:
            while True:
                chunk = reader.read(DEFAULT_BUFFER_SIZE)
                if not chunk:
                    break
                fp.write(chunk)

        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(tmp_file_path, file_path)

        logger.info(f"Saved to {file_path} .")
        return file_path


def download_file(
    url: str,
    directory: str | os.PathLike[str],
    filename: str | None = None,
) -> None:
    if filename:
        file_path = Path(directory).joinpath(filename)
        if file_path.exists():
            logger.info(f"File {file_path} already exists, skipping download.")
            return

    logger.info(f"Downloading {url} ...")
    for i in range(3):
        try:
            _download_file(url, directory, filename)
            break
        except Exception as e:
            if isinstance(e, HTTPError) and e.code == 404:
                raise
            logger.info(f"Attempt {i + 1} times failed: {e}")


def download_extension(
    publisher: str,
    name: str,
    version: str,
    platform: str | None = None,
    output: str = ".",
) -> None:
    url = f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{name}/{version}/vspackage"
    if platform:
        url = f"{url}?targetPlatform={platform}"
    filename = f"{publisher}.{name}-{version}{f'@{platform}' if platform else ''}.vsix"
    download_file(url, output, filename)


def download_vscode_extensions(
    extensions_config: os.PathLike[str], target_platform: str, output: str = "."
) -> None:
    logger.info(f"Reading extensions config from {extensions_config}")
    with open(extensions_config) as fp:
        data = json.loads(fp.read())

    os.makedirs(output, exist_ok=True)
    for extension in data:
        identifier = extension["identifier"]
        publisher, name = identifier["id"].split(".")
        version = extension["version"]
        try:
            download_extension(publisher, name, version, target_platform, output=output)
        except HTTPError as e:
            if e.code != 404:
                raise
            download_extension(publisher, name, version, output=output)


def download_vscode_server(
    commit: str,
    output: str,
    target_platform: str,
) -> None:
    """Download VS Code Server and CLI for the given commit and target platform.

    See Also:
        https://www.cnblogs.com/michaelcjl/p/18262833
        https://blog.csdn.net/qq_69668825/article/details/144224417
    """
    os.makedirs(output, exist_ok=True)
    download_file(
        f"https://update.code.visualstudio.com/commit:{commit}/server-{target_platform}/stable",
        output,
        f"vscode-server-{target_platform}.tar.gz",
    )
    cli_target_platform = get_cli_platform(target_platform)
    cli_target_platform_ = cli_target_platform.replace("-", "_")
    download_file(
        f"https://update.code.visualstudio.com/commit:{commit}/cli-{cli_target_platform}/stable",
        output,
        f"vscode_cli_{cli_target_platform_}_cli.tar.gz",
    )


def download_vscode_client(
    commit: str,
    output: str,
    target_platform: str,
) -> None:
    """Download VS Code for the given commit and target platform."""
    os.makedirs(output, exist_ok=True)
    download_file(
        f"https://update.code.visualstudio.com/commit:{commit}/{target_platform}/stable",
        output,
        # filename is like "VSCodeSetup-x64-1.104.3.exe" for windows
    )
