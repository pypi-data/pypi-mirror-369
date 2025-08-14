import flask
import traceback

from flask_restx import Api
from marshmallow.exceptions import ValidationError
from oslo_log import log as logging
from werkzeug import exceptions as w_exceptions

from certx.common import exceptions

logger = logging.getLogger(__name__)


def import_routes():
    import certx.api.certificate_api
    import certx.api.certificate_authority_api
    import certx.api.crl_api


def make_json_app(import_name, **kwargs):
    app = flask.Flask(import_name, **kwargs)

    @app.errorhandler(Exception)
    def make_json_error(ex):
        logger.error("Unexpected error happened: %s", traceback.format_exc())
        response = flask.jsonify({"message": str(ex)})
        response.status_code = w_exceptions.InternalServerError.code
        if isinstance(ex, w_exceptions.HTTPException):
            response.status_code = ex.code
        elif isinstance(ex, ValidationError):
            response.status_code = 400
        elif isinstance(ex, exceptions.ServiceException):
            response.status_code = ex.kwargs.get('code') or ex.code
        content_type = 'application/json; charset=utf-8'
        response.headers['Content-Type'] = content_type
        return response

    for code in w_exceptions.default_exceptions:
        app.register_error_handler(code, make_json_error)

    return app


app = make_json_app(__name__)
rest_api = Api(app)

import_routes()
