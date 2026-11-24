"""Custom exceptions for Praxia Security Hub."""

class PraxiaException(Exception):
    """Base exception for Praxia Security Hub."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class SecurityException(PraxiaException):
    """Raised on authentication or authorization failure."""
    pass

class PolicyViolationError(PraxiaException):
    """Raised when a request violates security or privacy policies."""
    pass

class FailClosedException(PolicyViolationError):
    """Raised when a fail-closed policy triggers (e.g. unmaskable secret detected)."""
    pass

class PathTraversalError(SecurityException):
    """Raised when an illegal filesystem path traversal is detected."""
    pass

class BLAExecutionError(PraxiaException):
    """Raised when BLA CLI fails during audit, protection or verification."""
    pass

class TokenVaultError(PraxiaException):
    """Raised on Token Vault encryption or decryption errors."""
    pass
