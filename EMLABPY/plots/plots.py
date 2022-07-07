import matplotlib.pyplot as plt
import os
import pandas as pd

from util.spinedb_reader_writer import *

# # from copy import deepcopy
# # df = deepcopy(annual_operational_capacity)
import numpy as np

logging.basicConfig(level=logging.ERROR)

def plot_annual_to_be_decommissioned_capacity(plot_annual_to_be_decommissioned_capacity, years_to_generate, path_to_plots):
    print('Create decommissioning plot')
    fig4, axs5 = plt.subplots()
    axs4 = plot_annual_to_be_decommissioned_capacity.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs4.set_axisbelow(True)
    axs4.set_xlabel('Years', fontsize='medium')
    axs4.set_ylabel('Capacity (MW)', fontsize='medium')
    # plt.ylim([-4.3e5, 5.5e5])
    axs4.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs4.set_title('Dismantled Capacity per Technology')
    #fig4 = a.get_figure()
    fig4.savefig(path_to_plots + '/' + 'To be decommissioned.png', bbox_inches='tight', dpi=300)
    plt.show()

def plot_decommissions(annual_decommissioned_capacity, years_to_generate, path_to_plots):
    print('Create decommissioning plot')
    fig5, axs5 = plt.subplots()
    axs5 = annual_decommissioned_capacity.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs5.set_axisbelow(True)
    axs5.set_xlabel('Years', fontsize='medium')
    axs5.set_ylabel('Capacity (MW)', fontsize='medium')
    # plt.ylim([-4.3e5, 5.5e5])
    axs5.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs5.set_title('Dismantled Capacity per Technology')
    fig5 = axs5.get_figure()
    fig5.savefig(path_to_plots + '/' + 'Dismantled.png', bbox_inches='tight', dpi=300)
    plt.show()

def plot_annual_operational_capacity(annual_operational_capacity, years_to_generate, path_to_plots):
    print('Annual operational capacity')
    plt.figure()
    axs10 = annual_operational_capacity.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs10.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity (MW)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs10.set_title('Operational Capacity per Technology')
    fig10 = axs10.get_figure()
    fig10.savefig(path_to_plots + '/' + 'Operational Capacity per Technology.png', bbox_inches='tight', dpi=300)



def plot_investments(annual_installed_capacity, years_to_generate, path_to_plots):
    print('Create Investments plot')
    plt.figure()
    axs6 = annual_installed_capacity.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs6.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity (MW)', fontsize='medium')
    # plt.ylim([-4.3e5, 5.5e5])
    leg = plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs6.set_title('Capacity Investments per Technology')
    fig6 = axs6.get_figure()
    fig6.savefig(path_to_plots + '/' + 'Capacity Investments.png', bbox_inches='tight', dpi=300)


