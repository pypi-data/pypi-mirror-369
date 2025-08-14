from pathlib import Path

from pandas import DataFrame

from pyholos.components.animals.common import AnimalType, BeddingMaterialType
from pyholos.components.land_management.common import TillageType
from pyholos.config import PathsHolosResources
from pyholos.core_constants import CoreConstants
from pyholos.soil import SoilFunctionalCategory


class _HolosTable:
    def __init__(
            self,
            name: str,
            data: list | DataFrame,
            path: Path
    ):
        self.name = name
        self.data = data
        self.path = path

    def write_data_to_csv(
            self,
            comments: list[str] | str = None
    ) -> None:
        if comments is None:
            comments = []
        elif isinstance(comments, str):
            comments = [comments]

        comments.insert(0, f'This table was automatically generated using "{Path(__file__).name}"')

        with self.path.open(mode='w', newline='') as f:
            for comment in comments:
                f.write(f'# {comment}\n')
            f.write('#\n')

            DataFrame.from_records(self.data).to_csv(f, sep=',', decimal='.', index=False)


def set_table_16():
    table_16 = _HolosTable(
        name='Table_16_Livestock_Coefficients_BeefAndDairy_Cattle_Provider',
        data=[
            # Beef Cattle Data Sources :

            # BaselineMaintenanceCoefficient = IPCC (2019, Table 10.4)
            # GainCoefficient = IPCC (2019, Eq. 10.6)
            # DefaultInitialWeight = Sheppard et al. (2015) , A.Alemu(pers.comm, 2022)
            # DefaultFinalWeight = Sheppard et al. (2015) , A.Alemu(pers.comm, 2022)

            dict(
                AnimalType=AnimalType.beef_calf.value,
                BaselineMaintenanceCoefficient=CoreConstants.NotApplicable,
                GainCoefficient=CoreConstants.NotApplicable,
                DefaultInitialWeight=39,
                DefaultFinalWeight=260
            ),
            dict(
                AnimalType=AnimalType.beef_cow_lactating.value,
                BaselineMaintenanceCoefficient=0.386,
                GainCoefficient=0.8,
                DefaultInitialWeight=610,
                DefaultFinalWeight=610
            ),
            dict(
                AnimalType=AnimalType.beef_cow_dry.value,
                BaselineMaintenanceCoefficient=0.322,
                GainCoefficient=0.8,
                DefaultInitialWeight=610,
                DefaultFinalWeight=610
            ),
            dict(
                AnimalType=AnimalType.beef_bulls.value,
                BaselineMaintenanceCoefficient=0.370,
                GainCoefficient=1.2,
                DefaultInitialWeight=900,
                DefaultFinalWeight=900
            ),
            dict(
                AnimalType=AnimalType.beef_backgrounder_steer.value,
                BaselineMaintenanceCoefficient=0.322,
                GainCoefficient=1,
                DefaultInitialWeight=250,
                DefaultFinalWeight=380
            ),
            # Aklilu says these two animal groups have the same values
            dict(
                AnimalType=AnimalType.beef_backgrounder_heifer.value,
                BaselineMaintenanceCoefficient=0.322,
                GainCoefficient=0.8,
                DefaultInitialWeight=240,
                DefaultFinalWeight=360
            ),
            dict(
                AnimalType=AnimalType.beef_replacement_heifers.value,
                BaselineMaintenanceCoefficient=0.322,
                GainCoefficient=0.8,
                DefaultInitialWeight=240,
                DefaultFinalWeight=360
            ),
            dict(
                AnimalType=AnimalType.beef_finishing_steer.value,
                BaselineMaintenanceCoefficient=0.322,
                GainCoefficient=1.0,
                DefaultInitialWeight=310,
                DefaultFinalWeight=610
            ),
            dict(
                AnimalType=AnimalType.beef_finishing_heifer.value,
                BaselineMaintenanceCoefficient=0.322,
                GainCoefficient=0.8,
                DefaultInitialWeight=300,
                DefaultFinalWeight=580
            ),

            # """
            # Dairy Cattle
            # Footnote 1
            # Dairy Cattle Data Sources :
            # BaselineMaintenanceCoefficient = IPCC (2019, Table 10.4)
            # GainCoefficient = IPCC (2019, Eq. 10.6)
            # DefaultInitialWeight = Lactanet (2020)
            # DefaultFinalWeight = Lactanet (2020)
            # """

            dict(
                AnimalType=AnimalType.dairy_lactating_cow.value,
                BaselineMaintenanceCoefficient=0.386,
                GainCoefficient=0.8,
                DefaultInitialWeight=687,
                DefaultFinalWeight=687
            ),
            dict(
                AnimalType=AnimalType.dairy_dry_cow.value,
                BaselineMaintenanceCoefficient=0.322,
                GainCoefficient=0.8,
                DefaultInitialWeight=687,
                DefaultFinalWeight=687
            ),
            dict(
                AnimalType=AnimalType.dairy_heifers.value,
                BaselineMaintenanceCoefficient=0.322,
                GainCoefficient=0.8,
                DefaultInitialWeight=637,
                DefaultFinalWeight=687
            ),
            dict(
                AnimalType=AnimalType.dairy_bulls.value,
                BaselineMaintenanceCoefficient=0.37,
                GainCoefficient=1.2,
                DefaultInitialWeight=1200,
                DefaultFinalWeight=1200
            ),
            dict(
                AnimalType=AnimalType.dairy_calves.value,
                BaselineMaintenanceCoefficient=0,
                GainCoefficient=0,
                DefaultInitialWeight=45,
                DefaultFinalWeight=127
            )
        ],
        path=PathsHolosResources.Table_16_Livestock_Coefficients_BeefAndDairy_Cattle_Provider
    )

    table_16.write_data_to_csv(
        comments=[
            'Table 16. Livestock coefficients for beef cattle and dairy cattle.',
            'source: https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_16_Livestock_Coefficients_BeefAndDairy_Cattle_Provider.cs#L13',
            '',
            'The value of "DefaultFinalWeight" was modified from 260 kg to 90 kg, according to the default values set in the GUI.'
        ])


