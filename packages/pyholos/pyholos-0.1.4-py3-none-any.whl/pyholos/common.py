from enum import Enum, StrEnum, auto, unique
from typing import Any

from pyholos.common2 import CanadianProvince
from pyholos.utils import AutoNameEnum


class EnumGeneric(Enum):
    @classmethod
    def get_value(cls, name: str) -> str:
        return getattr(cls, name).value

    @classmethod
    def get_member(cls, name: str):
        return getattr(cls, name)


class HolosVar:
    def __init__(
            self,
            name: str,
            value: Any = None
    ):
        self.name = name
        self.value = value


class Component:
    def __init__(self):
        pass

    def to_dict(self) -> dict:
        return {v.name: v.value for k, v in self.__dict__.items() if isinstance(v, HolosVar)}


class Region(AutoNameEnum):
    EasternCanada = auto()
    WesternCanada = auto()


def get_region(
        province: CanadianProvince
) -> str:
    if province in [
        CanadianProvince.Alberta,
        CanadianProvince.BritishColumbia,
        CanadianProvince.Manitoba,
        CanadianProvince.Saskatchewan,
        CanadianProvince.NorthwestTerritories,
        CanadianProvince.Nunavut]:

        res = Region.WesternCanada

    else:
        res = Region.EasternCanada

    return res


def verify_is_prairie_province(
        province: CanadianProvince
) -> bool:
    return province in [
        CanadianProvince.Alberta,
        CanadianProvince.Saskatchewan,
        CanadianProvince.Manitoba]


@unique
class ClimateZones(StrEnum):
    CoolTemperateMoist = auto()
    CoolTemperateDry = auto()
    BorealMoist = auto()
    BorealDry = auto()
    WarmTemperateMoist = auto()
    WarmTemperateDry = auto()


def get_climate_zone(
        mean_annual_temperature: float,
        mean_annual_precipitation: float,
        mean_annual_potential_evapotranspiration: float
) -> ClimateZones:
    """Returns a ClimateZones member for the specified climate conditions

    Args:
        mean_annual_temperature: (°C) mean annual air temperature
        mean_annual_precipitation: (mm) mean annual precipitation
        mean_annual_potential_evapotranspiration: (mm) mean annual potential evapotranspiration

    Returns:
        ClimateZones object

    Notes:
        For the determination of the methane conversion factor) MCF value, IPCC (2019) defines the different climate zones as follows:
            1. Warm temperate moist: mean annual temperature (MAT) > 10 °C, P:PE >1;
            2. Warm temperate dry: MAT >10 °C, P:PE < 1;
            3. Cool temperate moist: MAT > 0 °C, P:PE >1;
            4. Cool temperate dry: MAT > 0 °C, P:PE <1;
            5. Boreal moist: MAT < 0 °C but some monthly temperatures > 10 °C, P:PE >1;
            6. Boreal dry: MAT < 0 °C but some monthly temperatures > 10 °C, P:PE <1.
        The MAT for cool temperate moist, cool temperate dry, warm temperate moist and warm temperate dry were 4.6, 5.8, 13.9, 14.0, respectively.
        For deep pit manure storage systems for dairy cattle and swine, an average storage duration of 1 month was assumed.
        (Source: IPCC (2019), Table 10.17)

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_37_MCF_By_Climate_Livestock_MansureSystem_Provider.cs#L147
    """
    is_high_ratio_precipitation_to_potential_evapotranspiration = (
            (mean_annual_precipitation / mean_annual_potential_evapotranspiration) >= 1)

    if (mean_annual_temperature >= 10) and is_high_ratio_precipitation_to_potential_evapotranspiration:
        climate_zone = ClimateZones.WarmTemperateMoist

    elif (mean_annual_temperature >= 10) and not is_high_ratio_precipitation_to_potential_evapotranspiration:
        climate_zone = ClimateZones.WarmTemperateDry

    elif all([
        mean_annual_temperature >= 0,
        mean_annual_temperature < 10,
        is_high_ratio_precipitation_to_potential_evapotranspiration
    ]):
        climate_zone = ClimateZones.CoolTemperateMoist

    elif all([
        mean_annual_temperature >= 0,
        mean_annual_temperature < 10,
        not is_high_ratio_precipitation_to_potential_evapotranspiration
    ]):
        climate_zone = ClimateZones.CoolTemperateDry

    elif (mean_annual_temperature <= 0) and is_high_ratio_precipitation_to_potential_evapotranspiration:
        climate_zone = ClimateZones.WarmTemperateMoist

    elif (mean_annual_temperature <= 0) and not is_high_ratio_precipitation_to_potential_evapotranspiration:
        climate_zone = ClimateZones.WarmTemperateDry

    else:
        raise ValueError("Unable to get data for methane conversion factor since climate zone is unknown")

    return climate_zone
