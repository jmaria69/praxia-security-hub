# Gemini CLI Integration — Praxia Security Hub

## Environment Setup
Route Gemini CLI or SDK traffic through the Praxia Privacy Gateway:
```bash
export GEMINI_API_ENDPOINT="http://127.0.0.1:8888"
```

## MCP Tools Integration
Add to your Gemini CLI agent extensions:
```bash
gemini mcp add praxia-security /home/jmari/proyectosIA/praxia-security-hub/scripts/praxia-mcp
```
