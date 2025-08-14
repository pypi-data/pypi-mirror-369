import unittest

from certx.common import exceptions
from certx.common.model.models import KeyAlgorithm
from certx.provider.key import ec


class TestEcKeyProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = ec.EcKeyProvider(KeyAlgorithm.ECC_256)

    def test_new_object_should_return_bad_request_with_unsupported_alg(self):
        self.assertRaises(exceptions.UnsupportedAlgorithm, ec.EcKeyProvider, KeyAlgorithm.RSA_3072)

    def test_generate_private_key(self):
        key = self.provider.generate_private_key()
        self.assertIsNotNone(key)
        self.assertEqual(256, key.key_size)

    def test_get_private_bytes_with_password(self):
        key = self.provider.generate_private_key()
        pri_bytes = self.provider.get_private_bytes(key, 'xxx')
        self.assertTrue(pri_bytes.decode().startswith('-----BEGIN ENCRYPTED PRIVATE KEY-----'))

    def test_get_private_bytes_without_password(self):
        key = self.provider.generate_private_key()
        pri_bytes = self.provider.get_private_bytes(key, None)
        self.assertTrue(pri_bytes.decode().startswith('-----BEGIN PRIVATE KEY-----'))

    def test_load_private_key_without_password(self):
        key = self.provider.generate_private_key()
        pri_bytes = self.provider.get_private_bytes(key, None)
        pri_key = self.provider.load_private_key(pri_bytes)
        self.assertIsNotNone(pri_key)
        self.assertEqual(256, pri_key.key_size)

    def test_load_encrypted_private_key_should_fail_without_password(self):
        key = self.provider.generate_private_key()
        pri_bytes = self.provider.get_private_bytes(key, 'xx')
        self.assertRaises(TypeError, self.provider.load_private_key, pri_bytes)

    def test_load_uncrypted_private_key_should_fail_with_password(self):
        key = self.provider.generate_private_key()
        pri_bytes = self.provider.get_private_bytes(key)
        self.assertRaises(TypeError, self.provider.load_private_key, pri_bytes, 'xx')
