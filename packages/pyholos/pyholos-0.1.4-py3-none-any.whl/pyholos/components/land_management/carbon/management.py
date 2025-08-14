from pyholos.core_constants import CoreConstants


def calculate_management_factor(
        climate_parameter: float,
        tillage_factor: float,
) -> float:
    """Calculates the management factor.

    Args:
        climate_parameter: (-) climate parameter
        tillage_factor: (-) tillage factor

    Returns:

    Holos source code:
        https://github.com/holos-aafc/Holos/blob/90fad0a9950183da217137490cb756104ba3f7f4/H.Core/Services/LandManagement/FieldResultsService.cs#L294
        https://github.com/holos-aafc/Holos/blob/90fad0a9950183da217137490cb756104ba3f7f4/H.Core/Calculators/Climate/ClimateParameterCalculator.cs#L269
    """

    return round(climate_parameter * tillage_factor, CoreConstants.DefaultNumberOfDecimalPlaces)
