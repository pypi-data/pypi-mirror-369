from oslo_log import log as logging

from certx.common import exceptions
from certx.conf import CONF
from certx.common.model.models import KeyAlgorithm
from certx.provider.key.base import KeyProvider
from certx.utils import importutils

logger = logging.getLogger(__name__)

key_provider = CONF.gm_key_provider

gm_key_provider_conf = {
    'default': 'certx.provider.key.gm.DefaultSmKeyProvider',
    'openssl': 'certx.provider.x509.openssl.OpensslGmKeyProvider'
}


class GmKeyProvider(KeyProvider):
    def __init__(self, key_algorithm: KeyAlgorithm, **kwargs):
        super().__init__(key_algorithm, **kwargs)

        self.delegate = importutils.import_class(key_provider, gm_key_provider_conf,
                                                 key_algorithm,
                                                 **kwargs)

    def generate_private_key(self):
        return self.delegate.generate_private_key()

    def get_private_bytes(self, private_key, password: str = None):
        return self.delegate.get_private_bytes(private_key, password=password)

    def load_private_key(self, private_key_bytes, password: str = None):
        return self.delegate.load_private_key(private_key_bytes, password=password)


class DefaultSmKeyProvider(KeyProvider):
    def generate_private_key(self):
        raise exceptions.NotImplementException("GM algorithm not supported")

    def get_private_bytes(self, private_key, password: str = None):
        raise exceptions.NotImplementException()

    def load_private_key(self, private_key_bytes, password: str = None):
        raise exceptions.NotImplementException()
