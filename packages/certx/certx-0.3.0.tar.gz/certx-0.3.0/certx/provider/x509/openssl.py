import os
import platform
import shutil
from typing import List

from cryptography import x509
from OpenSSL import crypto
from oslo_config import cfg
from oslo_log import log as logging

from certx.common import exceptions
from certx.common.model.models import (
    Certificate,
    CrlConfiguration,
    DistinguishedName,
    KeyAlgorithm,
    SignatureAlgorithm,
    Validity
)
from certx.provider.key.base import KeyProvider
from certx.provider.x509.base import CertificateProvider
from certx.utils import executils
from certx.utils import generator

logger = logging.getLogger(__name__)

openssl_tempdir = os.path.normpath(cfg.CONF.openssl_tempdir)
enable_delete_temp_file = cfg.CONF.enable_delete_openssl_temp_file

_SIG_ALG_MAP = {
    SignatureAlgorithm.SM3_256: 'SM3'
}


def detect_openssl():
    if platform.system() == 'Windows':
        logger.error('Generate certificate by OpenSSL on Windows not supported')
        raise exceptions.ServiceException('Unsupported')

    if shutil.which('openssl') is None:
        logger.error('Cmd openssl not found, please check OpenSSL installed manually')
        raise exceptions.ServiceException('Unsupported')

    try:
        result = executils.execute('openssl version')
    except Exception as ignore:
        logger.error('Detect OpenSSL version failed')
        result = None

    if not result or not result.stdout or not result.stdout.lower().startswith('openssl 3.'):
        logger.error('OpenSSL version not matched. Required OpenSSL 3.x')
        logger.error('Detect OpenSSL version result: {}'.format(result))
        raise exceptions.ServiceException()


def make_openssl_directory():
    """预生成OpenSSL文件目录，使用OpenSSl命令生成的文件将暂时保存在该目录下"""
    if os.path.exists(openssl_tempdir):
        return

    os.makedirs(openssl_tempdir)


def generate_openssl_file_path(file_name=None):
    """在openssl文件目录下生成一个文件名称"""
    if not file_name:
        file_name = generator.gen_uuid()
    return os.path.join(openssl_tempdir, file_name)


def delete_openssl_file(file_path):
    if not file_path:
        return

    if not os.path.exists(file_path):
        return

    os.remove(file_path)


class OpensslPrivateKey(object):
    def __init__(self, private_key, file_path=None):
        self.private_key = private_key
        self.file_path = file_path


class OpensslX509Certificate(object):
    def __init__(self, cert: crypto.X509, cert_file_path=None, csr_file_path=None, key_file_path=None,
                 ca_cert_file_path=None, ca_key_file_path=None):
        """证书对象
        :param cert: OpenSSL X509证书对象
        :param cert_file_path: OpenSSL生成的证书的路径
        :param csr_file_path: OpenSSL生成的证书请求文件的路径
        :param key_file_path: OpenSSL生成的私钥文件的路径
        :param ca_cert_file_path: 证书所属的CA证书的路径
        :param ca_key_file_path: 证书所属的CA证书的私钥文件的路径
        """
        self.cert = cert
        self.cert_file_path = cert_file_path
        self.csr_file_path = csr_file_path
        self.key_file_path = key_file_path

        self.ca_cert_file_path = ca_cert_file_path
        self.ca_key_file_path = ca_key_file_path

    @property
    def serial_number(self):
        return self.cert.get_serial_number()

    def public_bytes(self, encoding):
        return crypto.dump_certificate(crypto.FILETYPE_PEM, self.cert)


