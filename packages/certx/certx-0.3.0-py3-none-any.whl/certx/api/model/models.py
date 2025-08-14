from marshmallow import EXCLUDE, fields, Schema, validate

from certx.common.model import models

distinguishedNameRegex = '[a-zA-Z0-9\u4e00-\u9fa5-_.,* ]+'
uuidRegex = '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
passwordRegex = r'[a-zA-Z0-9,.+-_=!@#$%^&*()\[\]]+'


class CaDistinguishedName(Schema):
    common_name = fields.String(required=True,
                                validate=validate.And(validate.Length(min=1, max=64),
                                                      validate.Regexp(distinguishedNameRegex)))
    country = fields.String(required=True, validate=validate.Regexp('[a-zA-Z]{2}'))
    state = fields.String(required=False,
                          validate=validate.And(validate.Length(min=1, max=128),
                                                validate.Regexp(distinguishedNameRegex)))
    locality = fields.String(required=False,
                             validate=validate.And(validate.Length(min=1, max=128),
                                                   validate.Regexp(distinguishedNameRegex)))
    organization = fields.String(required=False,
                                 validate=validate.And(validate.Length(min=1, max=64),
                                                       validate.Regexp(distinguishedNameRegex)))
    organization_unit = fields.String(required=False,
                                      validate=validate.And(validate.Length(min=1, max=64),
                                                            validate.Regexp(distinguishedNameRegex)))

    class Meta(object):
        unknown = EXCLUDE


class Validity(Schema):
    type = fields.Enum(models.ValidityType, load_default=models.ValidityType.YEAR)
    value = fields.Integer(required=True)

    class Meta(object):
        unknown = EXCLUDE


class KeyUsage(Schema):
    digital_signature = fields.Boolean(required=False, load_default=False)
    content_commitment = fields.Boolean(required=False, load_default=False)
    key_encipherment = fields.Boolean(required=False, load_default=False)
    data_encipherment = fields.Boolean(required=False, load_default=False)
    key_agreement = fields.Boolean(required=False, load_default=False)
    encipher_only = fields.Boolean(required=False, load_default=False)
    decipher_only = fields.Boolean(required=False, load_default=False)

    class Meta(object):
        unknown = EXCLUDE


class ExtendedKeyUsage(Schema):
    server_auth = fields.Boolean(required=False, load_default=False)  # 服务器认证
    client_auth = fields.Boolean(required=False, load_default=False)  # 客户端认证
    code_signing = fields.Boolean(required=False, load_default=False)  # 代码签名
    email_protection = fields.Boolean(required=False, load_default=False)  # 邮件保护
    time_stamping = fields.Boolean(required=False, load_default=False)  # 时间戳
    ocsp_signing = fields.Boolean(required=False, load_default=False)  # OCSP 签名
    others = fields.List(fields.String(), required=False, validate=validate.Length(max=6))  # 其他扩展密钥用法 OID

    class Meta(object):
        unknown = EXCLUDE


class SubjectAlternativeName(Schema):
    type = fields.Enum(models.SubjectAlternativeNameType, required=True)
    value = fields.String(required=True)

    class Meta(object):
        unknown = EXCLUDE


class CrlConfiguration(Schema):
    enabled = fields.Boolean(required=False, load_default=False)
    valid_days = fields.Integer(required=False, validate=validate.Range(min=1, max=30))

    class Meta(object):
        unknown = EXCLUDE


class ListCertificateAuthorityParameter(Schema):
    id = fields.String(validate=validate.Regexp(uuidRegex))
    common_name = fields.String(validate=validate.And(validate.Length(min=1, max=64),
                                                      validate.Regexp(distinguishedNameRegex)))
    key_algorithm = fields.Enum(models.KeyAlgorithm)
    signature_algorithm = fields.Enum(models.SignatureAlgorithm)
    limit = fields.Integer(load_default=10, validate=validate.Range(min=0, max=100))
    marker = fields.String(validate=validate.Regexp(uuidRegex))


class CreateCertificateAuthorityOption(Schema):
    type = fields.Enum(models.CaType, load_default=models.CaType.ROOT)
    distinguished_name = fields.Nested(CaDistinguishedName, required=True)
    key_algorithm = fields.Enum(models.KeyAlgorithm, load_default=models.KeyAlgorithm.RSA_4096)
    signature_algorithm = fields.Enum(models.SignatureAlgorithm, load_default=models.SignatureAlgorithm.SHA2_512)
    validity = fields.Nested(Validity, required=True)
    issuer_id = fields.String(required=False, validate=validate.Regexp(uuidRegex))
    path_length = fields.Integer(required=False, validate=validate.Range(min=0, max=3), load_default=0)
    crl_configuration = fields.Nested(CrlConfiguration, required=False)

    class Meta(object):
        unknown = EXCLUDE


