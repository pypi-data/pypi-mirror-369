import unittest

from certx.tests.unit.utils.mock_data import FakeClassA, FakeClassB
from certx.utils import importutils


class TestFilterUtil(unittest.TestCase):
    def test_import_class_when_class_path_is_none(self):
        self.assertRaises(ValueError, importutils.import_class, None)

    def test_import_class_when_class_path_not_in_class_map(self):
        self.assertRaises(ValueError, importutils.import_class, 'fakeA', class_map={})

    def test_import_class_when_class_path_in_class_map(self):
        obj = importutils.import_class('fakeA', class_map={'fakeA': 'certx.tests.unit.utils.mock_data.FakeClassA'})
        self.assertIsInstance(obj, FakeClassA)

    def test_import_class_direct_with_class_path(self):
        obj = importutils.import_class('certx.tests.unit.utils.mock_data.FakeClassA')
        self.assertIsInstance(obj, FakeClassA)

    def test_import_class_when_parameter_not_provide(self):
        self.assertRaises(TypeError, importutils.import_class, 'certx.tests.unit.utils.mock_data.FakeClassB')

    def test_import_class_when_with_init_parameter(self):
        obj = importutils.import_class('certx.tests.unit.utils.mock_data.FakeClassB', 1, y=2)
        self.assertIsInstance(obj, FakeClassB)
        self.assertEqual(1, obj.x)
        self.assertEqual(2, obj.y)
