from pyholos.common2 import CanadianProvince
from pyholos.components.common import convert_province_name
from pyholos.components.land_management.crop import (CropType,
                                                     convert_crop_type_name)
from pyholos.config import PathsHolosResources
from pyholos.utils import read_holos_resource_table


class LoadedData:
    def __init__(self):
        self.table_small_yield_area = self.read_small_yield_area_data()

    @staticmethod
    def read_small_yield_area_data():
        """Loads default yield data table.

        Holos source code:
            https://github.com/holos-aafc/Holos/blob/d6dba2d07413fd2d23439b60a6bb9217c8ebb048/H.Core/Providers/Soil/SmallAreaYieldProvider.cs#L113
        """
        excluded_cols = [4, 14, 15, 19, 20, 37, 38, 40]
        df = read_holos_resource_table(
            path_file=PathsHolosResources.Table_small_area_yields,
            usecols=[v for v in range(41) if v not in excluded_cols])

        columns = list(df.columns[:4]) + [convert_crop_type_name(name=v).value for v in df.columns[4:]]

        for crop, replacing_crop in [
            (CropType.MustardSeed, CropType.Mustard),
            (CropType.DryFieldPeas, CropType.DryPeas),
            (CropType.TimothyHay, CropType.TamePasture)
        ]:
            columns[columns.index(crop)] = replacing_crop

        df.columns = columns
        df['PROVINCE'] = df['PROVINCE'].apply(lambda x: convert_province_name(name=x).name)

        return df.set_index(['YEAR', 'PROVINCE', 'POLY_ID'])

    def get_yield(
            self,
            year: int,
            polygon_id: int,
            crop_type: CropType,
            province: CanadianProvince
    ) -> float:
        if crop_type.is_perennial():
            # Small area yield table only has one perennial type 'tame hay'. Had discussion with team on 8/17/2021  and it was agreed
            # that we would use tame hay yields as the default for all perennial types until better numbers were found
            lookup_crop_type = CropType.TamePasture

        elif crop_type == CropType.GrassSilage:
            lookup_crop_type = CropType.TamePasture

        elif crop_type == CropType.Flax:
            lookup_crop_type = CropType.FlaxSeed

        elif crop_type == CropType.FieldPeas:
            lookup_crop_type = CropType.DryPeas
        else:
            lookup_crop_type = crop_type

        try:
            res = self.table_small_yield_area.loc[(year, province.name, polygon_id), lookup_crop_type]
        except KeyError:
            res = None
        return res
