from oslo_log import log as logging
from six.moves import http_client

logger = logging.getLogger(__name__)


class ServiceException(Exception):
    """Default Service exception"""
    _msg_fmt = "An unknown exception occurred."
    code = http_client.INTERNAL_SERVER_ERROR

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code ' not in kwargs:
            self.kwargs['code'] = self.code

        if not message:
            try:
                message = self._msg_fmt % kwargs
            except Exception as ignore:
                prs = ', '.join('%s: %s' % pair for pair in kwargs.items())
                logger.exception('Exception in string format operation (arguments %s)', prs)
                message = self._msg_fmt

        super(ServiceException, self).__init__(message)


class NotImplementException(ServiceException):
    """The function not provided"""
    _msg_fmt = "Not implemented"


class BadRequest(ServiceException):
    code = http_client.BAD_REQUEST


class InvalidParameterValue(BadRequest):
    """Request data is invalid"""
    _msg_fmt = "Request data is invalid."
    code = http_client.BAD_REQUEST


class CaSignedCertificate(BadRequest):
    """CA已签发证书"""
    _msg_fmt = "The CA %(ca)s has signed certificate."
    code = http_client.BAD_REQUEST


class UnsupportedAlgorithm(BadRequest):
    """不（或尚未）支持的算法"""
    _msg_fmt = "Unsupported %(type)s algorithm %(name)s."
    code = http_client.BAD_REQUEST


class CertificateStatusInvalid(BadRequest):
    """证书状态不合法，不能执行操作"""
    _msg_fmt = "Cannot perform %(action)s with status %(status)s"


class CaNotEnableCrl(BadRequest):
    """CA未开启CRL功能"""
    _msg_fmt = "The CA %(ca)s does not enable CRL"


class NotFoundException(ServiceException):
    """The resource could not be found"""
    _msg_fmt = "Resource could not be found."
    code = http_client.NOT_FOUND


class CaNotFound(NotFoundException):
    _msg_fmt = "CA %(ca)s could not be found."
    code = http_client.NOT_FOUND


class CertificateNotFound(NotFoundException):
    _msg_fmt = "Certificate %(cert)s could not be found."


class CertificateResourceNotFound(NotFoundException):
    _msg_fmt = "Certificate Resource %(cert)s could not be found."
