import matplotlib.pyplot as plt
import os
from spinedb import SpineDB
import pandas as pd

def get_participating_technologies_in_capacity_market(db_emlab_powerplantdispatchplans, years_to_generate, years_emlab, start_simulation_year, db_emlab_powerplants):
    """
    This function returns all participating technologies that get revenue from the Capacity Market.
    It returns a set so all values are distinct.

    :param db_emlab_powerplantdispatchplans: PPDPs as queried from SpineDB EMLab
    :return: Set of technology names
    """
    capacity_market_participating_technologies_peryear = []

    capacity_market_aggregated_per_tech = pd.DataFrame()
    for year in years_emlab:
        capacity_market_ppdps = [row['object_name'] for row in db_emlab_powerplantdispatchplans if
                                 row['parameter_name'] == 'Market' and row['parameter_value'] == 'DutchCapacityMarket' and
                                 row['alternative'] == str(year)]
        capacity_market_accepted_ppdps = [row['object_name'] for row in db_emlab_powerplantdispatchplans if
                                          row['object_name'] in capacity_market_ppdps and row[
                                              'parameter_name'] == 'AcceptedAmount' and row['parameter_value'] > 0]
        capacity_market_participating_plants = [row['parameter_value'] for row in db_emlab_powerplantdispatchplans if
                                                row['object_name'] in capacity_market_accepted_ppdps and row[
                                                    'parameter_name'] == 'Plant']
        capacity_market_participating_capacity = [row['parameter_value'] for row in db_emlab_powerplantdispatchplans if
                                                  row['object_name'] in capacity_market_accepted_ppdps and row[
                                                      'parameter_name'] == 'AcceptedAmount']
        capacity_market_participating_technologies = [row['parameter_value'] for row in db_emlab_powerplants if
                                                       row['object_name'] in capacity_market_participating_plants and row[
                                                           'parameter_name'] == 'TECHTYPENL']
        capacity_market_participating_fuel = [row['parameter_value'] for row in db_emlab_powerplants if
                                              row['object_name'] in capacity_market_participating_plants and row[
                                                  'parameter_name'] == 'FUELNL']
        capacitytechnology = [i[0] + ', ' + i[1] for i in zip(capacity_market_participating_technologies, capacity_market_participating_fuel)]
        df_year = pd.DataFrame({'technology_fuel': capacitytechnology,
                           'capacity': capacity_market_participating_capacity})
        capacity_market_aggregated_per_tech[year] = df_year.groupby('technology_fuel').sum()
    years_dictionary = dict(zip(years_emlab, years_to_generate))
    print(years_dictionary)
    capacity_market_aggregated_per_tech.rename(columns=years_dictionary,
                                               inplace=True)
    return capacity_market_aggregated_per_tech.fillna(0)

def get_previous_cm_market_clearing_price(current_emlab_tick, db_emlab_marketclearingpoints, step):
    """
    This function gets the previous MCP in reference to the current year.

    :param current_emlab_tick: int
    :param db_emlab_marketclearingpoints: MCPs as queried from SpineDB EMLab
    :return: CM Market Clearing Price (float)
    """
    if current_emlab_tick > step:
        previous_cm_market_clearing_price = get_cm_market_clearing_price(current_emlab_tick - 2 * step,
                                                                         db_emlab_marketclearingpoints)
        print('Current EMLab tick > 1, previous Capacity Market clearing price is ' + str(
            previous_cm_market_clearing_price))
        return previous_cm_market_clearing_price
    else:
        print('Current EMLab tick <= 1, previous CM clearing price set to 0')
        return 0.0

