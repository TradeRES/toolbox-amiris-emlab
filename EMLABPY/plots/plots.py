import matplotlib.pyplot as plt
import os
import pandas as pd
import sys
from util.spinedb_reader_writer import *
from util.spinedb import SpineDB
import numpy as np

logging.basicConfig(level=logging.ERROR)


def prepare_investment_and_decom_data(years_to_generate, reps, annual_installed_capacity,
                                      annual_decommissioned_capacity, annual_operational_capacity,
                                      annual_capacity_to_be_decommissioned):

    for year in years_to_generate:
        for pp_name, pp in reps.power_plants.items():
            print(pp.technology.name, year, pp.capacity)
            if pp.status == globalNames.power_plant_status_operational:
                annual_operational_capacity.at[year, pp.technology.name] +=  pp.capacity
                print(annual_operational_capacity.at[year, pp.technology.name])
                #annual_operational_capacity.loc[year, pp.technology.name] += pp.capacity
            # elif pp.status == globalNames.power_plant_status_decommissioned:
            #     annual_decommissioned_capacity.at[year, pp.technology.name] += pp.capacity
            # elif pp.status == globalNames.power_plant_status_decommissioned:
            #     annual_installed_capacity.at[year, pp.technology.name] += pp.capacity
            # elif pp.status == globalNames.power_plant_status_to_be_decommissioned:
            #     annual_capacity_to_be_decommissioned.at[year, pp.technology.name] += pp.capacity

    print("here")
    # investments_grouped_and_summed = reps.investments.groupby('Technology').sum()
    # decommissioning_grouped_and_summed = decommissioned.groupby('Technology').sum()
    # index_years = list(range(years_to_generate[0], years_to_generate[-1] + reps.lookAhead + 1))
    return


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
    unique_technologies = reps.get_unique_technologies_names()
    if not os.path.exists(path_to_plots):
        os.makedirs(path_to_plots)

    # years_to_generate = [2020, 2021, 2022, 2023, 2024, 2025]
    years_to_generate = [2020]
    ticks = [i - reps.start_simulation_year for i in years_to_generate]
    annual_balance = dict()
    annual_installed_capacity = pd.DataFrame(columns=unique_technologies, index= years_to_generate)
    annual_decommissioned_capacity = pd.DataFrame(columns=unique_technologies, index= years_to_generate)
    annual_operational_capacity = pd.DataFrame(columns=unique_technologies, index= years_to_generate)
    annual_capacity_to_be_decommissioned = pd.DataFrame(columns=unique_technologies, index= years_to_generate)

    residual_load_curves = pd.DataFrame()
    load_duration_curves = pd.DataFrame()
    price_duration_curves = pd.DataFrame()
    technologies = pd.DataFrame(columns=unique_technologies)

    spinedb_reader_writer.db.close_connection()
    print('Done')
    # Generate plots
    print('Start generating plots per year')
    for year in years_to_generate:
        print('Preparing and plotting for year ' + str(year))
        # Preparing Data
        investment_sums = prepare_investment_and_decom_data(years_to_generate, reps, annual_installed_capacity,
                                                            annual_decommissioned_capacity, annual_operational_capacity,
                                                            annual_capacity_to_be_decommissioned)

        plt.close('all')

    print('Plotting prepared data')

    plot_investments(investment_sums, years_to_generate, path_to_plots, reps.look_ahead)

    # print('Showing plots...')
    # plt.show()
    plt.close('all')


print('===== Start Generating Plots =====')
generate_plots()
print('===== End Generating Plots =====')
