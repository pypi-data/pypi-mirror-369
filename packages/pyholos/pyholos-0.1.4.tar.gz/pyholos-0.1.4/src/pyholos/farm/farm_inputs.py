from datetime import date
from typing import ClassVar, Generator, Union
from uuid import UUID, uuid4

from pydantic import (BaseModel, Field, NonNegativeFloat, NonNegativeInt,
                      PositiveFloat, PositiveInt, confloat, conint, conlist,
                      field_validator)

from pyholos.common2 import CanadianProvince
from pyholos.components.animals import beef, dairy, sheep
from pyholos.components.animals.common import (BeddingMaterialType, Diet,
                                               DietAdditiveType, HousingType,
                                               ManureAnimalSourceTypes,
                                               ManureLocationSourceType,
                                               ManureStateType, Milk,
                                               ProductionStage,
                                               get_manure_emission_factors)
from pyholos.components.land_management.carbon.relative_biomass_information import (
    RelativeBiomassInformationData, get_relative_biomass_information_data,
    parse_table_7)
from pyholos.components.land_management.common import (FertilizerBlends,
                                                       HarvestMethod,
                                                       IrrigationType,
                                                       ManureApplicationTypes,
                                                       TillageType)
from pyholos.components.land_management.crop import CropType
from pyholos.components.land_management.field_system import CropViewItem
from pyholos.core_constants import CoreConstants
from pyholos.soil import SoilFunctionalCategory, SoilTexture
from pyholos.utils import concat_lists

AnimalComponent = Union[
    beef.Bulls, beef.ReplacementHeifers, beef.Cows, beef.Calves,
    beef.FinishingHeifers, beef.FinishingSteers,
    beef.BackgrounderHeifer, beef.BackgrounderSteer,
    dairy.DairyHeifers, dairy.DairyLactatingCow, dairy.DairyCalves, dairy.DairyDryCow,
    sheep.SheepFeedlot, sheep.Rams, sheep.Ewes, sheep.Lambs
]
type ManagementPeriods = list[BeefManagementPeriod | DairyManagementPeriod | SheepManagementPeriod]

TypeWaterData = confloat(strict=True, ge=0, allow_inf_nan=False)
TypeTemperatureData = confloat(strict=True, allow_inf_nan=False)


class WeatherData(BaseModel):
    """A class that holds daily values for precipitation (mm), potential_evapotranspiration (mm) and temperature (°C)
    for one year.
    """
    spec_daily_data: ClassVar = dict(min_length=365, max_length=366)

    year: int = Field(gt=CoreConstants.MinimumYear)
    precipitation: conlist(item_type=TypeWaterData, **spec_daily_data)
    potential_evapotranspiration: conlist(item_type=TypeWaterData, **spec_daily_data)
    temperature: conlist(item_type=TypeTemperatureData, **spec_daily_data)


class WeatherSummary(BaseModel):
    spec_monthly_data: ClassVar = dict(min_length=12, max_length=12)

    year: int = Field(gt=1970)
    mean_annual_precipitation: TypeWaterData
    mean_annual_temperature: TypeTemperatureData
    mean_annual_evapotranspiration: TypeWaterData
    growing_season_precipitation: TypeWaterData
    growing_season_evapotranspiration: TypeWaterData
    monthly_precipitation: conlist(item_type=TypeWaterData, **spec_monthly_data)
    monthly_potential_evapotranspiration: conlist(item_type=TypeWaterData, **spec_monthly_data)
    monthly_temperature: conlist(item_type=TypeTemperatureData, **spec_monthly_data)


class BeefManagementPeriod(BaseModel):
    name: str = Field(min_length=1)
    start_date: date
    days: conint(gt=0)
    group_pairing_number: conint(ge=0)
    number_of_animals: conint(ge=0)
    production_stage: ProductionStage
    number_of_young_animals: conint(ge=0)
    is_milk_fed_only: bool
    diet: Diet
    housing_type: HousingType
    manure_handling_system: ManureStateType
    weather_summary: WeatherSummary
    start_weight: confloat(ge=0, allow_inf_nan=False) = None
    end_weight: confloat(ge=0, allow_inf_nan=False) = None
    diet_additive_type: DietAdditiveType = DietAdditiveType.NONE
    bedding_material_type: BeddingMaterialType = BeddingMaterialType.straw


