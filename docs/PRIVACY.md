# Praxia Security Hub — Privacy & Data Classification

## 1. Data Classification Tiers
Every interaction processed by the Privacy Gateway is assigned a classification level:

| Level | Policy | PII Handling | Secrets Handling |
| :--- | :--- | :--- | :--- |
| **PUBLIC** | Forward unrestricted | None | Block if found |
| **INTERNAL** | Audit logged | Entity audit | Block if found |
| **CONFIDENTIAL** | Reversible pseudonymization | Pseudonymized via Token Vault | Block if found |
| **RESTRICTED** | Maximum security & strict isolation | Encrypted surrogates & verified | **FAIL-CLOSED** (Blocked) |

## 2. PII Detection Engines
- **Microsoft Presidio Analyzer:** Statistical NLP model (`en_core_web_lg`) identifying person names, emails, phones, locations.
- **Spanish Regulatory Recognizers:** Custom high-precision regex detectors for:
  - Spanish DNI / NIE (NIF): `\b([0-9]{8}[A-Z]|[XYZ][0-9]{7}[A-Z])\b`
  - Spanish Phone Numbers (+34 / 6xx, 7xx, 8xx, 9xx)
  - International Bank Account Numbers (IBAN ES)
  - Medical / Health diagnoses and clinical terminology

## 3. Reversible Token Vault Workflow
1. Inbound Prompt: `"El paciente Juan Perez (DNI: 12345678Z) consulta por cardiologia"`
2. Gateway Transformation: `"El [MEDICAL_DATA_001] [PERSON_001] (DNI: [ES_NIF_NIE_001]) consulta por cardiologia"`
3. Vault Storage: Encrypts `Juan Perez` with AES-256-GCM linked to surrogate `[PERSON_001]`.
4. Upstream LLM: Generates response referencing `[PERSON_001]`.
5. Gateway Reverse Restoration: Restores `[PERSON_001]` back to `Juan Perez` for the authenticated developer session.
