import abc

from oslo_config import cfg
from oslo_db import api as db_api

_BACKEND_MAPPING = {'sqlalchemy': 'certx.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


class Connection(abc.ABC):
    @abc.abstractmethod
    def get_certificate_authority(self, ca_id): ...

    @abc.abstractmethod
    def get_certificate_authorities(self, filters=None, limit=None, marker=None, sort_key=None, sort_dir=None): ...

    @abc.abstractmethod
    def create_certificate_authority(self, ca): ...

    @abc.abstractmethod
    def delete_certificate_authority(self, ca_id): ...

    @abc.abstractmethod
    def destroy_certificate_authority(self, ca_id): ...

    @abc.abstractmethod
    def get_certificate(self, ca_id): ...

    @abc.abstractmethod
    def get_certificates(self, filters=None, limit=None, marker=None, sort_key=None, sort_dir=None): ...

    @abc.abstractmethod
    def create_certificate(self, cert_id): ...

    @abc.abstractmethod
    def update_certificate(self, cert_id, values): ...

    @abc.abstractmethod
    def delete_certificate(self, ca_id): ...

    @abc.abstractmethod
    def destroy_certificate(self, cert_id): ...

    @abc.abstractmethod
    def get_certificate_resource(self, id, cert_id): ...

    @abc.abstractmethod
    def create_certificate_resource(self, content): ...

    @abc.abstractmethod
    def destroy_certificate_resource(self, cc_id, cert_id=None): ...


def get_instance() -> Connection:
    """Return a DB API instance."""
    return IMPL
