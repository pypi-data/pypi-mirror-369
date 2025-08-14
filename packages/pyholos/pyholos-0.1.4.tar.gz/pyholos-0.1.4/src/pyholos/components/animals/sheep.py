from datetime import date
from enum import Enum

from pyholos import utils
from pyholos.common import Component, HolosVar
from pyholos.components.animals.common import (
    AnimalType, Bedding, BeddingMaterialType, Diet, DietAdditiveType,
    HousingType, LivestockEmissionConversionFactorsData, ManureStateType,
    ProductionStage, convert_animal_type_name,
    get_default_manure_composition_data,
    get_default_methane_producing_capacity_of_manure,
    get_manure_excretion_rate)
from pyholos.components.common import ComponentType
from pyholos.config import DATE_FMT, PathsHolosResources


def get_feeding_activity_coefficient(
        housing_type: HousingType
) -> float:
    """Returns the feeding activity coefficient of feeding situation (CA) for sheep
    (Table_23_Feeding_Activity_Coefficient_Sheep_Provider)

    Args:
        housing_type: Housing type class instance

    Returns:
        (MJ d-1 kg-1) activity coefficient of feeding situation (CA)

    Notes:
        1. Animals are confined due to pregnancy in final trimester (50 days) (IPCC, 2019)
        2. Animals housed for fattening

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/97331845af308fe8aab6267edad4bbda6f5938b6/H.Core/Providers/Animals/Table_23_Feeding_Activity_Coefficient_Sheep_Provider.cs#L17

    """
    match housing_type:
        # Footnote 1
        case HousingType.housed_ewes:
            return 0.0096

        # Footnote 2
        case HousingType.confined:
            return 0.0067

        case HousingType.pasture | HousingType.flat_pasture:
            return 0.0107

        case HousingType.hilly_pasture_or_open_range:
            return 0.024

        case _:
            raise ValueError(f"unable to get data for housing type: {housing_type}. Returning default value of 0.")
            # return 0


class GroupNames(Enum):
    sheep_feedlot: str = "Sheep feedlot"
    rams: str = "Rams"
    ewes: str = "Ewes"
    lambs: str = "Lambs"
    lambs_and_ewes: str = "Lambs & ewes"


class AnimalCoefficientData:
    def __init__(
            self,
            maintenance_coefficient: float = 0,
            coefficient_a: float = 0,
            coefficient_b: float = 0,
            initial_weight: float = 0,
            final_weight: float = 0,
            wool_production: float = 0
    ):
        """Table_22_Livestock_Coefficients_For_Sheep.csv

        Args:
            maintenance_coefficient: (MJ d-1 kg-1) maintenance coefficient (cf)
            coefficient_a: (MJ kg-1)
            coefficient_b: (MJ kg-2)
            initial_weight: (kg)
            final_weight: (kg)
            wool_production: : (kg year-1)
        """
        self.baseline_maintenance_coefficient = maintenance_coefficient
        self.coefficient_a = coefficient_a
        self.coefficient_b = coefficient_b
        self.initial_weight = initial_weight
        self.final_weight = final_weight
        self.wool_production = wool_production