def set_table_30():
    """

    Holos Source Code Footnotes:
        Footnote 1: C, N and P composition values for straw (barley) and wood-chip bedding are averages of data recorded in 1998 and 1999 in Larney et al. (2008);
                straw bedding application rates for beef cattle are from Chai et al. (2014), originally based on Larney et al. (2008) and Gilhespy et al. (2009)
        *    Footnote 2: Wood-chip bedding is a mixture of sawdust and bark peelings derived from 80% lodgepole pine (Pinus contorta var. latifolia  Engelm.) and 20% white
                spruce [Picea glauca (Moench)Voss].
        *    Footnote 3: “Drylot” refers to milking parlours, yards and exercise lots.
        *    Footnote 4: Values for bedding amounts are based on minimum values for recommended bedding per 450 kg animal weight from Lorimor et al. (2004, Table 13).
                We assumed an average dairy cow weight of 687 kg (Lactanet, 2020) (sand for freestall barn: 15.9 kg/450 kg * 687 kg = 24.3 kg head-1 day-1;
                shavings and sawdust for tie-stall barn: 1.4 kg/450 kg * 687 kg = 1.9 kg head-1 day-1) – due to a lack of available data, bedding application
                rates for sand for freestall barns and shavings and sawdust for freestall barns were also applied to other dairy housing types. For swine, calculations
                assumed an average weight for sows and boars of 198 kg (ECCC, 2022) (chopped straw: 1.8 kg/450 kg * 198 kg = 0.79 kg head-1 day-1;
                long straw: 1.6 kg/450 kg * 198 kg = 0.7 kg head-1 day-1). For poultry we assumed an average weight of 0.9 kg for broilers, 1.8 kg for layers,
                and 6.8 kg for turkeys (ECCC, 2022). For sawdust bedding this gave application rates of: broilers – 0.7 kg/450 kg * 0.9 kg =  = 0.0014 kg head-1 day-1;
                for layers – 0.7 kg/450 kg * 1.8 kg = 0.0028 kg head-1 day-1; for turkeys – 0.7 kg/450 kg * 6.8 kg = 0.011 kg head-1 day-1.
        *    Footnote 5: Dairy manure soilds separated from manure liquid using a screw press and composted and dried; also sometimes referred to as recycled manure solids,
                dried manure solids, undigested feedstuffs or more commonly compost bedding (OMAFRA, 2015). Values from Misselbrook and Powell (2005, Table 1).
        *    Footnote 6: Values for long and chopped straw follow Chai et al. (2016) and are originally from Rotz et al. (2013).
        *    Footnote 7: Due to a lack of data, total C, total N, total P and C:N ratio values for wood-chip bedding from Larney et al. (2008) are used for wood shavings
                and sawdust bedding for dairy cattle, sheep, swine and poultry.
        *    Footnote 8: Bedding application rates for sheep were obtained from the Canadian Sheep Foundation (2021), and applied to all bedding options. The application
                rate of 0.57 was calculated as the midpoint of the recommended 0.45-0.68 kg head-1 day-1 range provided.
        *    Footnote 9: Following Chai et al. (2016), a total N content value of 0.0057 (derived from Larney et al., 2008) was used for chopped straw bedding for dairy
                cattle; due to a lack of data, the total C, total N, total P and C:N ratio values for straw bedding from Larney et al. (2008) were applied to
                long- and chopped-straw bedding for dairy cows, swine and poultry.
        *    Footnote 10: Bedding options for sheep were identified from the Canadian Sheep Foundation (2021). Nutrient concentration values for straw and wood shavings
                for beef cattle were used for sheep in a drylot/corral and barn.
        *    Footnote 11: For Other livestock, straw was assumed to be the main bedding type and total C, total N, total P and C:N ratio values for straw bedding from
                Larney et al. (2008) were applied. For llamas and alpacas and goats, the bedding application rate for sheep was used; for deer and elk, horses,
                mules and bison, the bedding application rate for beef cattle (feedlot) was used as no data for these animals groups was available.
        *   Footnote  12: Values for moisture content of bedding from Ferraz et al. (2020). The moisture content for straw is the mean of values for barley straw (9.8%)
                and wheat straw (9.33%); the moisture content for sawdust is the value for dried sawdust.

    """
    table_30 = _HolosTable(
        name='Table_30_Default_Bedding_Material_Composition_Provider',
        data=[
            # Beef
            dict(
                AnimalType=AnimalType.beef.value,
                BeddingMaterial=BeddingMaterialType.straw.value,  # Footnote 1
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.beef.value,
                BeddingMaterial=BeddingMaterialType.wood_chip.value,  # Footnotes 1, 2
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=12.82  # Footnote12
            ),
            # Dairy
            dict(
                AnimalType=AnimalType.dairy.value,
                BeddingMaterial=BeddingMaterialType.sand.value,  # Footnote 4

                # set all following values to 0 to mimic the behavior in cs code
                TotalNitrogenKilogramsDryMatter=0,
                TotalCarbonKilogramsDryMatter=0,
                TotalPhosphorusKilogramsDryMatter=0,
                CarbonToNitrogenRatio=0,
                MoistureContent=0  # Footnote12
            ),
            dict(
                AnimalType=AnimalType.dairy.value,
                BeddingMaterial=BeddingMaterialType.separated_manure_solid.value,  # Footnote 5
                TotalNitrogenKilogramsDryMatter=0.033,
                TotalCarbonKilogramsDryMatter=0.395,
                TotalPhosphorusKilogramsDryMatter=0,
                CarbonToNitrogenRatio=12,
                MoistureContent=0
            ),
            dict(
                AnimalType=AnimalType.dairy.value,
                BeddingMaterial=BeddingMaterialType.straw_long.value,  # Footnote 6
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.dairy.value,
                BeddingMaterial=BeddingMaterialType.straw_chopped.value,  # Footnote 6
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.dairy.value,
                BeddingMaterial=BeddingMaterialType.shavings.value,  # Footnotes 4, 7
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.09  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.dairy.value,
                BeddingMaterial=BeddingMaterialType.sawdust.value,  # Footnotes 4, 7
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.99  # Footnote 12
            ),
            # Swine
            dict(
                AnimalType=AnimalType.swine.value,
                BeddingMaterial=BeddingMaterialType.straw_long.value,  # Footnotes 4, 9
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.swine.value,
                BeddingMaterial=BeddingMaterialType.straw_chopped.value,  # Footnotes 4, 9
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57  # Footnote 12
            ),
            # Sheep
            dict(
                AnimalType=AnimalType.sheep.value,
                BeddingMaterial=BeddingMaterialType.straw.value,  # Footnote 7
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.sheep.value,
                BeddingMaterial=BeddingMaterialType.shavings.value,  # Footnote 7
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.09  # Footnote 12
            ),
            # Poultry
            dict(
                AnimalType=AnimalType.poultry.value,
                BeddingMaterial=BeddingMaterialType.straw.value,  # Footnote 9
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5,
                MoistureContent=9.57  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.poultry.value,
                BeddingMaterial=BeddingMaterialType.shavings.value,  # Footnote 9
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.09  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.poultry.value,
                BeddingMaterial=BeddingMaterialType.sawdust.value,  # Footnotes 4, 7
                TotalNitrogenKilogramsDryMatter=0.00185,
                TotalCarbonKilogramsDryMatter=0.506,
                TotalPhosphorusKilogramsDryMatter=0.000275,
                CarbonToNitrogenRatio=329.5,
                MoistureContent=10.99  # Footnote 12
            ),
            # Other Livestock
            dict(
                AnimalType=AnimalType.llamas.value,
                BeddingMaterial=BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.alpacas.value,
                BeddingMaterial=BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.deer.value,
                BeddingMaterial=BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.elk.value,
                BeddingMaterial=BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.goats.value,
                BeddingMaterial=BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.horses.value,
                BeddingMaterial=BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.mules.value,
                BeddingMaterial=BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5  # Footnote 12
            ),
            dict(
                AnimalType=AnimalType.bison.value,
                BeddingMaterial=BeddingMaterialType.straw.value,
                MoistureContent=9.57,
                TotalNitrogenKilogramsDryMatter=0.0057,
                TotalCarbonKilogramsDryMatter=0.447,
                TotalPhosphorusKilogramsDryMatter=0.000635,
                CarbonToNitrogenRatio=90.5  # Footnote 12
            )
        ],
        path=PathsHolosResources.Table_30_Default_Bedding_Material_Composition_Provider)
    table_30.write_data_to_csv(
        comments=[
            'Table 30. Default bedding application rates and composition of bedding materials for all livestock groups.',
            'source: https://github.com/holos-aafc/Holos/blob/396f1ab9bc7247e6d78766f9445c14d2eb7c0d9d/H.Core/Providers/Animals/Table_30_Default_Bedding_Material_Composition_Provider.cs#L15'
        ])
    pass


