from pathlib import Path
from typing import Generator

from pandas import DataFrame

from pyholos.components.common import convert_province_name
from pyholos.farm.farm_inputs import (BeefCattleInput, DairyCattleInput,
                                      FieldsInput, SheepFlockInput,
                                      WeatherSummary)
from pyholos.farm.farm_settings import ParamsFarmSettings
from pyholos.soil import (convert_soil_functional_category_name,
                          convert_soil_texture_name)


class Farm:
    def __init__(
            self,
            farm_settings: ParamsFarmSettings,
            beef_cattle_data: BeefCattleInput = None,
            dairy_cattle_data: DairyCattleInput = None,
            sheep_flock_data: SheepFlockInput = None,
            fields_data: FieldsInput = None,
    ):
        self.farm_settings = farm_settings
        self.beef = beef_cattle_data
        self.dairy = dairy_cattle_data
        self.sheep = sheep_flock_data
        self.fields = fields_data
        self.other_livestock = None
        self.poultry = None
        self.shelterbelts = None
        self.swine = None

    @staticmethod
    def _set_dir_name(entry: str) -> str:
        return ' '.join([s.capitalize() for s in entry.split('_')])

    def _iter_over_animal_components(self) -> Generator:
        for k, v in self.__dict__.items():
            if (v is not None) and (not isinstance(v, ParamsFarmSettings)):
                yield k, v

    def write_files(
            self,
            path_dir_farm: Path
    ):
        path_dir_farm.mkdir(parents=True, exist_ok=True)
        self.farm_settings.write(path_dir_farm=path_dir_farm)
        for k, v in self._iter_over_animal_components():
            path_dir = path_dir_farm / self._set_dir_name(entry=k)
            path_dir.mkdir(parents=True, exist_ok=True)
            dfs = [DataFrame.from_records([v.to_dict() for v in component]) for component in v]
            for df in dfs:
                name_output_file = df['Name'].unique()[0]
                df.to_csv(path_dir / f'{name_output_file}.csv', index=False)

    def export_to_dict(self) -> dict:
        res = {**self.farm_settings.export_to_dict()}
        for k, v in self._iter_over_animal_components():
            dir_name = self._set_dir_name(entry=k)
            res[dir_name] = [[v.to_dict() for v in component] for component in v]

        return res


def create_farm(
        latitude: float,
        longitude: float,
        weather_summary: WeatherSummary,
        beef_cattle_data: BeefCattleInput = None,
        dairy_cattle_data: DairyCattleInput = None,
        sheep_flock_data: SheepFlockInput = None,
        fields_data: FieldsInput = None,
) -> Farm:
    farm = Farm(
        farm_settings=ParamsFarmSettings(
            latitude=latitude,
            longitude=longitude,
            year=weather_summary.year,
            monthly_precipitation=weather_summary.monthly_precipitation,
            monthly_potential_evapotranspiration=weather_summary.monthly_potential_evapotranspiration,
            monthly_temperature=weather_summary.monthly_temperature)
    )

    params_soil = farm.farm_settings.params_soil

    province = convert_province_name(name=params_soil.province.value)
    soil_texture = convert_soil_texture_name(name=params_soil.soil_texture.value)

    if beef_cattle_data is not None:
        farm.beef = beef_cattle_data.create_components(
            province=province,
            soil_texture=soil_texture)

    if dairy_cattle_data is not None:
        farm.dairy = dairy_cattle_data.create_components(
            province=province,
            soil_texture=soil_texture)

    if sheep_flock_data is not None:
        farm.sheep = sheep_flock_data.create_components(
            province=province,
            soil_texture=soil_texture)

    if fields_data is not None:
        farm.fields = fields_data.create_components(
            province=province,
            clay_content=params_soil.proportion_of_clay_in_soil.value,
            sand_content=params_soil.proportion_of_sand_in_soil.value,
            organic_carbon_percentage=params_soil.proportion_of_soil_organic_carbon.value,
            soil_top_layer_thickness=params_soil.top_layer_thickness.value,
            soil_functional_category=convert_soil_functional_category_name(params_soil.soil_functional_category.value))

    return farm
