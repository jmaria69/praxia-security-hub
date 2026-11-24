"""Data Classification Service: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED."""
from enum import Enum
from typing import Any
from pydantic import BaseModel
from backend.privacy.pii_detector.detector import PIIDetectionResult
from backend.privacy.secret_scanner.scanner import SecretFinding

class DataClassificationLevel(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"

class ClassificationDecision(BaseModel):
    level: DataClassificationLevel
    reason: str
    reasons: list[str]
    has_secrets: bool
    requires_pseudonymization: bool
    fail_closed_triggered: bool

class DataClassifier:
    def classify(
        self,
        text: str,
        pii_results: list[PIIDetectionResult],
        secret_findings: list[Any],
        project_default: str = "INTERNAL"
    ) -> ClassificationDecision:
        reasons = []
        has_secrets = len(secret_findings) > 0
        
        # 1. Any secret automatically makes data RESTRICTED and triggers FAIL-CLOSED
        if has_secrets:
            reasons.append(f"Detected {len(secret_findings)} secret(s)/credential(s)")
            return ClassificationDecision(
                level=DataClassificationLevel.RESTRICTED,
                reason="Secrets detected; transmission prohibited",
                reasons=reasons,
                has_secrets=True,
                requires_pseudonymization=True,
                fail_closed_triggered=True
            )

        # 2. Check for Medical, Financial, or National ID (DNI/NIE)
        critical_entities = {"MEDICAL_DATA", "ES_NIF_NIE", "IBAN_CODE", "CREDIT_CARD"}
        detected_types = {p.entity_type for p in pii_results}
        
        if any(t in critical_entities for t in detected_types):
            critical_hits = [t for t in detected_types if t in critical_entities]
            reasons.append(f"Contains high-impact sensitive data: {', '.join(critical_hits)}")
            return ClassificationDecision(
                level=DataClassificationLevel.RESTRICTED,
                reason="High-risk regulatory or medical data detected",
                reasons=reasons,
                has_secrets=False,
                requires_pseudonymization=True,
                fail_closed_triggered=False
            )

        # 3. Check for general PII (Person names, emails, phones)
        if len(pii_results) > 0:
            reasons.append(f"Contains {len(pii_results)} PII entity/entities")
            return ClassificationDecision(
                level=DataClassificationLevel.CONFIDENTIAL,
                reason="Personal data detected; pseudonymization required",
                reasons=reasons,
                has_secrets=False,
                requires_pseudonymization=True,
                fail_closed_triggered=False
            )

        # 4. Fallback to Project Default Classification
        try:
            default_level = DataClassificationLevel(project_default.upper())
        except ValueError:
            default_level = DataClassificationLevel.INTERNAL

        return ClassificationDecision(
            level=default_level,
            reason=f"Default project baseline classification: {default_level.value}",
            reasons=[f"Baseline project policy: {default_level.value}"],
            has_secrets=False,
            requires_pseudonymization=(default_level in [DataClassificationLevel.CONFIDENTIAL, DataClassificationLevel.RESTRICTED]),
            fail_closed_triggered=False
        )

data_classifier = DataClassifier()