class DairyManagementPeriod(BaseModel):
    name: str = Field(min_length=1)
    start_date: date
    days: conint(gt=0)
    group_pairing_number: conint(ge=0)
    number_of_animals: conint(ge=0)
    production_stage: ProductionStage
    number_of_young_animals: conint(ge=0)
    milk_data: Milk
    diet: Diet
    housing_type: HousingType
    manure_handling_system: ManureStateType
    weather_summary: WeatherSummary
    start_weight: confloat(ge=0, allow_inf_nan=False) = None
    end_weight: confloat(ge=0, allow_inf_nan=False) = None
    diet_additive_type: DietAdditiveType = DietAdditiveType.NONE
    bedding_material_type: BeddingMaterialType = BeddingMaterialType.straw


class SheepManagementPeriod(BaseModel):
    name: str = Field(min_length=1)
    start_date: date
    days: conint(gt=0)
    group_pairing_number: conint(ge=0)
    number_of_animals: conint(ge=0)
    production_stage: ProductionStage
    number_of_young_animals: conint(ge=0)
    diet: Diet
    housing_type: HousingType
    manure_handling_system: ManureStateType
    weather_summary: WeatherSummary
    start_weight: confloat(ge=0, allow_inf_nan=False) = None
    end_weight: confloat(ge=0, allow_inf_nan=False) = None
    diet_additive_type: DietAdditiveType = DietAdditiveType.NONE
    bedding_material_type: BeddingMaterialType = BeddingMaterialType.straw


class AnimalInputBase(BaseModel):
    def __iter__(self):
        for k, v in self.__dict__.items():
            if v is not None:
                yield k, v

    def _filter_inputs(
            self,
            animal_groups: list[list[str]]
    ) -> list[list[str]]:
        res = []
        for component_type_animals in animal_groups:
            animal_data = [s for s in component_type_animals if getattr(self, s) is not None]
            if len(animal_data) > 0:
                res.append(animal_data)
        return res

    def filter_inputs(self) -> list[list[str]]:
        pass

    @staticmethod
    def map_component(**kwargs):
        pass

    @staticmethod
    def _create_component(**kwargs):
        pass

    def create_components(
            self,
            province: CanadianProvince,
            soil_texture: SoilTexture,
    ) -> list[list[AnimalComponent]]:
        res = []
        for non_empty_entry in self.filter_inputs():
            animal_components = []
            for animal_type in non_empty_entry:
                management_periods = getattr(self, animal_type)
                component_type = self.map_component(component_name=animal_type)
                animal_components.append(
                    [self._create_component(
                        province=province,
                        soil_texture=soil_texture,
                        component_class=component_type,
                        management_period=management_period)
                        for management_period in management_periods])

            res.append(concat_lists(*animal_components))
        return res


