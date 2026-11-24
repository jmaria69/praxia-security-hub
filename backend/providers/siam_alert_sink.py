"""SIAM Alert Sink: Forwards security incidents, reverse engineering attempts, and code exfiltration alerts to SIAM SOC."""
import datetime as dt
import json
import logging
from typing import Any, Dict, Optional
import httpx
from backend.core.config import settings

logger = logging.getLogger("praxia.siam")

class SiamAlertSink:
    def __init__(self, siam_url: Optional[str] = None, api_key: Optional[str] = None):
        self.siam_url = (siam_url or settings.SIAM_URL).rstrip("/")
        self.api_key = api_key or settings.SIAM_API_KEY
        self.enabled = settings.SIAM_ALERTS_ENABLED

    def send_alert(
        self,
        event_type: str,
        asset_name: str,
        severity: str,
        summary: str,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        timeout: float = 3.0
    ) -> Dict[str, Any]:
        """
        Sends a normalized security event to SIAM's /v1/ingest/webhook endpoint.
        Does not crash callers if SIAM is offline (fails gracefully with audit trail).
        """
        if not self.enabled:
            return {"status": "SKIPPED", "reason": "SIAM alerts disabled in settings"}

        payload = {
            "source": "praxia-security-hub",
            "asset_name": asset_name,
            "event_type": event_type,
            "severity": severity.lower(),
            "summary": summary,
            "description": description,
            "timestamp": dt.datetime.utcnow().isoformat() + "Z",
            "details": details or {}
        }

        headers = {
            "Content-Type": "application/json",
            "X-Provider": "praxia-security-hub"
        }
        if self.api_key:
            headers["X-SIAM-API-KEY"] = self.api_key

        target_url = f"{self.siam_url}/v1/ingest/webhook"

        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(target_url, json=payload, headers=headers)
                if resp.status_code in (200, 201):
                    return {
                        "status": "SENT",
                        "status_code": resp.status_code,
                        "event_id": resp.json().get("id")
                    }
                else:
                    logger.warning(f"SIAM ingest returned status {resp.status_code}: {resp.text}")
                    return {
                        "status": "FAILED",
                        "status_code": resp.status_code,
                        "response": resp.text
                    }
        except httpx.ConnectError:
            logger.warning(f"Could not connect to SIAM at {target_url} (Connection refused)")
            return {"status": "OFFLINE", "reason": "Connection to SIAM refused"}
        except Exception as e:
            logger.error(f"Error dispatching alert to SIAM: {str(e)}")
            return {"status": "ERROR", "reason": str(e)}

    def report_reverse_engineering_attempt(
        self,
        project_id: str,
        reason: str,
        severity: str = "HIGH",
        client_ip: Optional[str] = None,
        tool: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dispatched when an attempt to reverse engineer or decompile protected artifacts is detected."""
        return self.send_alert(
            event_type="software.reverse_engineering_attempt",
            asset_name=project_id,
            severity=severity,
            summary=f"Alerta Counter-REA: Intento de ingeniería inversa en '{project_id}'",
            description=f"Se detectó un intento de análisis adversarial o descompilación asistida por IA sobre el software protegido '{project_id}'. Causa: {reason}",
            details={"project_id": project_id, "reason": reason, "client_ip": client_ip, "tool": tool}
        )

    def report_code_leak_attempt(
        self,
        project_id: str,
        secrets_count: int,
        categories: list[str],
        rule_ids: list[str]
    ) -> Dict[str, Any]:
        """Dispatched when Privacy Gateway blocks code exfiltration or credential leakage."""
        return self.send_alert(
            event_type="privacy.code_exfiltration_blocked",
            asset_name=project_id,
            severity="CRITICAL",
            summary=f"Fuga Bloqueada: Intento de exfiltración de código/secretos en '{project_id}'",
            description=f"El Privacy Gateway bloqueó la transmisión de {secrets_count} secreto(s) o fragmento de código confidencial dirigido a un LLM externo.",
            details={"project_id": project_id, "categories": categories, "rule_ids": rule_ids}
        )

siam_alert_sink = SiamAlertSink()
