import unittest

from pyholos.defaults import Defaults


class MyDefaults(unittest.TestCase):
    def test_values(self):
        self.assertEqual(
            Defaults.EmissionFactorForLeachingAndRunoff,
            0.011)
        self.assertEqual(
            Defaults.PercentageOfProductReturnedToSoilForPerennials,
            35)
        self.assertEqual(
            Defaults.PercentageOfRootsReturnedToSoilForPerennials,
            100)
        self.assertEqual(
            Defaults.PercentageOfProductReturnedToSoilForAnnuals,
            2)
        self.assertEqual(
            Defaults.PercentageOfRootsReturnedToSoilForAnnuals,
            100)
        self.assertEqual(
            Defaults.PercentageOfStrawReturnedToSoilForAnnuals,
            100)
        self.assertEqual(
            Defaults.PercentageOfProductReturnedToSoilForRootCrops,
            0)
        self.assertEqual(
            Defaults.PercentageOfStrawReturnedToSoilForRootCrops,
            100)


if __name__ == '__main__':
    unittest.main()