class BeefCattleInput(AnimalInputBase):
    Bulls: ManagementPeriods = None
    ReplacementHeifers: ManagementPeriods = None
    Cows: ManagementPeriods = None
    Calves: ManagementPeriods = None
    FinishingHeifers: ManagementPeriods = None
    FinishingSteers: ManagementPeriods = None
    BackgrounderHeifer: ManagementPeriods = None
    BackgrounderSteer: ManagementPeriods = None

    component_types: ClassVar = Union[
        beef.Bulls,
        beef.ReplacementHeifers,
        beef.Cows,
        beef.Calves,
        beef.FinishingHeifers,
        beef.FinishingSteers,
        beef.BackgrounderHeifer,
        beef.BackgrounderSteer]

    def filter_inputs(self) -> list[list[str]]:
        return self._filter_inputs(animal_groups=[
            ["Bulls", "ReplacementHeifers", "Cows", "Calves"],
            ["FinishingHeifers", "FinishingSteers"],
            ["BackgrounderHeifer", "BackgrounderSteer"]
        ])

    @staticmethod
    def map_component(
            component_name: str
    ) -> component_types:

        match component_name:
            case 'Bulls':
                res = beef.Bulls
            case 'ReplacementHeifers':
                res = beef.ReplacementHeifers
            case 'Cows':
                res = beef.Cows
            case 'Calves':
                res = beef.Calves
            case 'FinishingHeifers':
                res = beef.FinishingHeifers
            case 'FinishingSteers':
                res = beef.FinishingSteers
            case 'BackgrounderHeifer':
                res = beef.BackgrounderHeifer
            case 'BackgrounderSteer':
                res = beef.BackgrounderSteer
            case _:
                raise ValueError(f'Unrecognized component name "({component_name})."')

        return res

    @staticmethod
    def _create_component(
            province: CanadianProvince,
            soil_texture: SoilTexture,
            component_class: [component_types],
            management_period: BeefManagementPeriod
    ) -> component_types:
        return component_class(
            management_period_name=management_period.name,
            management_period_start_date=management_period.start_date,
            management_period_days=management_period.days,
            group_pairing_number=management_period.group_pairing_number,
            production_stage=management_period.production_stage,
            number_of_animals=management_period.number_of_animals,
            number_of_young_animals=management_period.number_of_young_animals,
            is_milk_fed_only=management_period.is_milk_fed_only,
            milk_data=Milk(),
            diet=management_period.diet,
            housing_type=management_period.housing_type,
            manure_handling_system=management_period.manure_handling_system,
            manure_emission_factors=get_manure_emission_factors(
                animal_type=component_class.animal_type,
                year=management_period.weather_summary.year,
                manure_state_type=management_period.manure_handling_system,
                mean_annual_precipitation=management_period.weather_summary.mean_annual_precipitation,
                mean_annual_temperature=management_period.weather_summary.mean_annual_temperature,
                mean_annual_evapotranspiration=management_period.weather_summary.mean_annual_evapotranspiration,
                growing_season_precipitation=management_period.weather_summary.growing_season_precipitation,
                growing_season_evapotranspiration=management_period.weather_summary.growing_season_evapotranspiration,
                province=province,
                soil_texture=soil_texture),
            start_weight=management_period.start_weight,
            end_weight=management_period.end_weight,
            diet_additive_type=management_period.diet_additive_type,
            bedding_material_type=management_period.bedding_material_type
        )


class DairyCattleInput(AnimalInputBase):
    Heifers: ManagementPeriods = None
    LactatingCow: ManagementPeriods = None
    Calves: ManagementPeriods = None
    DryCow: ManagementPeriods = None

    component_types: ClassVar = Union[
        dairy.DairyHeifers,
        dairy.DairyLactatingCow,
        dairy.DairyCalves,
        dairy.DairyDryCow]

    @staticmethod
    def map_component(
            component_name: str
    ) -> component_types:

        match component_name:
            case 'Heifers':
                res = dairy.DairyHeifers
            case 'LactatingCow':
                res = dairy.DairyLactatingCow
            case 'Calves':
                res = dairy.DairyCalves
            case 'DryCow':
                res = dairy.DairyDryCow
            case _:
                raise ValueError(f'Unrecognized component name "({component_name})."')

        return res

    def filter_inputs(self) -> list[list[str]]:
        return self._filter_inputs(animal_groups=[
            ["Heifers", "LactatingCow", "Calves", "DryCow"]
        ])

    @staticmethod
    def _create_component(
            province: CanadianProvince,
            soil_texture: SoilTexture,
            component_class: [component_types],
            management_period: DairyManagementPeriod
    ) -> component_types:
        return component_class(
            management_period_name=management_period.name,
            management_period_start_date=management_period.start_date,
            management_period_days=management_period.days,
            group_pairing_number=management_period.group_pairing_number,
            number_of_animals=management_period.number_of_animals,
            production_stage=management_period.production_stage,
            number_of_young_animals=management_period.number_of_young_animals,
            milk_data=Milk(),
            diet=management_period.diet,
            housing_type=management_period.housing_type,
            manure_handling_system=management_period.manure_handling_system,
            diet_additive_type=management_period.diet_additive_type,
            bedding_material_type=management_period.bedding_material_type,

            manure_emission_factors=get_manure_emission_factors(
                manure_state_type=management_period.manure_handling_system,
                mean_annual_precipitation=management_period.weather_summary.mean_annual_precipitation,
                mean_annual_temperature=management_period.weather_summary.mean_annual_temperature,
                mean_annual_evapotranspiration=management_period.weather_summary.mean_annual_evapotranspiration,
                growing_season_precipitation=management_period.weather_summary.growing_season_precipitation,
                growing_season_evapotranspiration=management_period.weather_summary.growing_season_evapotranspiration,
                animal_type=component_class.animal_group.type,
                province=province,
                year=management_period.weather_summary.year,
                soil_texture=soil_texture)
        )


