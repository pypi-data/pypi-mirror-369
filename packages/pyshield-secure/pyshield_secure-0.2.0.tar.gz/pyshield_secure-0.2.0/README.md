# PyShield

PyShield is a professional Python library designed to securely handle sensitive in-memory variables such as passwords, tokens, API keys, and payment data. It wraps these values in protected objects that prevent accidental exposure during printing, logging, or debugging, while providing controlled access through authorization mechanisms.

## Features

- **Masking**: Displays a mask (e.g., "*****") instead of the real value in `print()`, `str()`, or `repr()`.
- **Authorized Access**: Enforces checks via passkey, custom callbacks, access limits, expiration, environment verification, and caller inspection.
- **Secure Deletion**: Wipes the value from memory to prevent further access.
- **Access Logging**: Logs all access attempts for auditing.
- **Thread-Safety**: Safe for use in multi-threaded environments.
- **Optional Encryption**: Simple in-memory XOR encryption for added protection.
- **Python 3.7+ Support**: Compatible with modern Python versions.

## Installation

Install via PyPI:pip install pyshield


## Usage

### Basic Usage

```python
from pyshield import ShieldedVar, AccessDeniedError

# Create a shielded variable with passkey authorization
secret = ShieldedVar("top_secret", passkey="my123")

print(secret)  # Outputs: *****
print(repr(secret))  # Outputs: <ShieldedVar: *****>

# Access with correct passkey
value = secret.get(passkey="my123")  # Returns: "top_secret"

# Access with wrong passkey
try:
    secret.get(passkey="wrong")
except AccessDeniedError:
    print("Access denied")

# Using callback authorization
def check_auth():
    # Dynamic logic, e.g., check user permissions
    return True

secret2 = ShieldedVar("another_secret", authorize=check_auth)
value2 = secret2.get()  # Returns value if check_auth() is True

# Return None on failure instead of raising
value_fail = secret.get(passkey="wrong", raise_on_fail=False)  # Returns: None
