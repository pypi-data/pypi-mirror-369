import unittest

from certx.common.model.models import KeyAlgorithm, SignatureAlgorithm
from certx.utils import algorithm_utils


class TestAlgorithmUtil(unittest.TestCase):
    def test_validate_key_and_signature_algorithm_with_matched_key_and_signature_alg(self):
        self.assertTrue(
            algorithm_utils.validate_key_and_signature_algorithm(KeyAlgorithm.RSA_2048, SignatureAlgorithm.SHA2_256))
        self.assertTrue(
            algorithm_utils.validate_key_and_signature_algorithm(KeyAlgorithm.ECC_256, SignatureAlgorithm.SHA2_512))
        self.assertTrue(
            algorithm_utils.validate_key_and_signature_algorithm(KeyAlgorithm.SM2_256, SignatureAlgorithm.SM3_256))

    def test_validate_key_and_signature_algorithm_with_unmatched_key_and_signature_alg(self):
        self.assertFalse(
            algorithm_utils.validate_key_and_signature_algorithm(KeyAlgorithm.RSA_2048, SignatureAlgorithm.SM3_256))
        self.assertFalse(
            algorithm_utils.validate_key_and_signature_algorithm(KeyAlgorithm.SM2_256, SignatureAlgorithm.SHA2_512))

    def test_validate_key_algorithm_for_issuer_and_cert_in_same_items(self):
        self.assertTrue(algorithm_utils.validate_key_algorithm(KeyAlgorithm.RSA_2048, KeyAlgorithm.RSA_2048))
        self.assertTrue(algorithm_utils.validate_key_algorithm(KeyAlgorithm.RSA_2048, KeyAlgorithm.RSA_4096))
        self.assertTrue(algorithm_utils.validate_key_algorithm(KeyAlgorithm.RSA_3072, KeyAlgorithm.ECC_256))
        self.assertTrue(algorithm_utils.validate_key_algorithm(KeyAlgorithm.SM2_256, KeyAlgorithm.SM2_256))

    def test_validate_key_algorithm_for_issuer_and_cert_not_in_same_items(self):
        self.assertFalse(algorithm_utils.validate_key_algorithm(KeyAlgorithm.RSA_2048, KeyAlgorithm.SM2_256))
        self.assertFalse(algorithm_utils.validate_key_algorithm(KeyAlgorithm.SM2_256, KeyAlgorithm.RSA_4096))
        self.assertFalse(algorithm_utils.validate_key_algorithm(KeyAlgorithm.SM2_256, KeyAlgorithm.ECC_256))

    def test_validate_signature_algorithm_for_issuer_and_cert_in_same_items(self):
        self.assertTrue(
            algorithm_utils.validate_signature_algorithm(SignatureAlgorithm.SHA2_256, SignatureAlgorithm.SHA2_512))
        self.assertTrue(
            algorithm_utils.validate_signature_algorithm(SignatureAlgorithm.SM3_256, SignatureAlgorithm.SM3_256))

    def test_validate_signature_algorithm_for_issuer_and_cert_not_in_same_items(self):
        self.assertFalse(
            algorithm_utils.validate_signature_algorithm(SignatureAlgorithm.SHA2_256, SignatureAlgorithm.SM3_256))
        self.assertFalse(
            algorithm_utils.validate_signature_algorithm(SignatureAlgorithm.SM3_256, SignatureAlgorithm.SHA2_512))
