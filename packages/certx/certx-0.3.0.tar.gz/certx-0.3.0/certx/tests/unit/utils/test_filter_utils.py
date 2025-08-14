from enum import Enum
import unittest

from certx.utils import filter_utils


class MockVal(Enum):
    KEY = 'VAL'


class TestFilterUtil(unittest.TestCase):
    def test_build_filters_should_return_empty_without_none_keys(self):
        self.assertEqual({}, filter_utils.build_filters({}, []))

    def test_build_filters_should_return_empty_for_keys_not_in_dict_values(self):
        self.assertEqual({}, filter_utils.build_filters({}, ['key1']))
        self.assertEqual({}, filter_utils.build_filters({'key2': '2'}, ['key1']))

    def test_build_filters_should_return_none_value_for_dict_value_is_none_and_not_ignore_empty(self):
        self.assertEqual({'key1': None},
                         filter_utils.build_filters({'key1': None, 'key2': 2}, ['key1'], ignore_empty=False))

    def test_build_filters_should_return_none_value_for_dict_value_is_none_and_ignore_empty(self):
        self.assertEqual({}, filter_utils.build_filters({'key1': None, 'key2': 2}, ['key1'], ignore_empty=True))

    def test_build_filters_should_return_val_when_dict_value_enum(self):
        self.assertEqual({'key1': 'VAL'},
                         filter_utils.build_filters({'key1': MockVal.KEY, 'key2': 2}, ['key1']))

    def test_build_filters_should_return_self_when_dict_value_is_not_enum(self):
        self.assertEqual({'key1': 'str'},
                         filter_utils.build_filters({'key1': 'str', 'key2': 2}, ['key1']))
        self.assertEqual({'key2': 2},
                         filter_utils.build_filters({'key1': 'str', 'key2': 2}, ['key2']))
