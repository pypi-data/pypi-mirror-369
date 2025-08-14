from flask import request
from flask_restx import Resource
from marshmallow.exceptions import ValidationError
from oslo_log import log as logging

from certx.api.model import models as api_model
from certx.common import exceptions
from certx import rest_api
from certx import service
from certx.utils import algorithm_utils

logger = logging.getLogger(__name__)

ca_ns = rest_api.namespace('', description='CA')


@ca_ns.route('/v1/certificate-authorities')
class CertificateAuthoritiesResource(Resource):
    certificate_service = service.get_certificate_service()

    @ca_ns.doc('ListCertificateAuthorities')
    def get(self):
        query_option = api_model.ListCertificateAuthorityParameter().load(request.args.to_dict())
        logger.debug('Query parameter: %s', query_option)
        cas = self.certificate_service.list_certificate_authorities(query_option)
        return {'certificate_authorities': api_model.CertificateAuthority().dump(cas, many=True)}

    @ca_ns.doc('CreateCertificateAuthority')
    def post(self):
        try:
            req_body = api_model.CreateCertificateAuthorityRequestBody().load(rest_api.payload)
            ca_dict = req_body['certificate_authority']
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        if not algorithm_utils.validate_key_and_signature_algorithm(ca_dict.get('key_algorithm'),
                                                                    ca_dict.get('signature_algorithm')):
            msg = 'Unmatched key_algorithm {} and signature_algorithm {}'.format(
                ca_dict.get('key_algorithm').value, ca_dict.get('signature_algorithm').value)
            logger.error(msg)
            raise exceptions.InvalidParameterValue(msg)

        crl_configuration = ca_dict.get('crl_configuration')
        if crl_configuration and crl_configuration.get('enabled') and crl_configuration.get('valid_days') is None:
            msg = 'Invalid CRL configuration due to valid_days required when CRL enabled'
            logger.error(msg)
            raise exceptions.InvalidParameterValue(msg)

        logger.info('Create private CA with params: {}'.format(ca_dict))
        ca = self.certificate_service.create_certificate_authority(ca_option=ca_dict)
        return {'certificate_authority': api_model.CertificateAuthority().dump(ca)}


@ca_ns.route('/v1/certificate-authorities/<string:ca_id>')
class CertificateAuthorityResource(Resource):
    certificate_service = service.get_certificate_service()

    @ca_ns.doc('ShowCertificateAuthority')
    def get(self, ca_id):
        ca = self.certificate_service.get_certificate_authority(ca_id)
        return {'certificate_authority': api_model.CertificateAuthority().dump(ca)}

    @ca_ns.doc('DeleteCertificateAuthority')
    def delete(self, ca_id):
        logger.info('Delete private CA %s', ca_id)
        self.certificate_service.delete_certificate_authority(ca_id)
        return None, 204


@ca_ns.route('/v1/certificate-authorities/<string:ca_id>/export')
class CertificateAuthorityExportResource(Resource):
    certificate_service = service.get_certificate_service()

    @ca_ns.doc('ExportCertificateAuthority')
    def post(self, ca_id):
        content = self.certificate_service.export_certificate_authority(ca_id)
        return api_model.CertificateAuthorityContent().dump(content)
