from enum import auto
from typing import ClassVar

from pandas import DataFrame
from pydantic import BaseModel, Field, NonNegativeFloat

from pyholos import utils
from pyholos.common import (ClimateZones, EnumGeneric, HolosVar, Region,
                            get_climate_zone, get_region)
from pyholos.common2 import CanadianProvince
from pyholos.components.common import (
    ComponentCategory,
    calculate_fraction_of_nitrogen_lost_by_leaching_and_runoff)
from pyholos.config import PathsHolosResources
from pyholos.defaults import Defaults
from pyholos.soil import SoilTexture
from pyholos.utils import AutoNameEnum, read_holos_resource_table


class DietAdditiveType(EnumGeneric):
    """Holos source code: https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Enumerations/DietAdditiveType.cs#L6

    """
    two_percent_fat: str = "TwoPercentFat"
    four_percent_fat: str = "FourPercentFat"
    five_percent_fat: str = "FivePercentFat"
    ionophore: str = "Inonophore"
    ionophore_plus_two_percent_fat: str = "InonophorePlusTwoPercentFat"
    ionophore_plus_four_percent_fat: str = "InonophorePlusFourPercentFat"
    ionophore_plus_five_percent_fat: str = "IonophorePlusFivePercentFat"
    custom: str = "Custom"
    NONE: str = "None"


class ProductionStage(EnumGeneric):
    gestating: str = "Gestating"
    """Animals that are pregnant.
    """

    lactating: str = "Lactating"
    """Animals that are lactating. Also known as farrowing in swine systems.
    """

    open: str = "Open"
    """Animals that are neither lactating or pregnant.
    """

    weaning: str = "Weaning"
    """Animals that have not been weaned yet.
    """

    growing_and_finishing: str = "GrowingAndFinishing"
    """Animals that have not been weaned yet.
    """

    breeding_stock: str = "BreedingStock"
    """Animals that are used for breeding (boars, bulls, etc.)
    """

    weaned: str = "Weaned"
    """Animals that have been weaned and are no longer milk fed.
    """


class AnimalType(EnumGeneric):
    not_selected: str = "NotSelected"
    alpacas: str = "Alpacas"
    beef_backgrounder: str = "BeefBackgrounder"
    beef_backgrounder_steer: str = "BeefBackgrounderSteer"
    beef_backgrounder_heifer: str = "BeefBackgrounderHeifer"
    beef_finishing_steer: str = "BeefFinishingSteer"
    beef_finishing_heifer: str = "BeefFinishingHeifer"
    beef: str = "Beef"
    beef_bulls: str = "BeefBulls"
    beef_calf: str = "BeefCalf"
    beef_cow_lactating: str = "BeefCowLactating"  # This also means 'regular' cows (i.e. non-lactating)
    beef_cow_dry: str = "BeefCowDry"
    beef_finisher: str = "BeefFinisher"  # /// Also known as buffalo
    bison: str = "Bison"
    swine_boar: str = "SwineBoar"
    broilers: str = "Broilers"
    chicken: str = "Chicken"
    cow_calf: str = "CowCalf"
    beef_cow: str = "BeefCow"
    calf: str = "Calf"
    dairy: str = "Dairy"
    dairy_bulls: str = "DairyBulls"
    dairy_dry_cow: str = "DairyDryCow"
    dairy_calves: str = "DairyCalves"
    dairy_heifers: str = "DairyHeifers"
    dairy_lactating_cow: str = "DairyLactatingCow"
    deer: str = "Deer"
    swine_dry_sow: str = "SwineDrySow"
    ducks: str = "Ducks"
    elk: str = "Elk"
    ewes: str = "Ewes"  # Assumption is all ewes are pregnant
    geese: str = "Geese"
    goats: str = "Goats"
    swine_grower: str = "SwineGrower"  # Also known as Hogs
    horses: str = "Horses"
    lambs: str = "Lambs"
    lambs_and_ewes: str = "LambsAndEwes"
    swine_lactating_sow: str = "SwineLactatingSow"
    layers_dry_poultry: str = "LayersDryPoultry"
    layers_wet_poultry: str = "LayersWetPoultry"
    llamas: str = "Llamas"
    mules: str = "Mules"
    other_livestock: str = "OtherLivestock"
    poultry: str = "Poultry"
    beef_replacement_heifers: str = "BeefReplacementHeifers"
    sheep: str = "Sheep"
    ram: str = "Ram"
    weaned_lamb: str = "WeanedLamb"
    sheep_feedlot: str = "SheepFeedlot"
    stockers: str = "Stockers"
    stocker_steers: str = "StockerSteers"
    stocker_heifers: str = "StockerHeifers"
    swine: str = "Swine"
    swine_starter: str = "SwineStarter"
    swine_finisher: str = "SwineFinisher"
    turkeys: str = "Turkeys"
    young_bulls: str = "YoungBulls"
    swine_gilts: str = "SwineGilts"  # Female pigs that have not farrowed a litter. Also known as maiden gilts.
    swine_sows: str = "SwineSows"
    swine_piglets: str = "SwinePiglets"
    chicken_pullets: str = "ChickenPullets"  # Juvenile female
    chicken_cockerels: str = "ChickenCockerels"  # Juvenile male
    chicken_roosters: str = "ChickenRoosters"  # Adult male
    chicken_hens: str = "ChickenHens"  # Adult female
    young_tom: str = "YoungTom"  # Juvenile male turkey
    tom: str = "Tom"  # Adult male turkey
    young_turkey_hen: str = "YoungTurkeyHen"  # Young female turkey
    turkey_hen: str = "TurkeyHen"  # Adult female turkey
    chicken_eggs: str = "ChickenEggs"
    turkey_eggs: str = "TurkeyEggs"
    chicks: str = "Chicks"  # Newly hatched chicken
    poults: str = "Poults"  # Newly hatched turkey
    cattle: str = "Cattle"
    layers: str = "Layers"

    def is_young_type(self):
        return self in {
            self.__class__.beef_calf,
            self.__class__.dairy_calves,
            self.__class__.swine_piglets,
            self.__class__.weaned_lamb,
            self.__class__.lambs
        }

    def is_beef_cattle_type(self):
        return self in {
            self.__class__.beef,
            self.__class__.beef_backgrounder,
            self.__class__.beef_bulls,
            self.__class__.beef_backgrounder_heifer,
            self.__class__.beef_finishing_steer,
            self.__class__.beef_finishing_heifer,
            self.__class__.beef_replacement_heifers,
            self.__class__.beef_finisher,
            self.__class__.beef_backgrounder_steer,
            self.__class__.beef_calf,
            self.__class__.stockers,
            self.__class__.stocker_heifers,
            self.__class__.stocker_steers,
            self.__class__.beef_cow_lactating,
            self.__class__.beef_cow,
            self.__class__.beef_cow_dry
        }

    def is_dairy_cattle_type(self):
        return self in {
            self.__class__.dairy,
            self.__class__.dairy_lactating_cow,
            self.__class__.dairy_bulls,
            self.__class__.dairy_calves,
            self.__class__.dairy_dry_cow,
            self.__class__.dairy_heifers
        }

    def is_swine_type(self):
        return self in {
            self.__class__.swine,
            self.__class__.swine_finisher,
            self.__class__.swine_starter,
            self.__class__.swine_lactating_sow,
            self.__class__.swine_dry_sow,
            self.__class__.swine_grower,
            self.__class__.swine_sows,
            self.__class__.swine_boar,
            self.__class__.swine_gilts,
            self.__class__.swine_piglets
        }

    def is_sheep_type(self):
        return self in {
            self.__class__.sheep,
            self.__class__.lambs_and_ewes,
            self.__class__.ram,
            self.__class__.weaned_lamb,
            self.__class__.lambs,
            self.__class__.ewes,
            self.__class__.sheep_feedlot
        }

    def is_poultry_type(self):
        return self in {
            self.__class__.poultry,
            self.__class__.layers_wet_poultry,
            self.__class__.layers_dry_poultry,
            self.__class__.layers,
            self.__class__.broilers,
            self.__class__.turkeys,
            self.__class__.ducks,
            self.__class__.geese,
            self.__class__.chicken_pullets,
            self.__class__.chicken_cockerels,
            self.__class__.chicken_roosters,
            self.__class__.chicken_hens,
            self.__class__.young_tom,
            self.__class__.tom,
            self.__class__.young_turkey_hen,
            self.__class__.turkey_hen,
            self.__class__.chicken_eggs,
            self.__class__.turkey_eggs,
            self.__class__.chicks,
            self.__class__.poults
        }

    def is_other_animal_type(self):
        return self in {
            self.__class__.other_livestock,
            self.__class__.goats,
            self.__class__.alpacas,
            self.__class__.deer,
            self.__class__.elk,
            self.__class__.llamas,
            self.__class__.horses,
            self.__class__.mules,
            self.__class__.bison
        }

    def is_chicken_type(self):
        return self in {
            self.__class__.chicken,
            self.__class__.chicken_hens,
            self.__class__.layers,
            self.__class__.broilers,
            self.__class__.chicken_roosters,
            self.__class__.chicken_pullets,
            self.__class__.chicken_cockerels,
            self.__class__.chicken_eggs,
            self.__class__.chicks
        }

    def is_turkey_type(self):
        return self in {
            self.__class__.turkey_hen,
            self.__class__.young_turkey_hen,
            self.__class__.tom,
            self.__class__.turkey_eggs,
            self.__class__.young_tom,
            self.__class__.poults
        }

    def is_layers_type(self):
        return self in {
            self.__class__.layers,
            self.__class__.layers_dry_poultry,
            self.__class__.layers_wet_poultry
        }

    def is_lactating_type(self):
        return self in {
            self.__class__.beef_cow_lactating,
            self.__class__.beef_cow,
            self.__class__.dairy_lactating_cow,
            self.__class__.ewes
        }

    def is_eggs(self):
        return self in {
            self.__class__.chicken_eggs,
            self.__class__.turkey_eggs
        }

    def is_newly_hatched_eggs(self):
        return self in {
            self.__class__.poults,
            self.__class__.chicks
        }

    def is_pregnant_type(self):
        return self in {
            self.__class__.beef_cow,
            self.__class__.beef_cow_lactating,
            self.__class__.dairy_lactating_cow,
            self.__class__.dairy_dry_cow,
            self.__class__.ewes
        }

    def get_category(self):
        if self.is_other_animal_type():
            res = self.other_livestock

        elif self.is_poultry_type():
            res = self.poultry

        elif self.is_sheep_type():
            res = self.sheep

        elif self.is_swine_type():
            res = self.swine

        elif self.is_dairy_cattle_type():
            res = self.dairy

        elif self.is_beef_cattle_type():
            res = self.beef

        else:
            res = self.not_selected

        return res

    def get_component_category_from_animal_type(self):
        if self.is_beef_cattle_type():
            res = ComponentCategory.BeefProduction
        elif self.is_dairy_cattle_type():
            res = ComponentCategory.Dairy
        elif self.is_swine_type():
            res = ComponentCategory.Swine
        elif self.is_poultry_type():
            res = ComponentCategory.Poultry
        elif self.is_sheep_type():
            res = ComponentCategory.Sheep
        else:
            res = ComponentCategory.OtherLivestock

        return res


