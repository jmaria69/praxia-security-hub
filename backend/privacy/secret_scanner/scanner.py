"""Secret and Credential Scanner: Never send secrets to external LLMs."""
import math
import re
from typing import Optional
from pydantic import BaseModel

class SecretFinding(BaseModel):
    rule_id: str
    category: str
    match_snippet: str
    entropy: float
    start: int
    end: int

# High precision regex patterns for real-world secrets
SECRET_PATTERNS = [
    ("OPENAI_KEY", "API_KEY", r"\bsk-[a-zA-Z0-9]{20,60}\b"),
    ("ANTHROPIC_KEY", "API_KEY", r"\bsk-ant-[a-zA-Z0-9_\-]{30,100}\b"),
    ("AWS_ACCESS_KEY", "CLOUD_CREDENTIAL", r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"),
    ("GOOGLE_API_KEY", "API_KEY", r"\bAIza[0-9A-Za-z\-_]{35}\b"),
    ("GITHUB_TOKEN", "TOKEN", r"\bgh[pousr]_[A-Za-z0-9_]{36,255}\b"),
    ("SLACK_TOKEN", "TOKEN", r"\bxox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9]*\b"),
    ("GENERIC_JWT", "TOKEN", r"\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"),
    ("PRIVATE_KEY", "CRYPTO_KEY", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    ("DATABASE_URL", "CREDENTIAL", r"\b(?:postgres|mysql|mongodb|redis):\/\/[a-zA-Z0-9_\-\.]+:[^@\s]+@[a-zA-Z0-9_\-\.]+:[0-9]+\/[a-zA-Z0-9_\-\.]+\b"),
]

def calculate_shannon_entropy(data: str) -> float:
    """Calculate the Shannon entropy of a string."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    for x in set(data):
        p_x = float(data.count(x)) / length
        entropy += - p_x * math.log2(p_x)
    return entropy

class SecretScanner:
    def scan(self, text: str, min_entropy: float = 3.6) -> list[SecretFinding]:
        """Scan text for credentials, keys, private certs and high entropy tokens."""
        findings: list[SecretFinding] = []
        if not text:
            return findings

        # 1. Pattern Matching
        for rule_id, category, pattern in SECRET_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                val = match.group(0)
                entropy = calculate_shannon_entropy(val)
                # Mask snippet for safety
                masked = val[:4] + "*" * (len(val) - 8) + val[-4:] if len(val) > 8 else "********"
                findings.append(SecretFinding(
                    rule_id=rule_id,
                    category=category,
                    match_snippet=masked,
                    entropy=round(entropy, 2),
                    start=match.start(),
                    end=match.end()
                ))

        # 2. Assignment Keyword Scanner (e.g. password = "...", api_key = "...")
        keyword_pattern = r"""(?i)\b(?:password|passwd|secret|token|api_key|access_token|private_key)\s*[:=]\s*["']([^"']{8,128})["']"""
        for match in re.finditer(keyword_pattern, text):
            val = match.group(1)
            entropy = calculate_shannon_entropy(val)
            if entropy >= min_entropy:
                masked = val[:2] + "*" * (len(val) - 4) + val[-2:] if len(val) > 4 else "******"
                findings.append(SecretFinding(
                    rule_id="PASSWORD_KEYWORD_ASSIGNMENT",
                    category="CREDENTIAL",
                    match_snippet=masked,
                    entropy=round(entropy, 2),
                    start=match.start(1),
                    end=match.end(1)
                ))

        return findings

secret_scanner = SecretScanner()