class SheepFlockInput(AnimalInputBase):
    SheepFeedlot: ManagementPeriods = None
    Rams: ManagementPeriods = None
    Ewes: ManagementPeriods = None
    Lambs: ManagementPeriods = None

    component_types: ClassVar = Union[
        sheep.SheepFeedlot,
        sheep.Rams,
        sheep.Ewes,
        sheep.Lambs]

    @staticmethod
    def map_component(
            component_name: str
    ) -> component_types:

        match component_name:
            case 'SheepFeedlot':
                res = sheep.SheepFeedlot
            case 'Rams':
                res = sheep.Rams
            case 'Ewes':
                res = sheep.Ewes
            case 'Lambs':
                res = sheep.Lambs
            case _:
                raise ValueError(f'Unrecognized component name "({component_name})."')

        return res

    def filter_inputs(self) -> list[list[str]]:
        return self._filter_inputs(animal_groups=[
            ["SheepFeedlot"],
            ["Rams"],
            ["Ewes", "Lambs"],
        ])

    @staticmethod
    def _create_component(
            province: CanadianProvince,
            soil_texture: SoilTexture,
            component_class: [component_types],
            management_period: SheepManagementPeriod
    ) -> component_types:
        return component_class(
            management_period_name=management_period.name,
            management_period_start_date=management_period.start_date,
            management_period_days=management_period.days,
            group_pairing_number=management_period.group_pairing_number,
            number_of_animals=management_period.number_of_animals,
            production_stage=management_period.production_stage,
            number_of_young_animals=management_period.number_of_young_animals,
            diet=management_period.diet,
            housing_type=management_period.housing_type,
            manure_handling_system=management_period.manure_handling_system,
            diet_additive_type=management_period.diet_additive_type,
            bedding_material_type=management_period.bedding_material_type,

            manure_emission_factors=get_manure_emission_factors(
                manure_state_type=management_period.manure_handling_system,
                mean_annual_precipitation=management_period.weather_summary.mean_annual_precipitation,
                mean_annual_temperature=management_period.weather_summary.mean_annual_temperature,
                mean_annual_evapotranspiration=management_period.weather_summary.mean_annual_evapotranspiration,
                growing_season_precipitation=management_period.weather_summary.growing_season_precipitation,
                growing_season_evapotranspiration=management_period.weather_summary.growing_season_evapotranspiration,
                animal_type=component_class.animal_type,
                province=province,
                year=management_period.weather_summary.year,
                soil_texture=soil_texture)
        )


