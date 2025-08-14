import datetime
from enum import Enum


class CaType(Enum):
    ROOT = 'ROOT'
    SUB = 'SUB'


class CaStatus(Enum):
    ISSUE = 'ISSUE'  # 表示正常签发
    REVOKE = 'REVOKE'  # 表示已被吊销


class KeyAlgorithm(Enum):
    RSA_2048 = 'RSA_2048'
    RSA_3072 = 'RSA_3072'
    RSA_4096 = 'RSA_4096'
    ECC_256 = 'ECC_256'  # ECDSA with key size 256
    ECC_384 = 'ECC_384'  # ECDSA with key size 384
    SM2_256 = 'SM2_256'


class SignatureAlgorithm(Enum):
    SHA2_256 = 'SHA2_256'
    SHA2_384 = 'SHA2_384'
    SHA2_512 = 'SHA2_512'
    SM3_256 = 'SM3_256'


class ValidityType(Enum):
    """证书有效期类型"""
    YEAR = 'YEAR'  # 年（12个月）
    MONTH = 'MONTH'  # 月（统一按31天）


class DistinguishedName(object):
    def __init__(self, country: str = None, state: str = None, locality: str = None, organization: str = None,
                 organization_unit: str = None, common_name: str = None):
        """
        证书名称配置
        :param country: 国家编码
        :param state: 省市名称
        :param locality: 地区名称
        :param organization: 组织名称
        :param organization_unit: 组织单元名称
        :param common_name: 证书通用名称
        """
        self.country = country
        self.state = state
        self.locality = locality
        self.organization = organization
        self.organization_unit = organization_unit
        self.common_name = common_name


class Validity(object):
    def __init__(self, type: ValidityType = None, value: int = None):
        """
        :param type: 有效期类型，YEAR(年，12个月)/MONTH(月，31天)
        :param value: 证书有效期值
        """
        self.type = type
        self.value = value

        self._not_before = None
        self._not_after = None

    def parse(self):
        """转化为证书有效期开始时间和结束时间
        :return tuple: 开始时间、结束时间
        """
        not_before = datetime.datetime.now(datetime.timezone.utc)
        not_after = not_before + datetime.timedelta(days=self.get_effective_days())
        self._not_before = not_before
        self._not_after = not_after
        return not_before, not_after

    def get_effective_days(self):
        """获取证书有效天数"""
        switcher = {
            ValidityType.YEAR: 12 * 31 * 24,
            ValidityType.MONTH: 31 * 24
        }

        return switcher.get(self.type) * self.value

    @property
    def not_before(self) -> datetime.datetime:
        if not self._not_before:
            self.parse()

        return self._not_before

    @property
    def not_after(self) -> datetime.datetime:
        if not self._not_after:
            self.parse()

        return self._not_after

    @property
    def days(self):
        return self.get_effective_days()


class SubjectAlternativeNameType(Enum):
    DNS = 'DNS'
    IP = 'IP'
    EMAIL = 'EMAIL'
    URI = 'URI'


class RevokeReason(Enum):
    UNSPECIFIED = 'UNSPECIFIED'  # 未指定原因
    KEY_COMPROMISE = 'KEY_COMPROMISE'  # 证书密钥材料泄露
    CERTIFICATE_AUTHORITY_COMPROMISE = 'CERTIFICATE_AUTHORITY_COMPROMISE'  # CA密钥材料泄露
    AFFILIATION_CHANGED = 'AFFILIATION_CHANGED'  # 证书中的主体或其他信息已经被改变
    SUPERSEDED = 'SUPERSEDED'  # 证书已被取代
    CESSATION_OF_OPERATION = 'CESSATION_OF_OPERATION'  # 停止运营
    CERTIFICATE_HOLD = 'CERTIFICATE_HOLD'  # 证书当前不应被视为有效
    PRIVILEGE_WITHDRAWN = 'PRIVILEGE_WITHDRAWN'
    ATTRIBUTE_AUTHORITY_COMPROMISE = 'ATTRIBUTE_AUTHORITY_COMPROMISE'


class CrlConfiguration(object):
    def __init__(self, enabled=False, valid_days: int = None):
        self.enabled = enabled
        self.valid_days = valid_days

    def get_last_next_update_time(self):
        if self.valid_days is None or self.valid_days <= 0:
            raise ValueError('valid_days is null or not valid')

        last_update = datetime.datetime.now(datetime.timezone.utc)
        next_update = last_update + datetime.timedelta(days=self.valid_days)
        return last_update, next_update


