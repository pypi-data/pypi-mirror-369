from datetime import date

from pyholos.common import Component, EnumGeneric, HolosVar
from pyholos.components.animals.common import (
    AnimalCoefficientData, AnimalType, Bedding, BeddingMaterialType, Diet,
    DietAdditiveType, HousingType, LivestockEmissionConversionFactorsData,
    ManureStateType, Milk, ProductionStage,
    get_beef_and_dairy_cattle_coefficient_data,
    get_beef_and_dairy_cattle_feeding_activity_coefficient,
    get_default_methane_producing_capacity_of_manure)
from pyholos.config import DATE_FMT
from pyholos.utils import convert_camel_case_to_space_delimited, get_local_args


class _GroupNameType:
    def __init__(
            self,
            animal_type: AnimalType,
    ):
        self.type = animal_type
        self.name = convert_camel_case_to_space_delimited(s=animal_type.value.replace('Cow', '')).capitalize()


class GroupNameType(EnumGeneric):
    dairy_heifers = _GroupNameType(animal_type=AnimalType.dairy_heifers)
    dairy_lactating_cow = _GroupNameType(animal_type=AnimalType.dairy_lactating_cow)
    dairy_calves = _GroupNameType(animal_type=AnimalType.dairy_calves)
    dairy_dry_cow = _GroupNameType(animal_type=AnimalType.dairy_dry_cow)


class DairyBase(Component):
    def __init__(self):
        super().__init__()
        self.name = HolosVar(name="Name", value="Dairy cattle")
        self.component_type = HolosVar(name="Component Type", value="H.Core.Models.Animals.Dairy.DairyComponent")
        self.group_name = HolosVar(name="Group Name", value=None)
        self.group_type = HolosVar(name="Group Type", value=None)
        self.management_period_name = HolosVar(name="Management Period Name", value=None)
        self.management_period_start_date = HolosVar(name="Management Period Start Date", value=None)
        self.management_period_days = HolosVar(name="Management Period Days", value=None)
        self.number_of_animals = HolosVar(name="Number Of Animals", value=None)
        self.production_stage = HolosVar(name="Production Stage", value=None)
        self.number_of_young_animals = HolosVar(name="Number Of Young Animals", value=None)
        self.group_pairing_number = HolosVar(name="Group Pairing Number", value=None)
        self.start_weight = HolosVar(name="Start Weight", value=None)
        self.end_weight = HolosVar(name="End Weight", value=None)
        self.average_daily_gain = HolosVar(name="Average Daily Gain", value=None)
        self.milk_production = HolosVar(name="Milk Production", value=None)
        self.milk_fat_content = HolosVar(name="Milk Fat Content", value=None)
        self.milk_protein_content_as_percentage = HolosVar(name="Milk Protein Content As Percentage", value=None)
        self.diet_additive_type = HolosVar(name="Diet Additive Type", value=None)
        self.methane_conversion_factor_of_diet = HolosVar(name="Methane Conversion Factor Of Diet", value=None)

        self.methane_conversion_factor_adjusted = HolosVar(name="Methane Conversion Factor Adjusted", value=0)
        """deprecated"""

        self.feed_intake = HolosVar(name="Feed Intake", value=0)
        """deprecated"""

        self.crude_protein = HolosVar(name="Crude Protein", value=None)
        self.ash_content_of_diet = HolosVar(name="Ash Content Of Diet", value=None)
        self.forage = HolosVar(name="Forage", value=None)
        self.tdn = HolosVar(name="TDN", value=None)
        self.starch = HolosVar(name="Starch", value=None)
        self.fat = HolosVar(name="Fat", value=None)
        self.me = HolosVar(name="ME", value=None)
        self.ndf = HolosVar(name="NDF", value=None)

        self.volatile_solid_adjusted = HolosVar(name="Volatile Solid Adjusted", value=1)
        """deprecated"""

        self.nitrogen_excretion_adjusted = HolosVar(name="Nitrogen Excretion Adjusted", value=1)
        """deprecated"""

        self.dietary_net_energy_concentration = HolosVar(name="Dietary Net Energy Concentration", value=None)
        self.gain_coefficient = HolosVar(name="Gain Coefficient", value=None)

        self.gain_coefficient_a = HolosVar(name="Gain Coefficient A", value=0)
        """deprecated"""

        self.gain_coefficient_b = HolosVar(name="Gain Coefficient B", value=0)
        """deprecated"""

        self.housing_type = HolosVar(name="Housing Type", value=None)
        self.activity_coefficient_of_feeding_situation = HolosVar(name="Activity Coefficient Of Feeding Situation",
                                                                  value=None)
        self.maintenance_coefficient = HolosVar(name="Maintenance Coefficient", value=None)
        self.user_defined_bedding_rate = HolosVar(name="User Defined Bedding Rate", value=None)
        self.total_carbon_kilograms_dry_matter_for_bedding = HolosVar(
            name="Total Carbon Kilograms Dry Matter For Bedding", value=None)
        self.total_nitrogen_kilograms_dry_matter_for_bedding = HolosVar(
            name="Total Nitrogen Kilograms Dry Matter For Bedding", value=None)
        self.moisture_content_of_bedding_material = HolosVar(name="Moisture Content Of Bedding Material", value=None)
        self.methane_conversion_factor_of_manure = HolosVar(name="Methane Conversion Factor Of Manure", value=None)
        self.n2o_direct_emission_factor = HolosVar(name="N2O Direct Emission Factor", value=None)
        self.emission_factor_volatilization = HolosVar(name="Emission Factor Volatilization", value=None)
        self.volatilization_fraction = HolosVar(name="Volatilization Fraction", value=None)
        self.emission_factor_leaching = HolosVar(name="Emission Factor Leaching", value=None)
        self.fraction_leaching = HolosVar(name="Fraction Leaching", value=None)

        self.ash_content = HolosVar(name="Ash Content", value=8.0)
        """deprecated"""

        self.methane_producing_capacity_of_manure = HolosVar(name="Methane Producing Capacity Of Manure", value=None)

        self._animal_coefficient_data: AnimalCoefficientData | None = None

    def get_animal_coefficient_data(self):
        self._animal_coefficient_data = get_beef_and_dairy_cattle_coefficient_data(animal_type=self.group_type.value)

    def set_feeding_activity_coefficient(self):
        self.activity_coefficient_of_feeding_situation.value = get_beef_and_dairy_cattle_feeding_activity_coefficient(
            housing_type=self.housing_type.value)