def convert_animal_type_name(name: str) -> AnimalType:
    """Maps animal type name to its nearest AnimalType Enum.

    Holos source code:
        https://github.com/RamiALBASHA/Holos/blob/71638efd97c84c6ded45e342ce664477df6f803f/H.Core/Converters/AnimalTypeStringConverter.cs#L10

    Notes:
        lines followed by multiple '#' were modified from the original code
    """
    cleaned_input = name.lower().strip().replace(' ', '').replace('-', '')

    match cleaned_input:
        # Beef cattle
        case "backgrounding" | "backgrounder":
            return AnimalType.beef_backgrounder
        case "backgroundingsteers":
            return AnimalType.beef_backgrounder_steer
        case "backgroundingheifers":
            return AnimalType.beef_backgrounder_heifer
        case "beef" | "nondairycattle" | "beefcattle":
            return AnimalType.beef
        case "beeffinisher" | "finisher":
            return AnimalType.beef_finisher
        case "cowcalf":
            return AnimalType.cow_calf
        case "stockers":
            return AnimalType.stockers
        case "beefcalves" | "beefcalf":
            return AnimalType.beef_calf

        # Dairy
        case "dairy" | "dairycattle":
            return AnimalType.dairy
        case "dairybulls":
            return AnimalType.dairy_bulls
        case "dairydry" | "dairydrycow":
            return AnimalType.dairy_dry_cow
        case "dairyheifers":
            return AnimalType.dairy_heifers
        case "dairylactating":
            return AnimalType.dairy_lactating_cow

        # Swine
        case "boar" | "swineboar":
            return AnimalType.swine_boar
        case "weaners" | "piglets":
            return AnimalType.swine_piglets
        case "drysow":
            return AnimalType.swine_dry_sow
        case "sow" | "sows":
            return AnimalType.swine_sows
        case "grower" | "hogs" | "swinegrower":
            return AnimalType.swine_grower
        case "lactatingsow":
            return AnimalType.swine_lactating_sow
        case "swine":
            return AnimalType.swine
        case "swinefinisher":
            return AnimalType.swine_finisher

        # Sheep
        case "sheepfeedlot":
            return AnimalType.sheep_feedlot
        case "ewe" | "ewes":
            return AnimalType.ewes
        case "ram" | "rams":  ###################
            return AnimalType.ram
        case "sheep" | "sheepandlambs":
            return AnimalType.sheep
        case "weanedlambs" | "lambs":  ####################
            return AnimalType.lambs

        # Other livestock
        case "horse" | "horses":
            return AnimalType.horses
        case "goat" | "goats":
            return AnimalType.goats
        case "mules" | "mule":
            return AnimalType.mules
        case "bull":
            return AnimalType.beef_bulls
        case "llamas":
            return AnimalType.llamas
        case "alpacas":
            return AnimalType.alpacas
        case "deer":
            return AnimalType.deer
        case "elk":
            return AnimalType.elk
        case "bison":
            return AnimalType.bison

        # Poultry
        case "poultry":
            return AnimalType.poultry
        case "poultrypulletsbroilers" | "chickenbroilers" | "broilers":
            return AnimalType.broilers
        case "chickenpullets" | "pullets":
            return AnimalType.chicken_pullets
        case "chicken":
            return AnimalType.chicken
        case "chickencockerels" | "cockerels":
            return AnimalType.chicken_cockerels
        case "roasters" | "roosters" | "chickenroosters":  ####################
            return AnimalType.chicken_roosters
        case "hens":
            return AnimalType.chicken_hens
        case "poultryturkeys" | "turkey" | "ducks":
            return AnimalType.ducks
        case "geese":
            return AnimalType.geese
        case "turkeys":
            return AnimalType.turkeys
        case "layersdry" | "layersdrypoultry":  ################
            return AnimalType.layers_dry_poultry
        case "layerswet" | "layerswetpoultry":  ################
            return AnimalType.layers_wet_poultry
        case "poultrylayers" | "chickenlayers" | "layers":
            return AnimalType.layers
        case _:
            # raise ValueError(f"unknown animal type. Returning {AnimalType.beef_backgrounder}")
            return AnimalType.beef_backgrounder


class ManureAnimalSourceTypes(AutoNameEnum):
    """
    Holos source type:
        https://github.com/holos-aafc/Holos/blob/c06f6619907fba89c3ddc29b4239a903a8c20a7a/H.Core/Enumerations/ManureAnimalSourceTypes.cs#L9
    """
    NotSelected = auto()
    BeefManure = auto()
    DairyManure = auto()
    SwineManure = auto()
    PoultryManure = auto()
    SheepManure = auto()
    OtherLivestockManure = auto()


class ManureLocationSourceType(AutoNameEnum):
    NotSelected = auto()
    Livestock = auto()
    Imported = auto()
    OnFarmAnaerobicDigestor = auto()


class Milk(BaseModel):
    """Milk production data

    Args:
        production: (kg) average milk production value based on the province and year specified by user
        fat_content: (%) fat content of milk
        protein_content_as_percentage: (%) protein content of milk

    Notes:
        arg 'protein_content_as_percentage' is deprecated and will be removed in future version.
    """
    production: float = 0
    fat_content: float = 4
    protein_content_as_percentage: float = 3.5


class Diet(BaseModel):
    specs: ClassVar = Field(NonNegativeFloat, ge=0, le=100)
    """Diet composition data

        Args:
            crude_protein_percentage: (-) percentage of crude protein in the diet dry matter (between 0 and 100)
            forage_percentage: (-) percentage of forage in the diet dry matter (between 0 and 100)
            total_digestible_nutrient_percentage: (-) percentage of total digestible nutrient in the diet dry matter (between 0 and 100)
            ash_percentage: (-) percentage of ash in the diet dry matter (between 0 and 100)
            starch_percentage: (-) percentage of starch in the diet dry matter (between 0 and 100)
            fat_percentage: (-) percentage of fat in the diet dry matter (between 0 and 100)
            neutral_detergent_fiber_percentage: (-) percentage of neutral detergent fiber in the diet dry matter (between 0 and 100)
            metabolizable_energy: (Mcal kg-1) metabolizable energy of the diet
        """
    crude_protein_percentage: NonNegativeFloat
    forage_percentage: NonNegativeFloat
    total_digestible_nutrient_percentage: NonNegativeFloat
    ash_percentage: NonNegativeFloat
    starch_percentage: NonNegativeFloat
    fat_percentage: NonNegativeFloat
    neutral_detergent_fiber_percentage: NonNegativeFloat
    metabolizable_energy: NonNegativeFloat

    # dietary_net_energy_concentration: float

    @staticmethod
    def calc_dietary_net_energy_concentration(
            net_energy_for_maintenance: float,
            net_energy_for_growth: float
    ) -> float:
        """Calculates the dietary net energy concentration

        Args:
            net_energy_for_maintenance: (Mcal/kg DM) net energy for maintenance
            net_energy_for_growth: (Mcal/kg DM) net energy for growth

        Returns:
            (MJ/kg DM): dietary net energy concentration

        Notes:
            NEmf (MJ/kg DM) = [NEma (Mcal/kg DM) + NEga (Mcal/kg DM)] * 4.184 (conversion factor for Mcal to MJ)

        References:
            Holos source code https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Feed/FeedIngredient.cs#L1319

        """
        return (net_energy_for_maintenance + net_energy_for_growth) * 4.184

    def calc_dietary_net_energy_concentration_for_beef(self) -> float:
        """Calculates the dietary net energy concentration of a beef cattle diet as a function of the metabolizable energy.

        Returns:
            (MJ (kg DM)^-1) dietary net energy concentration

        Notes:
            This relationship is deduced from the dairy cattle feed composition table provided in the Holos source code
            'https://github.com/holos-aafc/Holos/blob/main/H.Content/Resources/dairy_feed_composition.csv

        """
        return self.calc_dietary_net_energy_concentration(
            net_energy_for_maintenance=self.metabolizable_energy * 0.8756 - 0.5972,
            net_energy_for_growth=self.metabolizable_energy * 0.7632 - 0.9276)

    def calc_dietary_net_energy_concentration_for_dairy(self) -> float:
        """Calculates the dietary net energy concentration of a dairy cattle diet as a function of the metabolizable energy.

        Returns:
            (MJ (kg DM)^-1) dietary net energy concentration

        Notes:
            This relationship is deduced from the feed composition table provided in the Holos source code
            https://github.com/holos-aafc/Holos/blob/main/H.Content/Resources/feeds.csv

        """
        return self.calc_dietary_net_energy_concentration(
            net_energy_for_maintenance=self.metabolizable_energy * 0.8134 - 0.3518,
            net_energy_for_growth=self.metabolizable_energy * 0.6299 - 0.5162)

    def calc_methane_conversion_factor_for_beef_and_dairy_cattle(
            self,
            animal_type: AnimalType
    ) -> float:
        """Calculates the methane conversion factor based on the animal type.

        Args:
            animal_type: AnimalType class instance

        Returns:
            (kg CH4 kg CH4-1) methane conversion factor for diet (Y_m)

        Holos Source Code:
            https://github.com/holos-aafc/Holos/blob/2bc9704a51449a8ffd4005462a6a7e6fb8a27f2d/H.Core/Providers/Feed/Diet.cs#L602
        """
        # Assign a default ym so that if there are no cases that cover the diet below, there will be a value assigned
        result = 0.4
        total_digestible_nutrient = self.total_digestible_nutrient_percentage

        if animal_type.is_dairy_cattle_type():
            if total_digestible_nutrient >= 65:
                result = 0.063
            elif 55 <= total_digestible_nutrient < 65:
                result = 0.065
            else:
                result = 0.07

        if animal_type.is_beef_cattle_type():
            if total_digestible_nutrient >= 65:
                result = 0.065
            elif 55 <= total_digestible_nutrient < 65:
                result = 0.07
            else:
                result = 0.08

        if animal_type == AnimalType.beef_finisher:
            if total_digestible_nutrient >= 82:
                result = 0.03
            else:
                result = 0.04
            # The percentage threshold value of 82 is the rounded value of TDN for the basic diet CornGrainBasedDiet.
            # This TDN value is the weighted average of the TDN values of all three ingredients of this diet, i.e.
            # BarleySilage (% TDN = 60.6, % DM in diet=10) and BarleyGrain  (% TDN = 84.1, % DM in diet=90)
            # The original code for this part of the function in commented below.
            # if (string.IsNullOrWhiteSpace(this.Name) == false)
            # {
            #     if (this.Name.Equals(Resources.LabelCornGrainBasedDiet))
            #     {
            #         result = 0.03;
            #     }
            #
            #     if (this.Name.Equals(Resources.LabelBarleyGrainBasedDiet))
            #     {
            #         result = 0.04;
            #
            #     }
            # }

        return result

    @staticmethod
    def calc_methane_conversion_factor_for_sheep() -> float:
        """Returns the methane conversion factor for sheep irrespective of feed quality values

        Returns:
            (kg CH4 kg CH4-1) methane conversion factor for diet (Y_m)

        Holos Source Code:
            https://github.com/holos-aafc/Holos/blob/2bc9704a51449a8ffd4005462a6a7e6fb8a27f2d/H.Content/Resources/Table_18_26_Diet_Coefficients_For_Beef_Dairy_Sheep.csv#L33

        """
        return 0.067

    def calc_methane_conversion_factor(
            self,
            animal_type: AnimalType
    ) -> float:
        """Calculates the methane conversion factor based on the animal type.

        Args:
            animal_type: AnimalType class instance

        Returns:
            (kg CH4 kg CH4-1) methane conversion factor for diet (Y_m)
        """
        if animal_type.is_beef_cattle_type() or animal_type.is_dairy_cattle_type():
            res = self.calc_methane_conversion_factor_for_beef_and_dairy_cattle(animal_type=animal_type)
        elif animal_type.is_sheep_type():
            res = self.calc_methane_conversion_factor_for_sheep()
        else:
            res = None

        return res


