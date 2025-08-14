from pyholos.core_constants import CoreConstants


class Defaults:
    EmissionFactorForLeachingAndRunoff = 0.011  # Updated to IPCC 2019 value
    """(kg(N2O-N) kg(N)-1) emission factor for leaching and runoff"""

    PercentageOfProductReturnedToSoilForPerennials = 35
    """(%) percentage of the perennial crops biomass returned to soil after harvest"""

    PercentageOfRootsReturnedToSoilForPerennials = 100
    """(%) percentage of the perennial crops root biomass returned to soil after harvest"""

    PercentageOfProductReturnedToSoilForAnnuals = 2
    """(%) percentage of the annual crops biomass returned to soil after harvest"""

    PercentageOfRootsReturnedToSoilForAnnuals = 100
    """(%) percentage of the annual crops root biomass returned to soil after harvest"""

    PercentageOfStrawReturnedToSoilForAnnuals = 100
    """(%) percentage of the annual crops straw biomass returned to soil after harvest"""

    PercentageOfProductReturnedToSoilForRootCrops = 0
    """(%) percentage of the root crops biomass returned to soil after harvest"""

    PercentageOfStrawReturnedToSoilForRootCrops = 100
    """(%) percentage of the root crops straw biomass returned to soil after harvest"""

    PercentageOfProductYieldReturnedToSoilForSilageCrops = 35
    """(%) percentage of the silage crops biomass returned to soil after harvest"""

    PercentageOfRootsReturnedToSoilForSilageCrops = 100
    """(%) percentage of the annual crops root biomass returned to soil after harvest"""

    PercentageOfProductYieldReturnedToSoilForCoverCrops = 100
    """(%) percentage of the cover crops biomass returned to soil after harvest"""

    PercentageOfProductYieldReturnedToSoilForCoverCropsForage = 35
    """(%) percentage of the cover crops forage biomass returned to soil after harvest"""

    PercentageOfProductYieldReturnedToSoilForCoverCropsProduce = 0
    """(%) percentage of the cover crops produce biomass returned to soil after harvest"""

    PercentageOfStrawReturnedToSoilForCoverCrops = 100
    """(%) percentage of the cover crops straw biomass returned to soil after harvest"""

    PercentageOfRootsReturnedToSoilForCoverCrops = 100
    """(%) percentage of the cover crops root biomass returned to soil after harvest"""

    PercentageOfProductReturnedToSoilForRangelandDueToHarvestLoss = 35
    """(%) percentage of the rangeland product biomass returned to soil due to harvest loss"""

    PercentageOfProductReturnedToSoilForRangelandDueToGrazingLoss = CoreConstants.ValueNotDetermined
    """(%) percentage of the rangeland product biomass returned to soil due to grazing loss"""

    PercentageOfRootsReturnedToSoilForRangeland = 100
    """(%) percentage of the rangeland root biomass returned to soil after harvest"""

    PercentageOfProductReturnedToSoilForFodderCorn = 35
    """(%) percentage of the fodder corn product biomass returned to soil after harvest"""

    PercentageOfRootsReturnedToSoilForFodderCorn = 100
    """(%) percentage of the fodder corn root biomass returned to soil after harvest"""

    DecompositionRateConstantYoungPool = 0.8
    DecompositionRateConstantOldPool = 0.00605
    OldPoolCarbonN = 0.1
    NORatio = 0.1
    EmissionFactorForVolatilization = 0.01
    FractionOfNLostByVolatilization = 0.21
    MicrobeDeath = 0.2
    Denitrification = 0.5

    HumificationCoefficientAboveGround = 0.125
    HumificationCoefficientBelowGround = 0.3
    HumificationCoefficientManure = 0.31

    DefaultRunInPeriod = 15

    CarbonConcentration = CoreConstants.CarbonConcentration

    # for annual crops
    EmergenceDay = 141
    """(julian day) day of plant emergence for annual crops"""

    RipeningDay = 197
    """(julian day) day of plant ripening for annual crops"""

    Variance = 300
    """width of distribution function for annual crops"""

    # for perennial crops
    EmergenceDayForPerennials = 75
    """(julian day) day of plant emergence for perennial crops"""

    RipeningDayForPerennials = 300
    """(julian day) day of plant ripening for perennial crops"""

    VarianceForPerennials = 1500
    """width of distribution function for perennial crops"""

    # for all crops
    Alfa = 0.7
    """(-) minimum water storage fraction of wilting_point"""

    DecompositionMinimumTemperature = -3.78
    """(degree Celsius) maximum cardinal temperature for decomposition"""

    DecompositionMaximumTemperature = 30
    """(degree Celsius) minimum cardinal temperature for decomposition"""

    MoistureResponseFunctionAtWiltingPoint = 0.18
    """(mm3/mm3) soil volumetric water content at reference wilting point"""

    MoistureResponseFunctionAtSaturation = 0.42
    """(mm3/mm3) soil volumetric water content at reference saturation"""
