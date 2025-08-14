from cryptography.hazmat.primitives.serialization import Encoding
from oslo_log import log as logging
from oslo_utils import timeutils
from oslo_utils import uuidutils

from certx.common import exceptions, x509_helper
from certx.common.model import models
from certx.db import api as db_api
from certx.provider import crl_point, crypto, key, x509
from certx import service
from certx.service.certificate_service import CertificateService
from certx.utils import algorithm_utils, filter_utils, generator

logger = logging.getLogger(__name__)


class CertificateServiceImpl(CertificateService):
    dbapi = db_api.get_instance()

    def __init__(self, **kwargs):
        pass

    def create_certificate_authority(self, ca_option) -> models.CertificateAuthority:
        if ca_option is None:
            raise exceptions.InvalidParameterValue('Empty input')

        ca_type = ca_option.get('type')
        if ca_type == models.CaType.ROOT:
            self._valid_root_ca_option(ca_option)
            root_cert, root_key = None, None
        else:
            root_cert, root_key = self._valid_sub_ca_option(ca_option)

        key_algorithm = ca_option.get('key_algorithm')
        signature_algorithm = ca_option.get('signature_algorithm')
        logger.info('Generate %s CA private key...', ca_type.value)
        _key_provider = key.get_provider(key_algorithm)
        ca_key = _key_provider.generate_private_key()

        ca_dn = models.DistinguishedName(**ca_option.get('distinguished_name'))
        ca_validity = models.Validity(**ca_option.get('validity'))

        logger.info('Generate %s CA...', ca_type.value)
        _cert_provider = x509.get_provider(key_algorithm, signature_algorithm)
        ca_cert = _cert_provider.generate_ca_certificate(
            ca_dn, ca_key, ca_validity,
            signature_algorithm=signature_algorithm,
            root_cert=root_cert,
            root_key=root_key,
            path_length=ca_option.get('path_length'))

        key_pass = generator.gen_password()

        ca_id = uuidutils.generate_uuid()
        logger.info('Generate %s CA resource...', ca_type.value)
        resource_service = service.get_resource_service()
        ca_uri = resource_service.save_certificate(
            models.CertificateResourceType.CA,
            ca_cert.public_bytes(Encoding.PEM),
            _key_provider.get_private_bytes(ca_key, password=key_pass),
            certificate_id=ca_id)

        crl_configuration = models.CrlConfiguration(**(ca_option.get('crl_configuration') or {}))

        ca_values = {
            'id': ca_id,
            'type': ca_option.get('type').value,
            'status': models.CaStatus.ISSUE.value,
            'path_length': None if ca_type == models.CaType.ROOT else ca_option.get('path_length'),
            'issuer_id': ca_option.get('issuer_id'),
            'key_algorithm': key_algorithm.value,
            'signature_algorithm': signature_algorithm.value,
            'serial_number': str(ca_cert.serial_number),
            'not_before': ca_validity.not_before,
            'not_after': ca_validity.not_after,
            'common_name': ca_dn.common_name,
            'country': ca_dn.country,
            'state': ca_dn.state,
            'locality': ca_dn.locality,
            'organization': ca_dn.organization,
            'organization_unit': ca_dn.organization_unit,
            'uri': ca_uri,
            'password': crypto.encrypt(key_pass),
            'crl_enabled': crl_configuration.enabled,
            'crl_valid_days': crl_configuration.valid_days,
            'created_at': ca_validity.not_before
        }

        try:
            ca = self.dbapi.create_certificate_authority(ca_values)

            if crl_configuration.enabled:
                crl_point.publish_crl(ca.id, ca.serial_number,
                                      _cert_provider.generate_crl(ca_cert, ca_key, crl_configuration, []))
        except Exception as e:
            logger.error('Save CA failed, delete resource file %s...', ca_uri, e)
            resource_service.delete_certificate(ca_uri)

            if isinstance(e, exceptions.ServiceException):
                raise e
            raise exceptions.ServiceException('Create CA failed')

        return models.CertificateAuthority.from_db(ca)

    def _valid_ca_option(self, ca_option):
        ca_type = ca_option.get('type')
        if ca_type == models.CaType.ROOT:
            self._valid_root_ca_option(ca_option)
            return None, None
        else:
            return self._valid_sub_ca_option(ca_option)

    @staticmethod
    def _valid_root_ca_option(ca_option):
        key_algorithm = ca_option.get('key_algorithm')
        signature_algorithm = ca_option.get('signature_algorithm')

        if not key_algorithm or not signature_algorithm:
            msg = 'key_algorithm and signature_algorithm required'
            logger.error(msg)
            raise exceptions.InvalidParameterValue(msg)

        if not algorithm_utils.validate_key_and_signature_algorithm(key_algorithm, signature_algorithm):
            msg = 'Unmatched key_algorithm {} and signature_algorithm {}'.format(
                key_algorithm.value, signature_algorithm.value)
            logger.error(msg)
            raise exceptions.InvalidParameterValue(msg)

    def _valid_sub_ca_option(self, ca_option):
        issuer_id = ca_option.get('issuer_id')
        if not issuer_id:
            logger.error('issuer_id required when create sub ca')
            raise exceptions.InvalidParameterValue('issuer_id required when create sub ca')

        ca_model = self.get_certificate_authority(issuer_id)

        key_algorithm = ca_option.get('key_algorithm')
        signature_algorithm = ca_option.get('signature_algorithm')

        if not algorithm_utils.validate_key_algorithm(key_algorithm, ca_model.key_algorithm) \
                or not algorithm_utils.validate_signature_algorithm(signature_algorithm, ca_model.signature_algorithm):
            msg = 'ca %(ca)s with key_algorithm %(ca_key_algo)s and signature_algorithm %(ca_sign_algo)s could not ' \
                  'sign certificate with key_algorithm %(cert_key_algo)s and signature_algorithm %(cert_sign_algo)s' % {
                      'ca': ca_model.id,
                      'ca_key_algo': ca_model.key_algorithm.value,
                      'ca_sign_algo': ca_model.signature_algorithm.value,
                      'cert_key_algo': key_algorithm.value,
                      'cert_sign_algo': signature_algorithm.value,
                  }
            logger.error(msg)
            raise exceptions.InvalidParameterValue(msg)

        # Sub CA的path length要求小于父CA
        path_length = ca_option.get('path_length')
        if ca_model.path_length is not None and path_length >= ca_model.path_length:
            err_msg = "The path_length '%(path_len)s' of sub CA should less than issuer's path_length " \
                      "'%(issuer_path_len)s'" % {
                          'path_len': path_length,
                          'issuer_path_len': ca_model.path_length
                      }
            logger.info(err_msg)
            raise exceptions.InvalidParameterValue(err_msg)

        return self._load_cert_and_key(ca_model)

    @staticmethod
    def _load_cert_and_key(cert_model):
        """加载CA/Cert的证书和私钥"""
        _key_provider = key.get_provider(cert_model.key_algorithm)
        _cert_provider = x509.get_provider(cert_model.key_algorithm, cert_model.signature_algorithm)

        # Load CA
        resource_service = service.get_resource_service(cert_model.uri)
        ca_resource = resource_service.load_certificate(cert_model.uri)

        ca_cert = _cert_provider.load_certificate(ca_resource.certificate_data)

        _ca_key_provider = key.get_provider(cert_model.key_algorithm)
        ca_key = _ca_key_provider.load_private_key(ca_resource.private_key_data,
                                                   password=crypto.decrypt(cert_model.password))

        return ca_cert, ca_key

    def list_certificate_authorities(self, query_option=None):
        if query_option is None:
            query_option = {}

        filters = filter_utils.build_filters(query_option,
                                             ['id', 'common_name', 'key_algorithm', 'signature_algorithm', 'issuer_id'])
        return [models.CertificateAuthority.from_db(ca) for ca in
                self.dbapi.get_certificate_authorities(filters=filters,
                                                       limit=query_option.get('limit'),
                                                       marker=query_option.get('marker'),
                                                       sort_key=query_option.get('sort_key'),
                                                       sort_dir=query_option.get('sort_dir'))]

    def get_certificate_authority(self, ca_id) -> models.CertificateAuthority:
        db_ca = self.dbapi.get_certificate_authority(ca_id)
        if db_ca is None:
            logger.error('CA {} not found'.format(ca_id))
            raise exceptions.NotFoundException('CA {} not found'.format(ca_id))
        return models.CertificateAuthority.from_db(db_ca)

    def delete_certificate_authority(self, ca_id):
        ca = self.get_certificate_authority(ca_id)

        sub_cas = self.dbapi.get_certificate_authorities(filters={'issuer_id': ca_id})
        if sub_cas:
            logger.error('CA {} has signed sub CA, could not be deleted'.format(ca_id))
            raise exceptions.CaSignedCertificate('CA {} has signed sub CA, could not be deleted'.format(ca_id))

        db_certs = self.dbapi.get_certificates(filters={'issuer_id': ca_id})
        if db_certs:
            logger.error('CA {} has signed certificate, could not be deleted'.format(ca_id))
            raise exceptions.CaSignedCertificate('CA {} has signed certificate, could not be deleted'.format(ca_id))

        logger.info('Delete CA {}'.format(ca_id))
        self.dbapi.destroy_certificate_authority(ca_id)

        logger.info('Delete CA {} resource with uri {}'.format(ca_id, ca.uri))
        try:
            service.get_resource_service(ca.uri).delete_certificate(ca.uri)
        except exceptions.CertificateResourceNotFound:
            pass

    def export_certificate_authority(self, ca_id) -> models.CertificateContent:
        logger.info('Export CA {}...'.format(ca_id))
        ca = self.get_certificate_authority(ca_id)
        ca_resource = service.get_resource_service(ca.uri).load_certificate(ca.uri)
        certificate_chain = None
        if ca.issuer_id:
            certificate_chain = self._get_certificate_chain(ca.issuer_id)
        return models.CertificateContent(certificate=ca_resource.certificate_data,
                                         certificate_chain=certificate_chain)

    def export_certificate_authority_crl(self, ca_id):
        ca_model = self.get_certificate_authority(ca_id)
        if not ca_model.crl_configuration.enabled:
            msg = 'CA {} does not enable CRL'.format(ca_id)
            logger.error(msg)
            raise exceptions.InvalidParameterValue(msg)

        ca_cert, ca_key = self._load_cert_and_key(ca_model)

        revoked_certificates = self.list_certificates(query_option={
            'issuer_id': ca_id,
            'status': models.CertificateStatus.REVOKE.value
        })

        _cert_provider = x509.get_provider(ca_model.key_algorithm, ca_model.signature_algorithm)
        crl = _cert_provider.generate_crl(ca_cert, ca_key, ca_model.crl_configuration, revoked_certificates)
        return crl.public_bytes(Encoding.PEM)

    def create_certificate(self, cert_option) -> models.Certificate:
        issue_id = cert_option.get('issuer_id')
        ca_model = self.get_certificate_authority(issue_id)

        # 验证算法合法性
        key_algorithm = cert_option.get('key_algorithm') if cert_option.get(
            'key_algorithm') else ca_model.key_algorithm
        signature_algorithm = cert_option.get('signature_algorithm') if cert_option.get(
            'signature_algorithm') else ca_model.signature_algorithm

        if not algorithm_utils.validate_key_and_signature_algorithm(key_algorithm, signature_algorithm):
            msg = 'Unmatched key_algorithm {} and signature_algorithm {}'.format(
                key_algorithm.value, signature_algorithm.value)
            logger.error(msg)
            raise exceptions.InvalidParameterValue(msg)

        if not algorithm_utils.validate_key_algorithm(key_algorithm, ca_model.key_algorithm) \
                or not algorithm_utils.validate_signature_algorithm(signature_algorithm, ca_model.signature_algorithm):
            msg = 'ca %(ca)s with key_algorithm %(ca_key_algo)s and signature_algorithm %(ca_sign_algo)s could not ' \
                  'sign certificate with key_algorithm %(cert_key_algo)s and signature_algorithm %(cert_sign_algo)s' % {
                      'ca': ca_model.id,
                      'ca_key_algo': ca_model.key_algorithm.value,
                      'ca_sign_algo': ca_model.signature_algorithm.value,
                      'cert_key_algo': key_algorithm.value,
                      'cert_sign_algo': signature_algorithm.value,
                  }
            logger.error(msg)
            raise exceptions.InvalidParameterValue(msg)

        key_usage = x509_helper.build_x509_key_usage(cert_option.get('key_usage'))
        extended_key_usage = x509_helper.build_x509_extended_key_usage(cert_option.get('extended_key_usage'))
        subject_alternative_names = cert_option.get('subject_alternative_names')
        subject_alter_name = x509_helper.build_x509_subject_alternative_name(subject_alternative_names)

        _key_provider = key.get_provider(key_algorithm)
        _cert_provider = x509.get_provider(key_algorithm, signature_algorithm)

        logger.info('Loading CA and key...')
        ca_cert, ca_key = self._load_cert_and_key(ca_model)

        # Generate certificate
        logger.info('Generate certificate private key...')
        cert_key = _key_provider.generate_private_key()

        # DN
        cert_dn_option = cert_option.get('distinguished_name')
        cert_dn_country = cert_dn_option.get('country')
        cert_dn_state = cert_dn_option.get('state')
        cert_dn_locality = cert_dn_option.get('locality')
        cert_dn_organization = cert_dn_option.get('organization')
        cert_dn_organization_unit = cert_dn_option.get('organization_unit')
        cert_dn = models.DistinguishedName(
            common_name=cert_dn_option.get('common_name'),
            country=cert_dn_country if cert_dn_country else ca_model.distinguished_name.country,
            state=cert_dn_state if cert_dn_state else ca_model.distinguished_name.state,
            locality=cert_dn_locality if cert_dn_locality else ca_model.distinguished_name.locality,
            organization=cert_dn_organization if cert_dn_organization else ca_model.distinguished_name.organization,
            organization_unit=cert_dn_organization_unit if cert_dn_organization_unit else ca_model.distinguished_name.organization_unit)

        cert_validity = models.Validity(**cert_option.get('validity'))

        # CRL distribution points
        crl_distribution_points = crl_point.get_points(issue_id, ca_model.serial_number)

        logger.info('Generate certificate...')
        cert = _cert_provider.generate_certificate(ca_cert, ca_key, cert_dn, cert_key, cert_validity,
                                                   key_usage=key_usage,
                                                   extended_key_usage=extended_key_usage,
                                                   subject_alternative_name=subject_alter_name,
                                                   subject_alternative_names=subject_alternative_names,
                                                   crl_distribution_points=crl_distribution_points)

        logger.info('Generate certificate resource...')
        resource_service = service.get_resource_service()
        # Save certificate and private key
        key_pass = generator.gen_password()
        cert_id = uuidutils.generate_uuid()
        cert_uri = resource_service.save_certificate(
            models.CertificateResourceType.CERTIFICATE,
            cert.public_bytes(Encoding.PEM),
            _key_provider.get_private_bytes(cert_key, password=key_pass),
            certificate_id=cert_id)

        cert_values = {
            'id': cert_id,
            'status': models.CaStatus.ISSUE.value,
            'issuer_id': ca_model.id,
            'key_algorithm': key_algorithm.value,
            'signature_algorithm': signature_algorithm.value,
            'serial_number': str(ca_cert.serial_number),
            'not_before': cert_validity.not_before,
            'not_after': cert_validity.not_after,
            'common_name': cert_dn.common_name,
            'country': cert_dn.country,
            'state': cert_dn.state,
            'locality': cert_dn.locality,
            'organization': cert_dn.organization,
            'organization_unit': cert_dn.organization_unit,
            'uri': cert_uri,
            'password': crypto.encrypt(key_pass),
            'created_at': cert_validity.not_before
        }

        try:
            db_cert = self.dbapi.create_certificate(cert_values)
        except Exception as e:
            logger.error('Save certificate failed, delete resource file %s...', cert_uri, e)
            resource_service.delete_certificate(cert_uri)
            raise exceptions.ServiceException('Create certificate failed')

        return models.Certificate.from_db(db_cert)

    def list_certificates(self, query_option=None):
        if query_option is None:
            query_option = {}

        filters = filter_utils.build_filters(
            query_option,
            ['id', 'issuer_id', 'common_name', 'key_algorithm', 'signature_algorithm', 'status'])
        return [models.Certificate.from_db(ca) for ca in
                self.dbapi.get_certificates(filters=filters,
                                            limit=query_option.get('limit'),
                                            marker=query_option.get('marker'),
                                            sort_key=query_option.get('sort_key'),
                                            sort_dir=query_option.get('sort_dir'))]

    def get_certificate(self, cert_id) -> models.Certificate:
        db_cert = self.dbapi.get_certificate(cert_id)
        if db_cert is None:
            logger.error('Certificate %s not found', cert_id)
            raise exceptions.NotFoundException('certificate {} not found'.format(cert_id))
        return models.Certificate.from_db(db_cert)

    def delete_certificate(self, cert_id):
        cert = self.get_certificate(cert_id)

        logger.info('Delete certificate {}'.format(cert_id))
        self.dbapi.destroy_certificate(cert_id)

        logger.info('Delete certificate {} resource with uri {}'.format(cert_id, cert.uri))
        try:
            service.get_resource_service(cert.uri).delete_certificate(cert.uri)
        except exceptions.CertificateResourceNotFound:
            pass

    def export_certificate(self, cert_id, export_option) -> models.CertificateContent:
        logger.info('Export certificate {}...'.format(cert_id))
        cert = self.get_certificate(cert_id)

        cert_resource = service.get_resource_service(cert.uri).load_certificate(cert.uri)

        _cert_key_provider = key.get_provider(cert.key_algorithm)
        cert_key = _cert_key_provider.load_private_key(cert_resource.private_key_data,
                                                       password=crypto.decrypt(cert.password))

        user_pass = export_option.get('password')

        return models.CertificateContent(
            certificate=cert_resource.certificate_data,
            private_key=_cert_key_provider.get_private_bytes(cert_key, password=user_pass),
            certificate_chain=self._get_certificate_chain(cert.issuer_id))

    def _get_certificate_chain(self, ca_id):
        chain = []

        ca_model = self.get_certificate_authority(ca_id)

        ca_resource = service.get_resource_service(ca_model.uri).load_certificate(ca_model.uri)
        chain.append(ca_resource.certificate_data)

        if ca_model.issuer_id:
            chain.extend(self._get_certificate_chain(ca_model.issuer_id))

        chain.reverse()
        return chain

    def revoke_certificate(self, cert_id, revoke_option):
        logger.info('Revoke certificate {}...'.format(cert_id))
        cert = self.get_certificate(cert_id)
        if cert.status != models.CertificateStatus.ISSUE:
            logger.error('Cannot perform revoke certificate with status %s', cert.status.value)
            raise exceptions.CertificateStatusInvalid(action='revoke certificate', status=cert.status.value)

        ca_model = self.get_certificate_authority(cert.issuer_id)
        if not ca_model.crl_configuration.enabled:
            logger.error('The CA %s does not enable CRL', cert.issuer_id)
            raise exceptions.CaNotEnableCrl(ca=cert.issuer_id)

        self.dbapi.update_certificate(cert_id, {
            'status': models.CertificateStatus.REVOKE.value,
            'revoked_at': timeutils.utcnow(),
            'revoked_reason': revoke_option.get('reason').value
        })
