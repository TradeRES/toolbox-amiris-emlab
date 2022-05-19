"""
This file contains some helper functions for the scripts in resources/scripts.
Ingrid Sanchez 17-2-2022 reused
Jim Hommes - 29-6-2021
"""
from helpers.spinedb import *
import pandas as pd

def get_current_ticks(db: SpineDB, offset: int):
    """
    This function retrieves the most recent system clock ticks and translates it also to the COMPETES clock ticks.

    """
    class_name = "Configuration"
    object_name = "SimulationYears"
    current_tick = next(int(i['parameter_value']) for i in db.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                        if i['parameter_name'] == 'CurrentYear')
    return current_tick

def get_traderes_technologies(db: SpineDB):
    """
    This function retrieves the most recent system clock ticks and translates it also to the COMPETES clock ticks.

    :param db: SpineDB

    """
    class_name = "unit"
    technology = []
    for i in db.query_object_parameter_values_by_object_class(class_name):
        if i['object_name'] not in technology:
            technology.append(i['object_name'])
    df = pd.DataFrame(technology)
    df.to_excel('technology.xlsx', index = False)



if __name__ == "__main__":
    print('===== Starting script =====')
    db_url = 'sqlite:///C:\\Users\\isanchezjimene\\Documents\\TraderesCode\\toolbox-amiris-emlab\\.spinetoolbox\\items\\tradereslocal\\traderesLocal.sqlite'
    db_traderes = SpineDB(db_url)
    get_traderes_technologies(db_traderes)
    db_traderes.close_connection()
    print('===== End  =====')