from abc import ABC, abstractmethod
from typing import List

from certx.common.model import models


class CertificateService(ABC):
    @abstractmethod
    def create_certificate_authority(self, ca_option) -> models.CertificateAuthority: ...

    @abstractmethod
    def list_certificate_authorities(self, query_option=None) -> List[models.CertificateAuthority]: ...

    @abstractmethod
    def get_certificate_authority(self, ca_id) -> models.CertificateAuthority: ...

    @abstractmethod
    def delete_certificate_authority(self, ca_id): ...

    @abstractmethod
    def export_certificate_authority(self, ca_id) -> models.CertificateContent: ...

    @abstractmethod
    def export_certificate_authority_crl(self, ca_id): ...

    @abstractmethod
    def create_certificate(self, cert_option) -> models.Certificate: ...

    @abstractmethod
    def list_certificates(self, query_option=None) -> List[models.Certificate]:
        """查询证书列表
        :param query_option:
        :return:
        """

    @abstractmethod
    def get_certificate(self, cert_id) -> models.Certificate: ...

    @abstractmethod
    def delete_certificate(self, cert_id) -> models.Certificate: ...

    @abstractmethod
    def export_certificate(self, cert_id, export_option) -> models.CertificateContent:
        """导出证书
        :param cert_id 证书ID
        :param export_option 导出参数
        :param export_option.type 导出证书的格式
        :param export_option.password 证书密钥密码，如不提供，则返回未加密的证书
        :return 证书内容，包括 证书、证书链、密钥文件 等
        """

    @abstractmethod
    def revoke_certificate(self, cert_id, revoke_option): ...