class Dairy(DairyBase):
    def __init__(
            self,
            group_name: str,
            animal_type: AnimalType,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,
            milk_data: Milk,
            diet: Diet,
            housing_type: HousingType,
            manure_handling_system: ManureStateType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            start_weight: float = None,
            end_weight: float = None,
            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        """

        Args:
            group_name: GroupNames member
            animal_type: AnimalType class instance
            management_period_name: given name for the management period
            group_pairing_number: number of paired animals
            management_period_start_date: starting date for the management period
            management_period_days: number of days of the management period
            number_of_animals: number of animals
            production_stage: ProductionStage class instance
            number_of_young_animals: number of young animals
            milk_data: class object that contains all required milk production data
            diet: class object that contains all required diet data
            housing_type: HousingType class instance
            manure_handling_system: ManureStateType class instance
            manure_emission_factors: LivestockEmissionConversionFactorsData class instance
            start_weight: (kg) animal weight at the beginning of the management period
            end_weight: (kg) animal weight at the end of the management period
            diet_additive_type: type of the diet additive
            bedding_material_type: bedding material type
        """
        super().__init__()
        self.group_name.value = group_name
        self.group_type.value = animal_type.value
        self.management_period_name.value = management_period_name
        self.management_period_start_date.value = management_period_start_date.strftime(DATE_FMT)
        self.management_period_days.value = management_period_days
        self.number_of_animals.value = number_of_animals
        self.production_stage.value = production_stage.value
        self.number_of_young_animals.value = number_of_young_animals
        self.group_pairing_number.value = group_pairing_number

        self.get_animal_coefficient_data()
        self.start_weight.value = self._animal_coefficient_data.default_initial_weight if start_weight is None else start_weight
        self.end_weight.value = self._animal_coefficient_data.default_final_weight if end_weight is None else end_weight
        self.maintenance_coefficient.value = self._animal_coefficient_data.baseline_maintenance_coefficient
        self.gain_coefficient.value = self._animal_coefficient_data.gain_coefficient

        self.average_daily_gain.value = (self.end_weight.value - self.start_weight.value) / management_period_days

        self.milk_production.value = milk_data.production
        self.milk_fat_content.value = milk_data.fat_content
        self.milk_protein_content_as_percentage.value = milk_data.protein_content_as_percentage

        self.diet_additive_type.value = diet_additive_type.value

        self.crude_protein.value = diet.crude_protein_percentage
        self.forage.value = diet.forage_percentage
        self.tdn.value = diet.total_digestible_nutrient_percentage
        self.ash_content_of_diet.value = diet.ash_percentage
        self.starch.value = diet.starch_percentage
        self.fat.value = diet.fat_percentage
        self.me.value = diet.metabolizable_energy
        self.ndf.value = diet.neutral_detergent_fiber_percentage

        self.dietary_net_energy_concentration.value = diet.calc_dietary_net_energy_concentration_for_beef()
        self.methane_conversion_factor_of_diet.value = diet.calc_methane_conversion_factor(animal_type=animal_type)

        self.housing_type.value = housing_type.value

        bedding = Bedding(
            housing_type=housing_type,
            bedding_material_type=bedding_material_type,
            animal_type=animal_type)

        self.user_defined_bedding_rate.value = bedding.user_defined_bedding_rate.value
        self.total_carbon_kilograms_dry_matter_for_bedding.value = bedding.total_carbon_kilograms_dry_matter_for_bedding.value
        self.total_nitrogen_kilograms_dry_matter_for_bedding.value = bedding.total_nitrogen_kilograms_dry_matter_for_bedding.value
        self.moisture_content_of_bedding_material.value = bedding.moisture_content_of_bedding_material.value

        self.set_feeding_activity_coefficient()

        self.methane_producing_capacity_of_manure.value = get_default_methane_producing_capacity_of_manure(
            is_pasture=housing_type.is_pasture(),
            animal_type=animal_type)

        self.methane_conversion_factor_of_manure.value = manure_emission_factors.MethaneConversionFactor
        self.n2o_direct_emission_factor.value = manure_emission_factors.N2ODirectEmissionFactor
        self.volatilization_fraction.value = manure_emission_factors.VolatilizationFraction
        self.emission_factor_volatilization.value = manure_emission_factors.EmissionFactorVolatilization
        self.fraction_leaching.value = manure_emission_factors.LeachingFraction
        self.emission_factor_leaching.value = manure_emission_factors.EmissionFactorLeach

        self.volatile_solid_adjusted.value = 1
        self.nitrogen_excretion_adjusted.value = 1
        self.gain_coefficient_a.value = 0
        self.gain_coefficient_b.value = 0


class DairyHeifers(Dairy):
    animal_group = GroupNameType.dairy_heifers.value

    def __init__(
            self,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,
            milk_data: Milk,
            diet: Diet,
            housing_type: HousingType,
            manure_handling_system: ManureStateType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            start_weight: float = None,
            end_weight: float = None,
            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        super().__init__(
            group_name=self.animal_group.name,
            animal_type=self.animal_group.type,
            **get_local_args(locals())
        )


class DairyLactatingCow(Dairy):
    animal_group = GroupNameType.dairy_lactating_cow.value

    def __init__(
            self,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,
            milk_data: Milk,
            diet: Diet,
            housing_type: HousingType,
            manure_handling_system: ManureStateType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            start_weight: float = None,
            end_weight: float = None,
            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        super().__init__(
            group_name=self.animal_group.name,
            animal_type=self.animal_group.type,
            **get_local_args(locals())
        )


class DairyCalves(Dairy):
    animal_group = GroupNameType.dairy_calves.value

    def __init__(
            self,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,
            milk_data: Milk,
            diet: Diet,
            housing_type: HousingType,
            manure_handling_system: ManureStateType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            start_weight: float = None,
            end_weight: float = None,
            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        super().__init__(
            group_name=self.animal_group.name,
            animal_type=self.animal_group.type,
            **get_local_args(locals())
        )


class DairyDryCow(Dairy):
    animal_group = GroupNameType.dairy_dry_cow.value

    def __init__(
            self,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,
            milk_data: Milk,
            diet: Diet,
            housing_type: HousingType,
            manure_handling_system: ManureStateType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            start_weight: float = None,
            end_weight: float = None,
            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        super().__init__(
            group_name=self.animal_group.name,
            animal_type=self.animal_group.type,
            **get_local_args(locals())
        )
