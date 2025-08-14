from flask import Response
from flask_restx import Resource

from certx import rest_api
from certx import service

ca_ns = rest_api.namespace('', description='CRL')


@ca_ns.route('/crl/<string:ca_id>')
class CertificateAuthorityCrlResource(Resource):
    certificate_service = service.get_certificate_service()

    def get(self, ca_id):
        crl = self.certificate_service.export_certificate_authority_crl(ca_id)
        return Response(crl,
                        mimetype='application/octet-stream',
                        headers={'Content-Disposition': 'attachment;filename=crl.pem'})