class HousingType(EnumGeneric):
    not_selected: str = "NotSelected"
    confined_no_barn: str = "ConfinedNoBarn"
    """Also known as 'Confined no barn (feedlot)'
    """
    housed_in_barn: str = "HousedInBarn"
    housed_ewes: str = "HousedEwes"
    housed_in_barn_solid: str = "HousedInBarnSolid"
    housed_in_barn_slurry: str = "HousedInBarnSlurry"
    enclosed_pasture: str = "EnclosedPasture"
    open_range_or_hills: str = "OpenRangeOrHills"
    tie_stall: str = "TieStall"
    small_free_stall: str = "SmallFreeStall"
    large_free_stall: str = "LargeFreeStall"
    grazing_under3km: str = "GrazingUnder3km"
    grazing_over3km: str = "GrazingOver3km"
    confined: str = "Confined"
    flat_pasture: str = "FlatPasture"
    hilly_pasture_or_open_range: str = "HillyPastureOrOpenRange"
    pasture: str = "Pasture"
    """Pasture, range, or paddock
    """
    dry_lot: str = "DryLot"
    """Also known as 'Standing or exercise yard'
    """
    swath_grazing: str = "SwathGrazing"
    custom: str = "Custom"
    free_stall_barn_solid_litter: str = "FreeStallBarnSolidLitter"
    free_stall_barn_slurry_scraping: str = "FreeStallBarnSlurryScraping"
    free_stall_barn_flushing: str = "FreeStallBarnFlushing"
    free_stall_barn_milk_parlour_slurry_flushing: str = "FreeStallBarnMilkParlourSlurryFlushing"
    """Also known as 'Milking parlour (slurry - flushing)'
    """
    tie_stall_solid_litter: str = "TieStallSolidLitter"
    """Also known as 'Tie-stall barn (solid)'
    """
    tie_stall_slurry: str = "TieStallSlurry"
    """Also known as 'Tie-stall barn (slurry)'
    """

    # This section corresponds to the HousingTypeExtensions class in the original holos source code
    # https://github.com/holos-aafc/Holos/blob/53f778f9bd4579d164de10f5b04db34d020b96a9/H.Core/Enumerations/HousingTypeExtensions.cs#L10

    def is_free_stall(self):
        return self in {
            self.__class__.small_free_stall,
            self.__class__.large_free_stall,
            self.__class__.free_stall_barn_flushing,
            self.__class__.free_stall_barn_milk_parlour_slurry_flushing,
            self.__class__.free_stall_barn_slurry_scraping,
            self.__class__.free_stall_barn_solid_litter
        }

    def is_tie_stall(self):
        return self in {
            self.__class__.tie_stall,
            self.__class__.tie_stall_slurry,
            self.__class__.tie_stall_solid_litter
        }

    def is_barn(self):
        return self in {
            self.__class__.housed_in_barn,
            self.__class__.housed_in_barn_slurry,
            self.__class__.housed_in_barn_solid
        }

    def is_feed_lot(self):
        return self in {
            self.__class__.confined,
            self.__class__.confined_no_barn
        }

    def is_electrical_consuming_housing_type(self):
        return any([
            self.is_free_stall(),
            self.is_barn(),
            self.is_tie_stall(),
            self.is_feed_lot()])

    def is_indoor_housing(self):
        return self in {
            self.__class__.housed_in_barn,
            self.__class__.housed_in_barn_slurry,
            self.__class__.housed_in_barn_solid,
            self.__class__.free_stall_barn_flushing,
            self.__class__.free_stall_barn_solid_litter,
            self.__class__.free_stall_barn_slurry_scraping,
            self.__class__.free_stall_barn_milk_parlour_slurry_flushing
        }

    def is_pasture(self):
        return self in {
            self.__class__.pasture,
            self.__class__.enclosed_pasture,
            self.__class__.flat_pasture,
            self.__class__.grazing_over3km,
            self.__class__.grazing_under3km,
            self.__class__.hilly_pasture_or_open_range,
            self.__class__.open_range_or_hills,
            self.__class__.swath_grazing
        }


class BeddingMaterialType(EnumGeneric):
    straw: str = 'Straw'
    wood_chip: str = 'WoodChip'
    separated_manure_solid: str = 'SeparatedManureSolid'
    sand: str = 'Sand'
    straw_long: str = 'StrawLong'
    straw_chopped: str = 'StrawChopped'
    shavings: str = 'Shavings'
    sawdust: str = 'Sawdust'
    paper_products: str = 'PaperProducts'
    peat: str = 'Peat'
    hemp: str = 'Hemp'
    NONE = None


