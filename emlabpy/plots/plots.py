import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy_financial as npf
from util.spinedb_reader_writer import *
from util.spinedb import SpineDB
# # from copy import deepcopy
# # df = deepcopy(annual_operational_capacity)
import numpy as np

logging.basicConfig(level=logging.ERROR)


def plot_investments_and_NPV_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration,
                                           test_year, path_to_plots, colors_unique_candidates):
    print('investments and NPV')
    fig1, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    candidate_plants_project_value.plot(ax=ax1, color=colors_unique_candidates)
    installed_capacity_per_iteration.plot(ax=ax2, color=colors_unique_candidates, linestyle='None', marker='o')
    ax1.set_xlabel('Iterations', fontsize='medium')
    ax1.set_ylabel('NPV [Eur] (lines)', fontsize='medium')
    ax2.set_ylabel('Investments MW (dotted)', fontsize='medium')
    ax1.set_title('Investments and NPV per iterations ' + str(test_year))
    ax1.legend(candidate_plants_project_value.columns.values.tolist(), fontsize='medium', loc='upper left',
               bbox_to_anchor=(1.2, 1.1))
    ax2.legend(installed_capacity_per_iteration.columns.values.tolist(), fontsize='medium', loc='upper left',
               bbox_to_anchor=(1.2, 0.5))
    fig1.savefig(path_to_plots + '/' + 'Candidate power plants NPV and Investment decisions' + str(
        test_year) + '.png', bbox_inches='tight', dpi=300)


def plot_annual_to_be_decommissioned_capacity(plot_annual_to_be_decommissioned_capacity, years_to_generate,
                                              path_to_plots, colors):
    fig4, axs5 = plt.subplots()
    axs4 = plot_annual_to_be_decommissioned_capacity.plot.bar(stacked=True, rot=0, color=colors, grid=True,
                                                              legend=False)
    axs4.set_axisbelow(True)
    axs4.set_xlabel('Years', fontsize='medium')
    axs4.set_ylabel('Capacity (MW)', fontsize='medium')
    # plt.ylim([-4.3e5, 5.5e5])
    axs4.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs4.set_title('Capacity per Technology to be decommissioned')
    # fig4 = a.get_figure()
    fig4.savefig(path_to_plots + '/' + 'Capacity to be decommissioned.png', bbox_inches='tight', dpi=300)
    plt.show()


def plot_decommissions(annual_decommissioned_capacity, years_to_generate, path_to_plots, colors):
    print('Create decommissioning plot')
    fig5, axs5 = plt.subplots()
    axs5 = annual_decommissioned_capacity.plot.bar(stacked=True, rot=0, color=colors, grid=True, legend=False)
    axs5.set_axisbelow(True)
    axs5.set_xlabel('Years', fontsize='medium')
    for label in axs5.get_xticklabels(which='major'):
        label.set(rotation=50, horizontalalignment='right')
    axs5.set_ylabel('Capacity (MW)', fontsize='medium')
    # plt.ylim([-4.3e5, 5.5e5])
    axs5.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs5.set_title('Dismantled Capacity per Technology')
    fig5 = axs5.get_figure()
    fig5.savefig(path_to_plots + '/' + 'Dismantled.png', bbox_inches='tight', dpi=300)
    plt.show()


def plot_investments(annual_installed_capacity, annual_commissioned, annual_decommissioned_capacity, years_to_generate, path_to_plots, colors):
    print('Capacity Investments plot')
    fig6, axs6 = plt.subplots(3, 1)
    fig6.tight_layout()
    annual_installed_capacity.plot.bar(ax=axs6[0], stacked=True, rot=0, color=colors, grid=True, legend=False)
    annual_commissioned.plot.bar(ax=axs6[1], stacked=True, rot=0, color=colors, grid=True, legend=False)
    annual_decommissioned_capacity.plot.bar(ax=axs6[2], stacked=True, rot=0, color=colors, grid=True, legend=False)
    axs6[0].set_axisbelow(True)
    axs6[2].set_xlabel('Years', fontsize='medium')
    for label in axs6[0].get_xticklabels(which='major'):
        label.set(rotation=50, horizontalalignment='right')
    for label in axs6[1].get_xticklabels(which='major'):
        label.set(rotation=50, horizontalalignment='right')
    for label in axs6[2].get_xticklabels(which='major'):
        label.set(rotation=50, horizontalalignment='right')
    axs6[0].set_ylabel('In pipeline MW', fontsize='small')
    axs6[1].set_ylabel('Commissioned MW', fontsize='small')
    axs6[1].set_ylabel('Decommissioned MW', fontsize='small')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.5))
    axs6[0].set_title('Investments by decision year (up) and by commissioning year (down)')
    fig6.savefig(path_to_plots + '/' + 'Capacity Investments.png', bbox_inches='tight', dpi=300)


