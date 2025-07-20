# flick
开发工具管理


## 开发

安装虚拟环境

```bash
uv sync
```

### 启动web服务

powershell 执行

```bash
$env:PYTHONPATH='src'
```

linux 执行

```bash
export PYTHONPATH=src
```

启动web服务

```bash
uv run python -m flick.cmd.cli serve -d --dev
```

启动web服务+webview

```bash
$env:PYTHONPATH='src'
uv run python -m flick.cmd.cli serve -d --dev --webview
```

## 安装依赖

> ubuntu
```bash
apt-get install -y python3-cleo python3-tornado python3-httpx python3-requests python3-docker python3-retry python3-psutil python3-distro python3-webview
```


```bash
pyinstaller src/flick/cmd/cli.py --onefile -n flick --add-data '../flick-view/dist;./flick-view'
```