def generate_plots():
    # Select what years you want to generate plots for
    path_to_competes_results = 'C:/Users/isanchezjimene/Documents/Spine_EMLab_COMPETES/COMPETES/Results'

    # Create plots directory if it does not exist yet
    path_to_plots = path_to_competes_results + '/plots'
    if not os.path.exists(path_to_plots):
        os.makedirs(path_to_plots)

    years_to_generate = [2020, 2021, 2022, 2023, 2024, 2025]

    # EMLab Plots
    print('Establishing and querying SpineDB...')

    emlab_spinedb = SpineDB('sqlite:///C:\\Users\\isanchezjimene\\Documents\\Spine_EMLab_COMPETES\\.spinetoolbox\\items\\db_amiris\\DB.sqlite')
    competes_spinedb = SpineDB('sqlite:///C:\\Users\\isanchezjimene\\Documents\\Spine_EMLab_COMPETES\\.spinetoolbox\\items\\db_competes\\DB COMPETES.sqlite')
    config_spinedb = SpineDB('sqlite:///C:\\Users\\isanchezjimene\\Documents\\Spine_EMLab_COMPETES\\.spinetoolbox\\items\\simulation_configuration_parameters\\Simulation Configuration Parameters.sqlite')
    #sqlite_prepend = "sqlite:///"
    #emlab_spinedb = SpineDB(sqlite_prepend + path_to_competes_results + '/db.sqlite')
    #competes_spinedb = SpineDB(sqlite_prepend + path_to_competes_results + '/db competes.sqlite')
    try:
        emlab_spine_powerplants = emlab_spinedb.query_object_parameter_values_by_object_class('PowerPlants')
        competes_spine_powerplants = competes_spinedb.query_object_parameter_values_by_object_classes(
            ['Installed Capacity Abroad', 'Installed Capacity-RES Abroad'])
        emlab_spine_technologies = emlab_spinedb.query_object_parameter_values_by_object_class('PowerGeneratingTechnologies')
        db_config_parameters = config_spinedb.query_object_parameter_values_by_object_class('Coupling Parameters')
        db_mcps = emlab_spinedb.query_object_parameter_values_by_object_class('MarketClearingPoints')
        start_simulation_year = next(int(i['parameter_value']) for i in db_config_parameters
                                     if i['object_name'] == 'Start Year')
        years_emlab = [i - start_simulation_year for i in years_to_generate]
        db_emlab_powerplantdispatchplans = emlab_spinedb.query_object_parameter_values_by_object_class('PowerPlantDispatchPlans')
        capacity_market_participating_technologies_peryear = get_participating_technologies_in_capacity_market(db_emlab_powerplantdispatchplans,
                                                                                                               years_to_generate, years_emlab,
                                                                                                               start_simulation_year, emlab_spine_powerplants)
        # EMLAB is in Euro / MWh
        #start_simulation_year = next(int(i['parameter_value']) for i in db_config_parameters if i['object_name'] == 'Start Year')
    finally:
        competes_spinedb.close_connection()
        emlab_spinedb.close_connection()

    plot_capacityMarket_technologies(capacity_market_participating_technologies_peryear,  path_to_plots,  years_to_generate, 'NL Capacity Market technologies',
                          'NL Capacity Market Technologies.png', 'Awarded capacity (MW)')
    plot_capacityMarket_revenues(capacity_market_participating_technologies_peryear, db_mcps,  path_to_plots,  years_to_generate, years_emlab, 'NL Capacity Market Revenues',
                                     'NL Capacity Market revenues.png', 'CM Revenues [Millions]')
    print('Showing plots...')
    plt.show()
    plt.close('all')

def plot_capacityMarket_technologies(capacity_market_participating_technologies_peryear, path_to_plots, years_to_generate, title, file_name, yl):
    fig1 = capacity_market_participating_technologies_peryear.T.plot.bar(stacked=True)
    fig1.set_axisbelow(True)
    plt.xlabel('Years')
    plt.ylabel(yl)
    plt.title(title)
    plt.savefig(path_to_plots + '/' + file_name, bbox_inches='tight')

def plot_capacityMarket_revenues(capacity_market_participating_technologies_peryear, db_mcps,  path_to_plots,  years_to_generate, years_emlab, title, file_name, yl):

    filtered_mcps = [i['object_name'] for i in db_mcps if
                     i['parameter_name'] == 'Market' and i['parameter_value'] == 'DutchCapacityMarket']

    years_dictionary = dict(zip(years_emlab, years_to_generate))
    for row in [i for i in db_mcps if i['object_name'] in filtered_mcps]:
        for yearemlab, yearreal in years_dictionary.items():
            if int(row['alternative']) == yearemlab and row['parameter_name'] == 'Price':
                    capacity_market_participating_technologies_peryear[yearreal] = capacity_market_participating_technologies_peryear[yearreal].multiply(row['parameter_value']/1000000)
                    print(capacity_market_participating_technologies_peryear)

    fig2 = capacity_market_participating_technologies_peryear.T.plot.bar(stacked=True)
    fig2.set_axisbelow(True)
    plt.xlabel('Years')
    plt.ylabel(yl)
    plt.title(title)
    plt.savefig(path_to_plots + '/' + file_name, bbox_inches='tight')


print('===== Start Generating Plots =====')
generate_plots()
print('===== End Generating Plots =====')