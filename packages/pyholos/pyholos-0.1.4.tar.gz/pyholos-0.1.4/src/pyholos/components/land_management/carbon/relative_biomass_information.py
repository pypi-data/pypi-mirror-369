from dataclasses import dataclass, field

from pydantic import BaseModel, Field, NonNegativeFloat

from pyholos.common2 import CanadianProvince
from pyholos.components.common import convert_province_name
from pyholos.components.land_management.common import IrrigationType
from pyholos.components.land_management.crop import (CropType,
                                                     convert_crop_type_name)
from pyholos.config import PathsHolosResources
from pyholos.utils import clean_string


class _IrrigationData:
    def __init__(
            self,
            irrigation_type: IrrigationType,
            irrigation_lower_range_limit: float,
            irrigation_upper_range_limit: float
    ):
        self.irrigation_type = irrigation_type
        self.irrigation_lower_range_limit = irrigation_lower_range_limit
        self.irrigation_upper_range_limit = irrigation_upper_range_limit


class _CarbonResidueData:
    def __init__(
            self,
            relative_biomass_product: float,
            relative_biomass_straw: float,
            relative_biomass_root: float,
            relative_biomass_extraroot: float
    ):
        self.relative_biomass_product = relative_biomass_product
        self.relative_biomass_straw = relative_biomass_straw
        self.relative_biomass_root = relative_biomass_root
        self.relative_biomass_extraroot = relative_biomass_extraroot


class _NitrogenResidueData:
    def __init__(
            self,
            nitrogen_content_product: float,
            nitrogen_content_straw: float,
            nitrogen_content_root: float
    ):
        self.nitrogen_content_product = nitrogen_content_product
        self.nitrogen_content_straw = nitrogen_content_straw
        self.nitrogen_content_root = nitrogen_content_root
        self.nitrogen_content_extraroot = nitrogen_content_root


class BiogasAndMethaneProductionParametersData:
    def __init__(
            self,
            crop_type: CropType = CropType.NotSelected,
            bio_methane_potential: float = 0,
            methane_fraction: float = 0,
            volatile_solids: float = 0,
            total_solids: float = 0,
            total_nitrogen: float = 0
    ):
        """Table_46_Biogas_Methane_Production_CropResidue_Data

        Args:
            crop_type: CropType class member
            bio_methane_potential: (Nm3 ton-1 VS) biomethane potential given a substrate type (BMP)
            methane_fraction: (-) fraction of methane in biogas (f_CH4)
            volatile_solids: (%) percentage of total solids
            total_solids: (kg t^-1)^3 total solids in the substrate type (TS)
            total_nitrogen: (KG N t^-1)^5 total Nitrogen in the substrate
        """
        self.crop_type = crop_type
        self.bio_methane_potential = bio_methane_potential
        self.methane_fraction = methane_fraction
        self.volatile_solids = volatile_solids
        self.total_solids = total_solids
        self.total_nitrogen = total_nitrogen

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ if isinstance(other, self.__class__) else False


class RelativeBiomassInformationData(BaseModel):
    """Table_7_Relative_Biomass_Information_Data

        Args:
            crop_type: CropType class instance
            irrigation_type: IrrigationType class instance
            irrigation_lower_range_limit: (mm)
            irrigation_upper_range_limit: (mm)
            moisture_content_of_product: (%) product moisture content (between 0 and 100)
            relative_biomass_product: (-) relative biomass allocation coefficient for product
            relative_biomass_straw: (-) relative biomass allocation coefficient for straw
            relative_biomass_root: (-) relative biomass allocation coefficient for root
            relative_biomass_extraroot: (-) relative biomass allocation coefficient for extraroot
            nitrogen_content_product: (g(N)/kg) product Nitrogen content
            nitrogen_content_straw: (g(N)/kg) straw Nitrogen content
            nitrogen_content_root: (g(N)/kg) root Nitrogen content
            nitrogen_content_extraroot: (g(N)/kg) extraroot Nitrogen content
            lignin_content: (-) fraction of lignin content in the carbon input (on dry basis, between 0 and 1)
            province: CanadianProvince class instance

    Holos Source Code:
        https://github.com/holos-aafc/Holos/blob/b183dab99d211158d1fed9da5370ce599ac7c914/H.Core/Providers/Carbon/Table_7_Relative_Biomass_Information_Data.cs#L13
    """
    crop_type: CropType = Field(default=CropType.NotSelected)
    irrigation_type: IrrigationType | None = Field(default=None)
    irrigation_lower_range_limit: NonNegativeFloat = Field(default=0)
    irrigation_upper_range_limit: NonNegativeFloat = Field(default=0)
    # irrigation_amount: NonNegativeFloat = Field(default=0)
    moisture_content_of_product: float = Field(default=0, ge=0, lt=100)
    relative_biomass_product: float = Field(default=0, ge=0, lt=100)
    relative_biomass_straw: float = Field(default=0, ge=0, lt=100)
    relative_biomass_root: float = Field(default=0, ge=0, lt=100)
    relative_biomass_extraroot: float = Field(default=0, ge=0, lt=100)
    nitrogen_content_product: NonNegativeFloat = Field(default=0)
    nitrogen_content_straw: NonNegativeFloat = Field(default=0)
    nitrogen_content_root: NonNegativeFloat = Field(default=0)
    nitrogen_content_extraroot: NonNegativeFloat = Field(default=0)
    # nitrogen_fertilizer_rate: float = Field(default=0)
    # phosphorus_fertilizer_rate: float = Field(default=0)
    lignin_content: float = Field(default=0, ge=0, le=1)
    province: CanadianProvince | None = Field(default=None)

    # biogas_and_methane_production_parameters_data: BiogasAndMethaneProductionParametersData = Field(
    #     default=BiogasAndMethaneProductionParametersData())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ if isinstance(other, self.__class__) else False


