# Praxia Security Hub — Deployment & Operations Guide

## 1. Quickstart (Local Development)
```bash
cd /home/jmari/proyectosIA/praxia-security-hub

# 1. Activate dedicated Python virtual environment
source .venv/bin/activate

# 2. Run backend service
uvicorn backend.main:app --host 127.0.0.1 --port 8888 --reload

# 3. CLI usage
./scripts/praxia-security status
./scripts/praxia-security projects list
./scripts/praxia-security privacy scan --text "Prueba de escaneo"
```

## 2. Production Docker Deployment
```bash
docker-compose up -d --build
```
The service binds to host network mode to interface directly with local Headroom (`8787`) and OmniRoute (`20128`).
