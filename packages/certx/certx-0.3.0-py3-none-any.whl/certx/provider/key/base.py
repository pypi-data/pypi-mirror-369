import abc

from certx.common.model.models import KeyAlgorithm


class KeyProvider(abc.ABC):
    def __init__(self, key_algorithm: KeyAlgorithm, **kwargs):
        self.key_algorithm = key_algorithm
        self.kwargs = kwargs

    @abc.abstractmethod
    def generate_private_key(self):
        pass

    @abc.abstractmethod
    def get_private_bytes(self, private_key, password: str = None):
        pass

    @abc.abstractmethod
    def load_private_key(self, private_key_bytes, password: str = None):
        pass
