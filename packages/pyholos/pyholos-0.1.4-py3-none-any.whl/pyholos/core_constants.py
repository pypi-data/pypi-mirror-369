class CoreConstants:
    DefaultNumberOfDecimalPlaces: int = 3

    DaysInYear: int = 365

    ValueNotDetermined = 0
    NotApplicable = -100000

    NitrogenDepositionAmount = 5
    """(kg(N)/ha/year) Atmospheric Nitrogen deposition amount
    Holos source doc: page 74 in https://github.com/holos-aafc/Holos/raw/refs/heads/main/AAFC_Technical_Report_Holos_V4.0_Algorithm_Document_DRAFTVersion_18Nov2024.docx
    """

    CarbonConcentration = 0.45
    """(kg(C)/kg(plant biomass)) carbon concentration in plant biomass
    Holos source code: https://github.com/holos-aafc/Holos/blob/b183dab99d211158d1fed9da5370ce599ac7c914/H.Core/CoreConstants.cs#L90
    Holos source doc: footnote in page 37 in https://github.com/holos-aafc/Holos/raw/refs/heads/main/AAFC_Technical_Report_Holos_V4.0_Algorithm_Document_DRAFTVersion_18Nov2024.docx
    """

    MinimumYear = 1970
