import threading

from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import utils as db_utils
from oslo_log import log as logging
from oslo_utils import timeutils
from oslo_utils import uuidutils
import sqlalchemy as sa
from sqlalchemy.orm.exc import NoResultFound

from certx.common import exceptions
from certx.db import api
from certx.db.sqlalchemy import models

logger = logging.getLogger(__name__)

_CONTEXT = threading.local()


def _session_for_read():
    return enginefacade.reader.using(_CONTEXT)


def _session_for_write():
    return enginefacade.writer.using(_CONTEXT)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """
    with _session_for_read() as session:
        query = session.query(model, *args)
        return query


def _base_query(model):
    return sa.select(model)


def _paginate_query(model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None):
    if query is None:
        query = sa.select(model)

    sort_keys = ['id']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    try:
        query = db_utils.paginate_query(query, model, limit, sort_keys,
                                        marker=marker, sort_dir=sort_dir)
    except db_exc.InvalidSortKey:
        raise exceptions.InvalidParameterValue(
            'The sort_key value "%(key)s" is an invalid field for sorting' % {'key': sort_key})

    with _session_for_read() as session:
        res = session.execute(query).fetchall()
        if len(res) == 0:
            return []
        ref = [r[0] for r in res]
    return ref


class Connection(api.Connection):
    _CA_QUERY_FIELDS = {'id', 'common_name', 'key_algorithm', 'signature_algorithm', 'issuer_id'}
    _CERT_QUERY_FIELDS = {'id', 'common_name', 'key_algorithm', 'signature_algorithm', 'issuer_id', 'status'}
    _REVOKED_CERT_QUERY_FIELDS = {'issuer_id', 'certificate_id'}

    @staticmethod
    def _validate_filters(filters, enabled_items):
        if filters is None:
            filters = dict()

        unsupported_filters = set(filters).difference(enabled_items)
        if unsupported_filters:
            msg = 'SqlAlchemy API does not support filtering by %s' % ', '.join(unsupported_filters)
            raise ValueError(msg)
        return filters

    def get_certificate_authorities(self, filters=None, limit=None, marker=None, sort_key=None, sort_dir=None):
        marker_obj = self.get_certificate_authority(marker) if marker else None
        query = _base_query(models.CertificateAuthorityModel)
        query = self._add_certificate_authorities_filters(query, filters)
        return _paginate_query(models.CertificateAuthorityModel, limit, marker_obj,
                               sort_key or 'created_at', sort_dir or 'desc', query)

    def _add_certificate_authorities_filters(self, query, filters):
        filters = self._validate_filters(filters, self._CA_QUERY_FIELDS)

        for field in self._CA_QUERY_FIELDS:
            if field in filters:
                query = query.filter_by(**{field: filters[field]})
        return query

    def get_certificate_authority(self, ca_id):
        try:
            with _session_for_read() as session:
                query = session.query(models.CertificateAuthorityModel).filter_by(id=ca_id)
                return query.one()
        except NoResultFound:
            raise exceptions.CaNotFound(ca=ca_id)

    def create_certificate_authority(self, values):
        if 'id' not in values:
            values['id'] = uuidutils.generate_uuid()

        ca = models.CertificateAuthorityModel()
        ca.update(values)
        with _session_for_write() as session:
            session.add(ca)
            session.flush()
        return ca

    def delete_certificate_authority(self, ca_id):
        with _session_for_write() as session:
            query = session.query(models.CertificateAuthorityModel).filter_by(id=ca_id)
            result = query.soft_delete()
            if result:
                raise exceptions.CaNotFound(ca=ca_id)

    def destroy_certificate_authority(self, ca_id):
        with _session_for_write() as session:
            query = session.query(models.CertificateAuthorityModel).filter_by(id=ca_id)
            count = query.delete()
            if count == 0:
                raise exceptions.CaNotFound(ca=ca_id)

    def get_certificate(self, cert_id):
        try:
            with _session_for_read() as session:
                query = session.query(models.CertificateModel).filter_by(id=cert_id)
                return query.one()
        except NoResultFound:
            raise exceptions.CertificateNotFound(cert=cert_id)

    def get_certificates(self, filters=None, limit=None, marker=None, sort_key=None, sort_dir=None):
        marker_obj = self.get_certificate(marker) if marker else None
        query = _base_query(models.CertificateModel)
        query = self._add_certificates_filters(query, filters)
        return _paginate_query(models.CertificateModel, limit, marker_obj,
                               sort_key or 'created_at', sort_dir or 'desc', query)

    def _add_certificates_filters(self, query, filters):
        filters = self._validate_filters(filters, self._CERT_QUERY_FIELDS)

        for field in self._CERT_QUERY_FIELDS:
            if field in filters:
                query = query.filter_by(**{field: filters[field]})
        return query

    def create_certificate(self, values):
        if 'id' not in values:
            values['id'] = uuidutils.generate_uuid()

        cert = models.CertificateModel()
        cert.update(values)
        with _session_for_write() as session:
            session.add(cert)
            session.flush()
        return cert

    def update_certificate(self, cert_id, values):
        if 'id' in values:
            msg = "Cannot overwrite ID for an existing certificate."
            raise exceptions.InvalidParameterValue(err=msg)

        with _session_for_write() as session:
            query = session.query(models.CertificateModel).filter_by(id=cert_id)

            try:
                ref = query.with_for_update().one()
            except NoResultFound:
                raise exceptions.CertificateNotFound(cert=cert_id)

            values['updated_at'] = timeutils.utcnow()
            ref.update(values)

        self.get_certificate(cert_id)

    def delete_certificate(self, cert_id):
        with _session_for_write() as session:
            query = session.query(models.CertificateModel).filter_by(id=cert_id)
            result = query.soft_delete()
            if result:
                raise exceptions.CertificateNotFound(cert=cert_id)

    def destroy_certificate(self, cert_id):
        with _session_for_write() as session:
            query = session.query(models.CertificateModel).filter_by(id=cert_id)
            count = query.delete()
            if count == 0:
                raise exceptions.CertificateNotFound(cert=cert_id)

    def get_certificate_resource(self, cc_id, cert_id=None):
        try:
            with _session_for_read() as session:
                query = session.query(models.CertificateResourceModel).filter_by(id=cc_id)
                return query.one()
        except NoResultFound:
            logger.error('Certificate %(cert)s resource %(res)s not found.' % {'cert': cert_id or '', 'res': cc_id})
            raise exceptions.CertificateResourceNotFound(cert=cert_id or '')

    def create_certificate_resource(self, values):
        if 'id' not in values:
            values['id'] = uuidutils.generate_uuid()

        res = models.CertificateResourceModel()
        res.update(values)
        with _session_for_write() as session:
            session.add(res)
            session.flush()
        return res

    def destroy_certificate_resource(self, cc_id, cert_id=None):
        with _session_for_write() as session:
            query = session.query(models.CertificateResourceModel).filter_by(id=cc_id)
            count = query.delete()
            if count == 0:
                logger.warning(
                    'Certificate %(cert)s resource %(res)s not found.' % {'cert': cert_id or '', 'res': cc_id})