class OpensslExtensionParamBuilder(object):
    def __init__(self, basic_constraints: x509.BasicConstraints = None, key_usage: x509.KeyUsage = None,
                 extended_key_usage: x509.ExtendedKeyUsage = None,
                 subject_alternative_names: list = None):
        self.basic_constraints = basic_constraints
        self.key_usage = key_usage
        self.extended_key_usage = extended_key_usage
        self.subject_alternative_names = subject_alternative_names

    def build(self, extension_name='v3_ca'):
        ext_params = [
            'echo "[{}]"'.format(extension_name),
            'echo "subjectKeyIdentifier=hash"',
            'echo "authorityKeyIdentifier=keyid"'
        ]
        if self.basic_constraints:
            ext_params.append('echo "{}"'.format(self._build_basic_constraints()))

        if self.key_usage:
            ext_params.append('echo "{}"'.format(self._build_key_usage()))

        if self.extended_key_usage:
            ext_params.append('echo "{}"'.format(self._build_extended_key_usage()))

        subject_alt_name_params = []
        if self.subject_alternative_names:
            ext_params.append('echo "subjectAltName=@alt_names"')
            subject_alt_name_params.append('echo [alt_names]')
            subject_alt_name_params.extend(self._build_subject_alternative_names())

        if subject_alt_name_params:
            ext_params.extend(subject_alt_name_params)

        return ';'.join(ext_params)

    def _build_basic_constraints(self):
        basic_constraints_attrs = ['CA:{}'.format(str(self.basic_constraints.ca).lower())]
        if self.basic_constraints.path_length is not None:
            basic_constraints_attrs.append('pathlen:{}'.format(self.basic_constraints.path_length))
        return 'basicConstraints=' + ','.join(basic_constraints_attrs)

    def _build_key_usage(self):
        key_usage_attr_map = {
            'digital_signature': 'digitalSignature',
            'content_commitment': 'contentCommitment',
            'key_encipherment': 'keyEncipherment',
            'data_encipherment': 'dataEncipherment',
            'key_agreement': 'keyAgreement',
            'key_cert_sign': 'keyCertSign',
            'crl_sign': 'cRLSign',
            'encipher_only': 'encipherOnly',
            'decipher_only': 'decipherOnly',
        }

        disabled_keys = []
        if not self.key_usage.key_agreement:
            disabled_keys = ['encipher_only', 'decipher_only']

        return 'keyUsage=' + ','.join(
            list(filter(None, [value if key not in disabled_keys and getattr(self.key_usage, key) else None
                               for key, value in key_usage_attr_map.items()])))

    def _build_extended_key_usage(self):
        return 'extendedKeyUsage=' + ','.join(set(list(usage._name for usage in self.extended_key_usage._usages)))

    def _build_subject_alternative_names(self):
        existed_cache = {}  # key: name_type, value: items of name_value. {name_type: [name_value]}
        items = []
        for item in self.subject_alternative_names:
            name_type = item.get('type')
            name_value = item.get('value')
            existed = existed_cache.get(name_type) or []
            if name_value in existed:
                continue

            index = len(existed) + 1
            items.append('echo "{type}.{index}={value}"'.format(type=name_type.value, index=index, value=name_value))

            existed.append(name_value)
            existed_cache[name_type] = existed
        return items


class OpensslGmKeyProvider(KeyProvider):
    def __init__(self, key_algorithm: KeyAlgorithm, **kwargs):
        super().__init__(key_algorithm, **kwargs)

        detect_openssl()
        make_openssl_directory()

    def generate_private_key(self):
        """生成SM2密钥"""
        file_name = '{}.key'.format(generator.gen_uuid())
        pri_key_file = generate_openssl_file_path(file_name)
        cmd = 'openssl ecparam -genkey -name SM2 -out {pri_key_file}'.format(pri_key_file=pri_key_file)
        logger.info('Generate private key: {}'.format(cmd))
        executils.execute(cmd)

        with open(pri_key_file, 'rb') as pk_file:
            return OpensslPrivateKey(crypto.load_privatekey(crypto.FILETYPE_PEM, pk_file.read()),
                                     file_path=pri_key_file)

    def get_private_bytes(self, private_key, password: str = None):
        passphrase = password.encode('utf-8') if password is not None else None
        return crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key.private_key, passphrase=passphrase)

    def load_private_key(self, private_key_bytes, password: str = None):
        p_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_bytes, passphrase=password.encode('utf-8'))
        return OpensslPrivateKey(p_key)


