import sys

from oslo_config import cfg

from certx.conf import CONF
from certx.common import service
from certx.db import migration


class DBCommand(object):
    def create_schema(self):
        migration.create_schema()


def add_command_parsers(subparsers):
    command_object = DBCommand()

    parser = subparsers.add_parser(
        'create_schema',
        help="Create the database schema.")
    parser.set_defaults(func=command_object.create_schema)


def main():
    command_opt = cfg.SubCommandOpt('command',
                                    title='Command',
                                    help='Available commands',
                                    handler=add_command_parsers)

    CONF.register_cli_opt(command_opt)

    service.prepare_command(sys.argv)
    CONF.command.func()
