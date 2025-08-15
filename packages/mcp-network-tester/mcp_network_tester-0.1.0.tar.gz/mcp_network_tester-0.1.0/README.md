# MCP 网络连通性测试服务（Python）

该服务提供在模型调试与运维排障场景中常用的网络连通性测试能力：TCP 连通检查、次数统计的“TCP ping”、DNS 解析以及系统 `ping`。

## 安装

- 从源码：
  ```bash
  pip install -r requirements.txt
  ```
- 从 PyPI（发布后）：
  ```bash
  pip install mcp-network-tester
  ```

> 建议使用虚拟环境。

## 运行（命令行）
安装后将提供命令 `mcp-network-tester`，以 stdio 方式启动 MCP 服务器：
```bash
mcp-network-tester
```

## 运行（配合 MCP Inspector）
1. 启动 Inspector：
   ```bash
   npx @modelcontextprotocol/inspector
   ```
2. 在 Inspector 中添加自定义服务器：
   - Command: `mcp-network-tester`
3. 连接后即可在 Tools 面板看到以下工具：`tcp_check`、`tcp_ping`、`dns_resolve`、`system_ping`。

## 将其接入到支持 MCP 的客户端
以通用配置为例：
```json
{
  "mcpServers": {
    "fetch": {
      "args": [
        "-m",
        "mcp_network_tester"
      ],
      "command": "python"
    }
  }
}
```

## 工具说明
- `tcp_check(host: str, port: int, timeout_seconds: float = 2.0)`
  - 单次 TCP 连接测试，返回 JSON 字符串，含 `reachable` 与 `latency_ms`。
- `tcp_ping(host: str, port: int, count: int = 4, interval_seconds: float = 0.2, timeout_seconds: float = 2.0)`
  - 多次 TCP 连接测试，统计成功率与时延（适合排查本地到 Docker 暴露端口是否可达）。
- `dns_resolve(host: str)`
  - 解析 A/AAAA 记录，返回所有地址。
- `system_ping(target: str, count: int = 4, timeout_seconds: float = 2.0, size: int = 32)`
  - 调用系统 `ping`（Windows 与 Linux/macOS 自动适配）。可能需要权限。

## 发布到 PyPI（公共平台）
1. 安装构建与发布工具：
   ```bash
   pip install build twine
   ```
2. 构建分发包：
   ```bash
   python -m build
   ```
   生成 `dist/*.tar.gz` 与 `dist/*.whl`。
3. 上传到 TestPyPI 验证：
   ```bash
   twine upload -r testpypi dist/*
   ```
4. 上传到正式 PyPI：
   ```bash
   twine upload dist/*
   ```

> 请在 `pyproject.toml` 中更新作者信息、主页链接等元数据；确保 `LICENSE` 为你选择的许可协议（默认 MIT）。版本号按语义化版本管理递增。

## 注意
- `system_ping` 依赖系统命令；若不可用，将返回错误信息。
- TCP 检测依赖目标服务监听状态与本机出站规则，失败时请结合 DNS、系统防火墙与容器网络配置综合排查。