class SheepBase(Component):
    def __init__(self):
        super().__init__()

        self.name = HolosVar(name="Name", value="Sheep")
        self.component_type = HolosVar(name="Component Type", value="H.Core.Models.Animals.Sheep")
        self.group_name = HolosVar(name="Group Name", value=None)
        self.group_type = HolosVar(name="Group Type", value=None)
        self.management_period_name = HolosVar(name="Management Period Name", value=None)
        self.group_pairing_number = HolosVar(name="Group Pairing Number", value=None)
        self.management_period_start_date = HolosVar(name="Management Period Start Date", value=None)
        self.management_period_days = HolosVar(name="Management Period Days", value=None)
        self.number_of_animals = HolosVar(name="Number Of Animals", value=None)
        self.production_stage = HolosVar(name="Production Stage", value=None)
        self.number_of_young_animals = HolosVar(name="Number Of Young Animals", value=None)
        self.start_weight = HolosVar(name="Start Weight", value=None)
        self.end_weight = HolosVar(name="End Weight", value=None)
        self.average_daily_gain = HolosVar(name="Average Daily Gain", value=None)

        self.energy_required_to_produce_wool = HolosVar(name="Energy Required To Produce Wool", value=24)
        """(MJ kg-1)
        Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/97331845af308fe8aab6267edad4bbda6f5938b6/H.Core/Services/Initialization/Animals/AnimalInitializationService.Sheep.cs#L28
        """

        self.wool_production = HolosVar(name="Wool Production", value=None)

        self.energy_required_to_produce_milk = HolosVar(name="Energy Required To Produce Milk", value=4.6)
        """(MJ kg-1)
        Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/97331845af308fe8aab6267edad4bbda6f5938b6/H.Core/Services/Initialization/Animals/AnimalInitializationService.Sheep.cs#L28
        """

        self.diet_additive_type = HolosVar(name="Diet Additive Type", value=None)

        self.methane_conversion_factor_of_diet = HolosVar(name="Methane Conversion Factor Of Diet", value=None)

        self.methane_conversion_factor_adjusted = HolosVar(name="Methane Conversion Factor Adjusted", value=0)
        """deprecated"""

        self.feed_intake = HolosVar(name="Feed Intake", value=0)
        """only for swine"""

        self.crude_protein = HolosVar(name="Crude Protein", value=None)
        self.forage = HolosVar(name="Forage", value=None)
        self.tdn = HolosVar(name="TDN", value=None)
        self.ash_content_of_diet = HolosVar(name="Ash Content Of Diet", value=None)
        self.starch = HolosVar(name="Starch", value=None)
        self.fat = HolosVar(name="Fat", value=None)
        self.me = HolosVar(name="ME", value=None)
        self.ndf = HolosVar(name="NDF", value=None)
        self.gain_coefficient_a = HolosVar(name="Gain Coefficient A", value=None)
        self.gain_coefficient_b = HolosVar(name="Gain Coefficient B", value=None)
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
        self.manure_excretion_rate = HolosVar(name="Manure Excretion Rate", value=None)
        self.fraction_of_carbon_in_manure = HolosVar(name="Fraction Of Carbon In Manure", value=None)

    def update_component_type(self, component_type: str):
        self.component_type.value = '.'.join((self.component_type.value, component_type))

    def get_animal_coefficient_data(self) -> AnimalCoefficientData:
        df = utils.read_holos_resource_table(
            path_file=PathsHolosResources.Table_22_Livestock_Coefficients_For_Sheep)
        df.set_index(df.pop("Sheep Class").apply(lambda x: convert_animal_type_name(name=x)), inplace=True)

        animal_type = convert_animal_type_name(name=self.group_name.value)
        lookup_type = AnimalType.ram if animal_type == AnimalType.sheep_feedlot else animal_type

        if lookup_type in df.index:
            _df = df.loc[lookup_type]
            res = AnimalCoefficientData(
                maintenance_coefficient=_df['cf'],
                coefficient_a=_df['a'],
                coefficient_b=_df['b'],
                initial_weight=_df['Initial Weight'],
                final_weight=_df['Final Weight'],
                wool_production=_df['Wool Production'])
        else:
            res = AnimalCoefficientData()
        return res


