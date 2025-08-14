from typing import List

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509.extensions import Extension
from oslo_log import log as logging

from certx.common import exceptions, x509_helper
from certx.common.model.models import Certificate, CrlConfiguration, DistinguishedName, SignatureAlgorithm, Validity
from certx.provider.x509.base import CertificateProvider

logger = logging.getLogger(__name__)

_SIG_ALG_MAP = {
    SignatureAlgorithm.SHA2_256: hashes.SHA256(),
    SignatureAlgorithm.SHA2_384: hashes.SHA384(),
    SignatureAlgorithm.SHA2_512: hashes.SHA512()
}


class DefaultCertificateProvider(CertificateProvider):
    def generate_ca_certificate(self, dn: DistinguishedName, private_key,
                                validity: Validity,
                                signature_algorithm: SignatureAlgorithm = None,
                                root_cert=None, root_key=None, path_length=0):
        if (root_cert and not root_key) or (not root_cert and root_key):
            logger.error('Create CA failed due to root_cert and root_key should bath not emtpy or empty')
            raise exceptions.ServiceException('Create CA failed')

        if signature_algorithm is None:
            signature_algorithm = self.signature_algorithm

        ca_subject = self._build_subject(dn)

        issuer_subject = ca_subject if root_cert is None else root_cert.subject
        issuer_private_key = private_key if root_cert is None else root_key
        path_length = None if not root_cert else path_length

        extension_types = [
            x509.BasicConstraints(ca=True, path_length=path_length),
            x509.SubjectKeyIdentifier.from_public_key(private_key.public_key())
        ]

        if root_key:
            extension_types.append(x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()))

        # default key usage for CA: digitalSignature,keyCertSign,cRLSign
        key_usage = x509.KeyUsage(True, False, False, False, False, True, True, False, False)
        if root_cert:
            key_usage = x509.KeyUsage(True, False, False, False, False, True, True, False, False)
        extension_types.append(key_usage)

        return self._generate_certificate(issuer_subject,
                                          ca_subject,
                                          issuer_private_key,
                                          private_key.public_key(),
                                          self._to_sig_alg_impl(signature_algorithm),
                                          validity,
                                          extension_types=extension_types)

    def generate_certificate(self, ca_cert, ca_key, cert_dn: DistinguishedName, cert_private_key, validity: Validity,
                             signature_algorithm: SignatureAlgorithm = None,
                             key_usage=None,
                             extended_key_usage=None,
                             subject_alternative_name=None,
                             crl_distribution_points: List = None,
                             **kwargs):
        if signature_algorithm is None:
            signature_algorithm = self.signature_algorithm

        extension_types = [
            x509.BasicConstraints(ca=False, path_length=None),
            x509.SubjectKeyIdentifier.from_public_key(cert_private_key.public_key()),
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key())
        ]
        if key_usage:
            extension_types.append(key_usage)

        if extended_key_usage:
            extension_types.append(extended_key_usage)

        if subject_alternative_name:
            extension_types.append(subject_alternative_name)

        if crl_distribution_points:
            extension_types.append(crl_distribution_points)

        return self._generate_certificate(ca_cert.subject, self._build_subject(cert_dn), ca_key,
                                          cert_private_key.public_key(),
                                          self._to_sig_alg_impl(signature_algorithm), validity,
                                          extension_types=extension_types)

    def load_certificate(self, certificate_data):
        return x509.load_pem_x509_certificate(certificate_data)

    def generate_crl(self, ca_cert, ca_key, crl_configuration: CrlConfiguration,
                     certs: List[Certificate]):
        if not crl_configuration or not crl_configuration.enabled:
            logger.error('CRL configuration required or CRL disabled')
            raise exceptions.BadRequest('CRL configuration required or CRL disabled')

        logger.info('Generate CRL. issuer: {}, serial_number: {}'.format(ca_cert.issuer, ca_cert.serial_number))

        last_update, next_update = crl_configuration.get_last_next_update_time()

        builder = x509.CertificateRevocationListBuilder()
        builder = builder.issuer_name(ca_cert.issuer)
        builder = builder.last_update(last_update)
        builder = builder.next_update(next_update)

        if certs:
            for cert in certs:
                revoked_cert = x509.RevokedCertificateBuilder()
                revoked_cert = revoked_cert.serial_number(int(cert.serial_number))
                revoked_cert = revoked_cert.revocation_date(cert.revoked_at)
                revoked_reason = cert.revoked_reason
                if revoked_reason:
                    revoked_cert = revoked_cert.add_extension(x509_helper.to_x509_crl_reason(cert.revoked_reason),
                                                              critical=False)
                builder = builder.add_revoked_certificate(revoked_cert.build(default_backend()))

        return builder.sign(private_key=ca_key,
                            algorithm=ca_cert.signature_hash_algorithm,
                            backend=default_backend())

    @staticmethod
    def _to_sig_alg_impl(signature_algorithm: SignatureAlgorithm):
        if signature_algorithm not in _SIG_ALG_MAP:
            logger.error('unsupported signature_algorithm {}'.format(signature_algorithm.value))
            raise exceptions.NotImplementException('unsupported signature_algorithm')
        return _SIG_ALG_MAP[signature_algorithm]

    @staticmethod
    def _generate_certificate(issuer_name: x509.Name, subject_name: x509.Name,
                              issuer_private_key,
                              cert_public_key,
                              signature_algorithm,
                              validity: Validity,
                              serial_number: int = None,
                              extension_types=None):
        """生成证书
        :param issuer_name: 签发者CA对象
        :param subject_name: 证书对象
        :param issuer_private_key: 签发者私钥
        :param cert_public_key: 证书公钥
        :param signature_algorithm: 签名算法
        :param validity: 证书有效期
        :param serial_number: 证书序列好
        :param extension_types: 证书扩展用途
        :return:
        """
        extensions = []
        if extension_types is not None and isinstance(extension_types, list):
            for extension in extension_types:
                extensions.append(Extension(extension.oid, False, extension))

        return (x509.CertificateBuilder(extensions=extensions)
                .subject_name(subject_name)
                .issuer_name(issuer_name)
                .public_key(cert_public_key)
                .serial_number(x509.random_serial_number() if serial_number is None else serial_number)
                .not_valid_before(validity.not_before)
                .not_valid_after(validity.not_after)
                .sign(issuer_private_key, signature_algorithm, default_backend()))

    @staticmethod
    def _build_subject(dn) -> x509.Name:
        name_attrs = [
            x509.NameAttribute(x509.NameOID.COMMON_NAME, dn.common_name)
        ]
        if dn.country:
            name_attrs.append(x509.NameAttribute(x509.NameOID.COUNTRY_NAME, dn.country))
        if dn.state:
            name_attrs.append(x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, dn.state))
        if dn.locality:
            name_attrs.append(x509.NameAttribute(x509.NameOID.LOCALITY_NAME, dn.locality))
        if dn.organization:
            name_attrs.append(x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, dn.organization))
        if dn.organization_unit:
            name_attrs.append(x509.NameAttribute(x509.NameOID.ORGANIZATIONAL_UNIT_NAME, dn.organization_unit))
        return x509.Name(name_attrs)
