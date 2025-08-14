from enum import auto
from pathlib import Path

from pandas import DataFrame, MultiIndex

from pyholos.common import Region, get_region
from pyholos.common2 import CanadianProvince
from pyholos.components.common import convert_province_name
from pyholos.components.land_management.crop import (CropType,
                                                     convert_crop_type_name)
from pyholos.config import PathsHolosResources
from pyholos.soil import (SoilFunctionalCategory,
                          convert_soil_functional_category_name)
from pyholos.utils import (AutoNameEnum, keep_alphabetical_characters,
                           read_holos_resource_table)


class IrrigationType(AutoNameEnum):
    Irrigated = auto()
    RainFed = auto()


class TillageType(AutoNameEnum):
    """
    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/b183dab99d211158d1fed9da5370ce599ac7c914/H.Core/Enumerations/TillageType.cs#L6
    """
    NotSelected = auto()
    Reduced = auto()
    NoTill = auto()
    Intensive = auto()


def convert_tillage_type_name(
        name: str
) -> TillageType:
    match keep_alphabetical_characters(name=name):
        case "notill" | "nt":
            return TillageType.NoTill
        case "reduced" | "rt":
            return TillageType.Reduced
        case "intensive" | "it" | "conventional":
            return TillageType.Intensive
        case _:
            pass


class HarvestMethod(AutoNameEnum):
    """
    Holos source code:
        https://github.com/holos-aafc/Holos/blob/b183dab99d211158d1fed9da5370ce599ac7c914/H.Core/Enumerations/HarvestMethods.cs#L6
    """
    Silage = auto()
    Swathing = auto()
    GreenManure = auto()
    CashCrop = auto()
    StubbleGrazing = auto()
    NONE = auto()  # Used for fallow, etc.


class ManureApplicationTypes(AutoNameEnum):
    """
    Holos source code:
        https://github.com/holos-aafc/Holos/blob/c06f6619907fba89c3ddc29b4239a903a8c20a7a/H.Core/Enumerations/ManureApplicationTypes.cs#L9
    """
    NotSelected = auto()
    OptionA = auto()
    OptionB = auto()
    OptionC = auto()
    TilledLandSolidSpread = auto()  # Also known as 'Solid spread (intensive tillage)
    UntilledLandSolidSpread = auto()  # Also known as 'Solid spread (no tillage or reduced tillage)
    SlurryBroadcasting = auto()
    DropHoseBanding = auto()
    ShallowInjection = auto()
    DeepInjection = auto()


class TimePeriodCategory(AutoNameEnum):
    """
    Holos source code:
        https://github.com/holos-aafc/Holos/blob/c06f6619907fba89c3ddc29b4239a903a8c20a7a/H.Core/Enumerations/TimePeriodCategory.cs#L3C4-L7C16
    """
    Past = auto()
    Current = auto()
    Future = auto()


class FertilizerBlends(AutoNameEnum):
    """
    Holos source code:
        https://github.com/holos-aafc/Holos/blob/771f74699faafb12e5efe53157b03e0d29579f4b/H.Core/Enumerations/FertilizerBlends.cs#L6
    """
    Urea = auto()
    Ammonia = auto()
    UreaAmmoniumNitrate = auto()
    AmmoniumNitrate = auto()
    CalciumAmmoniumNitrate = auto()
    AmmoniumSulphate = auto()
    MesS15 = auto()
    MonoAmmoniumPhosphate = auto()
    DiAmmoniumPhosphate = auto()
    TripleSuperPhosphate = auto()
    Potash = auto()
    Npk = auto()
    CalciumNitrate = auto()
    AmmoniumNitroSulphate = auto()
    Custom = auto()  # Custom synthetic (there is also a custom organic)
    Lime = auto()
    CustomOrganic = auto()  # Custom organic
    AmmoniumNitratePrilled = auto()
    AmmoniumNitrateGranulated = auto()
    SuperPhosphate = auto()
    NpkMixedAcid = auto()
    NpkNitrophosphate = auto()
    PotassiumSulphate = auto()


