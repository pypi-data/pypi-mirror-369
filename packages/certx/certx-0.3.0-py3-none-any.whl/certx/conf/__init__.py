from oslo_config import cfg

from certx.conf import database
from certx.conf import default

CONF = cfg.CONF

default.register_opts(CONF)
database.register_opts(CONF)
