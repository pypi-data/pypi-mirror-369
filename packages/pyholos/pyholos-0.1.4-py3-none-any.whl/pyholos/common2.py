from enum import Enum
from pathlib import Path

from geojson import FeatureCollection, load
from pandas import DataFrame, read_csv
from shapely.geometry import Point, shape


class MapNamesGeneric(Enum):
    @classmethod
    def _get_name(cls, abbreviation: str) -> str:
        for member in cls:
            if member.value.abbreviation == abbreviation:
                return member.value.name

    @classmethod
    def get_name(cls, abbreviation: str) -> str:
        res = cls._get_name(abbreviation=abbreviation)
        return res if res is not None else "NotApplicable"


class NameSlc:
    def __init__(
            self,
            name: str,
            abbreviation: str
    ):
        self.name = name
        self.abbreviation = abbreviation


class CanadianProvince(MapNamesGeneric):
    Alberta: NameSlc = NameSlc(name='Alberta', abbreviation='AB')
    BritishColumbia: NameSlc = NameSlc(name='British Columbia', abbreviation="BC")
    Manitoba: NameSlc = NameSlc(name='Manitoba', abbreviation="MB")
    NewBrunswick: NameSlc = NameSlc(name='New Brunswick', abbreviation="NB")
    NewfoundlandAndLabrador: NameSlc = NameSlc(name='Newfoundland and Labrador', abbreviation="NL")
    NorthwestTerritories: NameSlc = NameSlc(name='Northwest Territories', abbreviation="NT")
    NovaScotia: NameSlc = NameSlc(name='Nova Scotia', abbreviation="NS")
    Nunavut: NameSlc = NameSlc(name='Nunavut', abbreviation="NU")
    Ontario: NameSlc = NameSlc(name='Ontario', abbreviation="ON")
    PrinceEdwardIsland: NameSlc = NameSlc(name='Prince Edward Island', abbreviation="PE")
    Quebec: NameSlc = NameSlc(name='Quebec', abbreviation="QC")
    Saskatchewan: NameSlc = NameSlc(name='Saskatchewan', abbreviation="SK")
    Yukon: NameSlc = NameSlc(name='Yukon', abbreviation="YT")


class SoilGreatGroupNamesSlc(MapNamesGeneric):
    MelanicBrunisol: NameSlc = NameSlc(name='Melanic Brunisol', abbreviation="MB")
    EutricBrunisol: NameSlc = NameSlc(name='Eutric Brunisol', abbreviation="EB")
    SombricBrunisol: NameSlc = NameSlc(name='Sombric Brunisol', abbreviation="SB")
    DystricBrunisol: NameSlc = NameSlc(name='Dystric Brunisol', abbreviation="DYB")
    BrownChernozem: NameSlc = NameSlc(name='Brown Chernozem', abbreviation="BC")
    DarkBrownChernozem: NameSlc = NameSlc(name='Dark Brown Chernozem', abbreviation="DBC")
    BlackChernozem: NameSlc = NameSlc(name='Black Chernozem', abbreviation="BLC")
    DarkGrayChernozem: NameSlc = NameSlc(name='Dark Gray Chernozem', abbreviation="DGC")
    TurbicCryosol: NameSlc = NameSlc(name='Turbic Cryosol', abbreviation="TC")
    StaticCryosol: NameSlc = NameSlc(name='Static Cryosol', abbreviation="SC")
    OrganicCryosol: NameSlc = NameSlc(name='Organic Cryosol', abbreviation="OC")
    HumicGleysol: NameSlc = NameSlc(name='Humic Gleysol', abbreviation="HG")
    Gleysol: NameSlc = NameSlc(name='Gleysol', abbreviation="G")
    LuvicGleysol: NameSlc = NameSlc(name='Luvic Gleysol', abbreviation="LG")
    GrayBrownLuvisol: NameSlc = NameSlc(name='Gray Brown Luvisol', abbreviation="GBL")
    GrayLuvisol: NameSlc = NameSlc(name='Gray Luvisol', abbreviation="GL")
    Fibrisol: NameSlc = NameSlc(name='Fibrisol', abbreviation="F")
    Mesisol: NameSlc = NameSlc(name='Mesisol', abbreviation="M")
    Humisol: NameSlc = NameSlc(name='Humisol', abbreviation="H")
    Folisol: NameSlc = NameSlc(name='Folisol', abbreviation="FO")
    HumicPodzol: NameSlc = NameSlc(name='Humic Podzol', abbreviation="HP")
    FerroHumicPodzol: NameSlc = NameSlc(name='Ferro-Humic Podzol', abbreviation="FHP")
    HumoFerricPodzol: NameSlc = NameSlc(name='Humo-Ferric Podzol', abbreviation="HFP")
    Regosol: NameSlc = NameSlc(name='Regosol', abbreviation="R")
    HumicRegosol: NameSlc = NameSlc(name='Humic Regosol', abbreviation="HR")
    Solonetz: NameSlc = NameSlc(name='Solonetz', abbreviation="SZ")
    SolodizedSolonetz: NameSlc = NameSlc(name='Solodized Solonetz', abbreviation="SS")
    Solod: NameSlc = NameSlc(name='Solod', abbreviation="SO")
    VerticSolonetz: NameSlc = NameSlc(name='Vertic Solonetz', abbreviation="VSZ")
    Vertisol: NameSlc = NameSlc(name='Vertisol', abbreviation="V")
    HumicVertisol: NameSlc = NameSlc(name='Humic Vertisol', abbreviation="HV")

    NotApplicable: NameSlc = NameSlc(name="NotApplicable", abbreviation='NA')
    Unknown: NameSlc = NameSlc(name="NotApplicable", abbreviation='NA')


