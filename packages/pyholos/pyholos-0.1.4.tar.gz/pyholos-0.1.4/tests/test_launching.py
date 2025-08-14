import sys
import unittest
from pathlib import Path
from shutil import rmtree

from pyholos import launching


@unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
class TestLaunching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path_sources = Path(__file__).parent / 'sources/launching_holos'
        cls.path_dir_farms = cls.path_sources / 'farms'
        cls.path_dir_outputs = cls.path_sources / 'outputs'
        cls.name_farm_json = 'farm.json'
        cls.name_dir_farms_json = None
        cls.name_settings = None
        cls.id_slc_polygon = 851003
        cls.timeout_secs = 60
        cls.expected_output_folders = ['farm_from_json']

        cls.clean_up()

    @classmethod
    def tearDownClass(cls):
        cls.clean_up()

    @classmethod
    def remove_empty_files(cls, pth: Path):
        if pth.is_file():
            with pth.open(mode='r') as f:
                is_empty_file = len(f.readlines()) == 1
            if is_empty_file:
                pth.unlink()
            if not any(pth.parent.iterdir()):
                pth.parent.rmdir()
        else:
            for child in pth.iterdir():
                cls.remove_empty_files(pth=child)

    @classmethod
    def clean_up(cls):
        for f in cls.path_dir_farms.iterdir():
            if f.is_dir():
                rmtree(f)
            else:
                if f.name != "farm.json":
                    f.unlink()
        try:
            rmtree(cls.path_dir_outputs)
        except FileNotFoundError:
            pass
        pass

    def setUp(self):
        try:
            self.remove_empty_files(pth=self.path_dir_farms / 'farm_from_json')
        except FileNotFoundError:
            pass
        try:
            rmtree(self.path_dir_farms / 'HolosExampleFarm')
        except FileNotFoundError:
            pass

    def test_create_farm_files_from_json_with_complete_inputs(self):
        path_dir_outputs = self.path_dir_outputs / 'complete_inputs'
        launching.launch_holos(
            path_dir_farms=self.path_dir_farms,
            name_farm_json=self.name_farm_json,
            name_dir_farms_json=self.name_dir_farms_json,
            name_settings=self.name_settings,
            path_dir_outputs=path_dir_outputs,
            id_slc_polygon=self.id_slc_polygon)

        outputs = [v.name for v in self.path_dir_farms.iterdir() if v.is_dir()]
        self.assertEqual(outputs, self.expected_output_folders)
        for f in ('farm_from_json_Results', 'TotalResultsForAllFarms'):
            self.assertTrue((path_dir_outputs / 'Outputs' / f).is_dir())

    def test_run_on_existing_farm_data(self):
        launching.launch_holos(
            path_dir_farms=self.path_dir_farms,
            name_farm_json=None,
            name_dir_farms_json=None,
            name_settings=None,
            path_dir_outputs=None,
            id_slc_polygon=None)

        outputs = [v.name for v in self.path_dir_farms.iterdir() if v.is_dir()]
        self.assertIn('Outputs', outputs)
        outputs.pop(outputs.index('Outputs'))
        self.assertEqual(outputs, self.expected_output_folders)
        for f in ('farm_from_json_Results', 'TotalResultsForAllFarms'):
            self.assertTrue((self.path_dir_farms / 'Outputs' / f).is_dir())


if __name__ == '__main__':
    unittest.main()
