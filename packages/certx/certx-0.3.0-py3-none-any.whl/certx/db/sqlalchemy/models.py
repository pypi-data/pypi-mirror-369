from os import path

from oslo_db import options
from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import Column, Index, Text
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, DateTime, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base

from certx.conf import CONF

_DEFAULT_SQL_CONNECTION = 'sqlite:///' + path.join(CONF.state_path, 'certx.sqlite')
options.set_defaults(CONF, connection=_DEFAULT_SQL_CONNECTION)


class SoftDeleteMixin(object):
    deleted_at = Column(DateTime)
    deleted = Column(String(36), default=None)

    def soft_delete(self, session):
        self.deleted = self.id
        self.deleted_at = timeutils.utcnow()
        self.save(session=session)


class CertXBase(models.TimestampMixin, models.ModelBase):
    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d


Base = declarative_base(cls=CertXBase)


class CertificateAuthorityModel(Base, SoftDeleteMixin):
    __tablename__ = 'certificate_authorities'

    id = Column(String(36), primary_key=True)
    type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    path_length = Column(Integer, nullable=False, default=7)
    issuer_id = Column(String(36), nullable=True)
    key_algorithm = Column(String(32), nullable=False)
    signature_algorithm = Column(String(32), nullable=False)
    serial_number = Column(String(64), nullable=False)
    not_before = Column(DateTime, nullable=False)
    not_after = Column(DateTime, nullable=False)
    common_name = Column(String(192), nullable=False)
    country = Column(String(2), nullable=False)
    state = Column(String(384), nullable=True)
    locality = Column(String(384), nullable=True)
    organization = Column(String(192), nullable=True)
    organization_unit = Column(String(192), nullable=True)
    uri = Column(Text)
    password = Column(Text)
    crl_enabled = Column(Boolean, default=False)
    crl_valid_days = Column(Integer, default=None)
    created_at = Column(DateTime, nullable=True, default=timeutils.utcnow())
    updated_at = Column(DateTime, nullable=True, default=None)


class CertificateModel(Base, SoftDeleteMixin):
    __tablename__ = 'certificates'

    id = Column(String(36), primary_key=True)
    status = Column(String(32), nullable=False)
    issuer_id = Column(String(36), ForeignKey('certificate_authorities.id'), nullable=True)
    key_algorithm = Column(String(32), nullable=False)
    signature_algorithm = Column(String(32), nullable=False)
    serial_number = Column(String(64), nullable=False)
    not_before = Column(DateTime, nullable=False)
    not_after = Column(DateTime, nullable=False)
    common_name = Column(String(192), nullable=False)
    country = Column(String(2), nullable=False)
    state = Column(String(384), nullable=True)
    locality = Column(String(384), nullable=True)
    organization = Column(String(192), nullable=True)
    organization_unit = Column(String(192), nullable=True)
    uri = Column(Text)
    password = Column(Text)
    revoked_at = Column(DateTime, nullable=True, default=None)
    revoked_reason = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=True, default=timeutils.utcnow())
    updated_at = Column(DateTime, nullable=True, default=None)


class RevokedCertificateModel(Base, SoftDeleteMixin):
    __tablename__ = 'revoked_certificates'
    __table_args__ = (
        Index('idx_revoked_cert_issuer_id_certificate_id', 'issuer_id', 'certificate_id', unique=True),
    )

    id = Column(String(36), primary_key=True)
    issuer_id = Column(String(36), ForeignKey('certificate_authorities.id'), nullable=False, index=True)
    certificate_id = Column(String(36), nullable=False)
    serial_number = Column(String(64), nullable=False)
    revoked_at = Column(DateTime, nullable=False)
    revoked_reason = Column(String(64), nullable=True)
    not_before = Column(DateTime, nullable=False)
    not_after = Column(DateTime, nullable=False)


class CertificateResourceModel(Base, SoftDeleteMixin):
    __tablename__ = 'certificate_resources'

    id = Column(String(36), primary_key=True)
    certificate_type = Column(String(32), nullable=False)  # CA, CERTIFICATE
    certificate_data = Column(LargeBinary)
    private_key_data = Column(LargeBinary)