class CertificateAuthority(object):
    def __init__(self, id=None, type: CaType = None, status: CaStatus = None, key_algorithm: KeyAlgorithm = None,
                 signature_algorithm: SignatureAlgorithm = None, distinguished_name: DistinguishedName = None,
                 issuer_id=None, path_length=None, not_before=None, not_after=None, serial_number=None,
                 created_at=None, updated_at=None, uri=None, password=None, crl_configuration: CrlConfiguration = None):
        self.id = id
        self.type = type
        self.status = status
        self.key_algorithm = key_algorithm
        self.signature_algorithm = signature_algorithm
        self.distinguished_name = distinguished_name
        self.issuer_id = issuer_id
        self.path_length = path_length
        self.not_before = not_before
        self.not_after = not_after
        self.serial_number = serial_number
        self.created_at = created_at
        self.updated_at = updated_at
        self.uri = uri
        self.password = password
        self.crl_configuration = crl_configuration

    @staticmethod
    def from_db(ca_entity):
        dn = DistinguishedName(country=ca_entity.country,
                               state=ca_entity.state,
                               locality=ca_entity.locality,
                               organization=ca_entity.organization,
                               organization_unit=ca_entity.organization_unit,
                               common_name=ca_entity.common_name)
        crl_configuration = CrlConfiguration(enabled=ca_entity.crl_enabled,
                                             valid_days=ca_entity.crl_valid_days)
        return CertificateAuthority(id=ca_entity.id,
                                    type=CaType(ca_entity.type),
                                    status=CaStatus(ca_entity.status),
                                    key_algorithm=KeyAlgorithm(ca_entity.key_algorithm),
                                    signature_algorithm=SignatureAlgorithm(ca_entity.signature_algorithm),
                                    distinguished_name=dn,
                                    issuer_id=ca_entity.issuer_id,
                                    path_length=ca_entity.path_length,
                                    not_before=ca_entity.not_before,
                                    not_after=ca_entity.not_after,
                                    serial_number=ca_entity.serial_number,
                                    created_at=ca_entity.created_at,
                                    updated_at=ca_entity.updated_at,
                                    uri=ca_entity.uri,
                                    password=ca_entity.password,
                                    crl_configuration=crl_configuration)


class CertificateStatus(Enum):
    ISSUE = 'ISSUE'  # 表示正常签发
    REVOKE = 'REVOKE'  # 表示已被吊销


class Certificate(object):
    def __init__(self, id=None, status: CertificateStatus = None, issuer_id=None, key_algorithm: KeyAlgorithm = None,
                 signature_algorithm: SignatureAlgorithm = None, distinguished_name: DistinguishedName = None,
                 not_before=None, not_after=None, serial_number=None, created_at=None, updated_at=None,
                 uri=None, password=None, revoked_at=None, revoked_reason=None):
        self.id = id
        self.status = status
        self.issuer_id = issuer_id
        self.key_algorithm = key_algorithm
        self.signature_algorithm = signature_algorithm
        self.distinguished_name = distinguished_name
        self.not_before = not_before
        self.not_after = not_after
        self.serial_number = serial_number
        self.created_at = created_at
        self.updated_at = updated_at
        self.uri = uri
        self.password = password
        self.revoked_at = revoked_at
        self.revoked_reason = revoked_reason

    @staticmethod
    def from_db(cert_entity):
        dn = DistinguishedName(country=cert_entity.country,
                               state=cert_entity.state,
                               locality=cert_entity.locality,
                               organization=cert_entity.organization,
                               organization_unit=cert_entity.organization_unit,
                               common_name=cert_entity.common_name)
        revoked_reason = None if not cert_entity.revoked_reason else RevokeReason(cert_entity.revoked_reason)
        return Certificate(id=cert_entity.id,
                           status=CertificateStatus(cert_entity.status),
                           issuer_id=cert_entity.issuer_id,
                           key_algorithm=KeyAlgorithm(cert_entity.key_algorithm),
                           signature_algorithm=SignatureAlgorithm(cert_entity.signature_algorithm),
                           distinguished_name=dn,
                           not_before=cert_entity.not_before,
                           not_after=cert_entity.not_after,
                           serial_number=cert_entity.serial_number,
                           created_at=cert_entity.created_at,
                           updated_at=cert_entity.updated_at,
                           uri=cert_entity.uri,
                           password=cert_entity.password,
                           revoked_at=cert_entity.revoked_at,
                           revoked_reason=revoked_reason)


class CertificateResourceType(Enum):
    CA = 'CA'
    CERTIFICATE = 'CERTIFICATE'


class CertificateResourceTag(Enum):
    CERTIFICATE = 'CERTIFICATE'
    PRIVATE_KEY = 'PRIVATE_KEY'


class CertificateResource(object):
    def __init__(self, certificate_type: CertificateResourceType,
                 certificate_data: bytes,
                 private_key_data: bytes = None):
        self.certificate_type = certificate_type
        self.certificate_data = certificate_data
        self.private_key_data = private_key_data


class CertificateContent(object):
    def __init__(self, certificate=None, private_key=None, certificate_chain: list = None):
        self.certificate = certificate
        self.private_key = private_key
        self.certificate_chain = certificate_chain
