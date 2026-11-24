# Codex Integration — Praxia Security Hub

## MCP Configuration for Codex / Cursor
In your Cursor or Codex MCP settings (`~/.cursor/mcp.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "praxia-security": {
      "command": "/home/jmari/proyectosIA/praxia-security-hub/scripts/praxia-mcp"
    }
  }
}
```

## Environment Proxying
```bash
export OPENAI_BASE_URL="http://127.0.0.1:8888/v1"
```
Requests will automatically pass through the PII pseudonymization and fail-closed secret scanner before routing upstream to OmniRoute (`20128`) or Headroom (`8787`).
