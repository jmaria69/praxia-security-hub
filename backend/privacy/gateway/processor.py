"""Privacy Gateway Processor: Orchestrates inspection, pseudonymization and fail-closed policies."""
import json
from typing import Any, Optional
from pydantic import BaseModel
from backend.privacy.pii_detector.detector import pii_detector, PIIDetectionResult
from backend.privacy.secret_scanner.scanner import secret_scanner, SecretFinding
from backend.privacy.classifier.classifier import data_classifier, ClassificationDecision, DataClassificationLevel
from backend.privacy.token_vault.vault import token_vault
from backend.core.errors import FailClosedException, PolicyViolationError
from backend.audit.logger import audit_logger

class ProcessingResult(BaseModel):
    original_text_masked: str
    processed_text: str
    classification: ClassificationDecision
    pii_entities_count: int
    secrets_count: int
    substitutions: dict[str, str]  # surrogate -> entity_type (NEVER logs original plaintext)
    allowed_to_forward: bool

class PrivacyGatewayProcessor:
    def process_prompt(
        self,
        text: str,
        project_id: str = "default",
        session_id: str = "default_session",
        project_policy: Optional[dict[str, Any]] = None
    ) -> ProcessingResult:
        policy = project_policy or {}
        fail_closed_enabled = policy.get("fail_closed", True)
        default_class = policy.get("classification_default", "INTERNAL")

        # 1. Scan for Secrets
        secret_findings = secret_scanner.scan(text)

        # 2. Detect PII
        pii_findings = pii_detector.detect(text)

        # 3. Classify Data
        classification = data_classifier.classify(
            text=text,
            pii_results=pii_findings,
            secret_findings=secret_findings,
            project_default=default_class
        )

        # 4. Enforce Fail-Closed if secrets exist
        if classification.has_secrets:
            audit_logger.log_incident(
                category="SECRET_LEAKAGE_ATTEMPT",
                severity="CRITICAL",
                summary=f"Blocked request for project '{project_id}': {len(secret_findings)} secret(s) detected",
                project_id=project_id,
                details={
                    "rule_ids": [s.rule_id for s in secret_findings],
                    "categories": [s.category for s in secret_findings]
                }
            )
            # Dispatch real-time incident alert to SIAM SOC
            try:
                from backend.providers.siam_alert_sink import siam_alert_sink
                siam_alert_sink.report_code_leak_attempt(
                    project_id=project_id,
                    secrets_count=len(secret_findings),
                    categories=[s.category for s in secret_findings],
                    rule_ids=[s.rule_id for s in secret_findings]
                )
            except Exception:
                pass

            if fail_closed_enabled:
                raise FailClosedException(
                    "Security Gateway Policy: Secrets or credentials detected in prompt. Request blocked by FAIL-CLOSED policy.",
                    details={"secrets_detected": len(secret_findings)}
                )

        # 5. Apply Reversible Pseudonymization if needed
        processed_text = text
        substitutions: dict[str, str] = {}

        if classification.requires_pseudonymization and pii_findings:
            # Deduplicate overlapping entity intervals (prefer longer match or higher score)
            cleaned_findings: list[PIIDetectionResult] = []
            sorted_by_len = sorted(pii_findings, key=lambda x: (x.end - x.start, x.score), reverse=True)
            for f in sorted_by_len:
                overlap = any(
                    not (f.end <= existing.start or f.start >= existing.end)
                    for existing in cleaned_findings
                )
                if not overlap:
                    cleaned_findings.append(f)

            # Replace from right to left using sanitized non-overlapping intervals
            sorted_pii = sorted(cleaned_findings, key=lambda x: x.start, reverse=True)
            for pii in sorted_pii:
                original_chunk = text[pii.start:pii.end]
                surrogate = token_vault.get_or_create_surrogate(
                    original_value=original_chunk,
                    entity_type=pii.entity_type,
                    project_id=project_id,
                    session_id=session_id
                )
                processed_text = processed_text[:pii.start] + surrogate + processed_text[pii.end:]
                substitutions[surrogate] = pii.entity_type

        # 6. Audit Logging (Zero-knowledge: stores only hashes and surrogate types)
        audit_logger.log_event(
            event_type="PRIVACY_GATEWAY",
            action="PROMPT_PROCESSED",
            severity="INFO" if not pii_findings else "WARNING",
            project_id=project_id,
            details={
                "classification": classification.level.value,
                "pii_count": len(pii_findings),
                "secrets_count": len(secret_findings),
                "substitutions_count": len(substitutions),
                "session_id": session_id
            },
            sensitive_payload=text
        )

        return ProcessingResult(
            original_text_masked=processed_text,
            processed_text=processed_text,
            classification=classification,
            pii_entities_count=len(pii_findings),
            secrets_count=len(secret_findings),
            substitutions=substitutions,
            allowed_to_forward=True
        )

    def restore_response(
        self,
        llm_response_text: str,
        project_id: str,
        session_id: str
    ) -> str:
        """Authorized reverse de-pseudonymization of LLM responses."""
        return token_vault.restore_text(llm_response_text, project_id, session_id)

privacy_processor = PrivacyGatewayProcessor()
