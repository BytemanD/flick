# flick
开发工具管理


## 开发

安装依赖

```bash
uv sync
```

启动web服务

```bash
$env:PYTHONPATH='src'
uv run python -m flick.cmd.cli -d --dev
```

启动web服务+webview

```bash
$env:PYTHONPATH='src'
uv run python -m flick.cmd.cli -d --dev --webview
```
