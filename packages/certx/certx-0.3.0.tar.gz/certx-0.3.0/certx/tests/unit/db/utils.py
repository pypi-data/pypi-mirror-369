import datetime

from oslo_utils import timeutils

from certx.db import api as db_api


def get_test_ca(**kwargs):
    not_before = kwargs.get('not_before', timeutils.utcnow())
    not_after = kwargs.get('not_before', not_before + datetime.timedelta(days=365))
    ca = {
        'id': kwargs.get('id', 'e218012d-2101-4348-9f9a-b3989b364d88'),
        'type': kwargs.get('type', 'ROOT'),  # 默认根CA
        'status': kwargs.get('status', 'ISSUE'),  # 默认创建后的签发状态
        'path_length': kwargs.get('path_length', None),
        'issuer_id': kwargs.get('issuer_id', None),
        'key_algorithm': kwargs.get('key_algorithm', 'RSA_4096'),
        'signature_algorithm': kwargs.get('signature_algorithm', 'SHA2_256'),
        'serial_number': kwargs.get('serial_number', 'None'),
        'not_before': not_before,
        'not_after': not_after,
        'common_name': 'MyCA',
        'country': 'CN',
        'state': 'BJ',
        'locality': 'BJ',
        'organization': 'O',
        'organization_unit': 'OU',
        'uri': 'ca_uri',
        'password': 'xxxxxx',
        'crl_enabled': True,
        'crl_valid_days': 15,
        'created_at': not_before
    }

    return ca


def create_test_ca(**kwargs):
    ca = get_test_ca(**kwargs)
    dbapi = db_api.get_instance()
    return dbapi.create_certificate_authority(ca)


def destroy_all_ca():
    dbapi = db_api.get_instance()
    cas = dbapi.get_certificate_authorities()
    for ca in cas:
        dbapi.destroy_certificate_authority(ca.id)


def destroy_all_cert():
    dbapi = db_api.get_instance()
    certs = dbapi.get_certificates()
    for cert in certs:
        dbapi.destroy_certificate(cert.id)
