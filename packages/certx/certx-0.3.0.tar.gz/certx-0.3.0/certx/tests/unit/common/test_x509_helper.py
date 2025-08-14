import unittest

from cryptography import x509
from cryptography.x509 import ObjectIdentifier
from cryptography.x509 import ExtendedKeyUsage

from certx.common import x509_helper, exceptions
from certx.common.model.models import RevokeReason, SubjectAlternativeNameType


class TestX509Helper(unittest.TestCase):
    def test_build_x509_key_usage_should_return_none_when_with_empty_input(self):
        self.assertIsNone(x509_helper.build_x509_key_usage(None))

    def test_build_x509_key_usage_should_raise_when_not_key_agreement_but_encipher_enabled(self):
        self.assertRaises(exceptions.InvalidParameterValue,
                          x509_helper.build_x509_key_usage,
                          {
                              'key_agreement': False,
                              'encipher_only': True
                          })

        self.assertRaises(exceptions.InvalidParameterValue,
                          x509_helper.build_x509_key_usage,
                          {
                              'key_agreement': False,
                              'decipher_only': True
                          })

    def test_build_x509_key_usage(self):
        key_usage = x509_helper.build_x509_key_usage({
            'digital_signature': True
        })
        self.assertTrue(key_usage.digital_signature)
        self.assertFalse(key_usage.content_commitment)
        self.assertFalse(key_usage.key_encipherment)
        self.assertFalse(key_usage.data_encipherment)
        self.assertFalse(key_usage.key_cert_sign)
        self.assertFalse(key_usage.crl_sign)

    def test_build_x509_extended_key_usage_with_exact_items(self):
        result = x509_helper.build_x509_extended_key_usage({
            'server_auth': True,
            'client_auth': False
        })

        self.assertEqual(ExtendedKeyUsage([ObjectIdentifier("1.3.6.1.5.5.7.3.1")]), result)

    def test_build_x509_extended_key_usage_with_others_items(self):
        result = x509_helper.build_x509_extended_key_usage({
            'others': ['1.3.6.1.5.5.7.3.17']
        })

        self.assertEqual(ExtendedKeyUsage([ObjectIdentifier("1.3.6.1.5.5.7.3.17")]), result)

    def test_build_x509_extended_key_usage_override_exact_items_with_others_items(self):
        result = x509_helper.build_x509_extended_key_usage({
            'server_auth': True,
            'others': ['1.3.6.1.5.5.7.3.1']
        })

        self.assertEqual(ExtendedKeyUsage([ObjectIdentifier("1.3.6.1.5.5.7.3.1")]), result)

    def test_build_x509_extended_key_usage_with_invalid_key(self):
        self.assertRaises(exceptions.BadRequest, x509_helper.build_x509_extended_key_usage, {'test': True})

    def test_build_x509_extended_key_usage_with_invalid_value(self):
        self.assertRaises(exceptions.BadRequest, x509_helper.build_x509_extended_key_usage, {'server_auth': 1})
        self.assertRaises(exceptions.BadRequest, x509_helper.build_x509_extended_key_usage, {'others': 1})

    def test_build_x509_extended_key_usage_with_invalid_oid(self):
        self.assertRaises(exceptions.BadRequest, x509_helper.build_x509_extended_key_usage, {'others': ['2.2.2.']})

    def test_build_x509_subject_alternative_name_with_two_different_dns(self):
        result = x509_helper.build_x509_subject_alternative_name([
            {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-1'},
            {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-2'}
        ])
        self.assertEqual(['dns-1', 'dns-2'], result.get_values_for_type(x509.DNSName))

    def test_build_x509_subject_alternative_name_with_two_same_dns(self):
        result = x509_helper.build_x509_subject_alternative_name([
            {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-1'},
            {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-1'}
        ])
        self.assertEqual(['dns-1'], result.get_values_for_type(x509.DNSName))

    def test_build_x509_subject_alternative_name_with_two_different_type_items(self):
        result = x509_helper.build_x509_subject_alternative_name([
            {'type': SubjectAlternativeNameType.DNS, 'value': 'dns-1'},
            {'type': SubjectAlternativeNameType.IP, 'value': '127.0.0.1'}
        ])
        self.assertEqual(['dns-1'], result.get_values_for_type(x509.DNSName))
        self.assertEqual(1, len(result.get_values_for_type(x509.IPAddress)))
        self.assertEqual('127.0.0.1', str(result.get_values_for_type(x509.IPAddress)[0]))

    def test_build_x509_subject_alternative_name_with_invalid_ip(self):
        self.assertRaises(exceptions.InvalidParameterValue, x509_helper.build_x509_subject_alternative_name, [
            {'type': SubjectAlternativeNameType.IP, 'value': 'ip-1'}
        ])

    def test_to_x509_crl_reason_should_return_none_when_with_empty_input(self):
        self.assertIsNone(x509_helper.to_x509_crl_reason(None))

    def test_to_x509_crl_reason(self):
        revoke_reason_map = {
            RevokeReason.UNSPECIFIED: x509.CRLReason(x509.ReasonFlags.unspecified),
            RevokeReason.KEY_COMPROMISE: x509.CRLReason(x509.ReasonFlags.key_compromise),
            RevokeReason.CERTIFICATE_AUTHORITY_COMPROMISE: x509.CRLReason(x509.ReasonFlags.ca_compromise),
            RevokeReason.AFFILIATION_CHANGED: x509.CRLReason(x509.ReasonFlags.affiliation_changed),
            RevokeReason.SUPERSEDED: x509.CRLReason(x509.ReasonFlags.superseded),
            RevokeReason.CESSATION_OF_OPERATION: x509.CRLReason(x509.ReasonFlags.cessation_of_operation),
            RevokeReason.CERTIFICATE_HOLD: x509.CRLReason(x509.ReasonFlags.certificate_hold),
            RevokeReason.PRIVILEGE_WITHDRAWN: x509.CRLReason(x509.ReasonFlags.privilege_withdrawn),
            RevokeReason.ATTRIBUTE_AUTHORITY_COMPROMISE: x509.CRLReason(x509.ReasonFlags.aa_compromise)
        }

        for k, v in revoke_reason_map.items():
            self.assertEqual(v, x509_helper.to_x509_crl_reason(k))
