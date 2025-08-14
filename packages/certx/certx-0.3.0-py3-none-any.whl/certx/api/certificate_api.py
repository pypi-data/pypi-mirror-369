from flask import request, Response
from flask_restx import Resource
from marshmallow.exceptions import ValidationError
from oslo_log import log as logging

from certx import rest_api
from certx.api.model import models as api_model
from certx import service
from certx.utils import compress_cert_utils

logger = logging.getLogger(__name__)

cert_ns = rest_api.namespace('', description='Certificate')


@cert_ns.route('/v1/certificates')
class CertificateResources(Resource):
    certificate_service = service.get_certificate_service()

    @cert_ns.doc('ListCertificates')
    def get(self):
        query_option = api_model.ListCertificateParameter().load(request.args.to_dict())
        logger.debug('Query parameter: %s', query_option)
        certs = self.certificate_service.list_certificates(query_option)
        return {'certificates': api_model.Certificate().dump(certs, many=True)}

    @cert_ns.doc('CreateCertificate')
    def post(self):
        try:
            req_body = api_model.CreateCertificateRequestBody().load(rest_api.payload)
            cert_dict = req_body['certificate']
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        logger.info('Create private certificate with params: %s', cert_dict)
        cert = self.certificate_service.create_certificate(cert_option=cert_dict)
        return {'certificate': api_model.Certificate().dump(cert)}


@cert_ns.route('/v1/certificates/<string:cert_id>')
class CertificateAuthorityResource(Resource):
    certificate_service = service.get_certificate_service()

    @cert_ns.doc('ShowCertificate')
    def get(self, cert_id):
        cert = self.certificate_service.get_certificate(cert_id)
        return {'certificate': api_model.Certificate().dump(cert)}

    @cert_ns.doc('DeleteCertificate')
    def delete(self, cert_id):
        logger.info('Delete private certificate %s', cert_id)
        self.certificate_service.delete_certificate(cert_id)
        return None, 204


@cert_ns.route('/v1/certificates/<string:cert_id>/export')
class CertificateExportResource(Resource):
    certificate_service = service.get_certificate_service()

    @cert_ns.doc('ExportCertificate')
    def post(self, cert_id):
        try:
            export_option = api_model.ExportCertificateRequestBody().load(rest_api.payload)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        cert_content = self.certificate_service.export_certificate(cert_id, export_option)
        if not export_option.get('is_compressed'):
            return api_model.CertificateContent().dump(cert_content)
        else:
            response = Response(compress_cert_utils.compress_cert(cert_content), mimetype='application/zip')
            response.headers['Content-Disposition'] = f'attachment; filename="{cert_id}.zip"'
            return response


@cert_ns.route('/v1/certificates/<string:cert_id>/revoke')
class CertificateRevokeResource(Resource):
    certificate_service = service.get_certificate_service()

    @cert_ns.doc('RevokeCertificate')
    def post(self, cert_id):
        try:
            revoke_option = api_model.RevokeCertificateRequestBody().load(rest_api.payload)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        self.certificate_service.revoke_certificate(cert_id, revoke_option)
        return None, 204
