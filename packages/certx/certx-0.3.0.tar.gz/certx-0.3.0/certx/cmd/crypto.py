import sys

from oslo_config import cfg

from certx.conf import CONF
from certx.provider.crypto.password import FernetPasswordEncoder


def gen_secret_key():
    print(FernetPasswordEncoder.gen_secret_key())


def encrypt():
    row_data = CONF.command.row_data
    key = CONF.command.key
    if key is None:
        print('-key required')
        sys.exit(1)

    print(FernetPasswordEncoder(key).encrypt(row_data))


def add_command_parsers(subparsers):
    parser = subparsers.add_parser(
        'gen_secret_key',
        help="Generate secret key.")
    parser.set_defaults(func=gen_secret_key)

    parser = subparsers.add_parser(
        'encrypt',
        help="Encrypt row data.")
    parser.add_argument("row_data", type=str, help="Row data")
    parser.add_argument("-key", type=str, help="Secret Key", dest="key")
    parser.set_defaults(func=encrypt)


def main():
    command_opt = cfg.SubCommandOpt('command',
                                    title='Command',
                                    help='Available commands',
                                    handler=add_command_parsers)
    CONF.register_cli_opt(command_opt)

    CONF(sys.argv[1:], __name__)
    CONF.command.func()
