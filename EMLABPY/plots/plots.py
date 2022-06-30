import matplotlib.pyplot as plt
import os
import pandas
import numpy as np
from util.spinedb_reader_writer import *
from util.spinedb import SpineDB
import pandas as pd
import sys



def prepare_investment_and_decom_data(year):

    investments =
    nl_investments = investments[investments['Node'] == 'NED'].copy()

    print('Preparing Investment plot data')
    investments['CombinedIndex'] = [i[0] + ', ' + i[1] for i in
                                    zip(investments['FUEL'].values, investments['FuelType'].values)]
    index_years = list(range(years_to_generate[0], years_to_generate[-1] + look_ahead + 1))

    for index, row in investments.iterrows():
        # Extracting buildtime
        online_in_year = get_year_online_by_technology(emlab_spine_technologies, row['FUEL'], row['FuelType'], year)

        if row['CombinedIndex'] not in investment_sums.keys():
            investment_sums[row['CombinedIndex']] = [0] * len(index_years)

        investment_sums[row['CombinedIndex']][index_years.index(online_in_year)] += row['MW']

    print('Preparing Decom plot data')
    decommissioning['Technology'] = [
        emlab_spine_powerplants_fuel_dict[i] + ', ' + emlab_spine_powerplants_tech_dict[i] + ' (D)' for i in
        decommissioning['unit'].values]
    decommissioning_grouped_and_summed = decommissioning.groupby('Technology')['MW'].sum()
    index_years = list(range(years_to_generate[0], years_to_generate[-1] + look_ahead + 1))

    for tech, mw_sum in decommissioning_grouped_and_summed.iteritems():
        if tech not in investment_sums.keys():
            investment_sums[tech] = [0] * len(index_years)
        investment_sums[tech][index_years.index(year + look_ahead)] = -1 * mw_sum

    return investment_sums


def plot_investments(investment_sums, years_to_generate, path_to_plots, look_ahead):
    # Investments plot
    print('Create Investments plot')
    plt.figure()
    investments_df = pd.DataFrame(investment_sums,
                                  index=list(range(years_to_generate[0], years_to_generate[-1] + look_ahead + 1)))
    axs6 = investments_df.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs6.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity (MW)', fontsize='medium')
    plt.ylim([-4.3e5, 5.5e5])
    # leg = plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs6.set_title('EU Capacity Investments per Technology')
    fig6 = axs6.get_figure()
    fig6.savefig(path_to_plots + '/' + 'EU Investments.png', bbox_inches='tight', dpi=300)


def generate_plots():
    # EMLab Plots
    print('Establishing and querying SpineDB...')
    db_url = sys.argv[0]
    emlab_spinedb = SpineDB(db_url)
    # Create plots directory if it does not exist yet
    scenario = sys.argv[1]
    path_to_plots = os.path.join(os.getcwd(), scenario)
    if not os.path.exists(path_to_plots):
        os.makedirs(path_to_plots)

    # years_to_generate = [2020, 2021, 2022, 2023, 2024, 2025]
    years_to_generate = [2020]

    spinedb_reader_writer = SpineDBReaderWriter(False, db_url)
    reps = spinedb_reader_writer.read_db_and_create_repository()
    ticks = [i - reps.start_simulation_year for i in years_to_generate]

    static_fuel_technology_legend = sorted(
        ['GAS, CCGT', 'COAL, PC (D)', 'LIGNITE, PC (D)', 'RESE, others (D)', 'GAS, CCS CCGT', 'NUCLEAR, -',
         'BIOMASS, Cofiring (D)', 'BIOMASS, Standalone (D)', 'Derived GAS, CHP (D)', 'Derived GAS, IC (D)',
         'GAS, CCGT (D)', 'GAS, CHP (D)', 'OIL, - (D)', 'GAS, GT (D)', 'GAS, CCS CCGT (D)', 'NUCLEAR, - (D)'])

    co2_emission_sums = dict()
    vre_nl_installed_capacity = dict()
    nl_investment_sums = {i: [0] * len(range(years_to_generate[0], years_to_generate[-1] + look_ahead + 1)) for i in
                          static_fuel_technology_legend}
    investment_sums = {i: [0] * len(range(years_to_generate[0], years_to_generate[-1] + look_ahead + 1)) for i in
                       static_fuel_technology_legend}
    annual_balance = dict()
    annual_installed_capacity = dict()
    residual_load_curves = pd.DataFrame()
    load_duration_curves = pd.DataFrame()
    price_duration_curves = pd.DataFrame()

    try:
        emlab_spine_powerplants = emlab_spinedb.query_object_parameter_values_by_object_class('PowerPlants')
        emlab_spine_technologies = emlab_spinedb.query_object_parameter_values_by_object_class(
            'PowerGeneratingTechnologies')

    finally:
        emlab_spinedb.close_connection()
    print('Done')

    # Generate plots
    print('Start generating plots per year')
    for year in years_to_generate:
        print('Preparing and plotting for year ' + str(year))
        # path_and_filename_dispatch = path_to_competes_results + '/' + filename_to_load_dispatch.replace('?', str(year))
        # path_and_filename_investments = path_to_competes_results + '/' + filename_to_load_investment.replace('?',
        #                                                                                                      str(year + look_ahead))

        # Preparing Data
        investment_sums, nl_investment_sums = prepare_investment_and_decom_data(path_and_filename_investments,
                                                                                investment_sums,
                                                                                years_to_generate, year,
                                                                                spine_powerplants_tech_dict,
                                                                                spine_powerplants_fuel_dict,
                                                                                emlab_spine_technologies,
                                                                                look_ahead, nl_investment_sums)


        # plot_nl_unit_generation(path_and_filename_dispatch, year, path_to_plots)
        plt.close('all')

    print('Plotting prepared data')

    plot_investments(investment_sums, years_to_generate, path_to_plots, look_ahead)

    # print('Showing plots...')
    # plt.show()
    plt.close('all')


print('===== Start Generating Plots =====')
generate_plots()
print('===== End Generating Plots =====')
