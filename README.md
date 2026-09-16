# fireworks-graph-mcp

独立 stdio MCP 服务：上传图 JSON、几何校验、SVG/PNG/离线 HTML 渲染，以及分块下载和 SHA-256 校验。

启动：

    uvx --from git+https://github.com/TerryHank/fireworks-graph-mcp.git fireworks-graph-mcp

仓库不包含任何凭据。

## ModelScope 配置

```json
{
  "mcpServers": {
    "fireworks": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/TerryHank/fireworks-graph-mcp.git", "fireworks-graph-mcp"]
    }
  }
}
```