def plot_candidate_profits(candidate_plants_profits_per_iteration, test_tick, path_to_plots):
    print('candidate profits')
    axs7 = candidate_plants_profits_per_iteration.plot.line()
    axs7.set_axisbelow(True)
    plt.xlabel('Iterations', fontsize='medium')
    plt.ylabel('Project value [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs7.set_title('NPV Candidate power plants')
    fig7 = axs7.get_figure()
    fig7.savefig(path_to_plots + '/' + 'Candidate plants profits per iteration ' + str(test_tick) + '.png',
                 bbox_inches='tight', dpi=300)


def power_plants_status(number_per_status, path_to_plots):
    print("power plants status")
    axs8 = number_per_status.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs8.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.xticks(rotation=60)
    plt.ylabel('Capacity per status (MW)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs8.set_title('Power plants status')
    fig8 = axs8.get_figure()
    fig8.savefig(path_to_plots + '/' + 'Power plants status per year.png', bbox_inches='tight', dpi=300)


def power_plants_last_year_status(power_plants_last_year_status, path_to_plots, last_year):
    plt.figure()
    axs9 = power_plants_last_year_status.plot.bar(stacked=True, rot=0, grid=True, legend=False)
    axs9.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity per status (MW)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs9.set_title('Power plants status ' + str(last_year))
    fig9 = axs9.get_figure()
    fig9.savefig(path_to_plots + '/' + 'Power plants status ' + str(last_year) + '.png', bbox_inches='tight', dpi=300)


def plot_annual_operational_capacity(annual_operational_capacity, path_to_plots, colors):
    print('Annual operational capacity')
    plt.figure()
    axs10 = annual_operational_capacity.plot.bar(stacked=True, rot=0, color=colors, grid=True, legend=False)
    axs10.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity (MW)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs10.set_title('Operational Capacity per Technology')
    fig10 = axs10.get_figure()
    fig10.savefig(path_to_plots + '/' + 'Operational Capacity per Technology.png', bbox_inches='tight', dpi=300)


def plot_revenues_per_iteration(revenues_iteration, tech_name, path_to_plots, first_year):
    print('Revenues per iteration for year ')
    plt.figure()
    axs11 = revenues_iteration[tech_name].plot()
    axs11.set_axisbelow(True)
    plt.xlabel('Iterations', fontsize='medium')
    plt.ylabel('Revenues [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs11.set_title('Revenues per technologies for year ' + str(first_year))
    fig11 = axs11.get_figure()
    fig11.savefig(path_to_plots + '/' + ' Technology Revenues per iteration ' + str(first_year) + '.png',
                  bbox_inches='tight', dpi=300)


def plot_average_revenues_per_iteration(revenues_iteration, path_to_plots, first_year, colors):
    print('Average Revenues per iteration')
    plt.figure()
    axs15 = revenues_iteration.plot(color=colors)
    axs15.set_axisbelow(True)
    plt.xlabel('Iterations', fontsize='medium')
    plt.ylabel('Revenues [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs15.set_title('Average revenues per technologies for year ' + str(first_year))
    fig15 = axs15.get_figure()
    fig15.savefig(path_to_plots + '/' + 'AverageTechnology Revenues per iteration ' + str(first_year) + '.png',
                  bbox_inches='tight', dpi=300)


def plot_future_fuel_prices(future_fuel_prices, path_to_plots):
    plt.figure()
    axs12 = future_fuel_prices.plot()
    axs12.set_axisbelow(True)
    plt.xlabel('years', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs12.set_title('Future Fuel prices per year')
    fig12 = axs12.get_figure()
    fig12.savefig(path_to_plots + '/' + 'Future Fuel prices per year.png', bbox_inches='tight', dpi=300)


def plot_screening_curve(yearly_costs, path_to_plots, test_year, colors_unique_techs):
    axs13 = yearly_costs.plot(color=colors_unique_techs)
    axs13.set_axisbelow(True)
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs13.set_title('Screening curve')
    fig13 = axs13.get_figure()
    fig13.savefig(path_to_plots + '/' + 'Screening curve (no CO2) ' + str(test_year) + '.png', bbox_inches='tight',
                  dpi=300)


def plot_screening_curve_candidates(yearly_costs_candidates, path_to_plots, future_year, colors_unique_candidates):
    axs14 = yearly_costs_candidates.plot(color=colors_unique_candidates)
    axs14.set_axisbelow(True)
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs14.set_title('Screening curve candidate technologies')
    fig14 = axs14.get_figure()
    fig14.savefig(path_to_plots + '/' + 'Screening curve candidate technologies (no CO2) ' + str(future_year) + '.png',
                  bbox_inches='tight', dpi=300)


def plot_CM_revenues(CM_revenues, path_to_plots):
    axs15 = CM_revenues.plot()
    axs15.set_axisbelow(True)
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Prices [Eur/MW]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs15.set_title('Capacity Mechanisms')
    fig15 = axs15.get_figure()
    fig15.savefig(path_to_plots + '/' + 'Capacity Mechanisms.png', bbox_inches='tight', dpi=300)


def plot_irrs_per_tech_per_year(irrs_per_tech_per_year, path_to_plots, colors):
    # irrs_per_tech_per_year.drop("PV_utility_systems",  axis=1,inplace=True)
    # irrs_per_tech_per_year.drop("WTG_onshore", axis=1, inplace=True)
    axs16 = irrs_per_tech_per_year.plot(color=colors)
    axs16.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('IRR', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs16.set_title('IRRs')
    fig16 = axs16.get_figure()
    fig16.savefig(path_to_plots + '/' + 'IRRs per year per technology.png', bbox_inches='tight', dpi=300)


def plot_total_profits_per_tech_per_year(total_profits_per_tech_per_year, path_to_plots, colors):
    axs25 = total_profits_per_tech_per_year.plot(color=colors)
    axs25.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('total porfits [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs25.set_title('Total Profits')
    fig25 = axs25.get_figure()
    fig25.savefig(path_to_plots + '/' + 'total profits per year per technology.png', bbox_inches='tight', dpi=300)

def plot_installed_capacity(all_techs_capacity, path_to_plots, colors_unique_techs):
    axs17 = all_techs_capacity.plot.area(color=colors_unique_techs)
    axs17.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Installed Capacity [MW]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs17.set_title('Installed Capacity')
    fig17 = axs17.get_figure()
    fig17.savefig(path_to_plots + '/' + 'Annual installed Capacity per technology.png', bbox_inches='tight', dpi=300)


def plot_capacity_factor(all_techs_capacity_factor, path_to_plots, colors_unique_techs):
    axs23 = all_techs_capacity_factor.plot.area(color=colors_unique_techs)
    axs23.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity factor [%]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs23.set_title('Capacity factor')
    fig23 = axs23.get_figure()
    fig23.savefig(path_to_plots + '/' + 'All technologies capacity factor.png', bbox_inches='tight', dpi=300)

def plot_annual_generation(all_techs_generation, path_to_plots, colors_unique_techs):
    axs18 = all_techs_generation.plot.area(color=colors_unique_techs)
    axs18.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Annual Generation [MWh]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs18.set_title('Annual Generation')
    fig18 = axs18.get_figure()
    fig18.savefig(path_to_plots + '/' + 'Annual generation per technology.png', bbox_inches='tight', dpi=300)


def plot_supply_ratio(supply_ratio, path_to_plots):
    axs19 = supply_ratio.plot()
    axs19.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('peak demand / total capacity', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs19.set_title('Supply ratio')
    fig19 = axs19.get_figure()
    fig19.savefig(path_to_plots + '/' + 'Supply ratio.png', bbox_inches='tight', dpi=300)


def plot_shortages(shortages, path_to_plots):
    axs20 = shortages.plot()
    axs20.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Number of shortage hours', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs20.set_title('Number of shortages')
    fig20 = axs20.get_figure()
    fig20.savefig(path_to_plots + '/' + 'Shortages.png', bbox_inches='tight', dpi=300)


def plot_market_values_generation(all_techs_capacity, path_to_plots, colors_unique_techs):
    # these market values only include plants if they have been dispatched
    axs21 = all_techs_capacity.plot(color=colors_unique_techs)
    axs21.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Market value (Euro/MWh)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs21.set_title('Market values (Market revenues / Production)')
    fig21 = axs21.get_figure()
    fig21.savefig(path_to_plots + '/' + 'Annual market values per technology.png', bbox_inches='tight', dpi=300)


def plot_electricity_prices(electricity_price, path_to_plots):
    axs22 = electricity_price.plot()
    axs22.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Market price (Eur/MWh)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs22.set_title('Average yearly electricity prices')
    fig22 = axs22.get_figure()
    fig22.savefig(path_to_plots + '/' + 'Electricity prices.png', bbox_inches='tight', dpi=300)
    pass


# section -----------------------------------------------------------------------------------------------data preparation


def prepare_pp_status(years_to_generate, years_to_generate_and_build, reps, unique_technologies):
    number_investments_per_technology = pd.DataFrame(columns=unique_technologies,
                                                     index=years_to_generate_and_build).fillna(0)
    for pp, investments in reps.investmentDecisions.items():
        for year, year_investments in investments.invested_in_iteration.items():
            number_investments_per_technology[int(year), reps.candidatePowerPlants[pp].technology.name] = len(
                year_investments)

    annual_decommissioned_capacity = pd.DataFrame(columns=unique_technologies,
                                                  index=years_to_generate_and_build).fillna(0)
    annual_in_pipeline_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate_and_build).fillna(0)
    annual_commissioned_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate_and_build).fillna(
        0)
    last_year = years_to_generate[-1]

    last_year_operational_capacity = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_to_be_decommissioned_capacity = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_strategic_reserve_capacity = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_not_set_status_capacity = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_in_pipeline = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_decommissioned = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)

    for pp_name, pp in reps.power_plants.items():
        if pp.status == globalNames.power_plant_status_decommissioned:
            year = pp.dismantleTime + reps.start_simulation_year
            annual_decommissioned_capacity.at[year, pp.technology.name] += pp.capacity

        elif pp.age <= reps.current_tick:
            # graphed according to commissioned year which is determined by age.
            year_decision = pp.commissionedYear - pp.technology.expected_leadtime - pp.technology.expected_permittime
            # the year when the investment decision was made
            annual_in_pipeline_capacity.at[year_decision, pp.technology.name] += pp.capacity
            #  the year when the investment entered in operation
            annual_commissioned_capacity.at[pp.commissionedYear, pp.technology.name] += pp.capacity
            if last_year != pp.commissionedYear + pp.age:
                print("the age and the commissioned year dont add up")

    for pp_name, pp in reps.power_plants.items():
        if pp.status == globalNames.power_plant_status_operational:  # this will be changed
            last_year_operational_capacity.at[last_year, pp.technology.name] += pp.capacity
        elif pp.status == globalNames.power_plant_status_decommissioned:
            last_year_decommissioned.at[last_year, pp.technology.name] += pp.capacity
        elif pp.status == globalNames.power_plant_status_inPipeline:
            last_year_in_pipeline.at[last_year, pp.technology.name] += pp.capacity
        elif pp.status == globalNames.power_plant_status_to_be_decommissioned:
            last_year_to_be_decommissioned_capacity.at[last_year, pp.technology.name] += pp.capacity
        elif pp.status == globalNames.power_plant_status_strategic_reserve:
            last_year_strategic_reserve_capacity.at[last_year, pp.technology.name] += pp.capacity
        elif pp.status == globalNames.power_plant_status_not_set:
            last_year_not_set_status_capacity.at[last_year, pp.technology.name] += pp.capacity
            print(pp_name, "has not status set")

    data_per_year = {
        globalNames.power_plant_status_decommissioned: (annual_decommissioned_capacity).sum(axis=1),
        globalNames.power_plant_status_inPipeline: (annual_in_pipeline_capacity).sum(axis=1),
    }

    data_last_year = {
        globalNames.power_plant_status_decommissioned: (last_year_decommissioned).sum(axis=1),
        globalNames.power_plant_status_inPipeline: (last_year_in_pipeline).sum(axis=1),
        globalNames.power_plant_status_operational: (last_year_operational_capacity).sum(axis=1),
        globalNames.power_plant_status_to_be_decommissioned: (last_year_to_be_decommissioned_capacity).sum(axis=1),
        globalNames.power_plant_status_strategic_reserve: (last_year_strategic_reserve_capacity).sum(axis=1),
        globalNames.power_plant_status_not_set: (last_year_not_set_status_capacity).sum(axis=1)
    }

    number_per_status = pd.DataFrame(data_per_year)
    number_per_status_last_year = pd.DataFrame(data_last_year)

    return annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_commissioned_capacity, last_year_in_pipeline, last_year_decommissioned, \
           last_year_operational_capacity, last_year_to_be_decommissioned_capacity, \
           last_year_strategic_reserve_capacity, number_per_status, number_per_status_last_year


def prepare_capacity_per_iteration(future_year, reps, unique_candidate_power_plants):
    # attention this graph is now only for the first year
    max_iteration = 0
    # preparing empty df
    for name, investment in reps.investments.items():
        if str(future_year) in investment.project_value_year.keys():
            if len(investment.project_value_year[str(future_year)]) > max_iteration:
                max_iteration = len(investment.project_value_year[str(future_year)])
    df_zeros = np.zeros(shape=(max_iteration, len(unique_candidate_power_plants)))
    candidate_plants_project_value = pd.DataFrame(df_zeros, columns=unique_candidate_power_plants)
    # preparing NPV per iteration
    for name, investment in reps.investments.items():
        if len(investment.project_value_year) > 0:
            if str(future_year) in investment.project_value_year.keys():
                candidate_plants_project_value[reps.candidatePowerPlants[name].technology.name] = \
                    pd.Series(dict(investment.project_value_year[str(future_year)]))

    # preparing investments per iteration
    df_zeros = np.zeros(shape=(max_iteration, len(unique_candidate_power_plants)))
    installed_capacity_per_iteration = pd.DataFrame(df_zeros, columns=unique_candidate_power_plants)

    for invest_name, investment in reps.investmentDecisions.items():
        if len(investment.invested_in_iteration) > 0:
            if str(future_year) in investment.invested_in_iteration.keys():
                index_invested_iteration = list(map(int, investment.invested_in_iteration[str(future_year)]))
                installed_capacity_per_iteration.loc[
                    index_invested_iteration, reps.candidatePowerPlants[invest_name].technology.name] = \
                    reps.candidatePowerPlants[invest_name].capacityTobeInstalled

    # for invest_name, investment in reps.investmentDecisions.items():
    #     if len(investment.invested_in_iteration) > 0:
    #         if str(future_year) in investment.invested_in_iteration.keys():
    #             index_invested_iteration = list(map(int, investment.invested_in_iteration[str(future_year)]))
    #             installed_capacity_per_iteration.loc[
    #                 index_invested_iteration, reps.candidatePowerPlants[invest_name].technology.name] = \
    #                 reps.candidatePowerPlants[invest_name].capacityTobeInstalled

    return installed_capacity_per_iteration, candidate_plants_project_value


def prepare_profits_candidates_per_iteration(reps, tick):
    # todo financial report are per tick????????????????????????????????
    profits = reps.get_profits_per_tick(tick)
    profits_per_iteration = pd.DataFrame(index=profits.profits_per_iteration_names_candidates[str(0)],
                                         columns=["zero"]).fillna(0)
    for iteration, profit_per_iteration in list(profits.profits_per_iteration_candidates.items()):
        temporal = pd.DataFrame(profit_per_iteration, index=profits.profits_per_iteration_names_candidates[iteration],
                                columns=[int(iteration)])
        profits_per_iteration = profits_per_iteration.join(temporal)
    profits_per_iteration.drop("zero", axis=1, inplace=True)
    tech = []
    for pp in profits_per_iteration.index.values:
        tech.append(reps.power_plants[pp].technology.name)
    profits_per_iteration["tech"] = tech
    profits_per_iteration = np.transpose(profits_per_iteration)
    profits_per_iteration.columns = profits_per_iteration.iloc[-1]
    profits_per_iteration.drop("tech", inplace=True)
    profits_per_iteration.index.map(int)
    profits_per_iteration.sort_index(ascending=True, inplace=True)
    return profits_per_iteration


def prepare_revenues_per_iteration(reps, tick):
    profits = reps.get_profits_per_tick(tick)
    # index of installed power plants
    power_plants_revenues_per_iteration = pd.DataFrame(index=profits.profits_per_iteration_names[str(tick)],
                                                       columns=["zero"]).fillna(0)
    # take only 10 iterations, otherwise there are memory problems add [2:11]
    for iteration, profit_per_iteration in list(profits.profits_per_iteration.items()):
        temporal = pd.DataFrame(profit_per_iteration, index=profits.profits_per_iteration_names[iteration],
                                columns=[int(iteration)])
        power_plants_revenues_per_iteration = power_plants_revenues_per_iteration.join(temporal)
    power_plants_revenues_per_iteration.drop("zero", axis=1, inplace=True)
    tech = []
    for pp in power_plants_revenues_per_iteration.index.values:
        tech.append(reps.power_plants[pp].technology.name)
    power_plants_revenues_per_iteration["tech"] = tech
    grouped_revenues = power_plants_revenues_per_iteration.groupby('tech').mean()
    sorted_average_revenues_per_iteration_first_year = grouped_revenues.T.sort_index()

    revenues_per_iteration = power_plants_revenues_per_iteration.set_index('tech').sort_index(level=0)
    return sorted_average_revenues_per_iteration_first_year, revenues_per_iteration.T


def prepare_operational_profit_per_year_per_tech(reps, unique_technologies, years_to_generate, first_year):
    simulation_years = [int(x - first_year) for x in years_to_generate]
    profits_per_tech_per_year = pd.DataFrame(index=simulation_years, columns=["zero"]).fillna(0)
    for technology_name in unique_technologies:
        powerplants_per_tech = reps.get_power_plants_by_technology(technology_name)
        profits_per_year = pd.DataFrame(index=simulation_years, columns=["zero"]).fillna(0)
        profits_per_year.index.name = "year"
        for plant in powerplants_per_tech:
            temporal = reps.get_total_profits_for_plant(plant.name)
            if temporal is None:
                print("power plant in pipeline", plant.name, plant.id)
            else:
                temporal.index.name = "year"
                temporal.columns = [plant.name]
                temporal.index = temporal.index.astype(int)
                profits_per_year = pd.merge(profits_per_year,
                                         temporal,
                                         on='year',
                                         how='left')
        profits_per_year.drop("zero", axis=1, inplace=True)
        numeric = profits_per_year.values.astype('float64')
        profits_per_tech_per_year[technology_name] = np.nanmean(numeric, axis=1)
    profits_per_tech_per_year.drop("zero", axis=1, inplace=True)
    return profits_per_tech_per_year

def prepare_extension_lifetime_per_tech(reps, unique_technologies):
    # calculate for all power plants the extended lifetime in average
    # todo finish
    life_extension = pd.DataFrame(columns=unique_technologies)
    for technology_name in unique_technologies:
        tech_power_plants = reps.get_power_plants_by_technology(technology_name)
        extension = []
        for pp in tech_power_plants:
            if pp.age >= pp.technology.expected_lifetime:
                years = pp.age - pp.technology.expected_lifetime
                extension.append(years / len(tech_power_plants))
        life_extension.loc[:, technology_name] = np.mean(extension)
        # life_extension = pd.DataFrame(data=data,columns=unique_technologies)
    return life_extension


def prepare_irr_per_technology_per_year(reps, unique_technologies, years_to_generate, first_year):
    simulation_years = [int(x - first_year) for x in years_to_generate]
    irrs_per_tech_per_year = pd.DataFrame(index=simulation_years, columns=["zero"]).fillna(0)
    for technology_name in unique_technologies:
        powerplants_per_tech = reps.get_power_plants_by_technology(technology_name)
        irrs_per_year = pd.DataFrame(index=simulation_years, columns=["zero"]).fillna(0)
        irrs_per_year.index.name = "year"
        for plant in powerplants_per_tech:
            temporal = reps.get_irrs_for_plant(plant.name)
            if temporal is None:
                print("power plant in pipeline", plant.name, plant.id)
            else:
                temporal.index.name = "year"
                temporal.columns = [plant.name]
                temporal.index = temporal.index.astype(int)
                irrs_per_year = pd.merge(irrs_per_year,
                                         temporal,
                                         on='year',
                                         how='left')
        irrs_per_year.drop("zero", axis=1, inplace=True)
        numeric = irrs_per_year.values.astype('float64')
        irrs_per_tech_per_year[technology_name] = np.nanmean(numeric, axis=1)
    irrs_per_tech_per_year.drop("zero", axis=1, inplace=True)
    return irrs_per_tech_per_year


def prepare_future_fuel_prices(reps, years_to_generate):
    substances_calculated_prices = pd.DataFrame(index=years_to_generate, columns=["zero"]).fillna(0)
    substances_calculated_prices.index.name = "year"
    substances_calculated_prices.index.astype(int, copy=True)
    for k, substance in reps.substances.items():
        calculatedPrices = substance.simulatedPrice.to_dict()
        df = pd.DataFrame(calculatedPrices['data'])
        df.set_index(0, inplace=True)
        df.index.name = "year"
        df.index = df.index.astype(int)
        df.columns = [substance.name]
        substances_calculated_prices = substances_calculated_prices.join(df)
    substances_calculated_prices.drop("zero", axis=1, inplace=True)
    return substances_calculated_prices


def prepare_screening_curves(reps, year):
    hours = np.array(list(range(1, 8760)))
    agent = reps.energy_producers[reps.agent]
    wacc = (1 - agent.debtRatioOfInvestments) * agent.equityInterestRate \
           + agent.debtRatioOfInvestments * agent.loanInterestRate
    yearly_costs = pd.DataFrame(index=hours)
    for tech_name, tech in reps.power_generating_technologies.items():
        annual_cost_capital = npf.pmt(wacc, tech.expected_lifetime, -tech.investment_cost_eur_MW)
        capex = annual_cost_capital + tech.fixed_operating_costs
        if tech.fuel == "":
            fuel_price = np.int64(0)
        else:
            calculatedPrices = tech.fuel.simulatedPrice.to_dict()
            df = pd.DataFrame(calculatedPrices['data'])
            df.set_index(0, inplace=True)
            fuel_price = df.at[str(year), 1]
        opex = tech.variable_operating_costs * hours + fuel_price * hours
        total = capex + opex
        yearly_costs[tech_name] = total
    return yearly_costs


def prepare_screening_curves_candidates(reps, year):
    hours = np.array(list(range(1, 8760)))
    agent = reps.energy_producers[reps.agent]
    wacc = (1 - agent.debtRatioOfInvestments) * agent.equityInterestRate \
           + agent.debtRatioOfInvestments * agent.loanInterestRate
    yearly_costs_candidates = pd.DataFrame(index=hours)
    for tech in reps.get_unique_candidate_technologies():
        annual_cost_capital = npf.pmt(wacc, tech.expected_lifetime, -tech.investment_cost_eur_MW)
        capex = annual_cost_capital + tech.fixed_operating_costs
        if tech.fuel == "":
            fuel_price = np.int64(0)
        else:
            future_prices = tech.fuel.futurePrice.to_dict()
            df = pd.DataFrame(future_prices['data'])
            df.set_index(0, inplace=True)
            fuel_price = df.at[str(year), 1]
        opex = tech.variable_operating_costs * hours + fuel_price * hours
        total = capex + opex
        yearly_costs_candidates[tech.name] = total
    return yearly_costs_candidates


def prepare_accepted_CapacityMechanism(reps, unique_technologies, years_to_generate):
    capacity_mechanisms_per_tech = pd.DataFrame(index=years_to_generate, columns=unique_technologies).fillna(0)
    for year in years_to_generate:
        for technology_name in unique_technologies:
            acceptedpertech = 0
            for power_plant in reps.get_power_plants_by_technology(technology_name):
                bid = reps.get_bid_for_plant_and_tick(power_plant.name, year)
                if bid != None:
                    acceptedpertech += bid.amount
            capacity_mechanisms_per_tech.loc[year, technology_name] = acceptedpertech
    return capacity_mechanisms_per_tech

    # for i in reps.financialPowerPlantReports.values():
    #         tech_names.append(reps.power_plants[i.name].technology.name)
    #         CM.append(i.capacityMarketRevenues_in_year)
    # grouped_CM_revenues = pd.DataFrame(CM, index=tech_names,
    #                                    columns=['Capacity Mechanism Revenues'])
    # grouped_CM_revenues = CM_revenues.groupby('index').mean()
    return


# def market_value_per_technology(reps, unique_technologies, years_to_generate):
#     all_techs_generation = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
#     for year in years_to_generate:
#         dispatch_per_year = reps.get_all_power_plant_dispatch_plans_by_tick(year)
#     for technology_name in unique_technologies:
#         capacity_per_tech = 0
#         generation_per_tech = 0
#         for id, v in dispatch_per_year.accepted_amount.items():
#             if  v > 0:
#                  pp_market_price =  pp_revenues /  pp_production_in_MWh
#             else:
#              pp_market_price = 0
#     pass


def prepare_capacity_and_generation_per_technology(reps, unique_technologies, years_to_generate):
    all_techs_capacity = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    all_techs_generation = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    all_techs_market_value = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    all_techs_capacity_factor = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    electricity_price = pd.DataFrame(index=years_to_generate).fillna(0)
    production_per_year = pd.DataFrame(index=years_to_generate).fillna(0)
    for year in years_to_generate:
        dispatch_per_year = reps.get_all_power_plant_dispatch_plans_by_tick(year)
        totalproduction = 0
        all_market_value = 0
        totalrevenues = 0
        for technology_name in unique_technologies:
            capacity_per_tech = 0
            generation_per_tech = 0
            market_value_per_tech = 0
            capacity_factor_per_tech = 0
            for id, pp_production_in_MWh in dispatch_per_year.accepted_amount.items():
                power_plant = reps.get_power_plant_by_id(id)
                if power_plant is not None:
                    if power_plant.technology.name == technology_name:
                        capacity_per_tech += power_plant.capacity
                        generation_per_tech += pp_production_in_MWh
                        capacity_factor_per_tech += pp_production_in_MWh / (power_plant.capacity * 8760)
                        if pp_production_in_MWh > 0:
                            # revenues in Euro/production in MWh
                            market_value_per_tech += dispatch_per_year.revenues[id] / pp_production_in_MWh
                            totalproduction += pp_production_in_MWh
                            totalrevenues += dispatch_per_year.revenues[id]
                            all_market_value += dispatch_per_year.revenues[id] / pp_production_in_MWh

            all_techs_capacity_factor.loc[technology_name, year] = capacity_factor_per_tech
            all_techs_market_value.loc[technology_name, year] = market_value_per_tech
            all_techs_capacity.loc[technology_name, year] = capacity_per_tech
            all_techs_generation.loc[technology_name, year] = generation_per_tech

        electricity_price.loc[year, 1] = totalrevenues / totalproduction
        production_per_year.loc[year, 1] = totalproduction
    return all_techs_capacity, all_techs_generation, all_techs_market_value, all_techs_capacity_factor, electricity_price, production_per_year


# from Bart van Nobelen
def get_shortage_hours(reps, years_to_generate, capacity):
    # demand_list = []
    shortage_hours = pd.DataFrame(index=years_to_generate)
    supply_ratio = pd.DataFrame(index=years_to_generate)
    for year in years_to_generate:
        trend = reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity", globalNames.simulated_prices,
                                                                       year)
        peak_load_without_trend = max(reps.get_hourly_demand_by_country(reps.country)[1])
        peak_load_volume = peak_load_without_trend * trend
        count = 0
        demand_list = reps.get_electricity_spot_market_demand()
        for i in demand_list:
            x = i * trend
            if x > capacity.loc[year]:
                count += 1
        shortage_hours.loc[year, 0] = count
        supply_ratio.loc[year, 0] = capacity.loc[year] / peak_load_volume

    return shortage_hours, supply_ratio


def generate_plots(reps,scenario_name ):
    print('Establishing and querying EmlabDB')
    path_to_plots = os.path.join(os.getcwd(), "plots", "Scenarios", scenario_name)

    # attention: erase this:
    # reps.current_year = 2029
    if not os.path.exists(path_to_plots):
        os.makedirs(path_to_plots)

    unique_technologies = reps.get_unique_technologies_names()
    unique_candidate_power_plants = reps.get_unique_candidate_technologies_names()
    years_to_generate = list(range(reps.start_simulation_year, reps.current_year + 1))  # control the current year

    years_to_generate_and_build = list(
        range(reps.start_simulation_year, reps.current_year + 1 + reps.max_permit_build_time))
    years_ahead_to_generate = [x + reps.lookAhead for x in years_to_generate]
    df_zeros = np.zeros(shape=(len(years_to_generate), len(unique_technologies)))
    ticks = [i - reps.start_simulation_year for i in years_to_generate]
    colors_unique_techs = []
    colors_unique_candidates = []
    for tech in unique_technologies:
        colors_unique_techs.append(technology_colors[tech])
    for tech in unique_candidate_power_plants:
        colors_unique_candidates.append(technology_colors[tech])

    # section -----------------------------------------------------------------------------------------------data preparation
    annual_balance = dict()

    print('Done reading db')
    first_year = years_to_generate[0]
    future_year = first_year + reps.lookAhead
    last_year = years_to_generate[-1]
    test_tick = 0
    test_tech = "CCGT"

    # check extension of power plants.
    # extension = prepare_extension_lifetime_per_tech(reps, unique_technologies)
    # section -----------------------------------------------------------------------------------------------Capacity Markets
    # CM_revenues = prepare_accepted_CapacityMechanism(reps, unique_technologies,
    #                                                  years_to_generate)
    # plot_CM_revenues(CM_revenues, path_to_plots)

    # section -----------------------------------------------------------------------------------------------capacities
    # todo: correct electricity prices
    all_techs_capacity, all_techs_generation, all_techs_market_price, all_techs_capacity_factor, electricity_price, production_per_year = prepare_capacity_and_generation_per_technology(
        reps, unique_technologies,
        years_to_generate)
    plot_capacity_factor(all_techs_capacity_factor.T, path_to_plots, colors_unique_techs)
    plot_electricity_prices(electricity_price, path_to_plots)
    total_capacity = all_techs_capacity.sum(axis=0)

    plot_installed_capacity(all_techs_capacity.T, path_to_plots, colors_unique_techs)
    plot_annual_generation(all_techs_generation.T, path_to_plots, colors_unique_techs)
    plot_market_values_generation(all_techs_market_price.T, path_to_plots, colors_unique_techs)
    shortages, supply_ratio = get_shortage_hours(reps, years_to_generate, total_capacity)
    plot_supply_ratio(supply_ratio, path_to_plots)
    plot_shortages(shortages, path_to_plots)
    # section -----------------------------------------------------------------------------------------------NPV and investments per iteration

    total_profits_per_tech_per_year = prepare_operational_profit_per_year_per_tech(reps, unique_technologies, years_to_generate,
                                                                 first_year)
    plot_total_profits_per_tech_per_year(total_profits_per_tech_per_year, path_to_plots, colors_unique_techs)
    irrs_per_tech_per_year = prepare_irr_per_technology_per_year(reps, unique_technologies, years_to_generate,
                                                                 first_year)
    plot_irrs_per_tech_per_year(irrs_per_tech_per_year, path_to_plots, colors_unique_techs)
    candidate_plants_profits_per_iteration = prepare_profits_candidates_per_iteration(
        reps, test_tick)
    plot_candidate_profits(candidate_plants_profits_per_iteration, test_tick, path_to_plots)

    installed_capacity_per_iteration, candidate_plants_project_value = prepare_capacity_per_iteration(
        future_year, reps, unique_candidate_power_plants)

    plot_investments_and_NPV_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration,
                                           first_year, path_to_plots, colors_unique_candidates)
    # section -----------------------------------------------------------------------------------------------revenues per iteration

    sorted_average_revenues_per_iteration_first_year, revenues_per_iteration = prepare_revenues_per_iteration(reps,
                                                                                                              test_tick)
    plot_revenues_per_iteration(revenues_per_iteration, test_tech, path_to_plots, test_tick)
    plot_average_revenues_per_iteration(sorted_average_revenues_per_iteration_first_year, path_to_plots, first_year,
                                        colors_unique_techs)

    annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_commissioned, \
    last_year_in_pipeline, last_year_decommissioned, \
    last_year_operational_capacity, last_year_to_be_decommissioned_capacity, \
    last_year_strategic_reserve_capacity, number_per_status, number_per_status_last_year = \
        prepare_pp_status(years_to_generate, years_to_generate_and_build, reps, unique_technologies)
    '''
    decommissioning is plotted according to the year when it is decided to get decommissioned
    '''
    future_fuel_prices = prepare_future_fuel_prices(reps, years_to_generate)

    plot_investments(annual_in_pipeline_capacity, annual_commissioned, annual_decommissioned_capacity, years_to_generate, path_to_plots,
                     colors_unique_techs)
    #plot_decommissions(annual_decommissioned_capacity, years_to_generate, path_to_plots, colors_unique_techs)
    # last_year_strategic_reserve_capacity
    plot_annual_operational_capacity(last_year_operational_capacity, path_to_plots, colors_unique_techs)
    plot_annual_to_be_decommissioned_capacity(last_year_to_be_decommissioned_capacity, years_to_generate, path_to_plots,
                                              colors_unique_techs)
    power_plants_status(number_per_status, path_to_plots)
    power_plants_last_year_status(number_per_status_last_year, path_to_plots, last_year)
    # section -----------------------------------------------------------------------------------------------revenues per iteration
    yearly_costs_candidates = prepare_screening_curves_candidates(reps, future_year)
    yearly_costs = prepare_screening_curves(reps, first_year)
    plot_screening_curve_candidates(yearly_costs_candidates, path_to_plots, first_year + reps.lookAhead,
                                    colors_unique_candidates)
    plot_screening_curve(yearly_costs, path_to_plots, first_year, colors_unique_techs)
    plot_future_fuel_prices(future_fuel_prices, path_to_plots)

    # section -----------------------------------------------------------------------------------------------todos
    residual_load_curves = pd.DataFrame()
    load_duration_curves = pd.DataFrame()
    price_duration_curves = pd.DataFrame()

    # section -----------------------------------------------------------------------------------------------AMIRIS
    # db_amiris_url = sys.argv[2]
    # print(db_amiris_url)
    # db_amiris = SpineDB(db_amiris_url)
    # all_dispatch_results = dict()
    # for i in years_to_generate:
    #     year = str(i)
    #     all_dispatch_results[year] = db_amiris.query_object_parameter_values_by_object_class(year)
    # db_amiris.close_connection()

    print('Showing plots...')
    plt.show()
    plt.close('all')


print('===== Start Generating Plots =====')

technology_colors = {
    'Biomass_CHP_wood_pellets_DH': "green",
    'Coal PSC': "black",
    "Fuel oil PGT": "gray",
    'Lignite PSC': "darkgoldenrod",
    'CCGT': "indianred",
    'OCGT': "darkred",
    'Hydropower_reservoir_medium': "darkcyan",
    'PV_utility_systems': "gold",
    'WTG_onshore': "cornflowerblue",
    "WTG_offshore": "navy",
    "Nuclear": "mediumorchid",
    "Hydropower_ROR": "aquamarine",
    "Lithium_ion_battery": "hotpink",
    "Pumped_hydro": "darkcyan"
}
try:

    name = "DE20202030_LA4_SD10_PH3_MI10000futureMarketWithHistoricProfit_extendedDE_dismantle_by_profit_no_dismantle"
    #name = "NL2030_LA4_SD4_PH3_MI10000futureMarketWithHistoricProfit_extendedDE_dis_by_profit_NL"
    #name = ""

    if name == "":
        emlab_url = sys.argv[1]
        amiris_url = sys.argv[2]
        # use "Amiris" if this should be read
        spinedb_reader_writer = SpineDBReaderWriter("Amiris", emlab_url, amiris_url)
        reps = spinedb_reader_writer.read_db_and_create_repository("plotting")
        name = reps.country  + str(reps.end_simulation_year) \
               + "_LA" + str(reps.lookAhead) + "_SD" + str(reps.start_year_dismantling) \
               + "_PH" + str(reps.pastTimeHorizon) + "_MI" + str(reps.maximum_investment_capacity_per_year) \
               + reps.simulation_name
    else:
        first = "sqlite:///C:\\Users\\isanchezjimene\\Documents\\TraderesCode\\toolbox-amiris-emlab\\emlabpy\\plots\\Scenarios\\"
        emlab_sql = "\\EmlabDB.sqlite"
        amiris_sql = "\\AMIRIS db.sqlite"
        emlab_url = first + name + emlab_sql
        amiris_url = first + name + amiris_sql
        spinedb_reader_writer = SpineDBReaderWriter("Amiris", emlab_url, amiris_url)
        reps = spinedb_reader_writer.read_db_and_create_repository("plotting")

    generate_plots(reps, name)

except Exception as e:
    logging.error('Exception occurred: ' + str(e))
    raise
finally:
    print("finished emlab")
    spinedb_reader_writer.db.close_connection()
    spinedb_reader_writer.amirisdb.close_connection()

print('===== End Generating Plots =====')

# amirisdb = SpineDB(sys.argv[2])
# db_amirisdata = amirisdb.export_data()
# object_parameter_values = db_amirisdata['object_parameter_values']
