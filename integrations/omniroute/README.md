# OmniRoute Integration — Praxia Security Hub

OmniRoute acts as the multi-provider LLM load balancer and failover router on `127.0.0.1:20128`.

## Architecture
```
Client / Agent -> Praxia Hub (8888) -> OmniRoute (20128) -> Anthropic / OpenAI / DeepSeek
```

- Target URL: `http://127.0.0.1:20128`
- Healthcheck: Verified in `praxia-security doctor`
- SSE Streaming: Supported with real-time token stream decoding and re-assembly.
