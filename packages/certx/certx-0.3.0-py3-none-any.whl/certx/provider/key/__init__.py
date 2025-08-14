from certx.provider.key import gm
from certx.provider.key import rsa
from certx.provider.key import ec

from certx.common import exceptions
from certx.common.model.models import KeyAlgorithm

_PROVIDER_MAP = {
    KeyAlgorithm.RSA_2048: rsa.RsaKeyProvider,
    KeyAlgorithm.RSA_3072: rsa.RsaKeyProvider,
    KeyAlgorithm.RSA_4096: rsa.RsaKeyProvider,
    KeyAlgorithm.ECC_256: ec.EcKeyProvider,
    KeyAlgorithm.ECC_384: ec.EcKeyProvider,
    KeyAlgorithm.SM2_256: gm.GmKeyProvider,
}


def get_provider(key_algorithm: KeyAlgorithm):
    if key_algorithm not in _PROVIDER_MAP:
        raise exceptions.UnsupportedAlgorithm(type='key', name=key_algorithm.value if key_algorithm else None)

    return _PROVIDER_MAP.get(key_algorithm)(key_algorithm)
