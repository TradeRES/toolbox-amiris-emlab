"""
Prepare data for usage in AMIRIS

Routines have to be done only once per new model run.
"""
import pandas as pd

DEMAND_DATA_CONFIG = {
    "INPUT_FOLDER": "amiris-config/data/demand_raw",
    "OUTPUT_FOLDER": "amiris-config/data/demand_processed",
    "LOAD_FILE": "load.csv",
    "SHEDDING_FILES": None,
}


def prepare_demand_data():
    """Read in and prepare demand data. Store prepared data sets to file"""
    obtain_shedding_series_from_file()


def obtain_shedding_series_from_file():
    pass