class Bedding:
    def __init__(
            self,
            housing_type: HousingType,
            bedding_material_type: BeddingMaterialType | None,
            animal_type: AnimalType,
            total_carbon_kilograms_dry_matter_for_bedding: float = None,
            total_nitrogen_kilograms_dry_matter_for_bedding: float = None,
            moisture_content_of_bedding_material: float = None
    ):
        default_bedding_material_composition = self.get_bedding_material_composition(
            bedding_material_type=bedding_material_type,
            animal_type=animal_type)

        if total_carbon_kilograms_dry_matter_for_bedding is None:
            total_carbon_kilograms_dry_matter_for_bedding = default_bedding_material_composition[
                'TotalCarbonKilogramsDryMatter']
        if total_nitrogen_kilograms_dry_matter_for_bedding is None:
            total_nitrogen_kilograms_dry_matter_for_bedding = default_bedding_material_composition[
                'TotalNitrogenKilogramsDryMatter']
        if moisture_content_of_bedding_material is None:
            moisture_content_of_bedding_material = default_bedding_material_composition['MoistureContent']

        self.user_defined_bedding_rate = HolosVar(
            name='User Defined Bedding Rate',
            value=self.get_default_bedding_rate(
                housing_type=housing_type,
                bedding_material_type=bedding_material_type,
                animal_type=animal_type))
        self.total_carbon_kilograms_dry_matter_for_bedding = HolosVar(
            name='Total Carbon Kilograms Dry Matter For Bedding',
            value=total_carbon_kilograms_dry_matter_for_bedding)
        self.total_nitrogen_kilograms_dry_matter_for_bedding = HolosVar(
            name='Total Nitrogen Kilograms Dry Matter For Bedding',
            value=total_nitrogen_kilograms_dry_matter_for_bedding)
        self.moisture_content_of_bedding_material = HolosVar(
            name='Moisture Content Of Bedding Material',
            value=moisture_content_of_bedding_material)

    @staticmethod
    def get_default_bedding_rate(
            housing_type: HousingType,
            bedding_material_type: BeddingMaterialType,
            animal_type: AnimalType
    ) -> int | float:
        # https://github.com/holos-aafc/Holos/blob/53f778f9bd4579d164de10f5b04db34d020b96a9/H.Core/Providers/Animals/Table_30_Default_Bedding_Material_Composition_Provider.cs#L301

        if housing_type.is_pasture():
            return 0

        if animal_type.is_young_type():
            return 0

        if animal_type.is_beef_cattle_type():
            if bedding_material_type == BeddingMaterialType.straw:
                if housing_type.is_feed_lot():
                    return 1.5

                if housing_type.is_barn():
                    return 3.5

            if bedding_material_type == BeddingMaterialType.wood_chip:
                if housing_type.is_feed_lot():
                    return 3.6

                if housing_type.is_barn():
                    return 5.0

        if animal_type.is_dairy_cattle_type():
            # Currently, all housing types have same rates for bedding types
            if any([
                housing_type.is_tie_stall(),
                housing_type.is_free_stall(),
                housing_type == HousingType.dry_lot]):
                if bedding_material_type == BeddingMaterialType.sand:
                    return 24.3

                if bedding_material_type == BeddingMaterialType.separated_manure_solid:
                    return 0

                if bedding_material_type == BeddingMaterialType.straw_long:
                    return 0.7

                if bedding_material_type == BeddingMaterialType.straw_chopped:
                    return 0.7

                if bedding_material_type == BeddingMaterialType.shavings:
                    return 2.1

                if bedding_material_type == BeddingMaterialType.sawdust:
                    return 2.1

        # Footnote 8 for sheep value reference.
        if animal_type.is_sheep_type():
            return 0.57

        if animal_type.is_swine_type():
            if bedding_material_type == BeddingMaterialType.straw_long:
                return 0.70
            else:
                return 0.79

        if animal_type.is_poultry_type():
            if any([
                bedding_material_type == BeddingMaterialType.sawdust,
                bedding_material_type == BeddingMaterialType.straw,
                bedding_material_type == BeddingMaterialType.shavings]):
                if animal_type == AnimalType.broilers:
                    return 0.0014

                if animal_type == AnimalType.chicken_pullets:
                    return 0.0014

                if any([
                    animal_type == AnimalType.layers,
                    animal_type == AnimalType.chicken_hens]):
                    return 0.0028

                if animal_type.is_turkey_type():
                    return 0.011

                else:
                    return 0
            else:
                return 0

        if animal_type.is_other_animal_type():
            # Footnote 11 for Other livestock value reference
            match animal_type:
                case AnimalType.llamas:
                    return 0.57

                case AnimalType.alpacas:
                    return 0.57

                case AnimalType.deer:
                    return 1.5

                case AnimalType.elk:
                    return 1.5

                case AnimalType.goats:
                    return 0.57

                case AnimalType.horses:
                    return 1.5

                case AnimalType.mules:
                    return 1.5

                case AnimalType.bison:
                    return 1.5

                # added here since the original case statement in C# does not cover all possibilities
                case _:
                    return 1
        else:
            return 1

        pass

    @staticmethod
    def get_bedding_material_composition(
            bedding_material_type: BeddingMaterialType,
            animal_type: AnimalType
    ) -> dict:
        if animal_type.is_beef_cattle_type():
            animal_lookup_type = AnimalType.beef
        elif animal_type.is_dairy_cattle_type():
            animal_lookup_type = AnimalType.dairy
        elif animal_type.is_sheep_type():
            animal_lookup_type = AnimalType.sheep
        elif animal_type.is_swine_type():
            animal_lookup_type = AnimalType.swine
        elif animal_type.is_poultry_type():
            animal_lookup_type = AnimalType.poultry
        else:
            # Other animals have a value for animal group (Horses, Goats, etc.)
            animal_lookup_type = animal_type

        df = HolosTables.Table_30_Default_Bedding_Material_Composition_Provider

        result = df[
            (df['BeddingMaterial'] == bedding_material_type.value) &
            (df['AnimalType'] == animal_lookup_type.value)]

        if not result.empty:
            return result.iloc[0].to_dict()
        else:
            # Trace.TraceError($"{nameof(Farm)}.{nameof(GetBeddingMaterialComposition)}: unable to return bedding material data for {animalType.GetDescription()}, and {beddingMaterialType.GetHashCode()}. Returning default value of 1.");

            # return new Table_30_Default_Bedding_Material_Composition_Data();
            return {k: None for k in result.columns}


class AnimalCoefficientData:
    def __init__(
            self,
            baseline_maintenance_coefficient: float = 0,
            gain_coefficient: float = 0,
            default_initial_weight: float = 0,
            default_final_weight: float = 0
    ):
        """Table 16. Livestock coefficients for beef cattle and dairy cattle.

        Args:
            baseline_maintenance_coefficient: (MJ d-1 kg-1) baseline maintenance coefficient (C_f)
            gain_coefficient: (dimensionless?) gain coefficient (C_d)
            default_initial_weight: (kg) initial weight
            default_final_weight: (kg) final weight
        """
        self.baseline_maintenance_coefficient = baseline_maintenance_coefficient
        self.gain_coefficient = gain_coefficient
        self.default_initial_weight = default_initial_weight
        self.default_final_weight = default_final_weight


def get_methane_producing_capacity_of_manure(
        animal_type: AnimalType
) -> float:
    """Returns the default methane producing capacity of manure as a function of the animal type

    Args:
        animal_type: animal type object

    Returns:
        (m^3 CH4 kg^-1 VS): Methane producing capacity of manure (B_o)

    References:
        https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_35_Methane_Producing_Capacity_Default_Values_Provider.cs#L15

    """
    # Table 35. Default values for maximum methane producing capacity (Bo).
    # <para>Source: IPCC (2019), Table 10.16</para>
    # Footnote 3 : For Methane producing capacity (B0) value reference.

    if animal_type.is_beef_cattle_type():
        res = 0.19

    elif animal_type.is_dairy_cattle_type():
        res = 0.24

    elif animal_type.is_swine_type():
        res = 0.48

    elif animal_type.is_sheep_type():
        res = 0.19

    elif any([
        animal_type == AnimalType.chicken_roosters,
        animal_type == AnimalType.broilers
    ]):
        # Used for broilers from algorithm document
        res = 0.36

    elif any((
            animal_type == AnimalType.chicken_hens,
            animal_type == AnimalType.chicken_pullets,
            animal_type == AnimalType.chicken_cockerels,
            animal_type == AnimalType.layers
    )):
        # Used for layers (wet/dry) from algorithm document
        res = 0.39

    elif animal_type == AnimalType.goats:
        res = 0.18

    elif animal_type == AnimalType.horses:
        res = 0.30

    elif animal_type == AnimalType.mules:
        res = 0.33

    # Footnote 2
    elif any((
            animal_type == AnimalType.llamas,
            animal_type == AnimalType.alpacas
    )):
        res = 0.19

    # Footnote 1
    elif animal_type == AnimalType.bison:
        res = 0.10

    else:
        res = 0

    # Footnote 1: Value for non-dairy cattle used
    # Footnote 2: Value for sheep used
    # Footnote 3: For all animals on pasture, range or paddock, the Bo should be set to 0.19

    return res


def get_default_methane_producing_capacity_of_manure(
        is_pasture: bool,
        animal_type: AnimalType
) -> float:
    """Returns the default methane producing capacity of manure.

    Args:
        is_pasture: True if the housing type is pasture, otherwise False
        animal_type: animal type class

    Returns:
        (m^3 CH4 kg^-1 VS): Methane producing capacity of manure (B_o)

    Notes:
        When housed on pasture, this value should be set to a constant.
        See table 38 "Default values (in Holos source code) for maximum methane producing capacity (Bo)" footnote 3.

    References:
        https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Services/Initialization/Animals/AnimalInitializationService.Methane.cs#L89
    """
    return 0.19 if is_pasture else get_methane_producing_capacity_of_manure(animal_type=animal_type)


class FractionOfOrganicNitrogenMineralizedData:
    def __init__(
            self,
            fraction_immobilized: float = 0,
            fraction_mineralized: float = 0,
            fraction_nitrified: float = 0,
            fraction_denitrified: float = 0,
            n2o_n: float = 0,
            no_n: float = 0,
            n2_n: float = 0,
            n_leached: float = 0,
    ):
        """Mineralization of organic N (fecal N and bedding N)

        Args:
            fraction_mineralized: (dimensionless) fraction of nitrogen mineralized
            fraction_immobilized: (dimensionless) fraction of nitrogen immobilized
            fraction_nitrified: (dimensionless) fraction of nitrogen nitrified
            fraction_denitrified: (dimensionless) fraction of nitrogen denitrified
            n2o_n:
            no_n:
            n2_n:
            n_leached:
        """
        self.fraction_mineralized = fraction_mineralized
        self.fraction_immobilized = fraction_immobilized
        self.fraction_nitrified = fraction_nitrified
        self.fraction_denitrified = fraction_denitrified
        self.n2o_n = n2o_n
        self.no_n = no_n
        self.n2_n = n2_n
        self.n_leached = n_leached

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ if isinstance(other, self.__class__) else False