def plot_candidate_pp_project_value(candidate_plants_project_value, years_to_generate, path_to_plots):
    print('project values')
    # plt.figure()
    axs7 = candidate_plants_project_value.plot.line()
    axs7.set_axisbelow(True)
    plt.xlabel('Iterations', fontsize='medium')
    plt.ylabel('Project value', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs7.set_title('NPV Candidate power plants')
    fig7 = axs7.get_figure()
    fig7.savefig(path_to_plots + '/' + 'NPV Candidate power plants.png', bbox_inches='tight', dpi=300)


def plot_investments_and_NPV_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration, years_to_generate,
                                   path_to_plots):
    print('project values')

    fig8, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot( candidate_plants_project_value )
    ax2.plot(installed_capacity_per_iteration , 'o')
    ax1.set_xlabel('Iterations', fontsize='medium')
    ax1.set_ylabel('Project value', fontsize='medium')
    ax2.set_ylabel('Investments', fontsize='medium')
    ax1.set_title('Investments and project value per iterations')
    print( candidate_plants_project_value.columns.values.tolist())
    print(installed_capacity_per_iteration.columns.values.tolist())
    ax1.legend( candidate_plants_project_value.columns.values.tolist(), fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
  #  ax2.legend( installed_capacity_per_iteration.columns.values.tolist(), fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))

    fig8.savefig(path_to_plots + '/' + 'Investments per iterations.png', bbox_inches='tight', dpi=300)


# def plot_and_prepare_hourly_nodal_price_duration_curve(hourly_nodal_prices_df, year, path_to_plots,
#                                                        price_duration_curves):
#     # Plot 2.5 Hourly Market Price Duration Curve
#     print('Create Hourly Nodal Price duration curve')
#     plt.figure()
#     axs25 = hourly_nodal_prices_df['NED'].sort_values(ascending=False).plot(use_index=False, grid=True, legend=False)
#     plt.xlabel('Hours')
#     plt.ylabel('Price (Euro / MWh)')
#     axs25.set_title('NL Hourly Electricity Spot Market Price Duration Curve ' + str(year))
#     axs25.set_axisbelow(True)
#     plt.ylim([0, min(hourly_nodal_prices_df['NED'].max() + 50, 250)])
#     fig25 = axs25.get_figure()
#     fig25.savefig(path_to_plots + '/' + 'NL Nodal Prices Duration Curve ' + str(year) + '.png', bbox_inches='tight', dpi=300)
#
#     price_duration_curves[year] = hourly_nodal_prices_df['NED'].sort_values(ascending=False).values
#     return price_duration_curves

# def plot_hourly_nodal_prices(path_and_filename_dispatch, year, path_to_plots):
#     # Plot 2 Hourly Nodal Prices
#     print('Read and create hourly nodal prices plot')
#     hourly_nodal_prices_df = pandas.read_excel(path_and_filename_dispatch, 'Hourly Nodal Prices', skiprows=1,
#                                                index_col=0)
#     # hourly_nodal_prices_df[hourly_nodal_prices_df > 250] = 250
#
#     plt.figure()
#     axs2 = hourly_nodal_prices_df['NED'].plot(grid=True)
#     axs2.set_axisbelow(True)
#     plt.xlabel('Hours')
#     plt.ylabel('Price (Euro / MWh)')
#     plt.xlim([0, 8760])
#     plt.ylim([0, min(hourly_nodal_prices_df['NED'].max() + 50, 250)])
#     axs2.set_title('NL Hourly Electricity Spot Market Prices ' + str(year))
#     fig2 = axs2.get_figure()
#     fig2.savefig(path_to_plots + '/' + 'NL Nodal Prices ' + str(year) + '.png', bbox_inches='tight', dpi=300)
#
#     return hourly_nodal_prices_df

# def plot_and_prepare_residual_load_duration_curve(hourly_nl_balance_demand, hourly_nl_balance_df, year, path_to_plots,
#                                                   residual_load_curves):
#     # Plot 1.75: Residual Load Curve
#     print('Create Res Load duration curve')
#     plt.figure()
#     hourly_nl_balance_residual_load = hourly_nl_balance_demand.subtract(hourly_nl_balance_df['Wind Onshore']) \
#         .subtract(hourly_nl_balance_df['Wind Offshore']) \
#         .subtract(hourly_nl_balance_df['Sun']) \
#         .subtract(hourly_nl_balance_df['Hydro Conv.'])
#     axs175 = hourly_nl_balance_residual_load.sort_values(ascending=False).plot(use_index=False, grid=True, legend=False)
#     axs175.set_title('NL Residual Load Duration Curve ' + str(year))
#     axs175.set_axisbelow(True)
#     plt.xlabel('Hours')
#     plt.ylabel('Residual Load (MWh)')
#     plt.xlim([0, 8760])
#     fig175 = axs175.get_figure()
#     fig175.savefig(path_to_plots + '/' + 'NL Residual Load Duration Curve ' + str(year) + '.png', bbox_inches='tight', dpi=300)
#
#     residual_load_curves[year] = hourly_nl_balance_residual_load.sort_values(ascending=False).values
#     return residual_load_curves

def prepare_decommissioned_investment_data(years_to_generate, reps, unique_technologies):
    annual_decommissioned_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate).fillna(0)
    annual_operational_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate).fillna(0)
    for year in years_to_generate:
        for pp_name, pp in reps.power_plants.items():
            if pp.status == globalNames.power_plant_status_operational:
                annual_operational_capacity.at[year, pp.technology.name] += pp.capacity
            elif pp.status == globalNames.power_plant_status_decommissioned:
                annual_decommissioned_capacity.at[year, pp.technology.name] += pp.capacity

    return annual_decommissioned_capacity,  annual_operational_capacity


def prepare_pipeline_operational(years_to_generate, reps, unique_technologies):
    annual_operational_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate).fillna(0)
    annual_to_be_decommissioned_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate).fillna(0)
    annual_in_pipeline_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate).fillna(0)

    for year in years_to_generate:
        for pp_name, pp in reps.power_plants.items():
            if pp.status == globalNames.power_plant_status_operational:
                annual_operational_capacity.at[year, pp.technology.name] += pp.capacity
            elif pp.status == globalNames.power_plant_status_inPipeline:
                annual_in_pipeline_capacity.at[year, pp.technology.name] += pp.capacity
            elif pp.status == globalNames.power_plant_status_to_be_decommissioned:
                annual_to_be_decommissioned_capacity.at[year, pp.technology.name] += pp.capacity

    return annual_operational_capacity, annual_in_pipeline_capacity, annual_to_be_decommissioned_capacity

