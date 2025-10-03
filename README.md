# vscode-offline

vscode-offline 主要用于在无网环境下安装 VSCode Server，方便使用 *Remote - SSH* 插件进行远程开发。

## 安装

```shell
pip install -U vscode-offline
```

## 用法

（1）在联网环境安装好 VSCode 和你需要的插件。

（2）联网环境执行如下命令，将会自动下载当前 VSCode 所有的插件

> `--commit` 为对应 VSCode 的 Commit 号，*帮助* -> *关于* -> *Commit*

```shell
vscode-offline download \
    --commit 385651c938df8a906869babee516bffd0ddb9829 \
    --target-platform linux-x64 \
    --installer ./vscode-offline-installer
```

（3）复制 `vscode-offline-installer` 到内网服务器

```shell
vscode-offline install \
    --commit 385651c938df8a906869babee516bffd0ddb9829 \
    --target-platform linux-x64 \
    --installer ./vscode-offline-installer
```

## 贡献

欢迎提交 Issue 和 PR 改进本项目。

## 许可证

[MIT License](./LICENSE)
