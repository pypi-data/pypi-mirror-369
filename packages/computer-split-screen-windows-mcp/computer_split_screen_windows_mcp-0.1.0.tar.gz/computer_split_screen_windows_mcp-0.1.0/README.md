# computer-split-screen-windows-mcp

Windows-only MCP server that exposes split-screen tools (halves, quadrants, thirds) plus maximize/minimize.  
Works with MCP clients via `uvx`.

## Install / Run via MCP client

Configure your MCP client:

```json
{
  "mcpServers": {
    "splitwin": {
      "command": "uvx",
      "args": ["computer-split-screen-windows-mcp"],
      "env": {}
    }
  }
}