def parse_crop_type(
        raw_input: str
) -> CropType:
    return convert_crop_type_name(name=raw_input.lower().replace(' ', '').replace('-', ''))


def parse_irrigation_data(
        raw_input: str,
) -> _IrrigationData:
    raw_input = raw_input.replace(' ', '').lower()

    irrigation_type = IrrigationType.RainFed if raw_input == "rainfed" else (
        IrrigationType.Irrigated if raw_input == "irrigated" else None)

    if "<" in raw_input:
        # Lower range
        irrigation_lower_range_limit = 0
        irrigation_upper_range_limit = float(raw_input.replace("<", "").replace("mm", ""))

    elif ">" in raw_input:
        # Upper range
        irrigation_lower_range_limit = float(raw_input.replace(">", "").replace("mm", ""))
        irrigation_upper_range_limit = float('inf')

    elif "-" in raw_input:
        # Irrigation is a range
        irrigation_lower_range_limit, irrigation_upper_range_limit = [
            float(s) for s in raw_input.replace("mm", "").replace(" ", "").split('-')]
    else:
        irrigation_lower_range_limit = 0
        irrigation_upper_range_limit = 0

    return _IrrigationData(
        irrigation_type=irrigation_type,
        irrigation_lower_range_limit=irrigation_lower_range_limit,
        irrigation_upper_range_limit=irrigation_upper_range_limit)


def parse_province_data(
        raw_input: str
) -> None | CanadianProvince:
    raw_input = raw_input.lower().replace(' ', '')
    if any([len(raw_input) == 0] + [v in raw_input for v in ["canada", "rainfed", "irrigated", ">", "<", "-"]]):
        province = None
    else:
        province = convert_province_name(name=raw_input)

    return province


def parse_moisture_content_data(
        raw_input: str
) -> float:
    raw_input = raw_input.lower().replace(" ", "")
    return float(raw_input) if not len(raw_input) == 0 else 0


def parse_carbon_residue_data(
        raw_inputs: list[str]
) -> _CarbonResidueData:
    raw_inputs = [float(s) if len(s.lower().replace(" ", "")) != 0 else 0 for s in raw_inputs]
    return _CarbonResidueData(
        relative_biomass_product=raw_inputs[0],
        relative_biomass_straw=raw_inputs[1],
        relative_biomass_root=raw_inputs[2],
        relative_biomass_extraroot=raw_inputs[3]
    )


def parse_nitrogen_residue_data(
        raw_inputs: list[str]
) -> _NitrogenResidueData:
    raw_inputs = [float(s) if len(s.lower().replace(" ", "")) != 0 else 0 for s in raw_inputs]
    return _NitrogenResidueData(
        nitrogen_content_product=raw_inputs[0],
        nitrogen_content_straw=raw_inputs[1],
        nitrogen_content_root=raw_inputs[2]
    )


def parse_lignin_content_data(
        raw_input: str
) -> float:
    return float(raw_input) if len(raw_input.lower().replace(" ", "")) != 0 else 0


