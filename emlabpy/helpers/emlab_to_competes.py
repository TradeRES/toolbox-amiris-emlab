"""
This script handles all communication passed from the EM-Lab SpineDB to the COMPETES SpineDB.
As of this moment this only entails the CO2 Price and Capacity Revenues.

Arg1: URL to SpineDB EMLAB
Arg2: URL to SpineDB COMPETES

Jim Hommes - 1-6-2021
"""
import sys
import math
from spinedb import SpineDB
from helper_functions import get_current_ticks


def export_capacity_market_revenues_for_technology_vre(db_competes, participating_technology, current_competes_tick,
                                                       cm_market_clearing_price, look_ahead):
    """
    This function exports the capacity market revenues for VRE technologies. It looks at the VRE Technologies table,
    which contains both the CAPEX and Fixed O&M costs.

    :param db_competes: SpineDB
    :param participating_technology: Tech name that will receive reduction (combi with fuel)
    :param current_competes_tick: Current clock tick
    :param cm_market_clearing_price: CM price
    :param look_ahead: Investment horizon (years)
    :param step: Time step of model
    """
    init_vre_technologies = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'INIT VRE Technologies', participating_technology)[0]['parameter_value']
    vre_technologies = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'VRE Technologies', participating_technology)[0]['parameter_value']

    init_fixed_om = init_vre_technologies.get_value(str(current_competes_tick)) \
        .get_value('Fixed O&M(Euro/kW/yr)')
    print('INIT Fixed O&M: ' + str(init_fixed_om))

    if init_fixed_om - cm_market_clearing_price < 0:
        print('CM Price > Fixed O&M')
        parameter_map = vre_technologies.get_value(str(current_competes_tick))
        parameter_map_with_step = vre_technologies.get_value(str(current_competes_tick + look_ahead))
        parameter_map.set_value('Fixed O&M(Euro/kW/yr)', float(0))

        init_capex = init_vre_technologies.get_value(str(current_competes_tick + look_ahead)) \
            .get_value('Capex(Euro/kW)')
        print('INIT CAPEX: ' + str(init_capex))

        parameter_map_with_step.set_value('Capex(Euro/kW)', float(init_capex - (cm_market_clearing_price - init_fixed_om)))
        print('New CAPEX: ' + str(init_capex - (cm_market_clearing_price - init_fixed_om)))
        vre_technologies.set_value(str(current_competes_tick), parameter_map)
        vre_technologies.set_value(str(current_competes_tick + look_ahead), parameter_map_with_step)
    else:
        print('CM Price <= Fixed O&M')
        parameter_map = vre_technologies.get_value(str(current_competes_tick))
        parameter_map.set_value('Fixed O&M(Euro/kW/yr)', float(init_fixed_om - cm_market_clearing_price))
        print('New Fixed O&M: ' + str(init_fixed_om - cm_market_clearing_price))
        vre_technologies.set_value(str(current_competes_tick), parameter_map)

    db_competes.import_object_parameter_values([('VRE Technologies', participating_technology,
                                                 'VRE Technologies', vre_technologies, '0')])


