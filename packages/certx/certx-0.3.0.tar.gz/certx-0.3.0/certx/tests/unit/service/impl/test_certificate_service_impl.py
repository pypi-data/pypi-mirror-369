import unittest

from certx.common import exceptions
from certx.common.model import models
from certx.service.impl.certificate_service_impl import CertificateServiceImpl


class TestCertificateServiceImpl(unittest.TestCase):
    def setUp(self) -> None:
        self.certificate_service = CertificateServiceImpl()

    def test_create_certificate_authority_with_empty_input(self):
        self.assertRaises(exceptions.InvalidParameterValue, self.certificate_service.create_certificate_authority, None)

    def test_create_root_ca_with_unmatched_key_and_signature_algorithm(self):
        test_data = [
            {'type': models.CaType.ROOT},
            {'type': models.CaType.ROOT, 'key_algorithm': models.KeyAlgorithm.RSA_2048},
            {'type': models.CaType.ROOT, 'signature_algorithm': models.SignatureAlgorithm.SHA2_256},
            {'type': models.CaType.ROOT, 'key_algorithm': models.KeyAlgorithm.RSA_2048,
             'signature_algorithm': models.SignatureAlgorithm.SM3_256},
        ]
        for data in test_data:
            with self.subTest(data=data):
                self.assertRaises(exceptions.InvalidParameterValue,
                                  self.certificate_service.create_certificate_authority,
                                  data)
