from cryptography import x509
from oslo_serialization import jsonutils

from certx.tests.unit.api import ApiResourceBaseTestCase


def mock_create_ca_request_option():
    return {
        "certificate_authority": {
            "type": "ROOT",
            "key_algorithm": "RSA_4096",
            "signature_algorithm": "SHA2_256",
            "distinguished_name": {
                "common_name": "MyCA",
                "country": "CN",
                "locality": "BJ",
                "organization": "O",
                "organization_unit": "OU",
                "state": "BJ"
            },
            "validity": {
                "type": "YEAR",
                "value": 3
            },
            "crl_configuration": {
                "enabled": True,
                "valid_days": 15
            }
        }
    }


def mock_create_cert_request_option(issuer_id=None):
    return {
        "certificate": {
            "key_algorithm": "RSA_4096",
            "signature_algorithm": "SHA2_512",
            "issuer_id": issuer_id,
            "distinguished_name": {
                "common_name": "MyCert"
            },
            "validity": {
                "type": "YEAR",
                "value": 2
            }
        }
    }


class TestCertificateAuthorityCrlResource(ApiResourceBaseTestCase):

    def test_get_crl(self):
        # Create CA and enable CRL
        fake_request = mock_create_ca_request_option()
        ca_response = self.app.post('/v1/certificate-authorities',
                                    content_type='application/json',
                                    data=jsonutils.dumps(fake_request))
        ca = jsonutils.loads(ca_response.data).get('certificate_authority')

        # Create Cert
        fake_request = mock_create_cert_request_option(issuer_id=ca['id'])
        cert_response = self.app.post('/v1/certificates',
                                      content_type='application/json',
                                      data=jsonutils.dumps(fake_request))
        cert = jsonutils.loads(cert_response.data).get('certificate')

        # Revoke Cert
        self.app.post(f'/v1/certificates/{cert.get("id")}/revoke',
                      content_type='application/json',
                      data=jsonutils.dumps({}))

        # Query CRL
        crl_response = self.app.get(f'/crl/{ca["id"]}',
                                    content_type='application/json')

        self.assertEqual(200, crl_response.status_code)
        self.assertIsNotNone(crl_response.data)
        crl = x509.load_pem_x509_crl(crl_response.data)
        revoked_cert = crl.get_revoked_certificate_by_serial_number(int(cert['serial_number']))
        self.assertIsNotNone(revoked_cert)
