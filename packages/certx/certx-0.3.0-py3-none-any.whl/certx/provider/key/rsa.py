from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, Encoding, NoEncryption, PrivateFormat
from oslo_log import log as logging

from certx.common import exceptions
from certx.common.model.models import KeyAlgorithm
from certx.provider.key.base import KeyProvider

logger = logging.getLogger(__name__)

_RSA_KEY_SIZE_MAP = {
    KeyAlgorithm.RSA_2048: 2048,
    KeyAlgorithm.RSA_3072: 3072,
    KeyAlgorithm.RSA_4096: 4096
}


class RsaKeyProvider(KeyProvider):
    def __init__(self, key_algorithm: KeyAlgorithm, **kwargs):
        super().__init__(key_algorithm, **kwargs)

        if self.key_algorithm not in _RSA_KEY_SIZE_MAP:
            logger.error('Unsupported key algorithm {}'.format(self.key_algorithm.value))
            raise exceptions.UnsupportedAlgorithm(type='key', name=self.key_algorithm.value)

    def generate_private_key(self):
        return rsa.generate_private_key(public_exponent=65537,
                                        key_size=_RSA_KEY_SIZE_MAP.get(self.key_algorithm),
                                        backend=default_backend())

    def get_private_bytes(self, private_key, password: str = None):
        encryption = BestAvailableEncryption(password.encode('utf-8')) if password else NoEncryption()
        return private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, encryption)

    def load_private_key(self, private_key_bytes, password: str = None):
        return serialization.load_pem_private_key(private_key_bytes,
                                                  password=password.encode('utf-8') if password else None)
