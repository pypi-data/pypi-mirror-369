import abc

from cryptography.fernet import Fernet
from oslo_config import cfg


class PasswordEncoder(abc.ABC):
    @abc.abstractmethod
    def encrypt(self, row_data):
        pass

    @abc.abstractmethod
    def decrypt(self, cipher_data):
        pass


class NonePasswordEncoder(PasswordEncoder):
    def encrypt(self, row_data):
        return row_data

    def decrypt(self, cipher_data):
        return cipher_data


class FernetPasswordEncoder(PasswordEncoder):
    def __init__(self, secret_key=None):
        self.secret_key = secret_key if secret_key else cfg.CONF.encryption_secret_key
        if not self.secret_key:
            raise ValueError('secret_key could not be empty')
        self._fernet = Fernet(self.secret_key)

    def encrypt(self, row_data) -> str:
        return self._fernet.encrypt(row_data.encode('utf-8') if isinstance(row_data, str) else row_data).decode('utf-8')

    def decrypt(self, cipher_data: str) -> str:
        return self._fernet.decrypt(cipher_data).decode('utf-8')

    @staticmethod
    def gen_secret_key():
        return str(Fernet.generate_key())