class ParentMaterialTextureNamesSlc(MapNamesGeneric):
    VeryCoarse: NameSlc = NameSlc(name='Very Coarse', abbreviation="VC")
    Coarse: NameSlc = NameSlc(name='Coarse', abbreviation="C")
    ModeratelyCoarse: NameSlc = NameSlc(name='Moderately Coarse', abbreviation="MC")
    Medium: NameSlc = NameSlc(name='Medium', abbreviation="M")
    ModeratelyFine: NameSlc = NameSlc(name='Moderately Fine', abbreviation="MF")
    Fine: NameSlc = NameSlc(name='Fine', abbreviation="F")
    VeryFine: NameSlc = NameSlc(name='Very Fine', abbreviation="VF")
    CoarseSkeletal: NameSlc = NameSlc(name='Coarse Skeletal', abbreviation="CS")
    MediumSkeletal: NameSlc = NameSlc(name='Medium Skeletal', abbreviation="MS")
    FineSkeletal: NameSlc = NameSlc(name='Fine Skeletal', abbreviation="FS")
    Fragmental: NameSlc = NameSlc(name='Fragmental', abbreviation="FR")
    StratifiedMineral: NameSlc = NameSlc(name='Stratified (Mineral)', abbreviation="SM")
    StratifiedMineralAndOrganic: NameSlc = NameSlc(name='Stratified (Mineral and Organic)', abbreviation="SU")
    Fibric: NameSlc = NameSlc(name='Fibric', abbreviation="FI")
    Mesic: NameSlc = NameSlc(name='Mesic', abbreviation="ME")
    Humic: NameSlc = NameSlc(name='Humic', abbreviation="HU")
    Undifferentiated: NameSlc = NameSlc(name='Undifferentiated', abbreviation="UD")


def read_slc_csv(
        path_file: Path,
        **kwargs
) -> DataFrame:
    return read_csv(path_file, sep=',', decimal='.', **kwargs)


def load_slc_data(path_slc_geojson_file: Path) -> FeatureCollection:
    with path_slc_geojson_file.open(mode='r') as f:
        return load(f)


def get_slc_polygon_properties(
        latitude: float | str,
        longitude: float | str,
        geojson_data: FeatureCollection
) -> dict | None:
    point = Point(longitude, latitude)

    for feature in geojson_data['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return feature['properties']

    return None


def get_dominant_component_properties(
        id_polygon: str,
        slc_components_table: DataFrame
) -> dict[str, str | int]:
    return slc_components_table[slc_components_table['POLY_ID'] == id_polygon].sort_values(
        by='PERCENT_', ascending=False).iloc[0].to_dict()


def get_soil_layer_table(
        id_soil: str,
        slc_soil_layer_table: DataFrame
) -> DataFrame:
    return slc_soil_layer_table[slc_soil_layer_table['SOIL_ID'] == id_soil].sort_values(by='UDEPTH', ascending=True)


def get_first_non_litter_layer(
        soil_layer_table: DataFrame
) -> dict:
    return soil_layer_table[soil_layer_table['UDEPTH'] >= 0].iloc[0].to_dict()


def get_soil_name_table(
        soil_name_table: DataFrame,
        id_soil: str
) -> dict:
    return soil_name_table.set_index('SOIL_ID').loc[id_soil].to_dict()