def export_capacity_market_revenues_for_technology_nonvre(db_competes, participating_technology,
                                                          db_technology_combi_map_list, participating_fuel,
                                                          cm_market_clearing_price, current_competes_tick, look_ahead):
    """
    This function exports the capacity market revenues for Non VRE technologies. It does so by using the Technologies
    and Overnight Cost (OC) tables.

    :param db_competes: SpineDB
    :param participating_technology: The Tech name that will receive the reduction (combination with Fuel)
    :param db_technology_combi_map_list: The list of parameters (maps) from the technology table.
    :param participating_fuel: The Fuel name that will receive the reduction (combination with Tech)
    :param cm_market_clearing_price: CM price
    :param current_competes_tick: Clock tick
    :param look_ahead: Investment horizon
    :param step: Time step of model
    """
    # In case of Overnight Cost and Technologies, there is always only 1 parameter which is a SpineDB Map
    db_overnight_cost_map = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'Overnight Cost (OC)', participating_technology)[0]['parameter_value']
    db_initial_overnight_cost_map = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'INIT Overnight Cost (OC)', participating_technology)[0]['parameter_value']
    db_technology_combi_map = db_technology_combi_map_list[0]['parameter_value']
    db_initial_technology_combi_map = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'INIT Technologies', participating_technology)[0]['parameter_value']

    current_technorder = ''
    for technorder in db_technology_combi_map.indexes:
        if db_technology_combi_map.get_value(technorder).get_value('FUELNEW') == participating_fuel:
            current_technorder = technorder
            break

    db_technology_map = db_technology_combi_map.get_value(current_technorder)
    db_initial_technology_map = db_initial_technology_combi_map.get_value(current_technorder)
    if db_initial_technology_map is not None:
        fixed_om = float(db_initial_technology_map.get_value('FIXED O&M'))
        print('INIT Fixed O&M: ' + str(fixed_om))

        if cm_market_clearing_price > fixed_om:
            print('CM Price > Fixed O&M')

            if participating_technology == 'CHP' and participating_fuel == 'Derived GAS':
                participating_fuel = 'GAS' # Hotfix for data inconsistency

            # Set CAPEX
            init_capex = db_initial_overnight_cost_map.get_value(participating_fuel).get_value(str(current_competes_tick +
                                                                                                   look_ahead))
            print('INIT CAPEX: ' + str(init_capex))
            capex_map = db_overnight_cost_map.get_value(participating_fuel)
            capex_map.set_value(str(current_competes_tick + look_ahead),
                                float(init_capex - (cm_market_clearing_price - fixed_om)))
            print('New CAPEX: ' + str(init_capex - (cm_market_clearing_price - fixed_om)))
            db_overnight_cost_map.set_value(current_technorder, capex_map)
            # Set Fixed O&M
            db_technology_map.set_value('FIXED O&M', float(0))
            db_technology_combi_map.set_value(current_technorder, db_technology_map)
        else:
            print('CM Price <= Fixed O&M')
            db_technology_map.set_value('FIXED O&M', float(fixed_om - cm_market_clearing_price))
            print('New Fixed O&M: ' + str(fixed_om - cm_market_clearing_price))
            db_technology_combi_map.set_value(current_technorder, db_technology_map)

        db_competes.import_object_parameter_values(
            [('Technologies', participating_technology, 'Technologies', db_technology_combi_map, '0'),
             ('Overnight Cost (OC)', participating_technology, 'Overnight Cost (OC)',
              db_overnight_cost_map, '0')])
    else:
        print('Techn. Map not found for ' + str(participating_technology) + ', ' + str(participating_fuel))


def export_capacity_market_revenues_for_technology(db_competes, participating_technology, participating_fuel,
                                                   current_competes_tick, cm_market_clearing_price, look_ahead, step):
    """
    This function exports all capacity market revenues as Fixed O&M and CAPEX costs. It checks whether the technology
    is VRE or Non-VRE, and uses the appropriate function.

    :param db_competes: SpineDB
    :param participating_technology: A Technology worthy of receiving the reductions (str)
    :param participating_fuel: The Fuel that makes the Tech Fuel combination
    :param current_competes_tick: int
    :param cm_market_clearing_price: float
    :param look_ahead: Investment horizon in years
    :param step: Time step of model
    """
    # Query the Overnight Cost (OC), INIT Overnight Cost (OC) and Technologies tables from SpineDB
    db_technology_combi_map_list = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'Technologies', participating_technology)

    # If the list is 0, it's VRE which is not in Technologies
    if len(db_technology_combi_map_list) > 0:
        export_capacity_market_revenues_for_technology_nonvre(db_competes, participating_technology,
                                                              db_technology_combi_map_list, participating_fuel,
                                                              cm_market_clearing_price, current_competes_tick,
                                                              look_ahead)
    else:
        export_capacity_market_revenues_for_technology_vre(db_competes, participating_technology, current_competes_tick,
                                                           cm_market_clearing_price, look_ahead)


def get_cm_market_clearing_price(tick, db_emlab_marketclearingpoints):
    """
    This function returns the CM MCP for tick specified.
    :param tick: int
    :param db_emlab_marketclearingpoints: MCPs as queried from SpineDB EMLab
    :return: MCP (float)
    """
    market_clearing_point = next(row['object_name'] for row in db_emlab_marketclearingpoints if
                                 row['parameter_name'] == 'Market' and row[
                                     'parameter_value'] == 'DutchCapacityMarket' and row['alternative'] == str(tick))
    market_clearing_price = next(row['parameter_value'] for row in db_emlab_marketclearingpoints if
                                 row['object_name'] == market_clearing_point and row['parameter_name'] == 'Price')
    market_clearing_price = market_clearing_price / 1000  # EMLAB is in Euro / MWh - COMPETES is in Euro / kWh
    print('Current CM Market Clearing Price: ' + str(market_clearing_price))
    return market_clearing_price


