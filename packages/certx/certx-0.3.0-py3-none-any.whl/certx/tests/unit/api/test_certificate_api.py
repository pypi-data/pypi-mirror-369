from oslo_serialization import jsonutils

from certx.tests.unit.api import ApiResourceBaseTestCase
from certx.tests.unit.api import test_certificate_authority_api


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
                "value": 50
            }
        }
    }


def mock_create_sm_cert_request_option(issuer_id=None):
    return {
        "certificate": {
            "key_algorithm": "SM2_256",
            "signature_algorithm": "SM3_256",
            "issuer_id": issuer_id,
            "distinguished_name": {
                "common_name": "MySMCert"
            },
            "validity": {
                "type": "YEAR",
                "value": 50
            }
        }
    }


class TestCertificateApiResource(ApiResourceBaseTestCase):
    def setUp(self):
        super(TestCertificateApiResource, self).setUp()
        self._setup_root_ca()

    def _setup_root_ca(self):
        fake_request = test_certificate_authority_api.mock_create_ca_request_option()
        response = self.app.post('/v1/certificate-authorities',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        resp_body = jsonutils.loads(response.data)
        ca = resp_body.get('certificate_authority')
        self.setup_root_ca_id = ca['id']

    def _setup_sub_ca(self):
        fake_request = test_certificate_authority_api.mock_create_ca_request_option()
        fake_request['certificate_authority']['type'] = 'SUB'
        fake_request['certificate_authority']['issuer_id'] = self.setup_root_ca_id
        fake_request['certificate_authority']['distinguished_name']['common_name'] = 'SubCA'
        fake_request['certificate_authority']['crl_configuration']['enabled'] = True
        fake_request['certificate_authority']['crl_configuration']['valid_days'] = 15
        response = self.app.post('/v1/certificate-authorities',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.setup_sub_ca_id = jsonutils.loads(response.data).get('certificate_authority').get('id')

    def _create_one_cert(self, issuer_id=None):
        fake_request = mock_create_cert_request_option(issuer_id=issuer_id or self.setup_root_ca_id)
        response = self.app.post('/v1/certificates',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        return response

    def test_create_cert_by_root_ca(self):
        response = self._create_one_cert()
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        self.assertIsNotNone(resp_body)
        cert = resp_body.get('certificate')
        self.assertIsNotNone(cert)
        self.assertIsNotNone(cert['id'])
        self.assertEqual('ISSUE', cert['status'])
        self.assertEqual('RSA_4096', cert['key_algorithm'])
        self.assertEqual('SHA2_512', cert['signature_algorithm'])
        self.assertEqual(self.setup_root_ca_id, cert.get('issuer_id'))
        self.assertEqual('MyCert', cert['distinguished_name']['common_name'])
        self.assertEqual('CN', cert['distinguished_name']['country'])

    def test_create_cert_when_not_provider_algorithm(self):
        fake_request = mock_create_cert_request_option(self.setup_root_ca_id)
        del fake_request['certificate']['key_algorithm']
        del fake_request['certificate']['signature_algorithm']

        response = self.app.post('/v1/certificates',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        self.assertIsNotNone(resp_body)
        cert = resp_body.get('certificate')
        self.assertIsNotNone(cert)
        self.assertIsNotNone(cert['id'])
        self.assertEqual('ISSUE', cert['status'])
        self.assertEqual('RSA_4096', cert['key_algorithm'])
        self.assertEqual('SHA2_256', cert['signature_algorithm'])  # 和 CA 保持一致

    def test_create_cert_failed_when_required_issuer_id_no_provided(self):
        fake_request = mock_create_cert_request_option()
        response = self.app.post('/v1/certificates',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(400, response.status_code)

    def test_create_cert_failed_when_ca_not_found(self):
        fake_request = mock_create_cert_request_option('e05042a3-6cc6-4664-81a5-1eb4838d26e2')
        response = self.app.post('/v1/certificates',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(404, response.status_code)

    def test_create_cert_failed_when_with_unmatched_algorithm(self):
        fake_request = mock_create_cert_request_option(issuer_id=self.setup_root_ca_id)
        fake_request['certificate']['key_algorithm'] = 'RSA_4096'
        fake_request['certificate']['signature_algorithm'] = 'SM3_256'
        response = self.app.post('/v1/certificates',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(400, response.status_code)

    def test_create_cert_failed_when_sign_sm_cert_by_rsa_ca(self):
        fake_request = mock_create_cert_request_option(issuer_id=self.setup_root_ca_id)
        fake_request['certificate']['key_algorithm'] = 'SM2_256'
        fake_request['certificate']['signature_algorithm'] = 'SM3_256'
        response = self.app.post('/v1/certificates',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(400, response.status_code)

    def test_create_cert_by_sub_ca(self):
        self._setup_sub_ca()
        fake_request = mock_create_cert_request_option(issuer_id=self.setup_sub_ca_id)
        response = self.app.post('/v1/certificates',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        self.assertIsNotNone(resp_body)
        cert = resp_body.get('certificate')
        self.assertEqual(self.setup_sub_ca_id, cert.get('issuer_id'))
        self.assertEqual('ISSUE', cert.get('status'))

    def test_list_cert_filter_by_id(self):
        create_response = self._create_one_cert()
        cert = jsonutils.loads(create_response.data).get('certificate')

        list_response = self.app.get('/v1/certificates?id=3163e2f6-1e0f-44cb-ab30-06892e699c3c',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        self.assertEqual(0, len(jsonutils.loads(list_response.data).get('certificates')))

        list_response = self.app.get(f'/v1/certificates?id={cert["id"]}',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        self.assertEqual(1, len(jsonutils.loads(list_response.data).get('certificates')))

    def test_list_cert_filter_by_common_name(self):
        create_response = self._create_one_cert()
        cert = jsonutils.loads(create_response.data).get('certificate')

        list_response = self.app.get('/v1/certificates?common_name=3163e2f6-1e0f-44cb-ab30-06892e699c3c',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        self.assertEqual(0, len(jsonutils.loads(list_response.data).get('certificates')))

        list_response = self.app.get('/v1/certificates?common_name=MyCert',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        certs_result = jsonutils.loads(list_response.data).get('certificates')
        self.assertEqual(1, len(certs_result))
        self.assertEqual(cert.get('id'), certs_result[0].get('id'))

    def test_list_cert_filter_by_key_algorithm(self):
        create_response = self._create_one_cert()
        cert = jsonutils.loads(create_response.data).get('certificate')

        list_response = self.app.get('/v1/certificates?key_algorithm=ECC_256',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        self.assertEqual(0, len(jsonutils.loads(list_response.data).get('certificates')))

        list_response = self.app.get('/v1/certificates?key_algorithm=RSA_4096',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        certs_result = jsonutils.loads(list_response.data).get('certificates')
        self.assertEqual(1, len(certs_result))
        self.assertEqual(cert.get('id'), certs_result[0].get('id'))

    def test_list_cert_filter_by_signature_algorithm(self):
        create_response = self._create_one_cert()
        cert = jsonutils.loads(create_response.data).get('certificate')

        list_response = self.app.get('/v1/certificates?signature_algorithm=SM3_256',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        self.assertEqual(0, len(jsonutils.loads(list_response.data).get('certificates')))

        list_response = self.app.get('/v1/certificates?signature_algorithm=SHA2_512',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        certs_result = jsonutils.loads(list_response.data).get('certificates')
        self.assertEqual(1, len(certs_result))
        self.assertEqual(cert.get('id'), certs_result[0].get('id'))

    def test_list_cert_filter_by_issuer_id(self):
        create_response = self._create_one_cert()
        cert = jsonutils.loads(create_response.data).get('certificate')

        list_response = self.app.get('/v1/certificates?issuer_id=3163e2f6-1e0f-44cb-ab30-06892e699c3c',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        self.assertEqual(0, len(jsonutils.loads(list_response.data).get('certificates')))

        list_response = self.app.get(f'/v1/certificates?issuer_id={cert.get("issuer_id")}',
                                     content_type='application/json')
        self.assertIsNotNone(list_response)
        self.assertEqual(200, list_response.status_code)
        certs_result = jsonutils.loads(list_response.data).get('certificates')
        self.assertEqual(1, len(certs_result))
        self.assertEqual(cert.get('id'), certs_result[0].get('id'))

    def test_get_certificate(self):
        cert_response = self._create_one_cert()
        cert = jsonutils.loads(cert_response.data).get('certificate')

        response = self.app.get(f'/v1/certificates/{cert.get("id")}',
                                content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.data)
        cert_result = jsonutils.loads(response.data).get('certificate')
        self.assertIsNotNone(cert_result)
        self.assertEqual(cert.get('id'), cert_result.get('id'))

    def test_get_certificate_should_return_404_when_cert_not_found(self):
        response = self.app.get(f'/v1/certificates/e05042a3-6cc6-4664-81a5-1eb4838d26e2',
                                content_type='application/json')
        self.assertEqual(404, response.status_code)

    def test_delete_certificate(self):
        cert_response = self._create_one_cert()
        cert = jsonutils.loads(cert_response.data).get('certificate')
        response = self.app.delete(f'/v1/certificates/{cert.get("id")}',
                                   content_type='application/json')
        self.assertEqual(204, response.status_code)

    def test_delete_certificate_should_return_404_when_cert_not_found(self):
        response = self.app.delete(f'/v1/certificates/e05042a3-6cc6-4664-81a5-1eb4838d26e2',
                                   content_type='application/json')
        self.assertEqual(404, response.status_code)

    def test_revoke_certificate_should_failed_when_ca_not_enable_crl(self):
        create_response = self._create_one_cert()
        cert = jsonutils.loads(create_response.data).get('certificate')
        revoke_response = self.app.post(f'/v1/certificates/{cert.get("id")}/revoke',
                                        content_type='application/json',
                                        data=jsonutils.dumps({}))
        self.assertEqual(400, revoke_response.status_code)

    def test_revoke_certificate(self):
        self._setup_sub_ca()
        create_response = self._create_one_cert(issuer_id=self.setup_sub_ca_id)
        cert = jsonutils.loads(create_response.data).get('certificate')
        revoke_response = self.app.post(f'/v1/certificates/{cert.get("id")}/revoke',
                                        content_type='application/json',
                                        data=jsonutils.dumps({}))
        self.assertEqual(204, revoke_response.status_code)

        show_response = self.app.get(f'/v1/certificates/{cert.get("id")}',
                                     content_type='application/json')
        self.assertEqual(200, show_response.status_code)
        cert_result = jsonutils.loads(show_response.data).get('certificate')
        self.assertIsNotNone(cert_result)
        self.assertEqual('REVOKE', cert_result.get('status'))

    def test_export_certificate_when_signed_by_root_ca(self):
        create_response = self._create_one_cert()
        cert = jsonutils.loads(create_response.data).get('certificate')

        export_response = self.app.post(f'/v1/certificates/{cert["id"]}/export',
                                        content_type='application/json',
                                        data=jsonutils.dumps({}))

        self.assertEqual(200, export_response.status_code)
        result = jsonutils.loads(export_response.data)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.get('certificate'))
        self.assertIsNotNone(result.get('certificate_chain'))
        self.assertEqual(1, len(result.get('certificate_chain')))

    def test_export_certificate_when_signed_by_sub_ca(self):
        self._setup_sub_ca()
        create_response = self._create_one_cert(self.setup_sub_ca_id)
        cert = jsonutils.loads(create_response.data).get('certificate')

        export_response = self.app.post(f'/v1/certificates/{cert["id"]}/export',
                                        content_type='application/json',
                                        data=jsonutils.dumps({}))

        self.assertEqual(200, export_response.status_code)
        result = jsonutils.loads(export_response.data)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.get('certificate'))
        self.assertIsNotNone(result.get('certificate_chain'))
        self.assertEqual(2, len(result.get('certificate_chain')))

    def test_export_certificate_by_zipfile(self):
        create_response = self._create_one_cert()
        cert = jsonutils.loads(create_response.data).get('certificate')

        export_response = self.app.post(f'/v1/certificates/{cert["id"]}/export',
                                        content_type='application/json',
                                        data=jsonutils.dumps({'is_compressed': True}))

        self.assertEqual(200, export_response.status_code)
        self.assertEqual('application/zip', export_response.headers.get('Content-Type'))
        self.assertEqual('attachment; filename="{}.zip"'.format(cert.get('id')),
                         export_response.headers.get('Content-Disposition'))