class FieldAnnualData(BaseModel):
    name: str = Field(min_length=1)
    field_area: PositiveFloat
    weather_data: WeatherData
    crop_type: CropType
    crop_yield: NonNegativeFloat
    crop_year: PositiveInt
    under_sown_crops_used: bool
    tillage_type: TillageType
    harvest_method: HarvestMethod
    nitrogen_fertilizer_rate: NonNegativeFloat = Field(default=0)
    fertilizer_blend: FertilizerBlends
    irrigation_type: IrrigationType = IrrigationType.RainFed
    amount_of_irrigation: NonNegativeFloat = 0
    number_of_pesticide_passes: NonNegativeInt = 0
    amount_of_manure_applied: NonNegativeFloat = 0
    manure_application_type: ManureApplicationTypes = ManureApplicationTypes.NotSelected
    manure_animal_source_type: ManureAnimalSourceTypes = ManureAnimalSourceTypes.NotSelected
    manure_state_type: ManureStateType = ManureStateType.not_selected
    manure_location_source_type: ManureLocationSourceType = ManureLocationSourceType.NotSelected

    year_in_perennial_stand: int = None
    field_system_component_guid: UUID = None
    current_year: int = None
    relative_biomass_information_data: RelativeBiomassInformationData = None
    province: CanadianProvince = None
    clay_content: float = None
    sand_content: float = None
    organic_carbon_percentage: float = None
    soil_top_layer_thickness: float = None
    soil_functional_category: SoilFunctionalCategory = None
    evapotranspiration: list[float] = None
    precipitation: list[float] = None
    temperature: list[float] = None

    @field_validator('weather_data', mode='after')
    @classmethod
    def revalidate_weather_data(cls, value) -> WeatherData:
        WeatherData(**value.model_dump())
        return value


