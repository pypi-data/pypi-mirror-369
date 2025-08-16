# pyshield/shieldedvar.py
import inspect
import os
import secrets
import threading
import time

from .exceptions import AccessDeniedError, DeletedValueError, ExpiredValueError,ShieldedVarError

class ShieldedVar:

    def __init__(
        self,
        value: str,
        passkey: str = None,
        authorize: callable = None,
        max_reads: int = None,
        expires_in: float = None,
        environments: list = None,
        env_var: str = 'ENV',
        authorized_callers: list = None,
        mask: str = '*****',
        encrypt: bool = False
    ):


        if not isinstance(value, str):
            raise ValueError("Value must be a string.")

        self._passkey = passkey
        self._authorize = authorize
        self._max_reads = max_reads
        self._read_count = 0
        self._expiration_time = time.time() + expires_in if expires_in is not None else None
        self._environments = environments or []
        self._env_var = env_var
        self._authorized_callers = authorized_callers or []
        self._mask = mask
        self._deleted = False
        self._log = []
        self._lock = threading.Lock()

        if encrypt:
            self._key = secrets.token_bytes(32)
            self._encrypted = self._xor(value.encode(), self._key)
            self._value = None
        else:
            self._key = None
            self._encrypted = None
            self._value = value

        self._encrypt = encrypt

    def _xor(self, data: bytes, key: bytes) -> bytes:
        """simple XOR encryption/decryption"""
        return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))

    def __str__(self):
        return self._mask

    def __repr__(self):
        return f"<ShieldedVar: {self._mask}>"

    def get(self, passkey: str = None, raise_on_fail: bool = True):
        with self._lock:
            entry = {'timestamp': time.time(), 'reason': None, 'authorized': None, 'success': False}

            try:
                if self._deleted:
                    entry['reason'] = 'deleted'
                    raise DeletedValueError("Value has been deleted.")

                if self._expiration_time is not None and time.time() > self._expiration_time:
                    entry['reason'] = 'expired'
                    raise ExpiredValueError("Value has expired.")

                if self._environments:
                    current_env = os.environ.get(self._env_var)
                    if current_env not in self._environments:
                        entry['reason'] = 'wrong_environment'
                        raise AccessDeniedError(f"Access denied: wrong environment '{current_env}'.")

                if self._authorized_callers:
                    caller_frame = inspect.stack()[1].frame
                    caller_module = caller_frame.f_globals.get('__name__')
                    if caller_module not in self._authorized_callers:
                        entry['reason'] = 'unauthorized_caller'
                        raise AccessDeniedError(f"Access denied: unauthorized caller '{caller_module}'.")

                # Authorization checks
                authorized = True
                if self._passkey is not None:
                    if passkey != self._passkey:
                        authorized = False
                if self._authorize is not None:
                    if not self._authorize():
                        authorized = False

                entry['authorized'] = authorized
                if not authorized:
                    entry['reason'] = 'authorization_failed'
                    raise AccessDeniedError("Access denied: authorization failed.")

                if self._max_reads is not None and self._read_count >= self._max_reads:
                    entry['reason'] = 'max_reads_exceeded'
                    raise AccessDeniedError("Access denied: maximum reads exceeded.")

                # All checks passed
                self._read_count += 1
                entry['success'] = True

                if self._encrypt:
                    return self._xor(self._encrypted, self._key).decode()
                else:
                    return self._value

            except ShieldedVarError as e:
                if raise_on_fail:
                    raise
                else:
                    return None
            finally:
                self._log.append(entry)

    def delete(self):
        """Securely delete the sensitive value from memory"""
        with self._lock:
            self._value = None
            self._encrypted = None
            self._key = None
            self._deleted = True

    def get_log(self):
        """Retrieve the access log"""
        with self._lock:
            return list(self._log)