def parse_biomethane_data(
        crop_type: CropType,
        raw_inputs: list[str]
) -> BiogasAndMethaneProductionParametersData:
    raw_inputs = [float(s) if len(s.lower().replace(" ", "")) != 0 else 0 for s in raw_inputs]
    return BiogasAndMethaneProductionParametersData(
        crop_type=crop_type,
        bio_methane_potential=raw_inputs[0],
        methane_fraction=raw_inputs[1],
        volatile_solids=raw_inputs[2],
        total_solids=raw_inputs[3],
        total_nitrogen=raw_inputs[4])


def parse_relative_biomass_information_data(
        raw_input: str
) -> RelativeBiomassInformationData:
    columns = raw_input.replace('\n', '').split(',')
    crop_type = parse_crop_type(raw_input=columns[1])
    irrigation_data = parse_irrigation_data(raw_input=columns[2])
    carbon_residue_data = parse_carbon_residue_data(columns[5: 9])
    nitrogen_residue_data = parse_nitrogen_residue_data(raw_inputs=columns[11:14])

    return RelativeBiomassInformationData(
        crop_type=crop_type,
        irrigation_type=irrigation_data.irrigation_type,
        irrigation_lower_range_limit=irrigation_data.irrigation_lower_range_limit,
        irrigation_upper_range_limit=irrigation_data.irrigation_upper_range_limit,
        moisture_content_of_product=parse_moisture_content_data(raw_input=columns[3]),
        relative_biomass_product=carbon_residue_data.relative_biomass_product,
        relative_biomass_straw=carbon_residue_data.relative_biomass_straw,
        relative_biomass_root=carbon_residue_data.relative_biomass_root,
        relative_biomass_extraroot=carbon_residue_data.relative_biomass_extraroot,
        nitrogen_content_product=nitrogen_residue_data.nitrogen_content_product,
        nitrogen_content_straw=nitrogen_residue_data.nitrogen_content_straw,
        nitrogen_content_root=nitrogen_residue_data.nitrogen_content_root,
        nitrogen_content_extraroot=nitrogen_residue_data.nitrogen_content_extraroot,
        lignin_content=parse_lignin_content_data(raw_input=columns[16]),
        province=parse_province_data(raw_input=columns[2]),
        # biogas_and_methane_production_parameters_data=parse_biomethane_data(crop_type=crop_type,
        #                                                                     raw_inputs=columns[17:22])
    )


def read_table_7():
    with PathsHolosResources.Table_7_Relative_Biomass_Information.open(mode='r') as f:
        return [v for v in f.readlines()[5:] if all([
            not len(v.replace(' ', '').replace(',', '').replace('\n', '')) == 0,
            not v.startswith('#')
        ])][2:]


def parse_table_7() -> list[RelativeBiomassInformationData]:
    return [parse_relative_biomass_information_data(raw_input=v) for v in read_table_7()]


def get_relative_biomass_information_data(
        table_7: list[RelativeBiomassInformationData],
        crop_type: CropType,
        irrigation_type: IrrigationType,
        irrigation_amount: float,
        province: CanadianProvince
) -> RelativeBiomassInformationData:
    if any([
        crop_type == CropType.NotSelected,
        crop_type.is_fallow()
    ]):
        return RelativeBiomassInformationData()

    if crop_type.is_grassland():
        # Only have values for grassland (native). If type is grassland (broken) or grassland (seeded), return values for grassland (native)
        crop_type = CropType.RangelandNative

    by_crop_type = [v for v in table_7 if v.crop_type == crop_type]
    if len(by_crop_type) == 0:
        # Trace.TraceError($"{nameof(Table_7_Relative_Biomass_Information_Provider)}.{nameof(this.GetResidueData)}: unknown crop type: '{cropType.GetDescription()}'. Returning default values.");
        return RelativeBiomassInformationData()

    elif len(by_crop_type) == 1:
        return by_crop_type[0]

    else:
        by_crop_type_and_irrigation_amount = [v for v in by_crop_type if all(
            [irrigation_amount >= v.irrigation_lower_range_limit,
             irrigation_amount < v.irrigation_upper_range_limit])]
        if len(by_crop_type_and_irrigation_amount) >= 1:
            return by_crop_type_and_irrigation_amount[0]
        else:
            by_crop_type_and_irrigation_type = [v for v in by_crop_type if v.irrigation_type == irrigation_type]
            if len(by_crop_type_and_irrigation_type) >= 1:
                return by_crop_type_and_irrigation_type[0]

    # Potato is a special case
    by_province = [v for v in by_crop_type if all([
        v.province is not None,
        v.province == province
    ])]
    if len(by_province) >= 1:
        return by_province[0]

    return [v for v in by_crop_type if v.province is None][0]


