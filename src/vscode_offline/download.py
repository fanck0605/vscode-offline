from __future__ import annotations

import json
import os
from gzip import GzipFile
from urllib.error import HTTPError
from urllib.request import urlopen

from vscode_offline.loggers import logger
from vscode_offline.utils import get_cli_os_arch


def _download_file(url: str, filename: str) -> None:
    with urlopen(url) as resp:
        content_encoding = resp.headers.get("Content-Encoding")
        if content_encoding in {"gzip", "deflate"}:
            logger.info(f"Content-Encoding is {content_encoding}, using GzipFile")
            reader = GzipFile(fileobj=resp)
        elif not content_encoding:
            reader = resp
        else:
            raise ValueError(f"Unsupported Content-Encoding: {content_encoding}")

        with reader, open(filename, "wb") as fp:
            while True:
                chunk = reader.read(1024)
                if not chunk:
                    break
                fp.write(chunk)


def download_file(
    url: str,
    filename: str,
) -> None:
    if os.path.exists(filename):
        logger.info(f"File {filename} already exists, skipping download.")
        return

    logger.info(f"Downloading {url}")
    tmp_filename = f"{filename}.tmp"

    for i in range(3):
        try:
            _download_file(url, tmp_filename)
            break
        except Exception as e:
            if isinstance(e, HTTPError) and e.code == 404:
                raise
            logger.info(f"Attempt {i + 1} failed: {e}")

    if os.path.exists(filename):
        os.remove(filename)
    os.rename(tmp_filename, filename)

    logger.info(f"Saved to {filename}")


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
    filename = f"{publisher}.{name}-{version}"
    if platform:
        filename = f"{filename}@{platform}"
    filename = f"{filename}.vsix"
    download_file(url, f"{output}/{filename}")


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
        f"{output}/vscode-server-{target_platform}.tar.gz",
    )
    target_os_arch = get_cli_os_arch(target_platform)
    target_os_arch_ = target_os_arch.replace("-", "_")
    download_file(
        f"https://update.code.visualstudio.com/commit:{commit}/cli-{target_os_arch}/stable",
        f"{output}/vscode_cli_{target_os_arch_}_cli.tar.gz",
    )
