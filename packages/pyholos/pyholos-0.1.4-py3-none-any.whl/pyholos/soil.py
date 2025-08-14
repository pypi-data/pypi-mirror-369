from enum import StrEnum, auto, unique

from pyholos import common2
from pyholos.common import Region, get_region
from pyholos.common2 import CanadianProvince
from pyholos.config import PathsSlcData
from pyholos.utils import AutoNameEnum, keep_alphabetical_characters


@unique
class SoilTexture(StrEnum):
    """Holos Source Code:
    https://github.com/holos-aafc/Holos/blob/main/H.Core/Enumerations/SoilTexture.cs
    """
    Fine = auto()
    Medium = auto()
    Coarse = auto()
    Unknown = auto()


class SoilFunctionalCategory(AutoNameEnum):
    NotApplicable = auto()
    Brown = auto()
    BrownChernozem = auto()
    DarkBrown = auto()
    DarkBrownChernozem = auto()
    Black = auto()
    BlackGrayChernozem = auto()
    Organic = auto()
    EasternCanada = auto()
    All = auto()
    Unknown = auto()
    Grey = auto()
    DarkGrey = auto()

    def get_simplified_soil_category(self):
        if self in [
            self.__class__.Brown,
            self.__class__.DarkBrown,
            self.__class__.BrownChernozem,
            self.__class__.DarkBrownChernozem
        ]:
            res = self.__class__.Brown
        elif self in [
            self.__class__.Black,
            self.__class__.BlackGrayChernozem
        ]:
            res = SoilFunctionalCategory.Black
        else:
            # Other types cannot be reduced/simplified (i.e. Organic, Eastern Canada, etc.)
            res = self

        return res


def convert_soil_texture_name(
        name: str
) -> SoilTexture:
    """Returns a SoilTexture member as a function of the soil name.

    Args:
        name: soil name

    Returns:
        SoilTexture member

    Holos source code:
        https://github.com/holos-aafc/Holos/blob/768b3d8fe2565dad0ba01fb8490974f1047a114f/H.Core/Converters/SoilTextureStringConverter.cs#L9
    """
    match keep_alphabetical_characters(name=name):
        case "fine":
            return SoilTexture.Fine
        case "coarse":
            return SoilTexture.Coarse
        case "medium":
            return SoilTexture.Medium
        case _:
            # throw new Exception(string.Format(Resources.ExceptionUnknownSoilTextureString, input));
            return SoilTexture.Unknown


def convert_soil_functional_category_name(
        name: str
) -> SoilFunctionalCategory:
    """Returns a SoilFunctionalCategory member as a function of the soil functional category name.

    Args:
        name: soil functional category name

    Returns:
        SoilFunctionalCategory member

    Holos source code:
        https://github.com/holos-aafc/Holos/blob/768b3d8fe2565dad0ba01fb8490974f1047a114f/H.Core/Converters/SoilFunctionalCategoryStringConverter.cs#L10
    """
    match keep_alphabetical_characters(name=name):
        case "brownchernozem":
            return SoilFunctionalCategory.BrownChernozem
        case "darkbrownchernozem":
            return SoilFunctionalCategory.DarkBrownChernozem
        case "blackgraychernozem":
            return SoilFunctionalCategory.BlackGrayChernozem
        case "all":
            return SoilFunctionalCategory.All
        case "brown":
            return SoilFunctionalCategory.Brown
        case "darkbrown":
            return SoilFunctionalCategory.DarkBrown
        case "black":
            return SoilFunctionalCategory.Black
        case "organic":
            return SoilFunctionalCategory.Organic
        case "easterncanada" | "east":
            return SoilFunctionalCategory.EasternCanada
        case _:
            # Trace.TraceError($"{nameof(SoilFunctionalCategoryStringConverter)}: Soil functional category '{input}' not mapped, returning default value.")
            return SoilFunctionalCategory.NotApplicable


class SoilGreatGroup:
    def __init__(
            self,
            soil_great_group_type: str,
            region: str,
            soil_functional_category: str
    ):
        self.soil_great_group_type = soil_great_group_type
        self.region = region
        self.soil_functional_category = soil_functional_category


def get_soil_great_group_table() -> list[SoilGreatGroup]:
    return [
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.BrownChernozem.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.BrownChernozem.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.NotApplicable),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.DarkBrownChernozem.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.DarkBrown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.DarkBrownChernozem.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.NotApplicable),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.BlackChernozem.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Black),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.BlackChernozem.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.NotApplicable),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.DarkGrayChernozem.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Black),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.DarkGrayChernozem.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.NotApplicable),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Solonetz.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Solonetz.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.SolodizedSolonetz.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.SolodizedSolonetz.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Solod.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Solod.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.VerticSolonetz.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.VerticSolonetz.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.GrayBrownLuvisol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.NotApplicable),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.GrayBrownLuvisol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.GrayLuvisol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Black),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.GrayLuvisol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.FerroHumicPodzol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.FerroHumicPodzol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.HumicPodzol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.HumicPodzol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.HumoFerricPodzol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.HumoFerricPodzol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.MelanicBrunisol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.MelanicBrunisol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.EutricBrunisol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.EutricBrunisol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.SombricBrunisol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.SombricBrunisol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.DystricBrunisol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.DystricBrunisol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.HumicGleysol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.HumicGleysol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Gleysol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Brown),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Gleysol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.LuvicGleysol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Black),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.LuvicGleysol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Fibrisol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Organic),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Fibrisol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.Organic),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Mesisol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Organic),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Mesisol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.Organic),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.OrganicCryosol.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.Organic),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.OrganicCryosol.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.Organic),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.NotApplicable.name,
            region=Region.WesternCanada,
            soil_functional_category=SoilFunctionalCategory.NotApplicable),
        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.NotApplicable.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.NotApplicable),

        SoilGreatGroup(
            soil_great_group_type=common2.SoilGreatGroupNamesSlc.Unknown.name,
            region=Region.EasternCanada,
            soil_functional_category=SoilFunctionalCategory.EasternCanada),
    ]


