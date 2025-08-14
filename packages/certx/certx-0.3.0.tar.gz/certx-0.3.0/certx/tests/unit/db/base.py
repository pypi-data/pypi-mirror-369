from oslo_config import cfg

from certx.db import api as db_api
from certx.db import migration
from certx.tests.unit import base
from certx.tests.unit.db import utils as db_utils

CONF = cfg.CONF


class DbTestCase(base.TestCase):
    def setUp(self):
        super(DbTestCase, self).setUp()

        migration.create_schema()
        self.dbapi = db_api.get_instance()

    def tearDown(self):
        super(DbTestCase, self).tearDown()
        db_utils.destroy_all_cert()
        db_utils.destroy_all_ca()