class ManureStateType(EnumGeneric):
    not_selected: str = "NotSelected"
    anaerobic_digester: str = "AnaerobicDigester"
    composted: str = "Composted"
    compost_intensive: str = "CompostIntensive"  # Also known as 'compost - intensive windrow'
    compost_passive: str = "CompostPassive"  # Also known as 'compost - passive windrow'
    daily_spread: str = "DailySpread"
    deep_bedding: str = "DeepBedding"
    deep_pit: str = "DeepPit"  # Also known as 'Deep pit under barn'
    liquid: str = "Liquid"
    liquid_crust: str = "LiquidCrust"  # [Obsolete]
    liquid_separated: str = "LiquidSeparated"  # [Obsolete]
    liquid_no_crust: str = "LiquidNoCrust"  # Also known as 'Liquid/Slurry with no natural crust'
    pasture: str = "Pasture"
    range: str = "Range"
    paddock: str = "Paddock"
    solid: str = "Solid"
    slurry: str = "Slurry"  # [Obsolete]
    slurry_with_natural_crust: str = "SlurryWithNaturalCrust"  # [Obsolete]
    slurry_without_natural_crust: str = "SlurryWithoutNaturalCrust"  # [Obsolete]
    solid_storage: str = "SolidStorage"  # Also known as 'Solid storage (stockpiled)'
    custom: str = "Custom"
    pit_lagoon_no_cover: str = "PitLagoonNoCover"  # [Obsolete]
    liquid_with_natural_crust: str = "LiquidWithNaturalCrust"  # Also known as 'Liquid/Slurry with natural crust'
    liquid_with_solid_cover: str = "LiquidWithSolidCover"  # Also known as Liquid/Slurry with solid cover
    composted_in_vessel: str = "CompostedInVessel"  # (Swine system)
    solid_storage_with_or_without_litter: str = "SolidStorageWithOrWithoutLitter"  # (Poultry system) No different than 'Solid Storage' but poultry solid storage needs the term 'litter' which is incorrect to use in the case of cattle 'Solid Storage' since there is no 'litter' only 'bedding' when considering the cattle system

    # These methods correspond to the ManureStateTypeExtensions
    # https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Enumerations/ManureStateTypeExtensions.cs#L9
    def is_grazing_area(self) -> bool:
        return self in {
            self.__class__.paddock,
            self.__class__.range,
            self.__class__.pasture
        }

    def is_liquid_manure(self) -> bool:
        """Indicates if the storage type being used houses liquid manure.

        Returns:
            True if the storage type is for liquid manure, False otherwise
        """
        return self in {
            self.__class__.liquid_no_crust,
            self.__class__.liquid_with_natural_crust,
            self.__class__.liquid_with_solid_cover,
            self.__class__.deep_pit
        }

    def is_compost(self) -> bool:
        return self in {
            self.__class__.compost_intensive,
            self.__class__.compost_passive,
            self.__class__.composted
        }

    def is_solid_manure(self) -> bool:
        """Indicates if the storage type being used houses solid manure.

        Returns:
            True if the storage type is for solid manure, False otherwise
        """
        return not self.is_liquid_manure()

    def is_covered_system(self) -> bool:
        # Dairy manure systems can be covered with a lid/cap etc.
        return self in {
            self.__class__.liquid_with_natural_crust,
            self.__class__.liquid_with_solid_cover
        }


def get_fraction_of_organic_nitrogen_mineralized_data(
        state_type: ManureStateType,
        animal_type: AnimalType,
        fraction_of_tan_in_liquid_manure_storage_system: float = 1
) -> FractionOfOrganicNitrogenMineralizedData:
    """Table 44. Fraction of organic N mineralized as TAN and the fraction of TAN immobilized to organic N and nitrified
    and denitrified during solid and liquid manure storage for beef and dairy cattle (based on TAN content)
    (Chai et al., 2014,2016).

    Args:
        state_type: manure handling system type
        animal_type: animal type
        fraction_of_tan_in_liquid_manure_storage_system: (-) fraction of excreted N in animal urine (cf. Note 4)

    Returns:


    Notes:
        1. Mineralization of organic N (fecal N and bedding N)
        2. Solid manure composted for ≥ 10 months; data from Chai et al. (2014); these values are used for compost passive and compost intensive beef and dairy cattle manure
        3. Solid manure stockpiled for ≥ 4 months; data from Chai et al. (2014); these values are also used for deep bedding beef and dairy cattle manure
        4. FracurinaryN is the fraction of TAN in the liquid manure storage system (includes liquid/slurry with natural crust, liquid/slurry with no natural crust, liquid/slurry with solid cover and deep pit under barn).
        5. Nitrification of TAN in liquid manure with natural crust (formed from manure, bedding, or waste forage) was considered since the natural crust can be assumed as similar to solid manure (stockpile) in terms of being aerobic. The N2O-N emission factor for liquid manure with a natural crust is 0.005 of total N IPCC (2006), which can be expressed as the TAN based EFs
        6. Nitrification of TAN in liquid manure with no natural crust is assumed to be zero because of anaerobic conditions
        7. All nitrified TAN (nitrate-N) was assumed to be denitrified (no leaching, runoff) in liquid systems.
    """
    if animal_type.is_beef_cattle_type():
        # FracMineralized = Note 1.
        match state_type:
            # // Solid-compost - beef
            # // Note 2
            case ManureStateType.compost_intensive | ManureStateType.compost_passive:
                return FractionOfOrganicNitrogenMineralizedData(
                    fraction_immobilized=0,
                    fraction_mineralized=0.46,
                    fraction_nitrified=0.25,
                    fraction_denitrified=0,
                    n2o_n=0.033,
                    no_n=0.0033,
                    n2_n=0.099,
                    n_leached=0.0575)

            # // Solid-stockpiled - beef
            # // Note 3
            case ManureStateType.deep_bedding | ManureStateType.solid_storage:
                return FractionOfOrganicNitrogenMineralizedData(
                    fraction_immobilized=0,
                    fraction_mineralized=0.28,
                    fraction_nitrified=0.125,
                    fraction_denitrified=0,
                    n2o_n=0.033,
                    no_n=0.0033,
                    n2_n=0.099,
                    n_leached=0.0575
                )
    elif animal_type.is_dairy_cattle_type():
        match state_type:
            # // Solid-compost - dairy
            # // Note 2
            case ManureStateType.compost_intensive | ManureStateType.compost_passive:
                return FractionOfOrganicNitrogenMineralizedData(
                    fraction_immobilized=0,
                    fraction_mineralized=0.46,
                    fraction_nitrified=0.282,
                    fraction_denitrified=0.152,
                    n2o_n=0.037,
                    no_n=0.0037,
                    n2_n=0.111,
                    n_leached=0.13)

            # // Solid-stockpiled - dairy
            # // Note 3
            case ManureStateType.deep_bedding | ManureStateType.solid_storage:
                return FractionOfOrganicNitrogenMineralizedData(
                    fraction_immobilized=0,
                    fraction_mineralized=0.28,
                    fraction_nitrified=0.141,
                    fraction_denitrified=0.076,
                    n2o_n=0.0185,
                    no_n=0.0019,
                    n2_n=0.0555,
                    n_leached=0.065)

    # // Liquid systems for both beef and dairy
    match state_type:
        # // Liquid with natural crust
        # // Note 5, 7
        case ManureStateType.liquid_with_natural_crust | ManureStateType.liquid_with_solid_cover | ManureStateType.deep_pit:
            return FractionOfOrganicNitrogenMineralizedData(
                fraction_immobilized=0,
                fraction_mineralized=0.1,
                fraction_nitrified=0.021 / min(1., fraction_of_tan_in_liquid_manure_storage_system),
                fraction_denitrified=0.021 / min(1., fraction_of_tan_in_liquid_manure_storage_system),
                n2o_n=0.005 / min(1., fraction_of_tan_in_liquid_manure_storage_system),
                no_n=0.0005 / min(1., fraction_of_tan_in_liquid_manure_storage_system),
                n2_n=0.015 / min(1., fraction_of_tan_in_liquid_manure_storage_system),
                n_leached=0)

        # // Liquid without natural crust
        # // Note 6, 7
        case ManureStateType.liquid_no_crust:
            return FractionOfOrganicNitrogenMineralizedData(
                fraction_immobilized=0,
                fraction_mineralized=0.1,
                fraction_nitrified=0.0,
                fraction_denitrified=0,
                n2o_n=0,
                no_n=0,
                n2_n=0,
                n_leached=0
            )

    return FractionOfOrganicNitrogenMineralizedData()


def get_ammonia_emission_factor_for_storage_of_poultry_manure(
        animal_type: AnimalType
) -> float:
    """Returns the default ammonia emission factor for housing manure of Poultry-type animals.

    Args:
        animal_type: animal type object

    Returns:
        (kg NH3-N kg^-1 TAN): default ammonia emission factor for housing

    References:
        Holos source code: https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/DefaultAmmoniaEmissionFactorsForPoultryManureStorageProvider.cs#L7

    """
    if animal_type.is_chicken_type():
        if any((
                animal_type == AnimalType.chicken_hens,
                animal_type == AnimalType.layers)):
            res = 0.24
        else:
            res = 0.25
    else:
        # Turkeys
        res = 0.24

    return res


def get_ammonia_emission_factor_for_storage_of_beef_and_dairy_cattle_manure(
        storage_type: ManureStateType
) -> float:
    """Returns the default ammonia emission factor for housing of beef and dairy cattle manure.

    Args:
        storage_type: manure handling system type

    Returns:
        (kg NH3-N kg^-1 TAN): default ammonia emission factor for housing

    References:
        Holos source code: https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_43_Beef_Dairy_Default_Emission_Factors_Provider.cs#L77

    """
    # Footnote 1: Read for data reference information.

    if any((
            storage_type.is_liquid_manure(),
            storage_type == ManureStateType.deep_pit
    )):
        res = 0.13

    elif storage_type.is_compost():
        res = 0.7

    elif any((
            storage_type == ManureStateType.solid_storage,
            storage_type == ManureStateType.deep_bedding)):
        res = 0.35

    else:
        res = 0

    return res


def get_emission_factor_for_volatilization_based_on_climate(
        mean_annual_precipitation: float,
        mean_annual_potential_evapotranspiration: float
) -> float:
    """Returns emission factor for volatilization (EF_volatilization)

    Args:
        mean_annual_precipitation: (mm) mean annual precipitation
        mean_annual_potential_evapotranspiration: (mm) mean annual potential evapotranspiration

    Returns:
        (kg(N2O-N) kg(N)-1): emission factor for volatilization

    Notes:
        In IPCC (2019), Table 11.3: Disaggregation by climate for EFvolatilization (based on long-term averages):
        Wet climates occur in temperate and boreal zones where the ratio of annual precipitation (P) / potential evapotranspiration (PE) >1
        Dry climates occur in temperate and boreal zones where the ratio of annual P/PE <1

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_36_Livestock_Emission_Conversion_Factors_Provider.cs#L515
    """
    return 0.014 if mean_annual_precipitation > mean_annual_potential_evapotranspiration else 0.005


