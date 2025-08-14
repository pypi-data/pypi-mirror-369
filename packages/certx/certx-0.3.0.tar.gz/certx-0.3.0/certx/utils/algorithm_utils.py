from certx.common.model.models import KeyAlgorithm, SignatureAlgorithm

_KEY_2_SIGNATURE_ALGORITHM = (
    (
        (KeyAlgorithm.RSA_2048, KeyAlgorithm.RSA_3072, KeyAlgorithm.RSA_4096, KeyAlgorithm.ECC_256,
         KeyAlgorithm.ECC_384),
        (SignatureAlgorithm.SHA2_256, SignatureAlgorithm.SHA2_384, SignatureAlgorithm.SHA2_512)
    ),
    (
        (KeyAlgorithm.SM2_256,),
        (SignatureAlgorithm.SM3_256,)
    )
)


def validate_key_and_signature_algorithm(key_algorithm: KeyAlgorithm, signature_algorithm: SignatureAlgorithm) -> bool:
    """Check key algorithm and signature algorithm is matching.
    :param key_algorithm: the key algorithm
    :param signature_algorithm: the signature algorithm
    :return True when matched and False when not matched or NO matching rules
    """
    for item in _KEY_2_SIGNATURE_ALGORITHM:
        if key_algorithm in item[0] and signature_algorithm in item[1]:
            return True
    return False


def validate_key_algorithm(issuer_key_algorithm, cert_key_algorithm):
    for item in _KEY_2_SIGNATURE_ALGORITHM:
        if issuer_key_algorithm in item[0] and cert_key_algorithm in item[0]:
            return True
    return False


def validate_signature_algorithm(issuer_signature_algorithm, cert_signature_algorithm):
    for item in _KEY_2_SIGNATURE_ALGORITHM:
        if issuer_signature_algorithm in item[1] and cert_signature_algorithm in item[1]:
            return True
    return False