def set_tillage_factor_table():
    table_tillage = _HolosTable(
        name='Table_Tillage_Factor',
        data=[
            dict(
                SoilFunctionalCategory=SoilFunctionalCategory.Brown,
                TillageType=TillageType.Intensive,
                TillageFactor=1),
            dict(
                SoilFunctionalCategory=SoilFunctionalCategory.Brown,
                TillageType=TillageType.Reduced,
                TillageFactor=0.9),
            dict(
                SoilFunctionalCategory=SoilFunctionalCategory.Brown,
                TillageType=TillageType.NoTill,
                TillageFactor=0.8),
            dict(
                SoilFunctionalCategory=SoilFunctionalCategory.DarkBrown,
                TillageType=TillageType.Intensive,
                TillageFactor=1),
            dict(
                SoilFunctionalCategory=SoilFunctionalCategory.DarkBrown,
                TillageType=TillageType.Reduced,
                TillageFactor=0.85),
            dict(
                SoilFunctionalCategory=SoilFunctionalCategory.DarkBrown,
                TillageType=TillageType.NoTill,
                TillageFactor=0.7),
            dict(
                SoilFunctionalCategory=SoilFunctionalCategory.Black,
                TillageType=TillageType.Intensive,
                TillageFactor=1),
            dict(
                SoilFunctionalCategory=SoilFunctionalCategory.Black,
                TillageType=TillageType.Reduced,
                TillageFactor=0.8),
            dict(
                SoilFunctionalCategory=SoilFunctionalCategory.Black,
                TillageType=TillageType.NoTill,
                TillageFactor=0.6)

        ],
        path=PathsHolosResources.Table_Tillage_Factor)

    table_tillage.write_data_to_csv(
        comments=[
            'Holos source code: https://github.com/holos-aafc/Holos/blob/e644d8e52446faefe3d7503565a723563bba61fe/H.Core/Calculators/Tillage/TillageFactorCalculator.cs#L27',
        ])


if __name__ == '__main__':
    set_table_16()
    set_table_30()
    set_tillage_factor_table()
