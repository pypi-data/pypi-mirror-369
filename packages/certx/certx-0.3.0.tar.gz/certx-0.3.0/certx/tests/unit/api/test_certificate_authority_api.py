from oslo_serialization import jsonutils

from certx.tests.unit.api import ApiResourceBaseTestCase
from certx.tests.unit.db import utils as db_utils


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
                "enabled": False
            }
        }
    }


class TestCertificateAuthoritiesResource(ApiResourceBaseTestCase):
    def setUp(self):
        super(TestCertificateAuthoritiesResource, self).setUp()
        self._setup_test_data()

    @staticmethod
    def _setup_test_data():
        db_utils.create_test_ca()

    def test_get_ca(self):
        response = self.app.get('/v1/certificate-authorities?id=e218012d-2101-4348-9f9a-b3989b364d88',
                                content_type='application/json')
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        self.assertIsNotNone(resp_body)
        cas = resp_body.get('certificate_authorities')
        self.assertIsNotNone(cas)
        ca = cas[0]
        self.assertIsNotNone(ca['id'])
        self.assertEqual('e218012d-2101-4348-9f9a-b3989b364d88', ca['id'])
        self.assertEqual('ROOT', ca['type'])
        self.assertEqual('ISSUE', ca['status'])
        self.assertEqual('RSA_4096', ca['key_algorithm'])
        self.assertEqual('SHA2_256', ca['signature_algorithm'])
        self.assertIsNone(ca.get('issuer_id'))
        self.assertEqual('MyCA', ca['distinguished_name']['common_name'])
        self.assertEqual('CN', ca['distinguished_name']['country'])

    def test_get_ca_should_failed_with_unsupported_algorithm(self):
        response = self.app.get('/v1/certificate-authorities?key_algorithm=rsa_666',
                                content_type='application/json')
        self.assertEqual(400, response.status_code)

        response = self.app.get('/v1/certificate-authorities?signature_algorithm=sha_666',
                                content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_get_ca_should_return_empty_when_not_found_filter_with_common_name(self):
        response = self.app.get('/v1/certificate-authorities?common_name=not_found_xxx',
                                content_type='application/json')
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        self.assertIsNotNone(resp_body)
        self.assertTrue(len(resp_body.get('certificate_authorities', [])) == 0)

    def test_create_ca(self):
        fake_request = mock_create_ca_request_option()
        response = self.app.post('/v1/certificate-authorities',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        self.assertIsNotNone(resp_body)
        ca = resp_body.get('certificate_authority')
        self.assertIsNotNone(ca)
        self.assertIsNotNone(ca['id'])
        self.assertEqual('ROOT', ca['type'])
        self.assertEqual('ISSUE', ca['status'])
        self.assertEqual('RSA_4096', ca['key_algorithm'])
        self.assertEqual('SHA2_256', ca['signature_algorithm'])
        self.assertIsNone(ca.get('issuer_id'))
        self.assertEqual('MyCA', ca['distinguished_name']['common_name'])
        self.assertEqual('CN', ca['distinguished_name']['country'])

    def test_create_ca_should_failed_when_key_and_signature_algorithm_not_matched(self):
        fake_request = mock_create_ca_request_option()
        fake_request['certificate_authority']['key_algorithm'] = 'RSA_4096'
        fake_request['certificate_authority']['signature_algorithm'] = 'SM3_256'
        response = self.app.post('/v1/certificate-authorities',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(400, response.status_code)

    def test_create_ca_should_failed_when_create_sub_ca_without_issuer_id(self):
        fake_request = mock_create_ca_request_option()
        fake_request['certificate_authority']['type'] = 'SUB'
        response = self.app.post('/v1/certificate-authorities',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(400, response.status_code)

    def test_create_ca_should_failed_when_enable_crl_but_valid_days_is_none(self):
        fake_request = mock_create_ca_request_option()
        fake_request['certificate_authority']['crl_configuration']['enabled'] = True
        response = self.app.post('/v1/certificate-authorities',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(400, response.status_code)


class TestCertificateAuthorityResource(ApiResourceBaseTestCase):
    def setUp(self):
        super(TestCertificateAuthorityResource, self).setUp()
        self._setup_test_data()

    def _setup_test_data(self):
        fake_request = mock_create_ca_request_option()
        response = self.app.post('/v1/certificate-authorities',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        resp_body = jsonutils.loads(response.data)
        ca = resp_body.get('certificate_authority')
        self.setup_ca_id = ca['id']

    def test_get_ca(self):
        response = self.app.get(f'/v1/certificate-authorities/{self.setup_ca_id}',
                                content_type='application/json')
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        ca = resp_body.get('certificate_authority')
        self.assertIsNotNone(ca)

    def test_delete_ca(self):
        response = self.app.delete(f'/v1/certificate-authorities/{self.setup_ca_id}',
                                   content_type='application/json')
        self.assertEqual(204, response.status_code)

        response = self.app.get(f'/v1/certificate-authorities/{self.setup_ca_id}',
                                content_type='application/json')
        self.assertEqual(404, response.status_code)

    def test_export_root_ca(self):
        response = self.app.post(f'/v1/certificate-authorities/{self.setup_ca_id}/export',
                                 content_type='application/json')
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        self.assertIsNotNone(resp_body)
        self.assertIsNotNone(resp_body.get('certificate'))
        self.assertIsNone(resp_body.get('certificate_chain'))

    def test_export_sub_ca(self):
        fake_request = mock_create_ca_request_option()
        fake_request['certificate_authority']['type'] = 'SUB'
        fake_request['certificate_authority']['issuer_id'] = self.setup_ca_id
        fake_request['certificate_authority']['distinguished_name']['common_name'] = 'SubCA'
        response = self.app.post('/v1/certificate-authorities',
                                 content_type='application/json',
                                 data=jsonutils.dumps(fake_request))
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        sub_ca = resp_body.get('certificate_authority')
        self.assertIsNotNone(sub_ca)
        self.assertEqual(self.setup_ca_id, sub_ca['issuer_id'])
        root_ca_export_response = self.app.post(f'/v1/certificate-authorities/{self.setup_ca_id}/export',
                                                content_type='application/json')
        self.assertEqual(200, response.status_code)
        root_ca_export_resp_body = jsonutils.loads(root_ca_export_response.data)

        response = self.app.post(f'/v1/certificate-authorities/{sub_ca["id"]}/export',
                                 content_type='application/json')
        self.assertEqual(200, response.status_code)
        resp_body = jsonutils.loads(response.data)
        self.assertIsNotNone(resp_body)
        self.assertIsNotNone(resp_body.get('certificate'))
        self.assertIsNotNone(resp_body.get('certificate_chain'))
        self.assertEqual(root_ca_export_resp_body.get('certificate'),
                         resp_body.get('certificate_chain')[0])