class Sheep(SheepBase):
    def __init__(
            self,
            name: str,
            animal_type: AnimalType,
            group_name: str,
            component_type: ComponentType,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,

            diet: Diet,
            housing_type: HousingType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            manure_handling_system: ManureStateType,

            start_weight: float = None,
            end_weight: float = None,

            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        super().__init__()

        # group_name = GroupNames.sheep_feedlot.value
        # animal_type: AnimalType = AnimalType.sheep_feedlot

        self.name.value = name
        self.update_component_type(component_type=component_type.to_str())
        self.group_name.value = group_name
        self.group_type.value = animal_type.value
        self.management_period_name.value = management_period_name
        self.group_pairing_number.value = group_pairing_number
        self.management_period_start_date.value = management_period_start_date.strftime(DATE_FMT)
        self.management_period_days.value = management_period_days
        self.number_of_animals.value = number_of_animals
        self.production_stage.value = production_stage.value
        self.number_of_young_animals.value = number_of_young_animals

        _animal_coefficient_data = self.get_animal_coefficient_data()

        self.maintenance_coefficient.value = _animal_coefficient_data.baseline_maintenance_coefficient
        self.start_weight.value = _animal_coefficient_data.initial_weight if start_weight is None else start_weight
        self.end_weight.value = _animal_coefficient_data.final_weight if end_weight is None else end_weight
        self.gain_coefficient_a.value = _animal_coefficient_data.coefficient_a
        self.gain_coefficient_b.value = _animal_coefficient_data.coefficient_b
        self.wool_production.value = _animal_coefficient_data.wool_production

        self.average_daily_gain.value = (self.end_weight.value - self.start_weight.value) / management_period_days

        self.diet_additive_type.value = diet_additive_type.value

        self.crude_protein.value = diet.crude_protein_percentage
        self.forage.value = diet.forage_percentage
        self.tdn.value = diet.total_digestible_nutrient_percentage
        self.ash_content_of_diet.value = diet.ash_percentage
        self.starch.value = diet.starch_percentage
        self.fat.value = diet.fat_percentage
        self.me.value = diet.metabolizable_energy
        self.ndf.value = diet.neutral_detergent_fiber_percentage

        self.activity_coefficient_of_feeding_situation.value = get_feeding_activity_coefficient(
            housing_type=housing_type)

        bedding = Bedding(
            housing_type=housing_type,
            bedding_material_type=bedding_material_type,
            animal_type=animal_type)

        self.user_defined_bedding_rate.value = bedding.user_defined_bedding_rate.value
        self.total_carbon_kilograms_dry_matter_for_bedding.value = bedding.total_carbon_kilograms_dry_matter_for_bedding.value
        self.total_nitrogen_kilograms_dry_matter_for_bedding.value = bedding.total_nitrogen_kilograms_dry_matter_for_bedding.value
        self.moisture_content_of_bedding_material.value = bedding.moisture_content_of_bedding_material.value

        self.methane_conversion_factor_of_manure.value = manure_emission_factors.MethaneConversionFactor
        self.n2o_direct_emission_factor.value = manure_emission_factors.N2ODirectEmissionFactor
        self.volatilization_fraction.value = manure_emission_factors.VolatilizationFraction
        self.emission_factor_volatilization.value = manure_emission_factors.EmissionFactorVolatilization
        self.fraction_leaching.value = manure_emission_factors.LeachingFraction
        self.emission_factor_leaching.value = manure_emission_factors.EmissionFactorLeach

        self.methane_conversion_factor_of_diet.value = diet.calc_methane_conversion_factor(animal_type=animal_type)
        self.methane_producing_capacity_of_manure.value = get_default_methane_producing_capacity_of_manure(
            is_pasture=housing_type.is_pasture(),
            animal_type=animal_type)

        self.manure_excretion_rate.value = get_manure_excretion_rate(animal_type=animal_type)
        self.fraction_of_carbon_in_manure.value = get_default_manure_composition_data(
            animal_type=animal_type,
            manure_state_type=manure_handling_system).carbon_content


class SheepFeedlot(Sheep):
    animal_type = AnimalType.sheep_feedlot
    def __init__(
            self,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,
            diet: Diet,
            housing_type: HousingType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            manure_handling_system: ManureStateType,
            start_weight: float = None,
            end_weight: float = None,
            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        _group_name = GroupNames.sheep_feedlot.value
        super().__init__(
            name=_group_name,
            animal_type=self.animal_type,
            group_name=_group_name,
            component_type=ComponentType.sheep_feedlot,

            **utils.get_local_args(locals())
        )


class Rams(Sheep):
    animal_type = AnimalType.ram
    def __init__(
            self,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,
            diet: Diet,
            housing_type: HousingType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            manure_handling_system: ManureStateType,
            start_weight: float = None,
            end_weight: float = None,
            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        _group_name = GroupNames.rams.value

        super().__init__(
            name=_group_name,
            animal_type=self.animal_type,
            group_name=_group_name,
            component_type=ComponentType.rams,

            **utils.get_local_args(locals())
        )


class Ewes(Sheep):
    animal_type = AnimalType.ewes

    def __init__(
            self,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,
            diet: Diet,
            housing_type: HousingType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            manure_handling_system: ManureStateType,
            start_weight: float = None,
            end_weight: float = None,
            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        super().__init__(
            name=GroupNames.lambs_and_ewes.value,
            animal_type=self.animal_type,
            group_name=GroupNames.ewes.value,
            component_type=ComponentType.ewes_and_lambs,

            **utils.get_local_args(locals())
        )


class Lambs(Sheep):
    animal_type = AnimalType.lambs

    def __init__(
            self,
            management_period_name: str,
            group_pairing_number: int,
            management_period_start_date: date,
            management_period_days: int,
            number_of_animals: int,
            production_stage: ProductionStage,
            number_of_young_animals: int,
            diet: Diet,
            housing_type: HousingType,
            manure_emission_factors: LivestockEmissionConversionFactorsData,
            manure_handling_system: ManureStateType,
            start_weight: float = None,
            end_weight: float = None,
            diet_additive_type: DietAdditiveType = DietAdditiveType.NONE,
            bedding_material_type: BeddingMaterialType = BeddingMaterialType.NONE,
    ):
        super().__init__(
            name=GroupNames.lambs_and_ewes.value,
            animal_type=self.animal_type,
            group_name=GroupNames.lambs.value,
            component_type=ComponentType.ewes_and_lambs,

            **utils.get_local_args(locals())
        )
