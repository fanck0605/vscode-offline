# vscode-offline

[![Build Status](https://github.com/fanck0605/vscode-offline/workflows/Build/badge.svg)](https://github.com/fanck0605/vscode-offline/actions/workflows/build.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI Version](https://img.shields.io/pypi/v/vscode-offline)](https://pypi.org/project/vscode-offline/)
[![License](https://img.shields.io/github/license/fanck0605/vscode-offline)](https://github.com/fanck0605/vscode-offline/blob/master/LICENSE)

**vscode-offline** 主要用于在无网环境下安装 VS Code 和 VS Code Server，方便使用 [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) 插件进行远程开发。

## 安装

```shell
pip install -U vscode-offline
```

## 优势

1. 自动识别并下载所有 `.vsix` 文件（包括间接依赖）
2. 一键安装 VS Code Server 以及其所有插件

## VS Code 离线安装

（1）在联网环境安装好 VS Code 和你需要的插件，如 [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh), [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) 等。

（2）执行如下命令，下载 VS Code 安装包，和目前安装的所有的插件

```shell
vscode-offline download-all --client-platform win32-x64 --server-platform linux-x64
```

（3）复制 `./vscode-offline-installer` 到内网 Windows 机器，安装 `client-<version>` 下的 VS Code，然后执行如下命令安装所有插件

```shell
vscode-offline install-extensions --installer ./vscode-offline-installer
```

（4）复制 `./vscode-offline-installer` 到内网 Linux 服务器，执行如下命令安装 VS Code Server 和所有插件

```shell
vscode-offline install-server --installer ./vscode-offline-installer
```

## 指定 VS Code 版本号

如果你想下载或安装指定版本的 VS Code，可以先通过 `code --version` 获取当前版本，然后通过 --code-version 参数指定版本号，例如：

```shell
vscode-offline download-all --code-version 1.104.3
```

也支持使用 commit hash 作为版本号，例如：

```shell
vscode-offline download-all --code-version commit:385651c938df8a906869babee516bffd0ddb9829
```


## 文件下载地址

如果你不想使用 `vscode-offline`，也可以手动下载对应的文件。

VS Code / VS Code Server / VS Code CLI  下载地址格式：

```shell
curl -O https://update.code.visualstudio.com/<version>/<platform>/stable
curl -O https://update.code.visualstudio.com/commit:<commit>/<platform>/stable

# 比如
curl -O https://update.code.visualstudio.com/1.104.3/cli-alpine-x64/stable
curl -O https://update.code.visualstudio.com/commit:385651c938df8a906869babee516bffd0ddb9829/win32-x64/stable
```


VS Code Extension 下载地址格式：

```shell
curl -O https://marketplace.visualstudio.com/_apis/public/gallery/publishers/<publisher>/vsextensions/<extension>/<version>/vspackage?targetPlatform=<platform>

# 比如
curl -O https://marketplace.visualstudio.com/_apis/public/gallery/publishers/ms-python/vsextensions/python/2025.14.0/vspackage?targetPlatform=linux-x64
```

Platform 映射关系:

| VS Code             | VS Code Server      | VS Code CLI      | VS Code Extension |
| ------------------- | ------------------- | ---------------- | ----------------- |
| win32-x64           | server-win32-x64    | cli-win32-x64    | win32-x64         |
| win32-x64-user      | server-win32-x64    | cli-win32-x64    | win32-x64         |
| win32-x64-archive   | server-win32-x64    | cli-win32-x64    | win32-x64         |
| win32-arm64         | server-win32-arm64  | cli-win32-arm64  | win32-arm64       |
| win32-arm64-user    | server-win32-arm64  | cli-win32-arm64  | win32-arm64       |
| win32-arm64-archive | server-win32-arm64  | cli-win32-arm64  | win32-arm64       |
| linux-x64           | server-linux-x64    | cli-alpine-x64   | linux-x64         |
| linux-deb-x64       | server-linux-x64    | cli-alpine-x64   | linux-x64         |
| linux-rpm-x64       | server-linux-x64    | cli-alpine-x64   | linux-x64         |
| linux-arm64         | server-linux-arm64  | cli-alpine-arm64 | linux-arm64       |
| linux-deb-arm64     | server-linux-arm64  | cli-alpine-arm64 | linux-arm64       |
| linux-rpm-arm64     | server-linux-arm64  | cli-alpine-arm64 | linux-arm64       |
| linux-armhf         | server-linux-armhf  | cli-linux-armhf  | linux-armhf       |
| linux-deb-armhf     | server-linux-armhf  | cli-linux-armhf  | linux-armhf       |
| linux-rpm-armhf     | server-linux-armhf  | cli-linux-armhf  | linux-armhf       |
| darwin              | server-darwin       | cli-darwin-x64   | darwin-x64        |
| darwin-arm64        | server-darwin-arm64 | cli-darwin-arm64 | darwin-arm64      |


## 贡献

欢迎提交 Issue 和 PR 改进本项目。

## License

Copyright (c) 2025 Chuck Fan.

Distributed under the terms of the  [MIT License](https://github.com/fanck0605/vscode-offline/blob/master/LICENSE).
