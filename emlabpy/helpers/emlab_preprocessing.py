"""
Because of the interpretation of Spine data, the EMLAB SpineDB needs preprocessing.
This script sets all the power plant statuses to OPR or DECOM according to EMLAB rules and not the COMPETES rules.
This is necessary as COMPETES works with aggregates: EMLAB with statuses actual to the current tick.

Arg1: URL to SpineDB EM-Lab

Jim Hommes - 29-6-2021
"""
import sys
from spinedb import SpineDB
from helper_functions import get_current_ticks


def set_correct_power_plant_statuses(db_emlab, db_emlab_powerplants, current_competes_tick):
    """
    This function sets all the PowerPlant statuses to whether they are decommissioned or not through the logic of
    COMPETES. COMPETES works in aggregates and will add a PowerPlant with (D) in the name to tell it's decom'd.
    If current_tick > decom year, the plant is decom'd.

    THe VRE are aggregated: see COMPETES structure as to why.

    :param db_emlab: SpineDB
    :param db_emlab_powerplants: Powerplants queried from EMLAB SpineDB
    :param current_competes_tick: int
    """
    print('Setting correct powerplant statuses...')
    powerplant_statuses = {row['object_name']: row['parameter_value'] for row in db_emlab_powerplants if
                           row['object_class_name'] == 'PowerPlants' and row['parameter_name'] == 'STATUSNL'}

    # Check if build year >= current_competes_tick
    for row in [i for i in db_emlab_powerplants if
                i['object_class_name'] == 'PowerPlants' and i['parameter_name'] == 'ON-STREAMNL']:
        if row['parameter_value'] <= current_competes_tick:
            powerplant_statuses[row['object_name']] = 'OPR'
        else:
            powerplant_statuses[row['object_name']] = 'DECOM'

    # If name has a (D), set referred to unit to DECOM
    for row in [i for i in db_emlab_powerplants if
                i['object_class_name'] == 'PowerPlants' and i['parameter_name'] == 'ON-STREAMNL']:
        if '(D)' in row['object_name']:
            powerplant_statuses[row['object_name']] = 'DECOM'
            if row['parameter_value'] <= current_competes_tick:
                powerplant_statuses[row['object_name'].replace('(D)', '')] = 'DECOM'

    # Sum all BIOMASS, WASTE and HYDRO
    # Set them all DECOM and introduce one new OPR with the sum
    powerplants_biomass = get_power_plants_by_string_in_object_name('BIOMASS Standalone', db_emlab_powerplants)
    powerplants_hydro = get_power_plants_by_string_in_object_name('HYDRO CONV', db_emlab_powerplants)
    powerplants_waste = get_power_plants_by_string_in_object_name('WASTE Standalone', db_emlab_powerplants)

    mw_biomass_sum = decom_power_plants_and_return_sum(powerplants_biomass, powerplant_statuses, current_competes_tick,
                                                       db_emlab_powerplants)
    mw_hydro_sum = decom_power_plants_and_return_sum(powerplants_hydro, powerplant_statuses, current_competes_tick,
                                                     db_emlab_powerplants)
    mw_waste_sum = decom_power_plants_and_return_sum(powerplants_waste, powerplant_statuses, current_competes_tick,
                                                     db_emlab_powerplants)

    print('Setting up for DB import...')
    db_emlab.import_object_parameter_values([('PowerPlants', 'NED BIOMASS Standalone SUM', 'MWNL', mw_biomass_sum, '0'),
                                             ('PowerPlants', 'NED HYDRO CONV SUM', 'MWNL', mw_hydro_sum, '0'),
                                             ('PowerPlants', 'NED WASTE Standalone SUM', 'MWNL', mw_waste_sum, '0')])

    object_parameter_values = [('PowerPlants', object_name.strip(), 'STATUSNL', value, '0') for (object_name, value) in
                               powerplant_statuses.items()]
    db_emlab.import_object_parameter_values(object_parameter_values)


def decom_power_plants_and_return_sum(list_of_plants, powerplant_statuses, current_competes_tick, db_emlab_powerplants):
    """
    This function decoms a list of plants and sums the MW until the current year is reached.
    There is one object with SUM in it's name: this represents the total amount in operation of the VRE.

    :param list_of_plants: List
    :param powerplant_statuses: Statuses
    :param current_competes_tick: int
    :param db_emlab_powerplants: PowerPlants as queried from SpineDB.
    :return: Sum of MWs in operation.
    """
    res = 0
    for (plant, year) in list_of_plants.items():
        if 'SUM' not in plant:
            powerplant_statuses[plant] = 'DECOM'
            if year <= current_competes_tick:
                res += next(row['parameter_value'] for row in db_emlab_powerplants if
                            row['object_class_name'] == 'PowerPlants' and row['object_name'] == plant and row[
                                'parameter_name'] == 'MWNL')
    return res


def get_power_plants_by_string_in_object_name(object_name_part, db_emlab_powerplants):
    """
    Return list of power plants in which the string can be found.

    :param object_name_part: string
    :param db_emlab_powerplants: PowerPlants as queried from EMLAB SpineDB
    :return: List
    """
    return {row['object_name']: row['parameter_value'] for row in db_emlab_powerplants
            if row['object_class_name'] == 'PowerPlants'
            and object_name_part in row['object_name']
            and row['parameter_name'] == 'ON-STREAMNL'}


def hotfix_disable_double_vre_plants(db_emlab, current_emlab_tick):
    object_names = ['NED SUN PV 2020', 'NED WIND OFFSHORE 2020', 'NED WIND ONSHORE 2020']
    db_emlab.import_object_parameter_values([('PowerPlants', i, 'STATUSNL', 'DECOM', str(current_emlab_tick))
                                             for i in object_names])


def execute_all_preprocessing():
    """
    This function executes all steps of this script.
    """
    print('Creating connection to SpineDB...')
    db_emlab = SpineDB(sys.argv[1])
    db_config = SpineDB(sys.argv[2])
    print('Querying SpineDB...')
    start_simulation_year = next(int(i['parameter_value']) for i
                                 in db_config.query_object_parameter_values_by_object_class('Coupling Parameters')
                                 if i['object_name'] == 'Start Year')
    db_emlab_powerplants = db_emlab.query_object_parameter_values_by_object_class('PowerPlants')

    current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab,
                                                                                                 start_simulation_year)
    print('Done querying')

    print('Current EMLAB Tick: ' + str(current_emlab_tick))
    print('Current COMPETES Tick: ' + str(current_competes_tick))

    try:
        set_correct_power_plant_statuses(db_emlab, db_emlab_powerplants, current_competes_tick)
        hotfix_disable_double_vre_plants(db_emlab, current_emlab_tick)

        print('Committing...')
        db_emlab.commit('DB EMLAB Preprocessing tick ' + str(current_competes_tick))

    except Exception as e:
        print('Exception thrown: ' + str(e))
        raise
    finally:
        db_emlab.close_connection()
        db_config.close_connection()


if __name__ == "__main__":
    print('===== Start EMLAB Preprocessing script =====')
    execute_all_preprocessing()
    print('===== End of EMLAB Preprocessing script =====')