class OpensslGMCertificateProvider(CertificateProvider):
    def __init__(self, key_algorithm: KeyAlgorithm, signature_algorithm: SignatureAlgorithm, **kwargs):
        super().__init__(key_algorithm, signature_algorithm, **kwargs)

        detect_openssl()
        make_openssl_directory()

    def generate_ca_certificate(self, dn: DistinguishedName, private_key, validity: Validity,
                                signature_algorithm: SignatureAlgorithm = None,
                                root_cert=None, root_key=None, path_length=0):
        """生成CA证书，执行成功后，将删除本地生成私钥、证书请求、证书文件。
           注：暂不支持生成子CA
        """
        if (root_cert and not root_key) or (not root_cert and root_key):
            logger.error('Create CA failed due to root_cert and root_key should bath not emtpy or empty')
            raise exceptions.ServiceException('Create CA failed')

        if signature_algorithm is None:
            signature_algorithm = self.signature_algorithm

        # default key usage for CA: digitalSignature,keyCertSign,cRLSign
        key_usage = x509.KeyUsage(True, False, False, False, False, True, True, False, False)

        path_length = None if not root_cert else path_length
        ext_param = OpensslExtensionParamBuilder(
            basic_constraints=x509.BasicConstraints(ca=True, path_length=path_length),
            key_usage=key_usage)

        if root_cert:
            return self._generate_certificate(
                root_cert, root_key, dn, private_key, validity, signature_algorithm, ext_param)
        else:
            return self._generate_ca_certificate(dn, private_key, validity, ext_param)

    def _generate_ca_certificate(self, dn, private_key, validity, extension_param: OpensslExtensionParamBuilder):
        csr_file_path = self._generate_csr(private_key, dn)

        ca_cert_file = os.path.join(openssl_tempdir, '{}.crt'.format(generator.gen_uuid()))
        ca_cmd = 'openssl x509 -req -SM3 -days {days} -in {csr_file} ' \
                 '-signkey {ca_key_file} -out {ca_cert_file} -extensions v3_ca ' \
                 '-extfile <({ext_file})'.format(days=validity.days,
                                                 csr_file=csr_file_path,
                                                 ca_key_file=private_key.file_path,
                                                 ca_cert_file=ca_cert_file,
                                                 ext_file=extension_param.build('v3_ca'))
        logger.info('Generate ca cert: {}'.format(ca_cmd))
        ca_cmd_result = executils.execute(ca_cmd)
        if ca_cmd_result.returncode != 0:
            logger.error('Generate CA cert failed due to: {}'.format(ca_cmd_result.stderr))
            raise exceptions.ServiceException("Generate CA cert failed")

        with open(ca_cert_file, 'rb') as ca_fp:
            ca_cert = OpensslX509Certificate(crypto.load_certificate(crypto.FILETYPE_PEM, ca_fp.read()),
                                             cert_file_path=ca_cert_file)

        ca_cert.key_file_path = private_key.file_path
        ca_cert.csr_file_path = csr_file_path
        self._delete_tmp_file(ca_cert)

        return ca_cert

    def generate_certificate(self, ca_cert, ca_key, cert_dn: DistinguishedName, cert_private_key, validity: Validity,
                             signature_algorithm: SignatureAlgorithm = None,
                             key_usage=None,
                             extended_key_usage=None,
                             subject_alternative_names=None,
                             **kwargs):
        if signature_algorithm is None:
            signature_algorithm = self.signature_algorithm

        ext_param = OpensslExtensionParamBuilder(key_usage=key_usage,
                                                 extended_key_usage=extended_key_usage,
                                                 subject_alternative_names=subject_alternative_names)

        return self._generate_certificate(ca_cert, ca_key, cert_dn, cert_private_key, validity, signature_algorithm,
                                          ext_param)

    def _generate_csr(self, private_key, dn: DistinguishedName):
        csr_file_path = generate_openssl_file_path('{}.csr'.format(generator.gen_uuid()))

        csr_cmd = 'openssl req -new -key {ca_key_file} -out {csr_file} -subj "{subject}"'.format(
            ca_key_file=private_key.file_path,
            csr_file=csr_file_path,
            subject=self._build_subject(dn))

        logger.info('generate csr: {}'.format(csr_cmd))
        csr_cmd_result = executils.execute(csr_cmd)
        if csr_cmd_result.returncode != 0:
            logger.error('Generate csr failed due to: {}'.format(csr_cmd_result.stderr))
            raise exceptions.ServiceException("Generate cert failed")

        return csr_file_path

    def _generate_certificate(self, ca_cert, ca_key, cert_dn: DistinguishedName, cert_private_key, validity: Validity,
                              signature_algorithm: SignatureAlgorithm,
                              extension_param: OpensslExtensionParamBuilder):
        """ 生成证书，包括SubCA
        :param ca_cert: 签发者CA
        :param ca_key: 签发者CA私钥
        :param cert_dn: 证书通用对象
        :param cert_private_key: 证书私钥
        :param validity: 证书有效期
        :param signature_algorithm: 签名算法
        :param extension_param: 证书扩展用途
        :return:
        """
        csr_file_path = self._generate_csr(cert_private_key, cert_dn)

        self._preprocess_private_key(ca_key)
        self._preprocess_certificate(ca_cert)

        cert_file = os.path.join(openssl_tempdir, '{}.crt'.format(generator.gen_uuid()))

        cert_cmd = 'openssl x509 -req -in {csr_file} -CA {ca_cert_file} -CAkey {ca_key_file} -CAcreateserial ' \
                   '-out {cert_file} -days {days} -{signature_alg} -extensions v3_cert ' \
                   '-extfile <({ext_file})'.format(csr_file=csr_file_path,
                                                   ca_cert_file=ca_cert.cert_file_path,
                                                   ca_key_file=ca_key.file_path,
                                                   cert_file=cert_file,
                                                   days=validity.days,
                                                   signature_alg=self._to_sig_alg_impl(signature_algorithm),
                                                   ext_file=extension_param.build('v3_cert'))
        logger.info('Generate certificate: {}'.format(cert_cmd))
        cert_cmd_result = executils.execute(cert_cmd)
        if cert_cmd_result.returncode != 0:
            logger.error('Generate cert failed due to: {}'.format(cert_cmd_result.stderr))
            raise exceptions.ServiceException("Generate cert failed")

        with open(cert_file, 'rb') as ca_fp:
            cert = OpensslX509Certificate(crypto.load_certificate(crypto.FILETYPE_PEM, ca_fp.read()),
                                          cert_file_path=cert_file)

        cert.key_file_path = cert_private_key.file_path
        cert.csr_file_path = csr_file_path
        cert.ca_cert_file_path = ca_cert.cert_file_path
        cert.ca_key_file_path = ca_key.file_path
        self._delete_tmp_file(cert)

        return cert

    def load_certificate(self, certificate_data):
        logger.info('load_pem_x509_certificate: {}'.format(certificate_data))
        return OpensslX509Certificate(crypto.load_certificate(crypto.FILETYPE_PEM, certificate_data))

    def generate_crl(self, ca_cert, ca_key, crl_configuration: CrlConfiguration,
                     certs: List[Certificate]):
        raise exceptions.NotImplementException()

    @staticmethod
    def _to_sig_alg_impl(signature_algorithm: SignatureAlgorithm):
        if signature_algorithm not in _SIG_ALG_MAP:
            logger.error('unsupported signature_algorithm {}'.format(signature_algorithm.value))
            raise exceptions.NotImplementException('unsupported signature_algorithm')
        return _SIG_ALG_MAP[signature_algorithm]

    @staticmethod
    def _preprocess_private_key(pri_key: OpensslPrivateKey):
        logger.info('preprocess private key...')
        if pri_key.file_path is not None:
            return pri_key

        pri_key_file = generate_openssl_file_path('{}.key'.format(generator.gen_uuid()))
        with open(pri_key_file, 'wb') as fp:
            fp.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pri_key.private_key))

        pri_key.file_path = pri_key_file
        return pri_key

    @staticmethod
    def _preprocess_certificate(cert: OpensslX509Certificate):
        """对证书预处理。当证书没有路径不存在时，通过证书内容重写，获取相关参数"""
        logger.info('preprocess certificate...')
        if cert.cert_file_path is not None:
            return cert

        cert_file_path = generate_openssl_file_path('{}.crt'.format(generator.gen_uuid()))
        with open(cert_file_path, 'wb') as fp:
            fp.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert.cert))

        cert.cert_file_path = cert_file_path
        return cert

    @staticmethod
    def _build_subject(dn) -> str:
        dn_attrs = []
        if dn.country:
            dn_attrs.append('/C=' + dn.country)
        if dn.state:
            dn_attrs.append('/ST=' + dn.state)
        if dn.locality:
            dn_attrs.append('/ST=' + dn.locality)
        if dn.organization:
            dn_attrs.append('/O=' + dn.organization)
        if dn.organization_unit:
            dn_attrs.append('/OU=' + dn.organization_unit)
        dn_attrs.append('/CN=' + dn.common_name)
        return ''.join(dn_attrs)

    @staticmethod
    def _delete_tmp_file(cert: OpensslX509Certificate):
        if not cert:
            return

        if not enable_delete_temp_file:
            logger.info('Disabled to delete OpenSSL temporary file, skipping')
            return

        logger.info('Delete OpenSSL temporary file after certificate generated')
        for file_path in (cert.cert_file_path, cert.key_file_path, cert.csr_file_path, cert.ca_cert_file_path,
                          cert.ca_key_file_path):
            delete_openssl_file(file_path)