def seek_soil_functional_category(
        province: common2.CanadianProvince,
        soil_great_group: str
) -> str:
    region = get_region(province=province)

    for v in get_soil_great_group_table():
        if all([v.soil_great_group_type == soil_great_group, v.region == region]):
            return v.soil_functional_category


def get_soil_functional_category(
        province: common2.CanadianProvince,
        soil_great_group: str
) -> str:
    soil_functional_category = seek_soil_functional_category(
        province=province,
        soil_great_group=soil_great_group)
    return soil_functional_category if soil_functional_category is not None else SoilFunctionalCategory.Black


def set_soil_texture_according_to_holos(
        soil_texture_abbreviation_from_slc: str
) -> str:
    soil_name = common2.ParentMaterialTextureNamesSlc.get_name(abbreviation=soil_texture_abbreviation_from_slc)
    if soil_name in ('Very Coarse', 'Coarse', 'Moderately Coarse'):
        res = SoilTexture.Coarse.name
    elif soil_name in ('Medium', 'Medium Skeletal'):
        res = SoilTexture.Medium.name
    elif soil_name in ('Moderately Fine', 'Fine', 'Very Fine', 'Fine Skeletal'):
        res = SoilTexture.Fine.name
    else:
        res = SoilTexture.Medium.name
    return res


def set_soil_properties(
        latitude: float,
        longitude: float
) -> dict:
    """Calculates the soil properties required by Holos 4.0

    Args:
        latitude: (decimal degrees) latitude of the simulated site
        longitude: (decimal degrees) longitude of the simulated site

    Returns:
        The following key-value pairs:
            id_polygon (int): ID of the SLC polygon in which the site is located
            province (str): The Canadian Province in which the site is located
            ecodistrict_id (int): ID of the Ecodistrict within which the farm is located
            soil_great_group (str): soil great group (e.g. "Regosol")
            soil_functional_category (str): soil functional (e.g. "Black")
            bulk_density (float): (g cm-3) soil bulk density
            soil_texture (str): soil texture (e.g. "Fine")
            soil_ph (float): (-) soil pH
            top_layer_thickness (float): (mm) thickness of the soil top layer
            sand_proportion (float): (between 0 and 1) fraction of sand in soil
            clay_proportion (float): (between 0 and 1) fraction of clay in soil
            organic_carbon_proportion (float): (between 0 and 100) percentage of soil organic carbon in soil

    """
    polygon_properties = common2.get_slc_polygon_properties(
        latitude=latitude,
        longitude=longitude,
        geojson_data=common2.load_slc_data(
            path_slc_geojson_file=PathsSlcData.geojson_file))
    id_polygon = polygon_properties['POLY_ID']
    dominant_component_properties = common2.get_dominant_component_properties(
        id_polygon=id_polygon,
        slc_components_table=common2.read_slc_csv(
            path_file=PathsSlcData.cmp_file,
            usecols=['POLY_ID', 'PROVINCE', 'PERCENT_', 'SOIL_ID']))
    id_soil = dominant_component_properties['SOIL_ID']
    soil_layer_table = common2.get_soil_layer_table(
        id_soil=id_soil,
        slc_soil_layer_table=common2.read_slc_csv(path_file=PathsSlcData.slt_file))
    first_non_litter_layer = common2.get_first_non_litter_layer(
        soil_layer_table=soil_layer_table)
    soil_name_table = common2.get_soil_name_table(
        soil_name_table=common2.read_slc_csv(
            path_file=PathsSlcData.snt_file, usecols=['SOIL_ID', 'PMTEX1', 'G_GROUP3']),
        id_soil=id_soil)

    province = common2.CanadianProvince.get_name(abbreviation=dominant_component_properties['PROVINCE'])
    soil_great_group = common2.SoilGreatGroupNamesSlc.get_name(
        abbreviation=soil_name_table['G_GROUP3']).replace(' ', '')

    return dict(
        id_polygon=id_polygon,
        province=province,
        ecodistrict_id=polygon_properties['ECO_ID'],
        soil_great_group=soil_great_group,
        soil_functional_category=get_soil_functional_category(
            province=getattr(CanadianProvince, province),
            soil_great_group=soil_great_group),
        bulk_density=first_non_litter_layer['BD'],
        soil_texture=set_soil_texture_according_to_holos(
            soil_texture_abbreviation_from_slc=soil_name_table['PMTEX1']),
        soil_ph=round(first_non_litter_layer['PH2'], 1),
        top_layer_thickness=first_non_litter_layer['LDEPTH'] * 10,
        sand_proportion=first_non_litter_layer['TSAND'] / 100.,
        clay_proportion=first_non_litter_layer['TCLAY'] / 100.,
        organic_carbon_proportion=round(first_non_litter_layer['ORGCARB'], 2))

    pass
