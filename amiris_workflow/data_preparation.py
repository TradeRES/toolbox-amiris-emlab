"""
Prepare data for usage in AMIRIS

Routines have to be done only once per new model run.
"""
import os
from typing import List, Dict

import pandas as pd
from matplotlib import pyplot as plt

DEMAND_DATA_CONFIG = {
    "INPUT_FOLDER": "amiris-config/data/demand_raw/",
    "OUTPUT_FOLDER": "amiris-config/data/demand_processed/",
    "LOAD_FILE": "load.csv",
    "INDEX_FILE": "proper_index.csv",
}


def prepare_demand_data():
    """Read in and prepare demand data. Store prepared data sets to file"""
    load_incl_shedding_clusters = pd.read_csv(
        f"{DEMAND_DATA_CONFIG['INPUT_FOLDER']}{DEMAND_DATA_CONFIG['LOAD_FILE']}", sep=";", header=None, index_col=0
    )
    shedding_series = obtain_shedding_series_from_file(DEMAND_DATA_CONFIG)
    proper_index = pd.read_csv(
        f"{DEMAND_DATA_CONFIG['INPUT_FOLDER']}{DEMAND_DATA_CONFIG['INDEX_FILE']}", sep=";", header=None, index_col=0
    ).index
    load_incl_shedding_clusters = reindex_time_series(load_incl_shedding_clusters, proper_index)
    load_excl_shedding_clusters = load_incl_shedding_clusters.copy()
    for name, series in shedding_series.items():
        reindexed_series = reindex_time_series(series, proper_index)
        reindexed_series.to_csv(f"{DEMAND_DATA_CONFIG['OUTPUT_FOLDER']}{name}", sep=";", header=False)
        load_excl_shedding_clusters -= reindexed_series
    load_excl_shedding_clusters.to_csv(
        f"{DEMAND_DATA_CONFIG['OUTPUT_FOLDER']}{DEMAND_DATA_CONFIG['LOAD_FILE']}", sep=";", header=False
    )


def obtain_shedding_series_from_file(config: Dict[str, str]) -> Dict[str, pd.DataFrame]:
    """Read in shedding time series from file"""
    shedding_series = {}
    shedding_series_names = get_all_csv_files_in_folder_except(
        folder=config["INPUT_FOLDER"],
        exceptions=[config["LOAD_FILE"], config["INDEX_FILE"]],
    )
    for name in shedding_series_names:
        shedding_series[name.rsplit("/", 1)[1]] = pd.read_csv(name, sep=";", header=None, index_col=0)

    return shedding_series


def get_all_csv_files_in_folder_except(folder: str, exceptions: List) -> List[str]:
    """Return all csv files in a folder except the given ones"""
    if exceptions is None:
        exceptions = list()
    return [folder + "/" + file for file in os.listdir(folder) if file.endswith(".csv") and file not in exceptions]


def reindex_time_series(time_series: pd.DataFrame, proper_index: pd.Index) -> pd.DataFrame:
    """Reindex given time series by assigning proper index for AMIRIS simulations"""
    time_series.index = proper_index
    return time_series


if __name__ == "__main__":
    prepare_demand_data()
