import unittest
from json import load
from pathlib import Path

from pyholos import soil


class TestSetSoilTextureAccordingToHolos(unittest.TestCase):
    def test_very_coarse(self):
        self.assertEqual(soil.set_soil_texture_according_to_holos('VC'), 'Coarse')

    def test_coarse(self):
        self.assertEqual(soil.set_soil_texture_according_to_holos('C'), 'Coarse')

    def test_moderately_coarse(self):
        self.assertEqual(soil.set_soil_texture_according_to_holos('MC'), 'Coarse')

    def test_medium(self):
        self.assertEqual(soil.set_soil_texture_according_to_holos('M'), 'Medium')

    def test_medium_skeletal(self):
        self.assertEqual(soil.set_soil_texture_according_to_holos('MS'), 'Medium')

    def test_moderately_fine(self):
        self.assertEqual(soil.set_soil_texture_according_to_holos('MF'), 'Fine')

    def test_fine(self):
        self.assertEqual(soil.set_soil_texture_according_to_holos('F'), 'Fine')

    def test_very_fine(self):
        self.assertEqual(soil.set_soil_texture_according_to_holos('VF'), 'Fine')

    def test_fine_skeletal(self):
        self.assertEqual(soil.set_soil_texture_according_to_holos('FS'), 'Fine')

    def test_unknown(self):
        for s in ['CS', 'FR', 'SM', 'SU', 'FI', 'ME', 'HU', 'UD']:
            self.assertEqual(soil.set_soil_texture_according_to_holos(s), 'Medium')


class TestConvertSoilTextureName(unittest.TestCase):
    def test_fine_soil(self):
        self.assertEqual(
            soil.SoilTexture.Fine,
            soil.convert_soil_texture_name(name='fine'))

    def test_coarse_soil(self):
        self.assertEqual(
            soil.SoilTexture.Coarse,
            soil.convert_soil_texture_name(name='coarse'))

    def test_medium_soil(self):
        self.assertEqual(
            soil.SoilTexture.Medium,
            soil.convert_soil_texture_name(name='medium'))

    def test_unknown_soil(self):
        self.assertEqual(
            soil.SoilTexture.Unknown,
            soil.convert_soil_texture_name(name='any_other_soil_type'))


class TestSetSoilProperties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (Path(__file__).parent / 'sources/soil_data_example.json').open(mode='r') as f:
            cls.example_data = load(f)['data']

    def test_set_soil_properties_returns_expected_results(self):
        for example_data in self.example_data:
            example_inputs = example_data['inputs']
            self.assertEqual(
                soil.set_soil_properties(
                    latitude=example_inputs['Latitude'],
                    longitude=example_inputs['Longitude']),
                example_data['outputs'])


class TestSoilFunctionalCategory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.soil_functional_categories = []

    def test_get_simplified_soil_category_brown(self):
        for soil_functional_category in [
            soil.SoilFunctionalCategory.Brown,
            soil.SoilFunctionalCategory.DarkBrown,
            soil.SoilFunctionalCategory.BrownChernozem,
            soil.SoilFunctionalCategory.DarkBrownChernozem
        ]:
            self.assertEqual(
                soil.SoilFunctionalCategory.Brown,
                soil_functional_category.get_simplified_soil_category())
            self.soil_functional_categories.append(soil_functional_category)

    def test_get_simplified_soil_category_black(self):
        for soil_functional_category in [
            soil.SoilFunctionalCategory.Black,
            soil.SoilFunctionalCategory.BlackGrayChernozem
        ]:
            self.assertEqual(
                soil.SoilFunctionalCategory.Black,
                soil_functional_category.get_simplified_soil_category())
            self.soil_functional_categories.append(soil_functional_category)

    def test_z_get_simplified_soil_category_default(self):
        for soil_functional_category in soil.SoilFunctionalCategory:
            if soil_functional_category not in self.soil_functional_categories:
                self.assertEqual(
                    soil_functional_category,
                    soil_functional_category.get_simplified_soil_category())


class TestConvertSoilFunctionalCategoryName(unittest.TestCase):
    def test_brown_chernozem(self):
        self.assertEqual(
            soil.SoilFunctionalCategory.BrownChernozem,
            soil.convert_soil_functional_category_name("brownchernozem"))

    def test_dark_brown_chernozem(self):
        self.assertEqual(
            soil.SoilFunctionalCategory.DarkBrownChernozem,
            soil.convert_soil_functional_category_name("darkbrownchernozem"))

    def test_dark_gray_chernozem(self):
        self.assertEqual(
            soil.SoilFunctionalCategory.BlackGrayChernozem,
            soil.convert_soil_functional_category_name("blackgraychernozem"))

    def test_all(self):
        self.assertEqual(
            soil.SoilFunctionalCategory.All,
            soil.convert_soil_functional_category_name("all"))

    def test_brown(self):
        self.assertEqual(
            soil.SoilFunctionalCategory.Brown,
            soil.convert_soil_functional_category_name("brown"))

    def test_dark_brown(self):
        self.assertEqual(
            soil.SoilFunctionalCategory.DarkBrown,
            soil.convert_soil_functional_category_name("darkbrown"))

    def test_black(self):
        self.assertEqual(
            soil.SoilFunctionalCategory.Black,
            soil.convert_soil_functional_category_name("black"))

    def test_organic(self):
        self.assertEqual(
            soil.SoilFunctionalCategory.Organic,
            soil.convert_soil_functional_category_name("organic"))

    def test_eastern_canada(self):
        for s in ("easterncanada", "east"):
            self.assertEqual(
                soil.SoilFunctionalCategory.EasternCanada,
                soil.convert_soil_functional_category_name(s))

    def test_default(self):
        for s in ("some", "random", "province", "name"):
            self.assertEqual(
                soil.SoilFunctionalCategory.NotApplicable,
                soil.convert_soil_functional_category_name(s))


if __name__ == '__main__':
    unittest.main()
