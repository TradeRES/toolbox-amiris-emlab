import matplotlib.pyplot as plt
import os
import pandas
import numpy as np

from util.spinedb_reader_writer import *
from util.spinedb import SpineDB
import pandas as pd
import sys
logging.basicConfig(level=logging.ERROR)

def prepare_investment_and_decom_data(year, reps):
    for index, row in reps.investments.iterrows():
        print(row)
        # investments


    # decommissioning

    decommissioned = reps.get_power_plants_by_status(globalNames.power_plant_status_decommissioned)


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
    db_url = sys.argv[1]
    print('Establishing and querying SpineDB...')
    spinedb_reader_writer = SpineDBReaderWriter("Investments", db_url)
    reps = spinedb_reader_writer.read_db_and_create_repository()
    spinedb_reader_writer.commit('Initialize all module import structures')
    scenario = sys.argv[2]
    path_to_plots = os.path.join(os.getcwd(), scenario)
    if not os.path.exists(path_to_plots):
        os.makedirs(path_to_plots)

    # years_to_generate = [2020, 2021, 2022, 2023, 2024, 2025]
    years_to_generate = [2020]
    ticks = [i - reps.start_simulation_year for i in years_to_generate]
    annual_balance = dict()
    annual_installed_capacity = dict()
    residual_load_curves = pd.DataFrame()
    load_duration_curves = pd.DataFrame()
    price_duration_curves = pd.DataFrame()

    try:
        emlab_spine_powerplants = reps.power_plants
        print("asdas")
        # emlab_spine_powerplants = emlab_spinedb.query_object_parameter_values_by_object_class('PowerPlants')
        # emlab_spine_technologies = emlab_spinedb.query_object_parameter_values_by_object_class('PowerGeneratingTechnologies')
        pass
    finally:
        spinedb_reader_writer.db.close_connection()
    print('Done')
    # Generate plots
    print('Start generating plots per year')
    for year in years_to_generate:
        print('Preparing and plotting for year ' + str(year))
        # Preparing Data
        investment_sums = prepare_investment_and_decom_data(year, reps)
        plt.close('all')

    print('Plotting prepared data')

    plot_investments(investment_sums, years_to_generate, path_to_plots, reps.look_ahead)

    # print('Showing plots...')
    # plt.show()
    plt.close('all')


print('===== Start Generating Plots =====')
generate_plots()
print('===== End Generating Plots =====')
