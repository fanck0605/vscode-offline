from __future__ import annotations

import json
import os
from gzip import GzipFile
from urllib.error import HTTPError
from urllib.request import urlopen

from vscode_offline.loggers import logger


def _download_file(url: str, filename: str) -> None:
    with urlopen(url) as resp:
        content_encoding = resp.headers.get("Content-Encoding")
        if content_encoding in {"gzip", "deflate"}:
            logger.info(f"Content encoding is {content_encoding}, using GzipFile")
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
    logger.info(f"Downloading {filename}")
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
        logger.info("============================================")


def download_vscode_server(
    commit: str, output: str, target_platform: str, cli_os: str
) -> None:
    os.makedirs(output, exist_ok=True)
    download_file(
        f"https://vscode.download.prss.microsoft.com/dbazure/download/stable/{commit}/vscode-server-linux-x64.tar.gz",
        f"{output}/vscode-server-linux-x64.tar.gz",
    )
    logger.info("============================================")
    cli_os_ = cli_os.replace("-", "_")
    download_file(
        f"https://vscode.download.prss.microsoft.com/dbazure/download/stable/{commit}/vscode_{cli_os_}_cli.tar.gz",
        f"{output}/vscode_{cli_os_}_cli.tar.gz",
    )
    logger.info("============================================")
