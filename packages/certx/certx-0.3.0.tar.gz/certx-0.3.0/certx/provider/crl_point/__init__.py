from typing import List

from cryptography.x509 import CRLDistributionPoints, DistributionPoint
from oslo_config import cfg

from certx.utils import importutils

CONF = cfg.CONF

_PROVIDERS = []

crl_provider_conf = {
    'default': 'certx.provider.crl_point.default.DefaultCrlDistributionPointProvider'
}


def _get_providers():
    global _PROVIDERS
    if not _PROVIDERS:
        crl_providers = CONF.crl_provider or []

        if crl_providers:
            for crl_provider in crl_providers:
                _PROVIDERS.append(importutils.import_class(crl_provider, class_map=crl_provider_conf))

    return _PROVIDERS


def _to_x509_crl_distribution_points(points: List[DistributionPoint]) -> CRLDistributionPoints | None:
    if not points:
        return None

    valid_points = filter(None, points)
    if not valid_points:
        return None

    return CRLDistributionPoints(valid_points)


def get_points(issuer_id: str, serial_number: str):
    points = []
    for provider in _get_providers():
        points.append(provider.get_points(issuer_id, serial_number))

    return _to_x509_crl_distribution_points(points)


def publish_crl(issuer_id: str, serial_number: str, crl_data: bytes):
    points = []
    for provider in _get_providers():
        points.append(provider.publish_crl(issuer_id, serial_number, crl_data))

    return _to_x509_crl_distribution_points(points)
