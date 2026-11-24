# Integración Praxia Security Hub ⟷ SIAM (SIEM & AI SOC)

Esta integración conecta **Praxia Security Hub** (motor de protección de software y privacidad LLM) con **SIAM** (el SOC virtual con inteligencia artificial de Praxia Labs).

---

## 1. Arquitectura de Detección de Amenazas

```
┌────────────────────────────────────────────────────────────────────────┐
│                        VECTORES DE AMENAZA                             │
│  • Intento de descompilación de código mediante IA (Counter-REA)       │
│  • Exfiltración o copia de código fuente confidencial en prompts LLM   │
│  • Fuga de credenciales o API keys hacia servicios externos            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Interceptado por
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     PRAXIA SECURITY HUB                                │
│                                                                        │
│  1. Privacy Gateway: Bloqueo Fail-Closed de secretos y código fuente   │
│  2. Motor BLA: Inyección de escudos adversariales y auditoría REA      │
│  3. Token Vault AES-256-GCM: Seudonimización reversible                │
│  4. SIAM Alert Sink (`siam_alert_sink.py`): Despacho de telemetría     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    │ Eventos JSON (POST /v1/ingest/webhook)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        SIAM (SOC VIRTUAL 2.0)                          │
│                                                                        │
│  • Correlación automática de incidentes por activo                     │
│  • Notificaciones y difusión SSE en tiempo real                        │
│  • AI SOC Analyst con herramientas forenses MCP                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Herramientas MCP para el Analista IA de SIAM

El archivo de configuración MCP se ha registrado en `SIAM/.claude/mcp.json`. Permite al agente de IA de SIAM ejecutar las siguientes herramientas forenses:

### `praxia_detect_code_leak`
- **Propósito:** Analiza fragmentos de código, texto o prompts sospechosos.
- **Acción:** Detecta si contienen código de los proyectos propietarios de Praxia Labs (`AdminApp`, `siam`, `saludos`, `radar-ai`, `crm-it`, `ageverify`), mide la entropía de Shannon y verifica si viola la política Fail-Closed.
- **Salida:** Clasificación de riesgo de exfiltración (`LOW`, `HIGH`, `CRITICAL`), firmas detectadas y secretos interceptados.

### `praxia_check_reverse_engineering`
- **Propósito:** Evalúa el nivel de vulnerabilidad de un artefacto compilado ante herramientas de ingeniería inversa asistidas por IA.
- **Acción:** Ejecuta el auditor BLA, calcula el **REA Exposure Score** (0–100) y verifica si tiene activos los escudos adversariales.
- **Salida:** Estado de blindaje (`PROTECTED`, `MEDIUM`, `HIGH`) y acciones de remediación recomendadas.

### `praxia_forward_alert_to_siam`
- **Propósito:** Permite a los agentes despachar alertas forenses formalizadas directamente a la cola de ingesta de incidentes de SIAM.

### `praxia_audit_artifacts` y `praxia_scan_prompt`
- **Propósito:** Permiten auditar distribuciones en disco y seudonimizar datos antes de invocar cualquier modelo fundacional.

---

## 3. Ingesta Automática de Alertas en SIAM

Cuando el Gateway de Praxia Hub detecta un intento de exfiltración o ingeniería inversa, envía inmediatamente un payload normalizado a SIAM:

```http
POST http://127.0.0.1:8001/v1/ingest/webhook
X-Provider: praxia-security-hub
Content-Type: application/json

{
  "source": "praxia-security-hub",
  "asset_name": "AdminApp",
  "event_type": "privacy.code_exfiltration_blocked",
  "severity": "critical",
  "summary": "Fuga Bloqueada: Intento de exfiltración de código/secretos en 'AdminApp'",
  "description": "El Privacy Gateway bloqueó la transmisión de 1 secreto(s) o fragmento de código confidencial dirigido a un LLM externo.",
  "details": {
    "project_id": "adminapp",
    "categories": ["ANTHROPIC_KEY"],
    "rule_ids": ["RULE_SECRETS_BLOCK"]
  }
}
```

---

## 4. Configuración de Entorno

En el archivo `.env` de Praxia Security Hub:
```bash
SIAM_URL=http://127.0.0.1:8001
SIAM_ALERTS_ENABLED=true
SIAM_API_KEY=tu-clave-si-esta-configurada
```
