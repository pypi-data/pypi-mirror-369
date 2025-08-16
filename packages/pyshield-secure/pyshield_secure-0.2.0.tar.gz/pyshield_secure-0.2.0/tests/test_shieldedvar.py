# tests/test_shieldedvar.py
import os
import time
import unittest
from unittest.mock import patch

from pyshield import ShieldedVar, AccessDeniedError, DeletedValueError, ExpiredValueError

class TestShieldedVar(unittest.TestCase):
    def test_masking(self):
        s = ShieldedVar("secret")
        self.assertEqual(str(s), "*****")
        self.assertEqual(repr(s), "<ShieldedVar: *****>")

    def test_basic_access(self):
        s = ShieldedVar("secret")
        self.assertEqual(s.get(), "secret")

    def test_passkey(self):
        s = ShieldedVar("secret", passkey="key")
        with self.assertRaises(AccessDeniedError):
            s.get(passkey="wrong")
        self.assertEqual(s.get(passkey="key"), "secret")
        self.assertEqual(s.get(passkey="wrong", raise_on_fail=False), None)

    def test_callback(self):
        def auth_true():
            return True
        def auth_false():
            return False

        s_true = ShieldedVar("secret", authorize=auth_true)
        self.assertEqual(s_true.get(), "secret")

        s_false = ShieldedVar("secret", authorize=auth_false)
        with self.assertRaises(AccessDeniedError):
            s_false.get()

    def test_max_reads(self):
        s = ShieldedVar("secret", max_reads=1)
        self.assertEqual(s.get(), "secret")
        with self.assertRaises(AccessDeniedError):
            s.get()

    def test_expiration(self):
        s = ShieldedVar("secret", expires_in=-1)
        with self.assertRaises(ExpiredValueError):
            s.get()

    def test_environment(self):
        os.environ['TEST_ENV'] = 'dev'
        s = ShieldedVar("secret", environments=["prod"], env_var="TEST_ENV")
        with self.assertRaises(AccessDeniedError):
            s.get()

        s_ok = ShieldedVar("secret", environments=["dev"], env_var="TEST_ENV")
        self.assertEqual(s_ok.get(), "secret")

    def test_caller(self):
        s = ShieldedVar("secret", authorized_callers=["__main__"])
        try:
            s.get()
        except AccessDeniedError:
            pass

    def test_delete(self):
        s = ShieldedVar("secret")
        s.delete()
        with self.assertRaises(DeletedValueError):
            s.get()

    def test_log(self):
        s = ShieldedVar("secret", passkey="key")
        try:
            s.get(passkey="wrong")
        except AccessDeniedError:
            pass
        s.get(passkey="key")
        logs = s.get_log()
        self.assertEqual(len(logs), 2)
        self.assertFalse(logs[0]['success'])
        self.assertTrue(logs[1]['success'])

    def test_encryption(self):
        s = ShieldedVar("secret", encrypt=True)
        self.assertEqual(s.get(), "secret")
        self.assertIsNone(s._value)  # encrypted not plain

    def test_thread_safety(self):
        s = ShieldedVar("secret", max_reads=1)
        def access():
            try:
                return s.get()
            except AccessDeniedError:
                return None

        from threading import Thread
        t1 = Thread(target=access)
        t2 = Thread(target=access)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        

if __name__ == '__main__':
    unittest.main()
