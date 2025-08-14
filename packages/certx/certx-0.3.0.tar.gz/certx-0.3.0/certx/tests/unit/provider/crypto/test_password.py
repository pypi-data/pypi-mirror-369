import unittest

from certx.provider.crypto import password


class TestNonePasswordEncoder(unittest.TestCase):
    def test_encrypt(self):
        row_data = 'xx'
        self.assertEqual('xx', password.NonePasswordEncoder().encrypt(row_data))

    def test_decrypt(self):
        cipher_data = 'xx'
        self.assertEqual('xx', password.NonePasswordEncoder().decrypt(cipher_data))


class TestFernetPasswordEncoder(unittest.TestCase):
    def test_encrypt_and_decrypt_with_bytes(self):
        mock_sk = '0nSZfQel0qxHoYzHzXDwWVvQoSsOTPtbx0bW7V4OyTQ='
        row_data = 'xx'.encode('utf-8')
        crypter = password.FernetPasswordEncoder(mock_sk)
        self.assertEqual('xx', crypter.decrypt(crypter.encrypt(row_data)))

    def test_encrypt_and_decrypt_with_str(self):
        mock_sk = '0nSZfQel0qxHoYzHzXDwWVvQoSsOTPtbx0bW7V4OyTQ='
        row_data = 'xx'
        crypter = password.FernetPasswordEncoder(mock_sk)
        self.assertEqual(row_data, crypter.decrypt(crypter.encrypt(row_data)))