def read_energy_table(path_table: Path) -> DataFrame:
    df = read_holos_resource_table(path_file=path_table, header=[0, 1, 2])
    df.index = [convert_crop_type_name(s) for s in df.pop(('Unnamed: 0_level_0', 'Unnamed: 0_level_1', 'CROP'))]
    df.columns = MultiIndex.from_tuples(
        [(convert_province_name(p), convert_soil_functional_category_name(s), convert_tillage_type_name(t))
         for p, s, t in df.columns])

    return df


class HolosTables:
    Table_50_Fuel_Energy_Requirement_Estimates_By_Region: DataFrame = read_energy_table(
        path_table=PathsHolosResources.Table_50_Fuel_Energy_Requirement_Estimates_By_Region)

    Table_51_Herbicide_Energy_Requirement_Estimates_By_Region: DataFrame = read_energy_table(
        path_table=PathsHolosResources.Table_51_Herbicide_Energy_Requirement_Estimates_By_Region)


def get_energy_estimate(
        data: DataFrame,
        province: CanadianProvince,
        soil_category: SoilFunctionalCategory,
        tillage_type: TillageType,
        crop_type: CropType
) -> float:
    """Returns the energy estimate for fuel or pesticide.

    Args:
        data: HolosTables member
        province: CanadianProvince member
        soil_category: SoilFunctionalCategory member
        tillage_type: TillageType member
        crop_type: CropType member
    Returns:
        (GJ ha-1) energy estimate

    Holos source code:
        Fuel: https://github.com/holos-aafc/Holos/blob/e6e79c3185b68999eaea1e68dbf77c89d1764b53/H.Core/Providers/Energy/Table_50_Fuel_Energy_Estimates_Provider.cs#L62
        Fuel: https://github.com/holos-aafc/Holos/blob/e6e79c3185b68999eaea1e68dbf77c89d1764b53/H.Core/Providers/Energy/Table_51_Herbicide_Energy_Estimates_Provider.cs#L60
    """
    soil_lookup_type = (
        SoilFunctionalCategory.EasternCanada if get_region(province=province) == Region.EasternCanada
        else soil_category.get_simplified_soil_category())

    # No summer fallow in table
    if crop_type.is_fallow():
        crop_type = CropType.Fallow

    try:
        res = data.loc[crop_type, (province, soil_lookup_type, tillage_type.value)]
    except KeyError:
        res = 0.

    return 0. if res is None else res


def get_fuel_energy_estimate(
        province: CanadianProvince,
        soil_category: SoilFunctionalCategory,
        tillage_type: TillageType,
        crop_type: CropType
) -> float:
    """Returns the fuel energy estimate.

    Args:
        province: CanadianProvince member
        soil_category: SoilFunctionalCategory member
        tillage_type: TillageType member
        crop_type: CropType member
    Returns:
        (GJ ha-1) fuel energy estimate

    Holos source code:
        https://github.com/holos-aafc/Holos/blob/e6e79c3185b68999eaea1e68dbf77c89d1764b53/H.Core/Providers/Energy/Table_50_Fuel_Energy_Estimates_Provider.cs#L62
    """

    return get_energy_estimate(
        data=HolosTables.Table_50_Fuel_Energy_Requirement_Estimates_By_Region,
        **locals())


def get_herbicide_energy_estimate(
        province: CanadianProvince,
        soil_category: SoilFunctionalCategory,
        tillage_type: TillageType,
        crop_type: CropType
) -> float:
    """Returns the herbicide energy estimate.

    Args:
        province: CanadianProvince member
        soil_category: SoilFunctionalCategory member
        tillage_type: TillageType member
        crop_type: CropType member
    Returns:
        (GJ ha-1) herbicide energy estimate

    Holos source code:
        https://github.com/holos-aafc/Holos/blob/e6e79c3185b68999eaea1e68dbf77c89d1764b53/H.Core/Providers/Energy/Table_51_Herbicide_Energy_Estimates_Provider.cs#L60
    """
    return get_energy_estimate(
        data=HolosTables.Table_51_Herbicide_Energy_Requirement_Estimates_By_Region,
        **locals())
