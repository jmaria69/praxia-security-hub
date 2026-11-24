# Praxia Security Hub — Security Architecture

## 1. Security by Design
Praxia Security Hub strictly enforces the principle of least privilege, zero-trust perimeter boundaries, and defensive programming:
- **Localhost Default:** Bound exclusively to `127.0.0.1` preventing inadvertent network exposure.
- **Path Traversal Defense:** All filesystem targets are checked against `ALLOWED_BASE_DIRS` (`/home/jmari/proyectosIA`, `/tmp`) resolving symlinks before I/O.
- **Command Injection Prevention:** External binaries are invoked exclusively via array-based argument vectors in `subprocess.run(check=False)`, never through shell string expansion.
- **RBAC Authentication:** PBKDF2-HMAC-SHA256 password hashing with role separation (`admin`, `operator`, `auditor`).

## 2. Cryptographic Token Vault
- **Encryption Algorithm:** AES-256-GCM (Authenticated Encryption with Associated Data).
- **Associated Data (AAD):** Bound to `project_id:session_id:surrogate` preventing ciphertext transplantation attacks.
- **Key Derivation:** 256-bit cryptographic key loaded via environment variable `TOKEN_VAULT_KEY`.
- **Zero Raw Logging:** Original plaintext entities and secrets are never committed to SQLite or audit logs; only cryptographically computed SHA-256 hashes are recorded.

## 3. Fail-Closed Enforcement
When a critical secret (e.g. AWS Key, OpenAI/Anthropic API token, Private Key, Database URI) is discovered in any incoming prompt:
1. An immediate `CRITICAL` security incident is registered in the audit database.
2. The request is aborted before reaching any network socket.
3. An HTTP 403 Forbidden response with `FAIL_CLOSED_TRIGGERED` is returned.