class FieldsInput(BaseModel):
    fields: FieldAnnualData | list[FieldAnnualData] = None
    table_7: ClassVar = parse_table_7()

    @property
    def fields_data(self) -> Generator[list[FieldAnnualData]] | Generator:
        if self.fields is None:
            return iter(())
        else:
            if not isinstance(self.fields, list):
                self.fields = [self.fields]
            for v in self.fields:
                yield [v]

    @staticmethod
    def calc_year_in_perennial_stand(
            crops: list[CropType]
    ) -> list[int]:
        v = 0
        res = []
        for i, crop in enumerate(crops):
            v = (v + 1) if crop.is_perennial() else 0
            res.append(v)
        return res

    @staticmethod
    def calc_perennial_stand_lengths(
            years_in_perennial_stand: list[int]
    ) -> list[int]:
        res = [max(1, years_in_perennial_stand[-1])]
        for v in reversed(years_in_perennial_stand[:-1]):
            res.append(max(v, res[-1]) if v != 0 else 1)
        return list(reversed(res))

    @staticmethod
    def set_perennial_stand_id(
            crops: list[CropType],
    ) -> list[UUID]:
        id_for_annual = UUID("00000000-0000-0000-0000-000000000000")
        perennial_stand_id = None

        crop_prev = None
        res = []
        for crop in crops:
            if not crop.is_perennial():
                perennial_stand_id = id_for_annual
            else:
                if crop != crop_prev:
                    perennial_stand_id = uuid4()
            crop_prev = crop

            res.append(perennial_stand_id)

        return res

    def _create_one_year_component(
            self,
            province: CanadianProvince,
            clay_content: float,
            sand_content: float,
            organic_carbon_percentage: float,
            soil_top_layer_thickness: float,
            soil_functional_category: SoilFunctionalCategory,
            perennial_stand_id: UUID,
            field_system_component_guid: UUID,
            perennial_stand_length: int,
            field_one_year_data: FieldAnnualData,
            year_in_perennial_stand: int,
    ) -> CropViewItem:
        weather_data = field_one_year_data.weather_data

        return CropViewItem(
            name=field_one_year_data.name,
            field_area=field_one_year_data.field_area,
            current_year=weather_data.year,
            crop_year=field_one_year_data.crop_year,
            year_in_perennial_stand=year_in_perennial_stand,
            crop_type=field_one_year_data.crop_type,
            tillage_type=field_one_year_data.tillage_type,
            perennial_stand_id=perennial_stand_id,
            perennial_stand_length=perennial_stand_length,
            relative_biomass_information_data=get_relative_biomass_information_data(
                table_7=self.table_7,
                crop_type=field_one_year_data.crop_type,
                irrigation_type=field_one_year_data.irrigation_type,
                irrigation_amount=sum(weather_data.precipitation),
                province=province),
            crop_yield=field_one_year_data.crop_yield,
            harvest_method=field_one_year_data.harvest_method,
            nitrogen_fertilizer_rate=field_one_year_data.nitrogen_fertilizer_rate,
            under_sown_crops_used=field_one_year_data.under_sown_crops_used,
            field_system_component_guid=field_system_component_guid,
            province=province,
            clay_content=clay_content,
            sand_content=sand_content,
            organic_carbon_percentage=organic_carbon_percentage,
            soil_top_layer_thickness=soil_top_layer_thickness,
            soil_functional_category=soil_functional_category,
            fertilizer_blend=field_one_year_data.fertilizer_blend,
            evapotranspiration=weather_data.potential_evapotranspiration,
            precipitation=weather_data.precipitation,
            temperature=weather_data.temperature,

            amount_of_irrigation=field_one_year_data.amount_of_irrigation,
            number_of_pesticide_passes=field_one_year_data.number_of_pesticide_passes,
            amount_of_manure_applied=field_one_year_data.amount_of_manure_applied,
            manure_application_type=field_one_year_data.manure_application_type,
            manure_animal_source_type=field_one_year_data.manure_animal_source_type,
            manure_state_type=field_one_year_data.manure_state_type,
            manure_location_source_type=field_one_year_data.manure_location_source_type
        )

    def _create_field_component(
            self,
            field_data: list[FieldAnnualData],
            province: CanadianProvince,
            clay_content: float,
            sand_content: float,
            organic_carbon_percentage: float,
            soil_top_layer_thickness: float,
            soil_functional_category: SoilFunctionalCategory,
    ) -> list[CropViewItem]:

        field_system_component_guid = uuid4()
        crops = [v.crop_type for v in field_data]
        years_in_perennial_stand = self.calc_year_in_perennial_stand(crops=crops)
        ids_perennial = self.set_perennial_stand_id(crops=crops)
        perennial_stand_lengths = self.calc_perennial_stand_lengths(years_in_perennial_stand=years_in_perennial_stand)

        res = []
        for annual_data, year_in_perennial_stand, perennial_stand_length, id_perennial in zip(
                field_data,
                years_in_perennial_stand,
                perennial_stand_lengths,
                ids_perennial
        ):
            one_year_component = self._create_one_year_component(
                province=province,
                clay_content=clay_content,
                sand_content=sand_content,
                organic_carbon_percentage=organic_carbon_percentage,
                soil_top_layer_thickness=soil_top_layer_thickness,
                soil_functional_category=soil_functional_category,
                perennial_stand_id=id_perennial,
                field_system_component_guid=field_system_component_guid,
                perennial_stand_length=perennial_stand_length,
                field_one_year_data=annual_data,
                year_in_perennial_stand=year_in_perennial_stand,
            )

            res.append(one_year_component)

        return res

    def create_components(
            self,
            province: CanadianProvince,
            clay_content: float,
            sand_content: float,
            organic_carbon_percentage: float,
            soil_top_layer_thickness: float,
            soil_functional_category: SoilFunctionalCategory,
    ) -> list[list[CropViewItem]]:
        res = []
        for field_data in self.fields_data:
            field_component = self._create_field_component(
                field_data=field_data,
                province=province,
                clay_content=clay_content,
                sand_content=sand_content,
                organic_carbon_percentage=organic_carbon_percentage,
                soil_top_layer_thickness=soil_top_layer_thickness,
                soil_functional_category=soil_functional_category
            )
            res.append(field_component)

        return res
