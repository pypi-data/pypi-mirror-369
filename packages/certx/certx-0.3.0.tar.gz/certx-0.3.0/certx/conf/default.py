import os

from oslo_config import cfg

from certx.conf.types import EncryptedStrOpt

path_opts = [
    cfg.StrOpt('pybasedir',
               default=os.path.abspath(os.path.join(os.path.dirname(__file__), '../')),
               sample_default='/usr/lib/python/site-packages/certx/certx',
               help='Directory where the certx python module is installed.'),
    cfg.StrOpt('state_path',
               default='$pybasedir',
               help="Top-level directory for maintaining certx's state."),
]

service_opts = [
    cfg.StrOpt('host', help='the server ip', default='0.0.0.0'),
    cfg.IntOpt('port', help='Port for server', default='9999'),
    cfg.BoolOpt('enable_https', help='Enable th server run on HTTPS mode', default=False),
    cfg.StrOpt('server_cert', help='Certificate file for HTTPS'),
    cfg.StrOpt('server_key', help='Certificate key for HTTPS'),
    EncryptedStrOpt('key_pass', secret=True, help='Certificate private key password'),
    cfg.BoolOpt('threaded', help='Make server run in multi-thread', default=True),
]

crypto_opts = [
    cfg.StrOpt('encryption_provider', help='Crypter provider type, default is "none", means using plaintext data',
               default='none'),
    cfg.StrOpt('encryption_secret_key', help='Data encryption secret key')
]

gm_opts = [
    cfg.StrOpt('gm_key_provider', help='GM key provider alias or class path', default='openssl'),
    cfg.StrOpt('gm_cert_provider', help='GM cert provider alias or class path', default='openssl'),
    cfg.StrOpt('openssl_tempdir', help='The base temporary path for save CA and certificate files',
               default='$pybasedir/openssl'),
    cfg.BoolOpt('enable_delete_openssl_temp_file', help='Delete key/cert file after created', default=True)
]

certificate_repository_opts = [
    cfg.StrOpt('cert_repo_type', help='Default Certificate repository type', default='db', choices=('db', 'file')),
    cfg.StrOpt('file_cert_repo_path', help='The base path for save CA and certificate files',
               default='$pybasedir/cert-repo')
]

crl_opts = [
    cfg.BoolOpt('enable_crl_distribution_points', help='Enable CRL distribution points', default=False),
    cfg.StrOpt('crl_endpoint',
               help='CRL distribution point endpoint, should configure when CRL provided by server self'),
    cfg.ListOpt('crl_provider', help='CRL distribution service provider alias or class path', default=['default'])
]


def list_opts():
    _default_opt_lists = [
        service_opts,
        path_opts,
        crypto_opts,
        gm_opts,
        certificate_repository_opts,
        crl_opts
    ]

    full_opt_list = []
    for options in _default_opt_lists:
        full_opt_list.extend(options)
    return full_opt_list


def register_opts(conf):
    conf.register_opts(service_opts)
    conf.register_opts(path_opts)
    conf.register_opts(crypto_opts)
    conf.register_opts(gm_opts)
    conf.register_opts(certificate_repository_opts)
    conf.register_opts(crl_opts)
