# vscode-offline

vscode-offline 主要用于在无网环境下安装 VS Code Server，方便使用 *Remote - SSH* 插件进行远程开发。

## 安装

```shell
pip install -U vscode-offline
```

## 优势

1. 自动识别并下载所有 `.vsix` 文件（包括间接依赖）
2. 一键安装 VS Code Server 以及所有插件

## VS Code 离线安装

（1）在联网环境安装好 VS Code 和你需要的插件，如 [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh), [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) 等。

（2）执行如下命令，下载 VS Code 安装包，和目前安装的所有的插件

```shell
vscode-offline download-all --installer ./vscode-offline-installer
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

## 贡献

欢迎提交 Issue 和 PR 改进本项目。

## License

Copyright (c) 2025 Chuck Fan.

Distributed under the terms of the  [MIT License](https://github.com/fanck0605/vscode-offline/blob/master/LICENSE).
