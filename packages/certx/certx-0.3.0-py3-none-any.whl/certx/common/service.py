import sys

from oslo_log import log

from certx.conf import CONF
from certx.common import config

logger = log.getLogger(__name__)


def prepare_command(argv=None):
    argv = sys.argv if argv is None else argv
    log.register_options(CONF)
    config.parse_args(argv[1:])
    log.setup(CONF, 'certx')
