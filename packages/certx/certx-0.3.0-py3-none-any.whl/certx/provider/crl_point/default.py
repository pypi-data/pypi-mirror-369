from urllib.parse import urljoin

from cryptography.x509 import DistributionPoint, UniformResourceIdentifier
from oslo_config import cfg

from certx.common import exceptions
from certx.provider.crl_point.base import CrlDistributionPointProvider

enable_crl_point = cfg.CONF.enable_crl_distribution_points
crl_point_endpoint = cfg.CONF.crl_endpoint


def is_enabled():
    return enable_crl_point


class DefaultCrlDistributionPointProvider(CrlDistributionPointProvider):
    """使用服务自身承载证书吊销能力"""

    def get_points(self, issuer_id: str, serial_number: str) -> DistributionPoint | None:
        if not is_enabled():
            return None

        if not issuer_id:
            raise exceptions.InvalidParameterValue('issuer_id required')

        # 如果未配置endpoint，则不返回points
        if not crl_point_endpoint:
            return None

        return DistributionPoint(
            full_name=[UniformResourceIdentifier(urljoin(crl_point_endpoint, '/crl/{}'.format(issuer_id)))],
            relative_name=None,
            reasons=None,
            crl_issuer=None)

    def publish_crl(self, issuer_id: str, serial_number: str, crl_data: bytes) -> DistributionPoint:
        return self.get_points(issuer_id, serial_number)