class LivestockEmissionConversionFactorsData:
    def __init__(
            self,
            methane_conversion_factor: float = 0,
            n2o_direct_emission_factor: float = 0,
            volatilization_fraction: float = 0,
            emission_factor_volatilization: float = 0,
            leaching_fraction: float = 0,
            emission_factor_leach: float = 0,
            methane_enteric_rat: float = 0,
            methane_manure_rate: float = 0,
            nitrogen_excretion_rate: float = 0
    ):
        """class that hosts manure emission factors of livestock

        Args:
            methane_conversion_factor: (kg kg^-1) Methane conversion factor of manure (MCF)
            n2o_direct_emission_factor: (kg(N2O-N) kg (N)-1) Direct N2O emission factor (EF_direct)
            volatilization_fraction: (kg(NH3-N) kg(N)-1) Fraction of volatilization (Frac_volatilization)
            emission_factor_volatilization: (kg(N2O-N) kg(N)-1) Emission factor for volatilization (EF_volatilization)
            leaching_fraction: (kg(N) kg(N)-1) Fraction of leaching (Frac_leach)
            emission_factor_leach: (kg(N2O-N) kg(N)-1) Emission factor for leaching (EF_leach)
            methane_enteric_rat: (kg Head-1 day-1)
            methane_manure_rate: (kg Head-1 day-1)
            nitrogen_excretion_rate: (kg Head-1 day-1)
        """
        # public AnimalType AnimalType { get; set; }
        # public ManureStateType HandlingSystem { get; set; }

        self.MethaneConversionFactor = methane_conversion_factor
        self.N2ODirectEmissionFactor = n2o_direct_emission_factor
        self.VolatilizationFraction = volatilization_fraction
        self.EmissionFactorVolatilization = emission_factor_volatilization
        self.LeachingFraction = leaching_fraction
        self.EmissionFactorLeach = emission_factor_leach
        self.MethaneEntericRat = methane_enteric_rat
        self.MethaneManureRate = methane_manure_rate
        self.NitrogenExcretionRate = nitrogen_excretion_rate


def get_methane_conversion_factor(
        manure_state_type: ManureStateType,
        climate_zone: ClimateZones,
) -> float:
    """Returns the methane conversion factor by climate zone (kg kg-1)

    Args:
        manure_state_type:
        climate_zone:

    Returns:
        (kg kg-1) methane conversion factor

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_37_MCF_By_Climate_Livestock_MansureSystem_Provider.cs#L16
    """
    if any([
        manure_state_type == ManureStateType.solid_storage,
        manure_state_type == ManureStateType.solid
    ]):
        match climate_zone:
            case ClimateZones.CoolTemperateMoist | ClimateZones.CoolTemperateDry | ClimateZones.BorealDry | ClimateZones.BorealMoist:
                return 0.02

            case ClimateZones.WarmTemperateDry | ClimateZones.WarmTemperateMoist:
                return 0.04

    if manure_state_type == ManureStateType.compost_intensive:
        match climate_zone:
            case ClimateZones.CoolTemperateMoist | ClimateZones.CoolTemperateDry | ClimateZones.BorealDry | ClimateZones.BorealMoist:
                return 0.005

            case ClimateZones.WarmTemperateDry | ClimateZones.WarmTemperateMoist:
                return 0.01

    if manure_state_type == ManureStateType.compost_passive:
        match climate_zone:
            case ClimateZones.CoolTemperateMoist | ClimateZones.CoolTemperateDry | ClimateZones.BorealDry | ClimateZones.BorealMoist:
                return 0.01

            case ClimateZones.WarmTemperateDry | ClimateZones.WarmTemperateMoist:
                return 0.02

    if manure_state_type == ManureStateType.deep_bedding:
        match climate_zone:
            case ClimateZones.CoolTemperateMoist:
                return 0.21
            case ClimateZones.CoolTemperateDry:
                return 0.26
            case ClimateZones.BorealDry | ClimateZones.BorealMoist:
                return 0.14
            case ClimateZones.WarmTemperateDry:
                return 0.37
            case ClimateZones.WarmTemperateMoist:
                return 0.41

    if manure_state_type == ManureStateType.composted_in_vessel:
        match climate_zone:
            case ClimateZones.CoolTemperateMoist | ClimateZones.CoolTemperateDry | ClimateZones.BorealDry | ClimateZones.BorealMoist | ClimateZones.WarmTemperateDry | ClimateZones.WarmTemperateMoist:
                return 0.005

    if manure_state_type == ManureStateType.daily_spread:
        match climate_zone:
            case ClimateZones.CoolTemperateMoist | ClimateZones.CoolTemperateDry | ClimateZones.BorealDry | ClimateZones.BorealMoist:
                return 0.001

            case ClimateZones.WarmTemperateDry | ClimateZones.WarmTemperateMoist:
                return 0.005

    if manure_state_type == ManureStateType.deep_pit:
        match climate_zone:
            case ClimateZones.CoolTemperateMoist:
                return 0.06
            case ClimateZones.CoolTemperateDry:
                return 0.08
            case ClimateZones.BorealDry:
                return 0.04
            case ClimateZones.BorealMoist:
                return 0.04
            case ClimateZones.WarmTemperateDry:
                return 0.15
            case ClimateZones.WarmTemperateMoist:
                return 0.13

    # Pasture, etc. have non-temperature dependent values
    return 0


def get_direct_emission_factor_based_on_climate(
        mean_annual_precipitation: float,
        mean_annual_potential_evapotranspiration: float
) -> float:
    """Returns the default N2O direct emission factor

    Args:
        mean_annual_precipitation: (mm) mean annual precipitation
        mean_annual_potential_evapotranspiration: (mm) mean annual potential evapotranspiration

    Returns:
        (kg(N2O-N) kg (N)-1) Direct N2O emission factor (EF_direct)

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_36_Livestock_Emission_Conversion_Factors_Provider.cs#L534
    """
    return 0.006 if mean_annual_precipitation > mean_annual_potential_evapotranspiration else 0.002


def get_volatilization_fractions_from_land_applied_manure_data_for_swine_type(
        province: CanadianProvince,
        year: int
) -> float:
    """Returns the average volatilization fraction of applied swine manure

    Args:
        province: Canadian Province class
        year: year

    Returns:
        (kg NH3-N volatilized kg-1 manure N applied)

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table%2070/Table_62_Volatilization_Fractions_From_Land_Applied_Swine_Manure_Provider.cs#L23
    """
    df = HolosTables.Table_62_Fractions_of_swine_N_volatilized
    return df.iloc[(df['Year'] - year).abs().idxmin()][province.value.abbreviation]


def get_volatilization_fractions_from_land_applied_manure_data_for_dairy_cattle_type(
        province: CanadianProvince,
        year: int
) -> float:
    """Returns the average volatilization fraction of applied dairy cattle manure

    Args:
        province: Canadian Province class
        year: year

    Returns:
        (kg NH3-N volatilized kg-1 manure N applied)

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table%2069/Table_61_Volatilization_Fractions_From_Land_Applied_Dairy_Manure_Provider.cs#L48
    """
    df = HolosTables.Table_61_Fractions_of_dairy_cattle_N_volatilized
    return df.iloc[(df['Year'] - year).abs().idxmin()][province.value.abbreviation]


def get_volatilization_fraction_for_land_application(
        animal_type: AnimalType,
        province: CanadianProvince,
        year: int
) -> float:
    """Returns the average volatilization fraction of applied manure

    Args:
        animal_type: animal type class
        province: Canadian Province class
        year: year

        (kg NH3-N volatilized kg-1 manure N applied)

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_36_Livestock_Emission_Conversion_Factors_Provider.cs#L96
    """
    # Swine and dairy have more accurate volatilization fractions based on province and year
    if animal_type.is_swine_type():
        volatilization_fraction = get_volatilization_fractions_from_land_applied_manure_data_for_swine_type(
            province=province,
            year=year)

        # return volatilizationFraction.ImpliedEmissionFactor;
    elif animal_type.is_dairy_cattle_type():
        volatilization_fraction = get_volatilization_fractions_from_land_applied_manure_data_for_dairy_cattle_type(
            province=province,
            year=year)

        # return volatilizationFraction.ImpliedEmissionFactor;

    else:
        volatilization_fraction = 0.21

    return volatilization_fraction


def get_land_application_factors(
        province: CanadianProvince,
        mean_annual_precipitation: float,
        mean_annual_evapotranspiration: float,
        growing_season_precipitation: float,
        growing_season_evapotranspiration: float,
        animal_type: AnimalType,
        year: int,
        soil_texture: SoilTexture
) -> LivestockEmissionConversionFactorsData:
    """Returns default manure application factor per region per year

    Args:
        province: Canadian Province class
        mean_annual_precipitation: (mm) mean annual precipitation
        mean_annual_evapotranspiration: (mm) mean annual potential evapotranspiration
        growing_season_precipitation: (mm) total amount of precipitations during the growing season (e.g. may to oct.)
        growing_season_evapotranspiration: (mm) total amount of evapotranspiration during the growing season (e.g. may to oct.)
        animal_type: animal type class
        year: year
        soil_texture: soil texture as set in Holos

    Holos Source Code:
        (1) https://github.com/RamiALBASHA/Holos/blob/71638efd97c84c6ded45e342ce664477df6f803f/H.Core/Providers/Animals/Table_36_Livestock_Emission_Conversion_Factors_Provider.cs#L41
        (2) https://github.com/holos-aafc/Holos/blob/267abf1066bb5494e5ec6a4085a85ab42dfa76c7/H.Core/Services/Initialization/Animals/AnimalInitializationService.Ammonia.cs#L55
    """
    region = get_region(province=province)
    climate_dependent_emission_factor_for_volatilization = get_emission_factor_for_volatilization_based_on_climate(
        mean_annual_precipitation=mean_annual_precipitation,
        mean_annual_potential_evapotranspiration=mean_annual_evapotranspiration)

    climate_dependent_direct_emission_factor = get_direct_emission_factor_based_on_climate(
        mean_annual_precipitation=mean_annual_precipitation,
        mean_annual_potential_evapotranspiration=mean_annual_evapotranspiration)

    factors = LivestockEmissionConversionFactorsData(
        methane_conversion_factor=0.0047,
        n2o_direct_emission_factor=climate_dependent_direct_emission_factor,
        volatilization_fraction=0.21,
        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization)

    factors.EmissionFactorLeach = Defaults.EmissionFactorForLeachingAndRunoff

    if region == Region.WesternCanada:
        factors.N2ODirectEmissionFactor = 0.00043
    else:
        if soil_texture == SoilTexture.Fine:
            factors.N2ODirectEmissionFactor = 0.0078
        elif soil_texture == SoilTexture.Medium:
            factors.N2ODirectEmissionFactor = 0.0062
        else:
            # SoilTexture = Coarse
            # Footnote 1
            factors.N2ODirectEmissionFactor = 0.0047

    factors.VolatilizationFraction = get_volatilization_fraction_for_land_application(
        animal_type=animal_type,
        province=province,
        year=year)

    # This part of the code comes from Holos Source Code (2)
    factors.LeachingFraction = calculate_fraction_of_nitrogen_lost_by_leaching_and_runoff(
        growing_season_precipitation=growing_season_precipitation,
        growing_season_evapotranspiration=growing_season_evapotranspiration)

    return factors


