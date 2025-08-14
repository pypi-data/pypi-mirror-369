import unittest

from certx.provider.crl_point.default import DefaultCrlDistributionPointProvider


class TestDefaultCrlDistributionPointProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = DefaultCrlDistributionPointProvider()

    def test_get_points_when_crl_not_enable(self):
        self.assertIsNone(self.provider.get_points('id', 'sn'))
