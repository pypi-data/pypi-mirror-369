# pyshield/exceptions.py
class ShieldedVarError(Exception):
    """Base exception for ShieldedVar errors."""
    pass

class AccessDeniedError(ShieldedVarError):
    """Raised when access is denied due to authorization failure."""
    pass

class DeletedValueError(ShieldedVarError):
    """Raised when attempting to access a deleted value."""
    pass

class ExpiredValueError(ShieldedVarError):
    """Raised when attempting to access an expired value."""
    pass
