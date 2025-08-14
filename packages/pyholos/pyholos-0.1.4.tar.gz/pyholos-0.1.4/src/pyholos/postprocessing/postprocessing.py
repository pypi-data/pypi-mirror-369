from pathlib import Path

from pandas import DataFrame, read_csv


def read_equivalent_co2_emissions(
        path_outputs: Path
) -> DataFrame:
    df = read_csv(path_outputs, decimal='.', sep=',').rename(columns=lambda x: x.strip()).ffill()
    cols_to_keep = [s for s in df.columns if "Unnamed" not in s]
    df = df[cols_to_keep].dropna(axis=0)
    df.loc[:, 'Farm Name'] = df['Farm Name'].apply(lambda x: x.replace('_Farm_', '')).to_list()

    df = df[~df['Component Group Name'].str.contains('Totals|Total')]
    df = df[~df['Farm Name'].str.contains('All Farms')]

    return df


def read_farm_monthly_equivalent_co2_emissions(
        path_outputs: Path,
        year: int
) -> DataFrame:
    df = read_csv(path_outputs, decimal='.', sep=',').rename(columns=lambda x: x.strip())
    df = df[[s for s in df.columns if "Unnamed" not in s]]
    fill_cols = ['Farm Name', 'Component Category', 'Component Name', 'Group Name']
    df.loc[:, fill_cols] = df.loc[:, fill_cols].ffill()
    df = df.dropna(axis=0)
    df.loc[:, 'Farm Name'] = df['Farm Name'].apply(lambda x: x.replace('_Farm', '')).to_list()
    df.loc[:, 'Year'] = df['Year'].astype(str)

    df = df[
        (~df['Year'].str.contains('Totals|Total')) &
        (df['Year'] == str(year))
        ]
    df = df[~df['Farm Name'].str.contains('All Farms')]

    return df.drop(columns=['Year'])
