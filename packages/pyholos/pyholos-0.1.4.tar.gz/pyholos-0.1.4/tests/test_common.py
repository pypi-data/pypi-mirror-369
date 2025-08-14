import unittest

from pyholos import common
from pyholos.common2 import CanadianProvince


class TestGetRegion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.west_region_provinces = (
            CanadianProvince.Alberta,
            CanadianProvince.BritishColumbia,
            CanadianProvince.Manitoba,
            CanadianProvince.Saskatchewan,
            CanadianProvince.NorthwestTerritories,
            CanadianProvince.Nunavut)

    def test_west_region(self):
        for province in self.west_region_provinces:
            self.assertEqual(
                common.Region.WesternCanada,
                common.get_region(province=province))

    def test_east_region(self):
        for province in CanadianProvince:
            if province not in self.west_region_provinces:
                self.assertEqual(
                    common.Region.EasternCanada,
                    common.get_region(province=province))


class TestVerifyIsPrairieProvince(unittest.TestCase):
    def test_prairie_provinces(self):
        for province in [
            CanadianProvince.Alberta,
            CanadianProvince.Saskatchewan,
            CanadianProvince.Manitoba
        ]:
            self.assertTrue(common.verify_is_prairie_province(province=province))

    def test_non_prairie_provinces(self):
        for province in CanadianProvince:
            if province not in [
                CanadianProvince.Alberta,
                CanadianProvince.Saskatchewan,
                CanadianProvince.Manitoba
            ]:
                self.assertFalse(common.verify_is_prairie_province(province=province))


class TestGetClimateZone(unittest.TestCase):
    def test_high_temperature_high_ratio_precipitation_to_evapotranspiration(self):
        self.assertEqual(
            common.ClimateZones.WarmTemperateMoist,
            common.get_climate_zone(
                mean_annual_temperature=20,
                mean_annual_precipitation=1000,
                mean_annual_potential_evapotranspiration=700))

    def test_high_temperature_low_ratio_precipitation_to_evapotranspiration(self):
        self.assertEqual(
            common.ClimateZones.WarmTemperateDry,
            common.get_climate_zone(
                mean_annual_temperature=20,
                mean_annual_precipitation=700,
                mean_annual_potential_evapotranspiration=1000))

    def test_medium_temperature_high_ratio_precipitation_to_evapotranspiration(self):
        self.assertEqual(
            common.ClimateZones.CoolTemperateMoist,
            common.get_climate_zone(
                mean_annual_temperature=5,
                mean_annual_precipitation=1000,
                mean_annual_potential_evapotranspiration=700))

    def test_medium_temperature_low_ratio_precipitation_to_evapotranspiration(self):
        self.assertEqual(
            common.ClimateZones.CoolTemperateDry,
            common.get_climate_zone(
                mean_annual_temperature=5,
                mean_annual_precipitation=700,
                mean_annual_potential_evapotranspiration=1000))

    def test_low_temperature_high_ratio_precipitation_to_evapotranspiration(self):
        self.assertEqual(
            common.ClimateZones.WarmTemperateMoist,
            common.get_climate_zone(
                mean_annual_temperature=-5,
                mean_annual_precipitation=1000,
                mean_annual_potential_evapotranspiration=700))

    def test_low_temperature_low_ratio_precipitation_to_evapotranspiration(self):
        self.assertEqual(
            common.ClimateZones.WarmTemperateDry,
            common.get_climate_zone(
                mean_annual_temperature=-5,
                mean_annual_precipitation=700,
                mean_annual_potential_evapotranspiration=1000))


if __name__ == '__main__':
    unittest.main()
