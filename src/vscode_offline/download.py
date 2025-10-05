from __future__ import annotations

import json
import os
from collections.abc import Set as AbstractSet
from gzip import GzipFile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from vscode_offline.loggers import logger
from vscode_offline.utils import extract_filename_from_headers, get_cli_platform

_DOWNLOAD_CHUNK_SIZE = 4 * 1024 * 1024  # 4 MiB


def _download_file_once(
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
            filename = extract_filename_from_headers(resp.headers)
            if not filename:
                raise ValueError(
                    "Cannot extract filename from HTTP headers, please specify argument `filename`."
                )
            logger.info(f"Extracted filename {filename} from HTTP headers.")
            file_path = Path(directory).joinpath(filename)
            if file_path.exists():
                logger.info(f"File {file_path} already exists, skipping download.")
                return file_path

        tmp_file_path = Path(directory).joinpath(f"{filename}.tmp")
        with reader, tmp_file_path.open("wb") as fp:
            while True:
                chunk = reader.read(_DOWNLOAD_CHUNK_SIZE)
                if not chunk:
                    break
                fp.write(chunk)

        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(tmp_file_path, file_path)

        logger.info(f"Saved to {file_path} .")
        return file_path


def _download_file(
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
    attempt_num = 0
    while True:
        try:
            _download_file_once(url, directory, filename)
            break
        except Exception as e:
            if isinstance(e, HTTPError) and e.code == 404:
                raise
            attempt_num += 1
            if attempt_num >= 3:
                raise
            logger.info(f"Attempt {attempt_num} times failed: {e}")


def _download_extension(
    publisher: str,
    name: str,
    version: str,
    platform: str | None = None,
    output: str | os.PathLike[str] = ".",
) -> None:
    url = f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{name}/{version}/vspackage"
    if platform:
        url = f"{url}?targetPlatform={platform}"
    filename = f"{publisher}.{name}-{version}{f'@{platform}' if platform else ''}.vsix"
    _download_file(url, output, filename)


def download_vscode_extensions(
    extensions_config: os.PathLike[str],
    target_platforms: AbstractSet[str],
    output: str | os.PathLike[str] = ".",
) -> None:
    """Download VS Code extensions listed in the given extensions config file.

    Args:
        extensions_config: Path to the extensions config file, which is a JSON file
            containing a list of extensions with their publisher, name, and version.
        target_platforms: List of target platforms for which to download the extensions.
        output: Directory to save the downloaded extensions.
    """
    logger.info(f"Reading extensions config from {extensions_config}")
    with open(extensions_config) as fp:
        data = json.loads(fp.read())

    os.makedirs(output, exist_ok=True)
    for extension in data:
        identifier = extension["identifier"]
        publisher, name = identifier["id"].split(".")
        version = extension["version"]

        requires_fallback_download = False
        for target_platform in target_platforms:
            try:
                _download_extension(
                    publisher, name, version, target_platform, output=output
                )
            except HTTPError as e:
                if e.code == 404:
                    requires_fallback_download = True
                    continue
                raise
        if requires_fallback_download:
            _download_extension(publisher, name, version, output=output)


def _download_vscode(
    version: str,
    output: str,
    platform: str,
) -> None:
    """Download VS Code for the given version and target platform."""

    # filename is like
    # "VS CodeSetup-x64-1.104.3.exe" for windows VS Code,
    # "vscode-server-linux-x64.tar.gz" for linux VS Code Server,
    # "vscode_cli_alpine_x64_cli.tar.gz" for linux VS Code CLI.
    _download_file(
        f"https://update.code.visualstudio.com/{version}/{platform}/stable", output
    )


def download_vscode_server(
    version: str,
    output: str,
    platform: str,
) -> None:
    """Download VS Code Server and CLI for the given commit and target platform.

    See Also:
        https://www.cnblogs.com/michaelcjl/p/18262833
        https://blog.csdn.net/qq_69668825/article/details/144224417
    """
    os.makedirs(output, exist_ok=True)
    _download_vscode(version, output, f"server-{platform}")
    cli_platform = get_cli_platform(platform)
    _download_vscode(version, output, f"cli-{cli_platform}")


def download_vscode_client(
    version: str,
    output: str,
    platform: str,
) -> None:
    """Download VS Code Client for the given version and target platform."""
    os.makedirs(output, exist_ok=True)
    _download_vscode(version, output, platform)
