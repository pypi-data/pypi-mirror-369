from certx import conf

_opts = [
    ('DEFAULT', conf.default.list_opts()),
    ('database', conf.database.database_opts),
]


def list_opts():
    return _opts