def get_manure_emission_factors(
        manure_state_type: ManureStateType,
        mean_annual_precipitation: float,
        mean_annual_temperature: float,
        mean_annual_evapotranspiration: float,
        growing_season_precipitation: float,
        growing_season_evapotranspiration: float,
        animal_type: AnimalType,
        province: CanadianProvince,
        year: int,
        soil_texture: SoilTexture
) -> LivestockEmissionConversionFactorsData:
    """Sets the emission factors for manure

    Args:
        manure_state_type: ManureStateType class instance
        mean_annual_precipitation: (mm) mean annual precipitation
        mean_annual_temperature: (degrees Celsius) mean annual air temperature
        mean_annual_evapotranspiration: (mm) mean annual potential evapotranspiration
        growing_season_precipitation: (mm) total amount of precipitations during the growing season (e.g. may to oct.)
        growing_season_evapotranspiration: (mm) total amount of evapotranspiration during the growing season (e.g. may to oct.)
        animal_type: animal type class
        province: CanadianProvince class instance
        year: year
        soil_texture: soil texture as set in Holos

    Returns:

    Holos Source Code:
        https://github.com/RamiALBASHA/Holos/blob/71638efd97c84c6ded45e342ce664477df6f803f/H.Core/Providers/Animals/Table_36_Livestock_Emission_Conversion_Factors_Provider.cs#L117
    """
    climate_dependent_methane_conversion_factor = get_methane_conversion_factor(
        manure_state_type=manure_state_type,
        climate_zone=get_climate_zone(
            mean_annual_temperature=mean_annual_temperature,
            mean_annual_precipitation=mean_annual_precipitation,
            mean_annual_potential_evapotranspiration=mean_annual_evapotranspiration))

    climate_dependent_emission_factor_for_volatilization = get_emission_factor_for_volatilization_based_on_climate(
        mean_annual_precipitation=mean_annual_precipitation,
        mean_annual_potential_evapotranspiration=mean_annual_evapotranspiration)

    # All factors are the same when considering any manure on pasture
    if any([
        manure_state_type == ManureStateType.pasture,
        manure_state_type == ManureStateType.paddock,
        manure_state_type == ManureStateType.range
    ]):
        return get_land_application_factors(
            province=province,
            mean_annual_precipitation=mean_annual_precipitation,
            mean_annual_evapotranspiration=mean_annual_evapotranspiration,
            growing_season_precipitation=growing_season_precipitation,
            growing_season_evapotranspiration=growing_season_evapotranspiration,
            animal_type=animal_type,
            year=year,
            soil_texture=soil_texture)

    # The following factors are for animals not on pasture.
    category = animal_type.get_component_category_from_animal_type()

    match category:
        case ComponentCategory.BeefProduction:
            match manure_state_type:
                case ManureStateType.solid_storage:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.01,
                        volatilization_fraction=0.45,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.02,
                        emission_factor_leach=0.011)

                case ManureStateType.compost_intensive:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.005,
                        volatilization_fraction=0.65,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.06,
                        emission_factor_leach=0.011)

                case ManureStateType.compost_passive:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.005,
                        volatilization_fraction=0.60,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.04,
                        emission_factor_leach=0.011)

                case ManureStateType.deep_bedding:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.01,
                        volatilization_fraction=0.25,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.035,
                        emission_factor_leach=0.011)

                case ManureStateType.anaerobic_digester:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=0.01,  # Footnote 4
                        n2o_direct_emission_factor=0.0006,
                        volatilization_fraction=0.1,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.0,
                        emission_factor_leach=0.011)

                case _:
                    # raise ValueError(
                    #     f"Unable to get data for manure state type: {manure_state_type}. Returning default value.")
                    return LivestockEmissionConversionFactorsData()

        case ComponentCategory.Dairy:
            match manure_state_type:
                case ManureStateType.daily_spread:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.0,
                        volatilization_fraction=0.07,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0,
                        emission_factor_leach=0.011)

                case ManureStateType.solid_storage:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.01,
                        volatilization_fraction=0.3,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.02,
                        emission_factor_leach=0.011)

                case ManureStateType.compost_intensive:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.005,
                        volatilization_fraction=0.5,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.06,
                        emission_factor_leach=0.011)

                case ManureStateType.compost_passive:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.005,
                        volatilization_fraction=0.45,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.04,
                        emission_factor_leach=0.011)

                case ManureStateType.deep_bedding:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.01,
                        volatilization_fraction=0.25,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.035,
                        emission_factor_leach=0.011)

                case ManureStateType.liquid_with_natural_crust:
                    return LivestockEmissionConversionFactorsData(
                        n2o_direct_emission_factor=0.005,
                        volatilization_fraction=0.3,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0,
                        emission_factor_leach=0.011)

                case ManureStateType.liquid_no_crust:
                    return LivestockEmissionConversionFactorsData(
                        n2o_direct_emission_factor=0.0,
                        volatilization_fraction=0.48,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0,
                        emission_factor_leach=0.011)

                case ManureStateType.liquid_with_solid_cover:
                    return LivestockEmissionConversionFactorsData(
                        n2o_direct_emission_factor=0.005,
                        volatilization_fraction=0.1,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0,
                        emission_factor_leach=0.011)

                case ManureStateType.deep_pit:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.002,
                        volatilization_fraction=0.28,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0,
                        emission_factor_leach=0.011)

                case ManureStateType.anaerobic_digester:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=0.01,  # Footnote 4
                        n2o_direct_emission_factor=0.0006,
                        volatilization_fraction=0.1,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        emission_factor_leach=0.011)

                case _:
                    raise ValueError(
                        f": Unable to get data for manure state type: {manure_state_type}. Returning default value.")

                    # return Table_36_Livestock_Emission_Conversion_Factors_Data()

        case ComponentCategory.Swine:
            match manure_state_type:
                case ManureStateType.composted_in_vessel:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=0.005,
                        n2o_direct_emission_factor=0.006,
                        volatilization_fraction=0.6,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0,
                        emission_factor_leach=0.011)

                case ManureStateType.liquid_with_natural_crust:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=0.0,
                        n2o_direct_emission_factor=0.005,
                        volatilization_fraction=0.3,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0,
                        emission_factor_leach=0.011)

                case ManureStateType.liquid_no_crust:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=0.0,
                        n2o_direct_emission_factor=0.0,
                        volatilization_fraction=0.48,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0,
                        emission_factor_leach=0.011)

                case ManureStateType.liquid_with_solid_cover:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=0.0,
                        n2o_direct_emission_factor=0.005,
                        volatilization_fraction=0.1,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0,
                        emission_factor_leach=0.011)

                case ManureStateType.deep_pit:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.002,
                        volatilization_fraction=0.25,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        emission_factor_leach=0.011)

                case ManureStateType.anaerobic_digester:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=0.01,  # Footnote 4
                        n2o_direct_emission_factor=0.0006,
                        volatilization_fraction=0.1,  # Footnote 5
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        emission_factor_leach=0.011)

                case _:
                    raise ValueError(
                        f"Unable to get data for manure state type: {manure_state_type}. Returning default value.")
                    # return Table_36_Livestock_Emission_Conversion_Factors_Data()

        case ComponentCategory.Sheep:
            match manure_state_type:
                case ManureStateType.solid_storage:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.01,
                        volatilization_fraction=0.12,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.02,
                        emission_factor_leach=0.011)

                case _:
                    raise ValueError(
                        f"Unable to get data for manure state type: {manure_state_type}. Returning default value.")
                    # return Table_36_Livestock_Emission_Conversion_Factors_Data();

        case ComponentCategory.Poultry:
            if manure_state_type == ManureStateType.anaerobic_digester:
                return LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0.01,  # Footnote 7
                    n2o_direct_emission_factor=0.0006,
                    volatilization_fraction=0.1,
                    emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                    leaching_fraction=0,
                    emission_factor_leach=0.011)

            if manure_state_type == ManureStateType.solid_storage_with_or_without_litter:
                # Bedding with litter
                return LivestockEmissionConversionFactorsData(
                    methane_conversion_factor=0.015,  # Footnote 7
                    n2o_direct_emission_factor=0.001,  # Footnote 7
                    volatilization_fraction=0.4,
                    emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                    leaching_fraction=0,
                    emission_factor_leach=0.011)

            raise ValueError(
                f"Unable to get data for manure state type: {manure_state_type}. Returning default value.")

            # return Table_36_Livestock_Emission_Conversion_Factors_Data()

        case ComponentCategory.OtherLivestock:
            match manure_state_type:
                case ManureStateType.solid_storage:
                    return LivestockEmissionConversionFactorsData(
                        methane_conversion_factor=climate_dependent_methane_conversion_factor,
                        n2o_direct_emission_factor=0.01,
                        volatilization_fraction=0.12,
                        emission_factor_volatilization=climate_dependent_emission_factor_for_volatilization,
                        leaching_fraction=0.02,
                        emission_factor_leach=0.011)

                case _:
                    raise ValueError(
                        f"Unable to get data for manure state type: {manure_state_type}. Returning default value.")
                    # return Table_36_Livestock_Emission_Conversion_Factors_Data();

        # Unknown component category (or no values for category yet)
        case _:
            raise ValueError(
                ' '.join([
                    f"Unable to get data for manure state type '{manure_state_type}'",
                    f"and component category '{category}'.",
                    "Returning default value."
                ]))
            # return Table_36_Livestock_Emission_Conversion_Factors_Data();


