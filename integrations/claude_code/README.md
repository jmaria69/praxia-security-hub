# Claude Code Integration — Praxia Security Hub

To connect Claude Code and Claude Desktop to Praxia Security Hub via MCP and Privacy Gateway:

## 1. Gateway Proxy Configuration
Direct Claude Code HTTP requests through the LLM Privacy Gateway:
```bash
export ANTHROPIC_BASE_URL="http://127.0.0.1:8888"
export ANTHROPIC_API_KEY="sk-praxia-managed"
```

## 2. MCP Server Configuration
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "praxia-security": {
      "command": "/home/jmari/proyectosIA/praxia-security-hub/scripts/praxia-mcp",
      "args": []
    }
  }
}
```

## Available MCP Tools
- `praxia_status`: Check health of BLA and Privacy Gateway.
- `praxia_list_projects`: List registered Praxia SaaS applications.
- `praxia_scan_prompt`: Pre-flight privacy and secret detection before sending text to external LLMs.
- `praxia_audit_artifacts`: Run REA exposure scan on project build outputs.
- `praxia_get_audit_events`: View security events and fail-closed incident history.