class CreateCertificateAuthorityRequestBody(Schema):
    certificate_authority = fields.Nested(CreateCertificateAuthorityOption, required=True)

    class Meta(object):
        unknown = EXCLUDE


class CertificateAuthorityContent(Schema):
    certificate = fields.String()
    certificate_chain = fields.List(fields.String())


class CertificateAuthority(Schema):
    id = fields.String()
    type = fields.Enum(models.CaType)
    status = fields.Enum(models.CaType)
    key_algorithm = fields.Enum(models.KeyAlgorithm)
    signature_algorithm = fields.Enum(models.SignatureAlgorithm)
    distinguished_name = fields.Nested(CaDistinguishedName)
    serial_number = fields.String()
    issuer_id = fields.String()
    path_length = fields.Integer()
    not_before = fields.DateTime()
    not_after = fields.DateTime()
    crl_configuration = fields.Nested(CrlConfiguration)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class ListCertificateParameter(Schema):
    id = fields.String(validate=validate.Regexp(uuidRegex))
    issuer_id = fields.String(validate=validate.Regexp(uuidRegex))
    common_name = fields.String(validate=validate.And(validate.Length(min=1, max=64),
                                                      validate.Regexp(distinguishedNameRegex)))
    key_algorithm = fields.Enum(models.KeyAlgorithm)
    signature_algorithm = fields.Enum(models.SignatureAlgorithm)
    limit = fields.Integer(load_default=10, validate=validate.Range(min=0, max=1000))
    marker = fields.String(validate=validate.Regexp(uuidRegex))


class CertDistinguishedName(Schema):
    common_name = fields.String(required=True,
                                validate=validate.And(validate.Length(min=1, max=64),
                                                      validate.Regexp(distinguishedNameRegex)))
    country = fields.String(required=False, validate=validate.Regexp('[a-zA-Z]{2}'))
    state = fields.String(required=False,
                          validate=validate.And(validate.Length(min=1, max=128),
                                                validate.Regexp(distinguishedNameRegex)))
    locality = fields.String(required=False,
                             validate=validate.And(validate.Length(min=1, max=128),
                                                   validate.Regexp(distinguishedNameRegex)))
    organization = fields.String(required=False,
                                 validate=validate.And(validate.Length(min=1, max=64),
                                                       validate.Regexp(distinguishedNameRegex)))
    organization_unit = fields.String(required=False,
                                      validate=validate.And(validate.Length(min=1, max=64),
                                                            validate.Regexp(distinguishedNameRegex)))

    class Meta(object):
        unknown = EXCLUDE


class Certificate(Schema):
    id = fields.String()
    status = fields.Enum(models.CertificateStatus)
    issuer_id = fields.String()
    key_algorithm = fields.Enum(models.KeyAlgorithm)
    signature_algorithm = fields.Enum(models.SignatureAlgorithm)
    distinguished_name = fields.Nested(CertDistinguishedName)
    serial_number = fields.String()
    not_before = fields.DateTime()
    not_after = fields.DateTime()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class CreateCertificateOption(Schema):
    issuer_id = fields.String(required=True, validate=validate.Regexp(uuidRegex))
    distinguished_name = fields.Nested(CertDistinguishedName, required=True)
    key_algorithm = fields.Enum(models.KeyAlgorithm, required=False)
    signature_algorithm = fields.Enum(models.SignatureAlgorithm, required=False)
    validity = fields.Nested(Validity, required=True)
    key_usage = fields.Nested(KeyUsage, required=False)  # 密钥用法
    extended_key_usage = fields.Nested(ExtendedKeyUsage, required=False)  # 扩展密钥用法
    subject_alternative_names = fields.List(fields.Nested(SubjectAlternativeName), required=False,
                                            validate=validate.Length(max=20))  # 证书主体别名

    class Meta(object):
        unknown = EXCLUDE


class CreateCertificateRequestBody(Schema):
    certificate = fields.Nested(CreateCertificateOption, required=True)

    class Meta(object):
        unknown = EXCLUDE


class ExportCertificateRequestBody(Schema):
    password = fields.String(required=False, validate=validate.And(validate.Length(min=1, max=32),
                                                                   validate.Regexp(passwordRegex)))
    is_compressed = fields.Boolean(required=False, load_default=False)

    class Meta(object):
        unknown = EXCLUDE


class CertificateContent(Schema):
    certificate = fields.String()
    private_key = fields.String()
    certificate_chain = fields.List(fields.String())


class RevokeCertificateRequestBody(Schema):
    reason = fields.Enum(models.RevokeReason, load_default=models.RevokeReason.UNSPECIFIED)

    class Meta(object):
        unknown = EXCLUDE
