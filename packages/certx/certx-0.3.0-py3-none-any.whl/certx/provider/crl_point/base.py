import abc

from cryptography.x509 import DistributionPoint


class CrlDistributionPointProvider(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_points(self, issuer_id: str, serial_number: str) -> DistributionPoint | None:
        """获取CRL的分发点
        :param issuer_id 签发者ID，即CA证书ID
        :param serial_number 签发者序列号，即CA证书序列号
        :return CRL分发点
        """

    @abc.abstractmethod
    def publish_crl(self, issuer_id: str, serial_number: str, crl_data: bytes) -> DistributionPoint | None:
        """发布吊销的证书
        :param issuer_id 签发者ID，即CA证书ID
        :param serial_number 签发者序列号，即CA证书序列号
        :param crl_data 证书吊销列表数据
        :return CRL分发点
        """
