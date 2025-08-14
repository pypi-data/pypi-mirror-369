import unittest

from cryptography import x509
from cryptography.x509 import ExtendedKeyUsage
from cryptography.x509 import ObjectIdentifier

from certx.common.model.models import SubjectAlternativeNameType

from certx.provider.x509 import openssl


class TestOpensslExtensionParamBuilder(unittest.TestCase):
    def test_build_empty_params(self):
        ext_param = openssl.OpensslExtensionParamBuilder().build()
        self.assertEqual(
            'echo "[v3_ca]";echo "subjectKeyIdentifier=hash";echo "authorityKeyIdentifier=keyid"',
            ext_param)

    def test_build_empty_params_with_extension_name(self):
        ext_param = openssl.OpensslExtensionParamBuilder().build('xx')
        self.assertEqual(
            'echo "[xx]";echo "subjectKeyIdentifier=hash";echo "authorityKeyIdentifier=keyid"',
            ext_param)

    def test_build_basic_constraints_for_ca(self):
        basic_constraints = x509.BasicConstraints(ca=True, path_length=None)
        ext_param = openssl.OpensslExtensionParamBuilder(basic_constraints=basic_constraints).build()
        self.assertTrue('echo "basicConstraints=CA:true"' in ext_param)

    def test_build_basic_constraints_for_ca_with_path_length(self):
        basic_constraints = x509.BasicConstraints(ca=True, path_length=1)
        ext_param = openssl.OpensslExtensionParamBuilder(basic_constraints=basic_constraints).build()
        self.assertTrue('echo "basicConstraints=CA:true,pathlen:1"', ext_param)

    def test_build_basic_constraints_for_not_ca(self):
        basic_constraints = x509.BasicConstraints(ca=False, path_length=None)
        ext_param = openssl.OpensslExtensionParamBuilder(basic_constraints=basic_constraints).build()
        self.assertTrue('echo "basicConstraints=CA:false"', ext_param)

    def test_build_key_usage(self):
        key_usage = x509.KeyUsage(True, False, False, False, False, True, True, False, False)
        result = openssl.OpensslExtensionParamBuilder(key_usage=key_usage).build()
        self.assertTrue(result.startswith('echo "[v3_ca]";'))
        self.assertIn('digitalSignature', result)
        self.assertIn('keyCertSign', result)
        self.assertIn('cRLSign', result)
        self.assertNotIn('keyAgreement', result)
        self.assertNotIn('encipherOnly', result)

    def test_build_extended_key_usage(self):
        result = openssl.OpensslExtensionParamBuilder(
            extended_key_usage=ExtendedKeyUsage([ObjectIdentifier("1.3.6.1.5.5.7.3.1")])).build()
        self.assertTrue('echo "extendedKeyUsage=serverAuth"', result)

    def test_build_subject_alternative_name_with_two_different_dns(self):
        result = openssl.OpensslExtensionParamBuilder(
            subject_alternative_names=[
                {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-1'},
                {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-2'}
            ]).build()
        self.assertTrue('DNS.1=dns-1' in result)
        self.assertTrue('DNS.2=dns-2' in result)

    def test_build_subject_alternative_name_with_two_same_dns(self):
        result = openssl.OpensslExtensionParamBuilder(
            subject_alternative_names=[
                {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-1'},
                {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-1'}
            ]).build()
        self.assertTrue('DNS.1=dns-1' in result)
        self.assertTrue('DNS.2=dns-2' not in result)

    def test_build_subject_alternative_name_with_two_different_type_items(self):
        result = openssl.OpensslExtensionParamBuilder(
            subject_alternative_names=[
                {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-1'},
                {'type': SubjectAlternativeNameType.IP, 'value': 'ip-1'}
            ]).build()
        self.assertTrue('DNS.1=dns-1' in result)
        self.assertTrue('IP.1=ip-1' in result)


def mock_meet_condition():
    try:
        openssl.detect_openssl()
    except Exception:
        return False

    return True


class TestOpensslGmKeyProvider(unittest.TestCase):
    @unittest.skipUnless(mock_meet_condition(), 'Only running on Linux')
    def setUp(self) -> None:
        pass

    def test_generate_private_key(self):
        pass
