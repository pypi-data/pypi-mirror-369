import unittest

from pyholos import config


class TestPaths(unittest.TestCase):
    def test_paths_exist(self):
        self.assertIsNotNone(config.PATH_HOLOS_CLI)

        assert config.PathsSlcData.geojson_file.exists()
        assert config.PathsSlcData.csv_dir.exists()
        assert config.PathsSlcData.cmp_file.exists()
        assert config.PathsSlcData.slt_file.exists()
        assert config.PathsSlcData.snt_file.exists()


if __name__ == '__main__':
    unittest.main()
