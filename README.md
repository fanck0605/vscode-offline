# vscode-offline

vscode-offline 主要用于在无网环境下安装 VS Code Server，方便使用 *Remote - SSH* 插件进行远程开发。

## 安装

```shell
pip install -U vscode-offline
```

## 优势

1. 自动识别并下载所有 `.vsix` 文件（包括间接依赖）
2. 一键安装 VS Code Server 以及所有插件

## VS Code Server 安装

（1）在联网环境安装好 VSCode 和你需要的插件。

（2）执行如下命令，将会自动下载 VS Code Server，和目前安装的所有的插件

> `--commit` 可以指定对应 VSCode 的 Commit，默认自动获取当前环境 VSCode 的 Commit。
>
> 手动查看方式：*帮助* -> *关于* -> *Commit*，

```shell
vscode-offline download-server --target-platform linux-x64 --installer ./vscode-offline-installer
```

（3）复制 `./vscode-offline-installer` 到内网服务器

```shell
vscode-offline install-server --installer ./vscode-offline-installer
```

## VS Code 插件安装

（1）联网环境执行如下命令，将会自动下载 VSCode 目前安装的所有的插件

```shell
vscode-offline download-extensions --target-platform win32-x64 --installer ./vscode-offline-installer
```

（2）复制 `./vscode-offline-installer` 到内网机器

```shell
vscode-offline install-extensions --installer ./vscode-offline-installer
```

## 贡献

欢迎提交 Issue 和 PR 改进本项目。

## License

Copyright (c) 2025 Chuck Fan.

Distributed under the terms of the  [MIT License](https://github.com/fanck0605/vscode-offline/blob/master/LICENSE).