def get_participating_technologies_in_capacity_market(db_emlab_powerplantdispatchplans, current_emlab_tick,
                                                      step, db_emlab_powerplants):
    """
    This function returns all participating technologies that get revenue from the Capacity Market.
    It returns a set so all values are distinct.

    :param db_emlab_powerplants: Power plants as extracted from SpineDB EM-Lab
    :param step: Time step of model
    :param db_emlab_powerplantdispatchplans: PPDPs as queried from SpineDB EMLab
    :param current_emlab_tick: int
    :return: Set of technology names
    """
    capacity_market_ppdps = [row['object_name'] for row in db_emlab_powerplantdispatchplans if
                             row['parameter_name'] == 'Market' and row['parameter_value'] == 'DutchCapacityMarket' and
                             row['alternative'] == str(current_emlab_tick - step)]
    capacity_market_accepted_ppdps = [row['object_name'] for row in db_emlab_powerplantdispatchplans if
                                      row['object_name'] in capacity_market_ppdps and row[
                                          'parameter_name'] == 'AcceptedAmount' and row['parameter_value'] > 0]
    capacity_market_participating_plants = [row['parameter_value'] for row in db_emlab_powerplantdispatchplans if
                                            row['object_name'] in capacity_market_accepted_ppdps and row[
                                                'parameter_name'] == 'Plant']
    capacity_market_participating_tech_fuel_combinations = set()
    for plant in capacity_market_participating_plants:
        tech = next(row['parameter_value'] for row in db_emlab_powerplants if
                    row['object_name'] == plant and
                    row['parameter_name'] == 'TECHTYPENL')
        fuel = next(row['parameter_value'] for row in db_emlab_powerplants if
                    row['object_name'] == plant and
                    row['parameter_name'] == 'FUELNL')
        capacity_market_participating_tech_fuel_combinations.add((tech, fuel))
    return capacity_market_participating_tech_fuel_combinations


def export_capacity_market_revenues(db_competes, current_emlab_tick, db_emlab_powerplantdispatchplans,
                                    db_emlab_marketclearingpoints, current_competes_tick, step, db_emlab_powerplants,
                                    look_ahead):
    """
    In the conceptual COMPETES EMLab coupling, the CM revenues are exported as Fixed O&M and CAPEX reduction.
    For all participating technologies the CM price gets subtracted from the Fixed O&M. If the Fixed O&M reaches 0,
    the rest is subtracted from the CAPEX.
    In order to correctly subtract this from year > 1 onwards, the function backtracks the previous Fixed O&M and
    CAPEX. In order to do this a second table, INIT Overnight Cost (OC) is used with the original CAPEX.

    :param db_emlab_powerplants: Power plants as extracted from EM-Lab SpineDB
    :param step: Model time step (years)
    :param look_ahead: Investment horizon (years)
    :param db_competes: SpineDB
    :param current_emlab_tick: int
    :param db_emlab_powerplantdispatchplans: PPDPs as queried from EMLab SpineDB
    :param db_emlab_marketclearingpoints: MCPs as queried from EMLab SpineDB
    :param current_competes_tick: int
    """
    print('Exporting CM Revenues to COMPETES...')
    if current_emlab_tick > 0:
        print('Current EMLAB tick ' + str(current_emlab_tick) + ' > 0 so editing Fixed O&M and CAPEX')

        capacity_market_participating_technologies = get_participating_technologies_in_capacity_market(
            db_emlab_powerplantdispatchplans, current_emlab_tick, step, db_emlab_powerplants)
        print('The participating technologies in the capacity market were: ' + str(
            capacity_market_participating_technologies))

        current_cm_market_clearing_price = get_cm_market_clearing_price(current_emlab_tick - step,
                                                                        db_emlab_marketclearingpoints)

        # For every participating technology the Fixed O&M, and if too little Fixed O&M the CAPEX will be reduced
        for participating_technology, participating_fuel in capacity_market_participating_technologies:
            print('Editing CAPEX and Fixed O&M for ' + str(participating_technology) + ', ' + participating_fuel)
            export_capacity_market_revenues_for_technology(db_competes, participating_technology, participating_fuel,
                                                           current_competes_tick, current_cm_market_clearing_price,
                                                           look_ahead, step)

    else:
        print('Current tick == 0, so not exporting anything of the CM revenues')


def get_co2_market_clearing_price(db_emlab_marketclearingpoints, current_emlab_tick):
    """
    This function retrieves the Market Clearing Price for the CO2Auction

    :param db_emlab_marketclearingpoints: Queried from SpineDB EMLab
    :param current_emlab_tick: int
    :return: The market clearing price (float)
    """
    print('Loading CO2 MarketClearingPrice...')
    mcp_object = next(row['object_name'] for row in db_emlab_marketclearingpoints if
                      row['parameter_name'] == 'Market' and row['parameter_value'] == 'CO2Auction' and row[
                          'alternative'] == str(current_emlab_tick))
    mcp = next(row['parameter_value'] for row in db_emlab_marketclearingpoints if
               row['object_name'] == mcp_object and row['parameter_name'] == 'Price')
    print('Price found: ' + str(mcp))
    return mcp


