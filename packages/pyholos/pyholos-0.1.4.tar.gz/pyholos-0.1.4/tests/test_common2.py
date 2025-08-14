import unittest
from pathlib import Path

from geojson import load

from pyholos import common2


class TestGetSlcPolygonProperties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path_geojson = Path(__file__).parent / (
            'sources/soil_data/example_soil_landscapes_of_canada_v3r2/soil_landscapes_of_canada_v3r2.geojson')
        with path_geojson.open(mode='r') as f:
            cls.geojson_data = load(f)
        common2.PATH_SLC_GEOJSON_FILE = path_geojson
        cls.expected_outputs = {
            'OBJECTID': 9139,
            'AREA': 0.06119253235,
            'PERIMETER': 2.0076591166,
            'POLY_ID': 851003,
            'ECO_ID': 851,
            'Shape_Length': 2.0076591152263235,
            'Shape_Area': 0.06119253234576638}

    def test_identify_slc_polygon_id_returns_expected_result(self):
        self.assertEqual(
            self.expected_outputs,
            common2.get_slc_polygon_properties(
                latitude=49.98,
                longitude=-98.04,
                geojson_data=self.geojson_data))

        self.assertEqual(
            self.expected_outputs,
            common2.get_slc_polygon_properties(
                latitude="49.98",
                longitude="-98.04",
                geojson_data=self.geojson_data))

    def test_identify_slc_polygon_id_fails_with_missing_location_data(self):
        self.assertRaises(
            TypeError,
            common2.get_slc_polygon_properties,
            dict(longitude=-98.04, geojson_data=self.geojson_data))


class TestGetDominantComponentProperties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cmp_data = common2.read_slc_csv(
            path_file=Path(__file__).parent / (
                'sources/soil_data/example_soil_landscapes_of_canada_v3r2/ca_all_slc_v3r2_cmp.csv'))

    def test_get_dominant_component_properties_returns_component_with_highest_polygon_occupation_percentage(self):
        self.assertEqual(
            'MBLSL~~~~~A',
            common2.get_dominant_component_properties(
                slc_components_table=self.cmp_data,
                id_polygon=851003)['SOIL_ID'])

        cmp_data = self.cmp_data.copy(deep=True)
        cmp_data['PERCENT_'] = 0
        cmp_data.loc[5, 'PERCENT_'] = 100
        self.assertEqual(
            'MBDGS~~~~~A',
            common2.get_dominant_component_properties(
                slc_components_table=cmp_data,
                id_polygon=851003)['SOIL_ID'])

    def test_get_dominant_component_properties_returns_first_component_for_equally_occupied_polygon(self):
        cmp_data = self.cmp_data.copy(deep=True)
        cmp_data['PERCENT_'] = 0
        self.assertEqual(
            'MBLSL~~~~~A',
            common2.get_dominant_component_properties(
                slc_components_table=cmp_data,
                id_polygon=851003)['SOIL_ID'])

        pass


class TestSoilLayerTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slt_data = common2.read_slc_csv(
            path_file=Path(__file__).parent / (
                'sources/soil_data/example_soil_landscapes_of_canada_v3r2/ca_all_slc_v3r2_slt.csv'))

    def test_get_soil_layer_table_sorts_data_according_to_depth(self):
        df = common2.get_soil_layer_table(
            id_soil='MBLSL~~~~~A',
            slc_soil_layer_table=self.slt_data)

        self.assertEqual(
            df['UDEPTH'].to_list(),
            sorted(df['UDEPTH']))

    def test_get_soil_layer_table_includes_only_data_with_provided_soil_id(self):
        id_soil = 'MBLSL~~~~~A'
        df = common2.get_soil_layer_table(
            id_soil=id_soil,
            slc_soil_layer_table=self.slt_data)

        self.assertEqual(
            len(df['SOIL_ID'].unique()),
            1)

        self.assertEqual(
            df['SOIL_ID'].unique()[0],
            id_soil)

    def test_get_first_non_litter_layer_ignores_litter_layers(self):
        self.assertEqual(
            20,
            common2.get_first_non_litter_layer(soil_layer_table=self.slt_data)['LDEPTH'])

        df = self.slt_data.copy(deep=True)
        df.loc[0, 'UDEPTH'] = -1

        self.assertEqual(
            60,
            common2.get_first_non_litter_layer(soil_layer_table=df)['LDEPTH'])


class TestGetSoilNameTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        snt_data = common2.read_slc_csv(
            path_file=Path(__file__).parent / (
                'sources/soil_data/example_soil_landscapes_of_canada_v3r2/ca_all_slc_v3r2_snt.csv'))
        cls.soil_name_table = common2.get_soil_name_table(
            soil_name_table=snt_data,
            id_soil='MBLSL~~~~~A')

    def test_get_soil_name_table_returns_one_data_row(self):
        self.assertTrue(all([not isinstance(v, list) == 1 for v in self.soil_name_table.values()]))

    def test_get_soil_name_table_returns_expected_soil_name(self):
        self.assertEqual(
            ['MF', 'R', 'CU'],
            [self.soil_name_table[s] for s in (['PMTEX1', 'G_GROUP3', 'S_GROUP3'])])


if __name__ == '__main__':
    unittest.main()