@dataclass
class NitrogenLigninContentInCropsData:
    """
    Args:
        CropType: CropType instance, the crop type for which we need the various information and values.
        InterceptValue: The intercept value given the crop type. Taken from national inventory numbers.
        SlopeValue: The slop value given the crop type. Taken from national inventory numbers.
        RSTRatio: Shoot to root ratio of the crop. The ratio of below-ground root biomass to above-ground shoot
        NitrogenContentResidues: Nitrogen Content of residues. Unit of measurement = Proportion of Carbon content
        LigninContentResidues: Lignin content of residue. Unit of measurement = Proportion of Carbon content
        MoistureContent: (%) Moisture content of crop
        # BiomethaneData: Table_46_Biogas_Methane_Production_CropResidue_Data

    Holos source code:
        https://github.com/holos-aafc/Holos/blob/d62072ff1362eb356ba00f2736293e3fe0f8acc2/H.Core/Providers/Plants/Table_9_Nitrogen_Lignin_Content_In_Crops_Data.cs#L9
    """
    CropType: CropType = CropType.NotSelected
    InterceptValue: float = 0
    SlopeValue: float = 0
    RSTRatio: float = 0
    NitrogenContentResidues: float = 0
    LigninContentResidues: float = 0
    MoistureContent: float = 0
    BiomethaneData: BiogasAndMethaneProductionParametersData = field(
        default_factory=BiogasAndMethaneProductionParametersData)


def parse_nitrogen_lignin_content_in_crops_data(
        raw_input: str
) -> NitrogenLigninContentInCropsData:
    """
    Holos source code:
        https://github.com/holos-aafc/Holos/blob/d62072ff1362eb356ba00f2736293e3fe0f8acc2/H.Core/Providers/Plants/Table_9_Nitrogen_Lignin_Content_In_Crops_Provider.cs#L104
    """
    columns = raw_input.replace('\n', '').split(',')
    crop_type = parse_crop_type(raw_input=columns[1])

    columns = [clean_string(input_string=v) for v in columns]
    biomethane_data = BiogasAndMethaneProductionParametersData() if (''.join(columns[8:]) == '') else (
        BiogasAndMethaneProductionParametersData(crop_type, *[float(v) if v != '' else 0 for v in columns[8:]]))

    return NitrogenLigninContentInCropsData(
        CropType=crop_type,
        InterceptValue=float(columns[2]),
        SlopeValue=float(columns[3]),
        RSTRatio=float(columns[4]),
        NitrogenContentResidues=float(columns[5]),
        LigninContentResidues=float(columns[6]),
        MoistureContent=float(columns[7]),
        BiomethaneData=biomethane_data
    )


def read_table_9() -> list[str]:
    with PathsHolosResources.Table_9_Default_Values_For_Nitrogen_Lignin_In_Crops.open(mode='r') as f:
        return [v for v in f.readlines() if all([
            not len(v.replace(' ', '').replace(',', '').replace('\n', '')) == 0,
            not v.startswith('#')
        ])][1:]


def parse_table_9() -> list[NitrogenLigninContentInCropsData]:
    """
    Holos source code:
        https://github.com/holos-aafc/Holos/blob/d62072ff1362eb356ba00f2736293e3fe0f8acc2/H.Core/Providers/Plants/Table_9_Nitrogen_Lignin_Content_In_Crops_Provider.cs#L104
    """
    return [parse_nitrogen_lignin_content_in_crops_data(raw_input=v) for v in read_table_9()]


def get_nitrogen_lignin_content_in_crops_data(
        table_9: list[NitrogenLigninContentInCropsData],
        crop_type: CropType
) -> NitrogenLigninContentInCropsData:
    """

    Args:
        table_9: parsed data of table 9
        crop_type: CropType class member

    Holos source code:
        https://github.com/holos-aafc/Holos/blob/d62072ff1362eb356ba00f2736293e3fe0f8acc2/H.Core/Providers/Plants/Table_9_Nitrogen_Lignin_Content_In_Crops_Provider.cs#L57
    """

    lookup_type = CropType.Durum if (crop_type == CropType.Wheat) else (
        CropType.Rye if crop_type == CropType.RyeSecaleCerealeWinterRyeCerealRye else crop_type)

    res = [v for v in table_9 if v.CropType == lookup_type]

    return res[0] if len(res) > 0 else NitrogenLigninContentInCropsData()
