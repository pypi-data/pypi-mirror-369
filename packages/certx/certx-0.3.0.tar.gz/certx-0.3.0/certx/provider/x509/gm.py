from typing import List

from oslo_config import cfg
from oslo_log import log as logging

from certx.common import exceptions
from certx.common.model.models import CrlConfiguration, DistinguishedName, SignatureAlgorithm, KeyAlgorithm, Validity
from certx.provider.x509.base import CertificateProvider
from certx.utils import importutils

logger = logging.getLogger(__name__)

x509_provider = cfg.CONF.gm_cert_provider

gm_cert_provider_conf = {
    'default': 'certx.provider.x509.gm.DefaultCertificateProvider',
    'openssl': 'certx.provider.x509.openssl.OpensslGMCertificateProvider'
}


class GMCertificateProvider(CertificateProvider):
    def __init__(self, key_algorithm: KeyAlgorithm, signature_algorithm: SignatureAlgorithm, **kwargs):
        super().__init__(key_algorithm, signature_algorithm, **kwargs)

        self.delegate = importutils.import_class(x509_provider, gm_cert_provider_conf,
                                                 key_algorithm, signature_algorithm,
                                                 **kwargs)

    def generate_ca_certificate(self, dn: DistinguishedName, private_key, validity: Validity,
                                signature_algorithm: SignatureAlgorithm = None,
                                root_cert=None, root_key=None, path_length=0):
        return self.delegate.generate_ca_certificate(dn, private_key, validity,
                                                     signature_algorithm=signature_algorithm,
                                                     root_cert=root_cert,
                                                     root_key=root_key,
                                                     path_length=path_length)

    def generate_certificate(self, ca_cert, ca_key, cert_dn: DistinguishedName, cert_private_key, validity: Validity,
                             signature_algorithm: SignatureAlgorithm = None, key_usage=None,
                             extended_key_usage=None,
                             subject_alternative_name=None,
                             **kwargs):
        return self.delegate.generate_certificate(ca_cert, ca_key, cert_dn, cert_private_key, validity,
                                                  signature_algorithm,
                                                  key_usage=key_usage,
                                                  extended_key_usage=extended_key_usage,
                                                  subject_alternative_name=None,
                                                  **kwargs)

    def load_certificate(self, certificate_data):
        return self.delegate.load_certificate(certificate_data)

    def generate_crl(self, *args, **kwargs):
        return self.delegate.generate_crl(*args, **kwargs)


class DefaultGmCertificateProvider(CertificateProvider):
    def generate_ca_certificate(self, dn: DistinguishedName, private_key, validity: Validity,
                                signature_algorithm: SignatureAlgorithm = None,
                                root_cert=None, root_key=None, path_length=0):
        raise exceptions.NotImplementException("GM algorithm not supported")

    def generate_certificate(self, ca_cert, ca_key, cert_dn: DistinguishedName, cert_private_key, validity: Validity,
                             signature_algorithm: SignatureAlgorithm = None,
                             key_usage=None,
                             extended_key_usage=None,
                             subject_alternative_name=None,
                             **kwargs):
        raise exceptions.NotImplementException("GM algorithm not supported")

    def load_certificate(self, certificate_data):
        raise exceptions.NotImplementException("GM algorithm not supported")

    def generate_crl(self, ca_id, ca_key, crl_configuration: CrlConfiguration, certs: List):
        raise exceptions.NotImplementException("GM algorithm not supported")
