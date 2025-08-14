from certx.conf.types import EncryptedStrOpt

database_opts = [
    EncryptedStrOpt('password', help='Database password. Used for encrypting database password'),
]


def register_opts(conf):
    conf.register_opts(database_opts, group='database')
