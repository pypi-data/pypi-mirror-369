from os import environ
from pathlib import Path

PATH_HOLOS_CLI = Path(environ['PATH_HOLOS_CLI'])
DATE_FMT = "%Y-%m-%d"

_PATH_HOLOS_SERVICE_RESOURCES = Path(__file__).parent / 'resources'


class PathsHolosResources:
    _path_root = _PATH_HOLOS_SERVICE_RESOURCES / 'holos'
    Table_Tillage_Factor = _path_root / (
        'Table_Tillage_Factor.csv')
    Table_6_Manure_Types_And_Default_Composition = _path_root / (
        'Table_6_Manure_Types_And_Default_Composition.csv')
    Table_7_Relative_Biomass_Information = _path_root / (
        'Table_7_Relative_Biomass_Information.csv')
    Table_9_Default_Values_For_Nitrogen_Lignin_In_Crops = _path_root / (
        'Table_9_Default_Values_For_Nitrogen_Lignin_In_Crops.csv')
    Table_16_Livestock_Coefficients_BeefAndDairy_Cattle_Provider = _path_root / (
        'Table_16_Livestock_Coefficients_BeefAndDairy_Cattle_Provider.csv')
    Table_21_Average_Milk_Production_For_Dairy_Cows_By_Province = _path_root / (
        'Table_21_Average_Milk_Production_For_Dairy_Cows_By_Province.csv')
    Table_22_Livestock_Coefficients_For_Sheep = _path_root / (
        "Table_22_Livestock_Coefficients_For_Sheep.csv")
    Table_29_Percentage_Total_Manure_Produced_In_Systems = _path_root / (
        "Table_29_Percentage_Total_Manure_Produced_In_Systems.csv")
    Table_30_Default_Bedding_Material_Composition_Provider = _path_root / (
        'Table_30_Default_Bedding_Material_Composition_Provider.csv')
    Table_50_Fuel_Energy_Requirement_Estimates_By_Region = _path_root / (
        'Table_50_Fuel_Energy_Requirement_Estimates_By_Region.csv')
    Table_51_Herbicide_Energy_Requirement_Estimates_By_Region = _path_root / (
        'Table_51_Herbicide_Energy_Requirement_Estimates_By_Region.csv')
    Table_61_Fractions_of_dairy_cattle_N_volatilized = _path_root / (
        'Table_61_Fractions_of_dairy_cattle_N_volatilized.csv')
    Table_62_Fractions_of_swine_N_volatilized = _path_root / (
        'Table_62_Fractions_of_swine_N_volatilized.csv')

    Table_small_area_yields = _path_root / (
        'small_area_yields.csv')


class PathsSlcData:
    _path_root = _PATH_HOLOS_SERVICE_RESOURCES / 'soil_landscapes_of_canada_v3r2'
    geojson_file = _path_root / 'soil_landscapes_of_canada_v3r2.geojson'
    csv_dir = _path_root / 'soil_landscapes_of_canada_v3r2_csv'
    cmp_file = csv_dir / 'ca_all_slc_v3r2_cmp.csv'
    slt_file = csv_dir / 'ca_all_slc_v3r2_slt.csv'
    snt_file = csv_dir / 'ca_all_slc_v3r2_snt.csv'