def export_co2_market_clearing_price(db_competes, db_emlab_marketclearingpoints, current_emlab_tick,
                                     co2_object_class_name, current_competes_tick, months, look_ahead):
    """
    This function exports the CO2 Market Clearing Price after the structure has been initialized.

    :param look_ahead: Amount of years ahead the investment will occur
    :param db_competes: SpineDB
    :param db_emlab_marketclearingpoints: MCP as queried at SpineDB EMLab
    :param current_emlab_tick: int
    :param co2_object_class_name: str
    :param current_competes_tick: int
    :param months: Array of months in COMPETES
    """
    mcp = get_co2_market_clearing_price(db_emlab_marketclearingpoints, current_emlab_tick)
    future_mcp = mcp * math.pow(1.025, look_ahead)   # A 5% increase per year
    print('Staging prices...')
    db_competes.import_object_parameter_values(
        [(co2_object_class_name, str(current_competes_tick), i, mcp, '0') for i in months] +
        [(co2_object_class_name, str(current_competes_tick + look_ahead), i, future_mcp, '0') for i in months])


def initialize_co2_spine_structure(db_competes, current_competes_tick, object_class_name, parameters, look_ahead):
    """
    In order to export the CO2 Market Clearing Price to COMPETES, the structure (object_class_name, object etc)
    has to be present in the SpineDB.

    :param look_ahead:
    :param db_competes: SpineDB
    :param current_competes_tick: int
    :param object_class_name: Object class name to import, so the CO2 object class name
    :param parameters: All object parameters that will be imported for this object_class
    """
    print('Creating structure...')
    print('Staging object class')
    db_competes.import_object_classes([object_class_name])
    print('Staging object')
    db_competes.import_objects([(object_class_name, str(current_competes_tick)),
                                (object_class_name, str(current_competes_tick + look_ahead))])
    print('Staging object parameters')
    db_competes.import_data({'object_parameters': [[object_class_name, i] for i in parameters]})
    print('Done exporting CO2 structure')


def execute_export_to_competes():
    """
    This function runs all the scripts in this file.
    """
    print('Establishing Database Connections...')
    db_emlab = SpineDB(sys.argv[1])
    db_competes = SpineDB(sys.argv[2])
    db_config = SpineDB(sys.argv[3])
    print('Done establishing connections')

    try:
        print('Querying databases...')
        db_emlab_marketclearingpoints = db_emlab.query_object_parameter_values_by_object_class('MarketClearingPoints')
        db_emlab_powerplantdispatchplans = db_emlab.query_object_parameter_values_by_object_class(
            'PowerPlantDispatchPlans')
        db_emlab_powerplants = db_emlab.query_object_parameter_values_by_object_class('PowerPlants')
        db_config_parameters = db_config.query_object_parameter_values_by_object_class('Coupling Parameters')
        print('Done querying Databases')

        time_step = next(int(i['parameter_value']) for i in db_config_parameters if i['object_name'] == 'Time Step')
        start_simulation_year = next(int(i['parameter_value']) for i in db_config_parameters
                                     if i['object_name'] == 'Start Year')
        look_ahead = next(int(i['parameter_value']) for i in db_config_parameters
                          if i['object_name'] == 'Look Ahead')
        current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab, start_simulation_year)
        print('Current EMLAB Tick: ' + str(current_emlab_tick))
        print('Current COMPETES Tick: ' + str(current_competes_tick))

        co2_object_class_name = 'EU_ETS_CO2price'
        months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        initialize_co2_spine_structure(db_competes, current_competes_tick, co2_object_class_name, months, look_ahead)
        export_co2_market_clearing_price(db_competes, db_emlab_marketclearingpoints, current_emlab_tick,
                                         co2_object_class_name, current_competes_tick, months, look_ahead)
        export_capacity_market_revenues(db_competes, current_emlab_tick, db_emlab_powerplantdispatchplans,
                                        db_emlab_marketclearingpoints, current_competes_tick, time_step,
                                        db_emlab_powerplants, look_ahead)

        print('Committing...')
        db_competes.commit('Committing EMLAB to COMPETES script. EMLab tick: ' + str(current_emlab_tick) +
                           ', COMPETES tick: ' + str(current_competes_tick))

        print('Done!')
    except Exception as e:
        print('Exception occurred: ' + str(e))
        raise
    finally:
        print('Closing database connections...')
        db_emlab.close_connection()
        db_competes.close_connection()
        db_config.close_connection()


if __name__ == "__main__":
    print('===== Starting EMLab to COMPETES script =====')
    execute_export_to_competes()
    print('===== End of EMLab to COMPETES script =====')
