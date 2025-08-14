import ipaddress

from cryptography import x509

from certx.common import exceptions
from certx.common.model import models

_SUPPORTED_EXTENDED_KEY_USAGE = {
    "server_auth": {
        "oid": x509.OID_SERVER_AUTH,
        "name": "serverAuth"
    },
    "client_auth": {
        "oid": x509.OID_CLIENT_AUTH,
        "name": "clientAuth"
    },
    "code_signing": {
        "oid": x509.OID_CODE_SIGNING,
        "name": "codeSigning",
    },
    "email_protection": {
        "oid": x509.OID_CODE_SIGNING,
        "name": "emailProtection"
    },
    "time_stamping": {
        "oid": x509.OID_TIME_STAMPING,
        "name": "timeStamping"
    },
    "ocsp_signing": {
        "oid": x509.OID_OCSP_SIGNING,
        "name": "OCSPSigning"
    }
}

_ENABLED_KEYS = ['others'] + list(_SUPPORTED_EXTENDED_KEY_USAGE.keys())


def build_x509_key_usage(key_usage) -> x509.KeyUsage:
    if not key_usage:
        return None

    key_agreement = key_usage.get('key_agreement')
    encipher_only = key_usage.get('encipher_only')
    decipher_only = key_usage.get('decipher_only')
    if not key_agreement and (encipher_only or decipher_only):
        raise exceptions.InvalidParameterValue(
            "encipher_only and decipher_only can only be true when "
            "key_agreement is true"
        )

    return x509.KeyUsage(key_usage.get('digital_signature'),
                         key_usage.get('content_commitment'),
                         key_usage.get('key_encipherment'),
                         key_usage.get('data_encipherment'),
                         key_agreement,
                         False, False,
                         encipher_only,
                         decipher_only)


def build_x509_extended_key_usage(extended_key_usage: dict) -> x509.ExtendedKeyUsage:
    if not extended_key_usage:
        return None

    usages = set()
    for usage_key, usage_value in extended_key_usage.items():
        if usage_key not in _ENABLED_KEYS:
            raise exceptions.BadRequest('Invalid item: %(key)s, %(val)s', key=usage_key, val=usage_value)

        if usage_key in _SUPPORTED_EXTENDED_KEY_USAGE:
            if usage_value is None:
                continue
            if not isinstance(usage_value, bool):
                raise exceptions.BadRequest('Invalid item: %(key)s, %(val)s', key=usage_key, val=usage_value)
            if not usage_value:
                continue

            usages.add(_SUPPORTED_EXTENDED_KEY_USAGE.get(usage_key).get("oid"))
        else:  # usage_key == 'others'
            if usage_value is None:
                continue
            if not isinstance(usage_value, list):
                raise exceptions.BadRequest('Custom extended key usage must be list')

            for v in usage_value:
                try:
                    usages.add(x509.ObjectIdentifier(v))
                except ValueError:
                    raise exceptions.InvalidParameterValue('Invalid object_identifier: {}'.format(v))

    return x509.ExtendedKeyUsage(usages)


_SUBJECT_ALTERNATIVE_NAME_MAP = {
    models.SubjectAlternativeNameType.DNS: x509.DNSName,
    models.SubjectAlternativeNameType.IP: x509.IPAddress,
    models.SubjectAlternativeNameType.EMAIL: x509.RFC822Name,
    models.SubjectAlternativeNameType.URI: x509.UniformResourceIdentifier
}


def build_x509_subject_alternative_name(subject_alternative_names: list) -> x509.SubjectAlternativeName:
    if not subject_alternative_names:
        return None

    existed_cache = {}  # key: name_type, value: items of name_value. {name_type: [name_value]}
    general_names = []
    for item in subject_alternative_names:
        name_type = item.get('type')
        name_value = item.get('value')

        existed = existed_cache.get(name_type) or []
        if name_value in existed:
            continue

        if name_type == models.SubjectAlternativeNameType.IP:
            try:
                name_value = ipaddress.ip_address(item.get('value'))
            except:
                try:
                    name_value = ipaddress.ip_network(item.get('value'))
                except:
                    raise exceptions.InvalidParameterValue('Invalid ip: {}'.format(item.get('value')))

        general_names.append(_SUBJECT_ALTERNATIVE_NAME_MAP.get(name_type)(name_value))
        existed.append(name_value)
        existed_cache[name_type] = existed

    return x509.SubjectAlternativeName(general_names)


_REVOKE_REASON_MAP = {
    models.RevokeReason.UNSPECIFIED: x509.ReasonFlags.unspecified,
    models.RevokeReason.KEY_COMPROMISE: x509.ReasonFlags.key_compromise,
    models.RevokeReason.CERTIFICATE_AUTHORITY_COMPROMISE: x509.ReasonFlags.ca_compromise,
    models.RevokeReason.AFFILIATION_CHANGED: x509.ReasonFlags.affiliation_changed,
    models.RevokeReason.SUPERSEDED: x509.ReasonFlags.superseded,
    models.RevokeReason.CESSATION_OF_OPERATION: x509.ReasonFlags.cessation_of_operation,
    models.RevokeReason.CERTIFICATE_HOLD: x509.ReasonFlags.certificate_hold,
    models.RevokeReason.PRIVILEGE_WITHDRAWN: x509.ReasonFlags.privilege_withdrawn,
    models.RevokeReason.ATTRIBUTE_AUTHORITY_COMPROMISE: x509.ReasonFlags.aa_compromise
}


def to_x509_crl_reason(revoke_reason: models.RevokeReason) -> x509.CRLReason:
    if not revoke_reason:
        return None

    if revoke_reason not in _REVOKE_REASON_MAP:
        raise exceptions.InvalidParameterValue('Invalid revoke reason: {}'.format(revoke_reason.value))

    return x509.CRLReason(_REVOKE_REASON_MAP[revoke_reason])
