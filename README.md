# vscode-offline

vscode-offline 主要用于在无网环境下安装 VSCode Server，方便使用 *Remote - SSH* 插件进行远程开发。

## 安装

```shell
pip install -U vscode-offline
```

## 优势

1. 自动识别并下载所有 `.vsix` 文件（包括间接依赖）
2. 一键安装 VSCode server 以及所有插件

## 用法

（1）在联网环境安装好 VSCode 和你需要的插件。

（2）联网环境执行如下命令，将会自动下载 VSCode server，和目前安装的所有的插件

> `--commit` 可以指定对应 VSCode 的 Commit，默认自动获取当前环境 VSCode 的 Commit。
>
> 手动查看方式：*帮助* -> *关于* -> *Commit*，

```shell
vscode-offline download \
    --target-platform linux-x64 \
    --installer ./vscode-offline-installer
```

（3）复制 `vscode-offline-installer` 到内网服务器

```shell
vscode-offline install --installer ./vscode-offline-installer
```

## 贡献

欢迎提交 Issue 和 PR 改进本项目。

## 许可证

[MIT License](./LICENSE)
