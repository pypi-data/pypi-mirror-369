from certx import app
from certx.tests.unit.db import base


class ApiResourceBaseTestCase(base.DbTestCase):
    def setUp(self):
        super(ApiResourceBaseTestCase, self).setUp()
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        self.app = app.test_client()
