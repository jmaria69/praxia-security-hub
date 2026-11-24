"""PII Detection using Microsoft Presidio and Spanish Regulatory Recognizers."""
import re
from typing import Any
from pydantic import BaseModel
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer

class PIIDetectionResult(BaseModel):
    entity_type: str
    start: int
    end: int
    score: float
    text: str

class PIIDetector:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self._add_spanish_recognizers()

    def _add_spanish_recognizers(self):
        # DNI / NIE (Spain)
        dni_pattern = Pattern(
            name="dni_pattern",
            regex=r"\b([0-9]{8}[A-Z]|[XYZ][0-9]{7}[A-Z])\b",
            score=0.95
        )
        dni_recognizer = PatternRecognizer(
            supported_entity="ES_NIF_NIE",
            patterns=[dni_pattern],
            context=["dni", "nie", "nif", "documento", "identidad", "pasaporte"]
        )
        self.analyzer.registry.add_recognizer(dni_recognizer)

        # Spanish Phone Numbers
        es_phone_pattern = Pattern(
            name="es_phone_pattern",
            regex=r"\b(?:\+34|0034)?[ -]?(?:[6789]\d{2})[ -]?(?:\d{3})[ -]?(?:\d{3})\b",
            score=0.85
        )
        phone_recognizer = PatternRecognizer(
            supported_entity="PHONE_NUMBER",
            patterns=[es_phone_pattern],
            context=["telefono", "tlf", "movil", "contacto", "phone"]
        )
        self.analyzer.registry.add_recognizer(phone_recognizer)

        # Health / Medical keyword pattern
        health_pattern = Pattern(
            name="health_data_pattern",
            regex=r"(?i)\b(diagn[oó]stico|tratamiento|enfermedad|paciente|historia cl[ií]nica|s[ií]ntoma|medicamento|prescripci[oó]n|VIH|c[aá]ncer|quir[uú]rgico)\b",
            score=0.80
        )
        health_recognizer = PatternRecognizer(
            supported_entity="MEDICAL_DATA",
            patterns=[health_pattern],
            context=["salud", "médico", "clínica", "hospital", "doctor"]
        )
        self.analyzer.registry.add_recognizer(health_recognizer)

    def detect(self, text: str, min_score: float = 0.6) -> list[PIIDetectionResult]:
        """Detect PII entities in text using Presidio + customized recognizers."""
        if not text:
            return []
            
        results = self.analyzer.analyze(
            text=text,
            language="en",  # presidio base
            score_threshold=min_score
        )
        
        output = []
        for r in results:
            output.append(PIIDetectionResult(
                entity_type=r.entity_type,
                start=r.start,
                end=r.end,
                score=r.score,
                text=text[r.start:r.end]
            ))
            
        # Additional regex fallback for emails and IBAN
        iban_regex = re.compile(r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{12,30}\b")
        for match in iban_regex.finditer(text):
            if not any(o.start == match.start() for o in output):
                output.append(PIIDetectionResult(
                    entity_type="IBAN_CODE",
                    start=match.start(),
                    end=match.end(),
                    score=0.95,
                    text=match.group(0)
                ))
                
        # Sort by start position
        output.sort(key=lambda x: x.start)
        return output

pii_detector = PIIDetector()