def prepare_capacity_per_iteration(years_to_generate, reps):
        # preparing  candidates NPV per iteration
    unique_candidate_power_plants = reps.get_unique_candidate_technologies()
    for year in years_to_generate:
        max_iteration = 0
        future_year = year + reps.lookAhead
        for name, invest in reps.investments.items():
            if len(invest.project_value_year[str(future_year)]) > max_iteration:
                max_iteration = len(invest.project_value_year[str(future_year)])
        df_zeros = np.zeros(shape=(max_iteration, len(unique_candidate_power_plants)))
        candidate_plants_project_value = pd.DataFrame(df_zeros, columns=unique_candidate_power_plants)
        for name, investment in reps.investments.items():
            if len(investment.project_value_year) > 0:
                candidate_plants_project_value[reps.candidatePowerPlants[name].technology.name] = pd.Series(
                    investment.project_value_year[str(future_year)])

        # preparing  investments per iteration
        df_zeros = np.zeros(shape=(max_iteration, len(unique_candidate_power_plants)))
        installed_capacity_per_iteration = pd.DataFrame(df_zeros, columns=unique_candidate_power_plants)
        for invest_name, investment in reps.investments.items():  # attention
            if len(investment.invested_in_iteration) > 0:
                index_invested_iteration = list(map(int, investment.invested_in_iteration[str(future_year)]))
                installed_capacity_per_iteration.loc[
                    index_invested_iteration, reps.candidatePowerPlants[invest_name].technology.name] = \
                    reps.candidatePowerPlants[invest_name].capacityTobeInstalled

    return  installed_capacity_per_iteration, candidate_plants_project_value



# def prepare_decom_data(decommissioning, emlab_spine_powerplants_tech_dict, investment_sums, years_to_generate, year,
#                        investments, emlab_spine_powerplants_fuel_dict, look_ahead):
#     print('Preparing Decom plot data')
#
#     index_years = list(range(years_to_generate[0], years_to_generate[-1] + look_ahead + 1))
#
#     for tech, mw_sum in decommissioning.iteritems():
#         if tech not in investment_sums.keys():
#             investment_sums[tech] = [0] * len(index_years)
#         investment_sums[tech][index_years.index(year + look_ahead)] = -1 * mw_sum
#
#     return investment_sums


def generate_plots():
    db_url = sys.argv[1]
    print('Establishing and querying SpineDB...')
    spinedb_reader_writer = SpineDBReaderWriter("Investments", db_url)
    reps = spinedb_reader_writer.read_db_and_create_repository()
    spinedb_reader_writer.commit('Initialize all module import structures')
    scenario = sys.argv[2]

    path_to_plots = os.path.join(os.getcwd(), "plots", scenario)

    if not os.path.exists(path_to_plots):
        os.makedirs(path_to_plots)

    unique_technologies = reps.get_unique_technologies_names()
    # years_to_generate = [2020, 2021, 2022, 2023, 2024, 2025]
    years_to_generate = [2020]
    years_ahead_to_generate = [x + reps.lookAhead for x in years_to_generate]
    df_zeros = np.zeros(shape=(len(years_to_generate), len(unique_technologies)))
    ticks = [i - reps.start_simulation_year for i in years_to_generate]
    annual_balance = dict()

    residual_load_curves = pd.DataFrame()
    load_duration_curves = pd.DataFrame()
    price_duration_curves = pd.DataFrame()

    spinedb_reader_writer.db.close_connection()
    print('Done')
    # Generate plots
    print('Start generating plots per year')
    for year in years_to_generate:
        print('Preparing and plotting for year ' + str(year))
        # Preparing Data
        annual_decommissioned_capacity , annual_operational_capacity = prepare_decommissioned_investment_data(years_to_generate, reps, unique_technologies)
        annual_operational_capacity, annual_in_pipeline_capacity, annual_to_be_decommissioned_capacity = prepare_pipeline_operational( years_to_generate, reps, unique_technologies)
        installed_capacity_per_iteration, candidate_plants_project_value =  prepare_capacity_per_iteration(years_to_generate, reps)
    print('Plotting prepared data')

    #
    # plot_investments(annual_in_pipeline_capacity, years_to_generate, path_to_plots)
    # plot_decommissions(annual_decommissioned_capacity, years_to_generate, path_to_plots)
    # plot_annual_operational_capacity(annual_operational_capacity, years_to_generate, path_to_plots)
    # plot_annual_to_be_decommissioned_capacity(annual_to_be_decommissioned_capacity, years_to_generate, path_to_plots)
    # plot_candidate_pp_project_value(candidate_plants_project_value, years_to_generate, path_to_plots)
    plot_investments_and_NPV_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration, years_to_generate,
                                   path_to_plots)
    print('Showing plots...')
    plt.show()
    plt.close('all')


print('===== Start Generating Plots =====')
generate_plots()
print('===== End Generating Plots =====')