def get_manure_excretion_rate(
        animal_type: AnimalType
) -> float:
    """Returns the manure excretion rate of animals

    Args:
        animal_type: AnimalType class instance

    Returns:
        (kg head-1 day-1) animal excretion rate

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/97331845af308fe8aab6267edad4bbda6f5938b6/H.Core/Providers/Animals/Table_29_Default_Manure_Excreted_Provider.cs#L100

    """
    _excretionRates = HolosTables.Table_29_Percentage_Total_Manure_Produced_In_Systems

    animal_type_lookup = animal_type
    if animal_type.is_beef_cattle_type():
        animal_type_lookup = AnimalType.beef
    elif animal_type.is_dairy_cattle_type():
        animal_type_lookup = AnimalType.dairy
    elif animal_type.is_sheep_type():
        animal_type_lookup = AnimalType.sheep
    elif animal_type.is_swine_type():
        animal_type_lookup = AnimalType.swine
    elif animal_type.is_turkey_type():
        animal_type_lookup = AnimalType.turkeys
    elif animal_type.is_poultry_type():
        if animal_type == AnimalType.chicken_hens:
            animal_type_lookup = AnimalType.layers

    return _excretionRates.loc[animal_type_lookup, 'manure_excreted_rate']


def convert_manure_state_type_name(name: str) -> ManureStateType:
    cleaned_input = name.lower().strip().replace(' ', '').replace('-', '').replace('/', '')
    match cleaned_input:
        case "pasture" | "pasturerangepaddock":
            return ManureStateType.pasture

        case "deepbedding":
            return ManureStateType.deep_bedding

        case "solidstorage" | "solidstoragestockpiled":
            return ManureStateType.solid_storage

        case "solidstoragewithorwithoutlitter":
            return ManureStateType.solid_storage_with_or_without_litter

        case "compostedpassive" | "compostpassive" | "compostpassivewindrow":
            return ManureStateType.compost_passive

        case "compostedintensive" | "compostintensive" | "compostintensivewindrow":
            return ManureStateType.compost_intensive

        case "compostedinvessel":
            return ManureStateType.composted_in_vessel

        case "composted":
            return ManureStateType.composted

        case "anaerobicdigestion" | "anaerobicdigestor":
            return ManureStateType.anaerobic_digester

        case "deeppit" | "deeppitunderbarn":
            return ManureStateType.deep_pit

        case "liquidsolidcover" | "liquidwithsolidcover" | "liquidslurrywithsolidcover":
            return ManureStateType.liquid_with_solid_cover

        case "liquidnaturalcrust" | "liquidwithnaturalcrust" | "liquidslurrywithnaturalcrust":
            return ManureStateType.liquid_with_natural_crust

        case "liquidnocrust" | "liquidwithnocrust" | "liquidslurrywithnonaturalcrust":
            return ManureStateType.liquid_no_crust

        case "dailyspread":
            return ManureStateType.daily_spread

        case _:
            # raise ValueError(f"was not able to convert {name}. Returning {ManureStateType.not_selected}")
            return ManureStateType.not_selected


class ManureComposition:
    def __init__(
            self,
            moisture_content: float,
            nitrogen_content: float,
            carbon_content: float,
            phosphorus_content: float,
            carbon_to_nitrogen_ratio: float,
            volatile_solid_content: float
    ):
        self.moisture_content = moisture_content
        self.nitrogen_content = nitrogen_content
        self.carbon_content = carbon_content
        self.phosphorus_content = phosphorus_content
        self.carbon_to_nitrogen_ratio = carbon_to_nitrogen_ratio
        self.volatile_solid_content = volatile_solid_content


def get_default_manure_composition_data(
        animal_type: AnimalType,
        manure_state_type: ManureStateType
) -> ManureComposition:
    """Returns the default manure composition values depending on animal type and manure state (handling system) type

    Args:
        animal_type: AnimalType class instance
        manure_state_type: ManureStateType class instance

    Returns:
        ManureComposition class instance

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/97331845af308fe8aab6267edad4bbda6f5938b6/H.Core/Models/Farm.Manure.cs#L34
    """

    # var defaultValue = new DefaultManureCompositionData();

    if animal_type.is_beef_cattle_type():
        animal_lookup_type = AnimalType.beef
    elif animal_type.is_dairy_cattle_type():
        animal_lookup_type = AnimalType.dairy
    elif animal_type.is_sheep_type():
        animal_lookup_type = AnimalType.sheep
    elif animal_type.is_swine_type():
        animal_lookup_type = AnimalType.swine
    elif animal_type.is_poultry_type():
        animal_lookup_type = AnimalType.poultry
    else:
        # Other animals have a value for animal group (Horses, Goats, etc.)
        animal_lookup_type = animal_type

    return ManureComposition(
        **HolosTables.Table_6_Manure_Types_And_Default_Composition.loc[(animal_lookup_type, manure_state_type)])


def get_beef_and_dairy_cattle_coefficient_data(
        animal_type: str
) -> AnimalCoefficientData:
    df = HolosTables.Table_16_Livestock_Coefficients_BeefAndDairy_Cattle_Provider

    if animal_type in df.index:
        _df = df.loc[animal_type]
        res = AnimalCoefficientData(
            baseline_maintenance_coefficient=_df['BaselineMaintenanceCoefficient'],
            gain_coefficient=_df['GainCoefficient'],
            default_initial_weight=_df['DefaultInitialWeight'],
            default_final_weight=_df['DefaultFinalWeight'])
    else:
        res = AnimalCoefficientData()
    return res


def get_beef_and_dairy_cattle_feeding_activity_coefficient(
        housing_type: HousingType
) -> float:
    """Returns the coefficient corresponding to animal’s feeding situation (Ca in IPCC's tables)

    Args:
        housing_type: HousingType class instance

    Returns:
        (MJ day-1 kg-1) coefficient corresponding to animal’s feeding situation (Ca)

    References:
        Table 10.5 in https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/4_Volume4/V4_10_Ch10_Livestock.pdf

    Holos source code:
        https://github.com/holos-aafc/Holos/blob/a84060af0e699de25158a1a9030dc9d78edd0e00/H.Core/Providers/Animals/Table_17_Beef_Dairy_Cattle_Feeding_Activity_Coefficient_Provider.cs#L21
    """
    match housing_type:
        case HousingType.housed_in_barn | HousingType.confined | HousingType.confined_no_barn:
            res = 0

        case HousingType.pasture | HousingType.flat_pasture | HousingType.enclosed_pasture:
            res = 0.17

        case HousingType.open_range_or_hills:
            res = 0.36

        case _:
            res = 0

    return res


def get_average_milk_production_for_dairy_cows_value(
        year: int,
        province: CanadianProvince
):
    """returns the average milk production value for a given Canadian Province.

    Args:
        year: year for which the average milk production will be returned
        province: Canadian Province object

    Returns:
        (kg head-1 day-1): the average milk production value

    References:
        Holos source code: https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_21_Average_Milk_Production_Dairy_Cows_Provider.cs#L56
    """
    df = HolosTables.Table_21_Average_Milk_Production_For_Dairy_Cows_By_Province
    year_min = min(df.index)
    year_max = max(df.index)

    df = df.merge(DataFrame(index=range(year_min, year_max + 1)), right_index=True, left_index=True, how="right")
    df.interpolate(method="linear", inplace=True)

    return df.loc[max(year_min, min(year_max, year)), province.value.abbreviation]


def read_table_6():
    manure_composition_data = read_holos_resource_table(
        path_file=PathsHolosResources.Table_6_Manure_Types_And_Default_Composition)
    manure_composition_data['animal_type'] = manure_composition_data['animal_type'].apply(
        lambda x: convert_animal_type_name(name=x))
    manure_composition_data['manure_state_type'] = manure_composition_data['manure_state_type'].apply(
        lambda x: convert_manure_state_type_name(name=x))
    return manure_composition_data.set_index(['animal_type', 'manure_state_type'])


def read_table_29():
    excretion_rates = read_holos_resource_table(
        path_file=PathsHolosResources.Table_29_Percentage_Total_Manure_Produced_In_Systems)
    excretion_rates.index = excretion_rates.pop('Animal group').apply(lambda x: convert_animal_type_name(name=x))
    return excretion_rates


class HolosTables:
    Table_6_Manure_Types_And_Default_Composition: DataFrame = read_table_6()
    Table_16_Livestock_Coefficients_BeefAndDairy_Cattle_Provider = read_holos_resource_table(
        path_file=PathsHolosResources.Table_16_Livestock_Coefficients_BeefAndDairy_Cattle_Provider,
        index_col="AnimalType")
    Table_21_Average_Milk_Production_For_Dairy_Cows_By_Province = utils.read_holos_resource_table(
        path_file=PathsHolosResources.Table_21_Average_Milk_Production_For_Dairy_Cows_By_Province,
        index_col='Year')
    Table_29_Percentage_Total_Manure_Produced_In_Systems = read_table_29()
    Table_30_Default_Bedding_Material_Composition_Provider = read_holos_resource_table(
        path_file=PathsHolosResources.Table_30_Default_Bedding_Material_Composition_Provider)
    Table_61_Fractions_of_dairy_cattle_N_volatilized = read_holos_resource_table(
        path_file=PathsHolosResources.Table_61_Fractions_of_dairy_cattle_N_volatilized)
    Table_62_Fractions_of_swine_N_volatilized = read_holos_resource_table(
        path_file=PathsHolosResources.Table_62_Fractions_of_swine_N_volatilized)
