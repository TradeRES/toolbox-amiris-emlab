"""
This script handles all preparations necessary for the execution of plots

Arg1: URL to EMLAB SpineDB
Arg2: URL to AMIRIS SpineDB
Arg3: URL of energy exhange SpineDB -> optional
leave name = "" to make a new folder with the repository name
or  name = "scenario name" with the DBs in the folder.
electricity = "" to dont graph the electricity prices

Sanchez
"""
import shutil
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import pandas as pd
import seaborn as sns
from util.spinedb_reader_writer import *
from util.spinedb import SpineDB
from copy import deepcopy
from matplotlib.offsetbox import AnchoredText
import numpy as np

logging.basicConfig(level=logging.ERROR)

plt.rcParams.update({'font.size': 14})


def plot_investments_and_NPV_per_iteration(candidate_plants_project_value_per_MW, installed_capacity_per_iteration,
                                           future_year, path_to_plots, colors_unique_candidates):
    print('investments and NPV')
    fig1, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    colors = [technology_colors[tech] for tech in candidate_plants_project_value_per_MW.columns.tolist()]
    candidate_plants_project_value_per_MW.plot(ax=ax1, color=colors)
    if installed_capacity_per_iteration.size != 0:
        installed_capacity_per_iteration.plot(ax=ax2, color=colors_unique_candidates, linestyle='None', marker='o')
    ax1.set_xlabel('Iterations', fontsize='medium')
    ax1.set_ylabel('NPV [€] (lines)', fontsize='medium')
    ax2.set_ylabel('Investments MW (dotted)', fontsize='medium')
    if write_titles == True:
        ax1.set_title(
            scenario_name + 'Investments and NPV per MW per iterations ' + '\n for future year ' + str(future_year))

    # ax1.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)  # void showing zero investments
    ax1.legend(candidate_plants_project_value_per_MW.columns.values.tolist(), fontsize='medium', loc='upper left',
               bbox_to_anchor=(1.2, 1.1))
    ax2.legend(installed_capacity_per_iteration.columns.values.tolist(), fontsize='medium', loc='upper left',
               bbox_to_anchor=(1.2, 0.5))
    fig1.savefig(path_to_plots + '/' + 'Candidate power plants NPV and Investment decisions for future year ' + str(
        future_year) + '.png', bbox_inches='tight', dpi=300)


def plot_candidate_profits_per_iteration(profits_per_iteration, path_to_plots, colors_unique_candidates):
    print('profits per iteration')
    axs13 = profits_per_iteration.plot(color=colors_unique_candidates)
    axs13.set_axisbelow(True)
    plt.xlabel('iterations', fontsize='medium')
    plt.ylabel('Revenues - Operational Costs €', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs13.annotate('legend = with tested capacity',
                   xy=(1.1, 1.1), xycoords='figure fraction',
                   horizontalalignment='right', verticalalignment='top',
                   fontsize='small')
    if write_titles == True:
        axs13.set_title(scenario_name + 'Expected future operational profits\n candidates in tick ' + str(test_tick))

    fig13 = axs13.get_figure()
    fig13.savefig(path_to_plots + '/' + 'Expected profits Candidates in tick ' + str(test_tick) + '.png',
                  bbox_inches='tight',
                  dpi=300)


# def plot_decommissions(annual_decommissioned_capacity, years_to_generate, path_to_plots, colors):
#     print('Create decommissioning plot')
#     fig5, axs5 = plt.subplots()
#     axs5 = annual_decommissioned_capacity.plot.bar(stacked=True, rot=0, color=colors, grid=True, legend=False)
#     axs5.set_axisbelow(True)
#     axs5.set_xlabel('Years', fontsize='medium')
#     for label in axs5.get_xticklabels(which='major'):
#         label.set(rotation=50, horizontalalignment='right')
#     axs5.set_ylabel('Capacity (MW)', fontsize='medium')
#     axs5.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
#     axs5.set_title('Dismantled Capacity per Technology')
#     fig5 = axs5.get_figure()
#     fig5.savefig(path_to_plots + '/' + 'Dismantled.png', bbox_inches='tight', dpi=300)
#     plt.show()


def plot_investments(annual_installed_capacity, annual_commissioned, annual_decommissioned_capacity,
                     path_to_plots, colors):
    print('Capacity Investments plot')
    annual_installed_capacity = annual_installed_capacity / 1000
    annual_decommissioned_capacity = annual_decommissioned_capacity / 1000
    annual_commissioned = annual_commissioned / 1000

    fig6, axs6 = plt.subplots(3, 1)
    fig6.tight_layout()
    annual_installed_capacity.plot.bar(ax=axs6[0], stacked=True, rot=0, color=colors, grid=True, legend=False)
    annual_commissioned.plot.bar(ax=axs6[1], stacked=True, rot=0, color=colors, grid=True, legend=False)
    annual_decommissioned_capacity.plot.bar(ax=axs6[2], stacked=True, rot=0, color=colors, grid=True, legend=False)
    axs6[0].set_axisbelow(True)
    axs6[2].set_xlabel('Years', fontsize='medium')
    axs6[0].grid(True, which='minor')
    axs6[1].grid(True, which='minor')
    axs6[2].grid(True, which='minor')
    axs6[0].xaxis.set_major_locator(ticker.MultipleLocator(5))
    axs6[1].xaxis.set_major_locator(ticker.MultipleLocator(5))
    axs6[2].xaxis.set_major_locator(ticker.MultipleLocator(5))

    axs6[0].set_ylabel('In pipeline GW', fontsize='small')
    axs6[1].set_ylabel('Commissioned GW', fontsize='small')
    axs6[2].set_ylabel('Decommissioned GW', fontsize='small')

    # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.5))
    if write_titles == True:
        axs6[0].set_title(
            scenario_name + '\n Investments by decision year (up) \n and by commissioning year (down)')
    fig6.savefig(path_to_plots + '/' + 'Capacity Investments.png', bbox_inches='tight', dpi=300)


def plot_power_plants_status(number_per_status, path_to_plots):
    print("power plants status")
    axs8 = number_per_status.plot.bar(rot=0, grid=True, legend=False)
    axs8.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.xticks(rotation=60)
    plt.ylabel('Capacity per status (MW)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    axs8.set_title('Power plants status')
    fig8 = axs8.get_figure()
    fig8.savefig(path_to_plots + '/' + 'Power plants status per year.png', bbox_inches='tight', dpi=300)


def plot_power_plants_last_year_status(power_plants_last_year_status, path_to_plots, last_year):
    plt.figure()
    axs9 = power_plants_last_year_status.plot.bar(stacked=True, rot=0, grid=True, legend=False)
    axs9.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity per status (MW)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    if write_titles == True:
        axs9.set_title(scenario_name + 'Power plants status ' + str(last_year))
    fig9 = axs9.get_figure()
    fig9.savefig(path_to_plots + '/' + 'Power plants status ' + str(last_year) + '.png', bbox_inches='tight', dpi=300)


# def plot_annual_operational_capacity(annual_operational_capacity, path_to_plots, colors):
#     print('Annual operational capacity')
#     plt.figure()
#     axs10 = annual_operational_capacity.plot.bar(stacked=True, rot=0, color=colors, grid=True, legend=False)
#     axs10.set_axisbelow(True)
#     plt.xlabel('Years', fontsize='medium')
#     plt.ylabel('Capacity (MW)', fontsize='medium')
#     plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
#     axs10.set_title('Operational Capacity per Technology')
#     fig10 = axs10.get_figure()
#     fig10.savefig(path_to_plots + '/' + 'Operational Capacity per Technology.png', bbox_inches='tight', dpi=300)


def plot_revenues_per_iteration_for_one_tech(all_future_operational_profit, path_to_plots, future_year,
                                             ):
    if all_future_operational_profit.shape[1] == 0:
        print("this technology is expected to be decommissioned")
    else:
        plt.figure()
        axs11 = all_future_operational_profit.plot()
        axs11.set_axisbelow(True)
        plt.xlabel('Iterations', fontsize='medium')
        plt.ylabel('Revenues - Operational Costs [€]', fontsize='medium')
        plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1), ncol=5)
        plt.grid()
        axs11.set_title('Operational profits of installed plants \n in tick '
                        + str(test_tick) + ' = future year ' + str(future_year) + ' \n and technology ' + test_tech)
        axs11.annotate('legend =  capacity, efficiency, age',
                       xy=(1.1, 1.1), xycoords='figure fraction',
                       horizontalalignment='right', verticalalignment='top',
                       fontsize='small')
        fig11 = axs11.get_figure()
        fig11.savefig(
            path_to_plots + '/' + 'Expected future profit in year ' + str(
                test_tick) + "future " + str(future_year) + ' ' + test_tech + '.png',
            bbox_inches='tight', dpi=300)


def plot_expected_candidate_profits_real_profits(candidates_profits_per_iteration, operational_profits_commissioned,
                                                 path_to_plots, future_year,
                                                 ):
    plt.figure()
    axs11 = candidates_profits_per_iteration.plot(style="*")
    # adding a new row, to shift series to right to be in line with candidate profits (thera re no results for first iteration)
    new_row = pd.Series(0, index=['A'])
    operational_profits_commissioned = new_row.append(operational_profits_commissioned)
    operational_profits_commissioned.plot(style=".", ax=axs11, label="REAL")
    for label in axs11.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')
    axs11.set_axisbelow(True)
    plt.xlabel('Iterations', fontsize='medium')
    plt.ylabel('Revenues - Operational Costs [€]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1), ncol=5)
    plt.grid()
    axs11.set_title(
        'Expected candidate future operational profits  vs real operational profits in tick in year '
        + str(future_year))

    fig11 = axs11.get_figure()
    fig11.savefig(
        path_to_plots + '/' + 'Expected candidate vs real profits in future year' + str(
            future_year) + ' and real profit.png',
        bbox_inches='tight', dpi=300)


def plot_average_revenues_per_iteration(revenues_iteration, path_to_plots, first_year, colors):
    print('Average Revenues per iteration')
    plt.figure()
    axs15 = revenues_iteration.plot(color=colors)
    axs15.set_axisbelow(True)
    plt.xlabel('Iterations', fontsize='medium')
    plt.ylabel('Revenues [€]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs15.set_title('Average revenues per technologies for year ' + str(first_year))
    fig15 = axs15.get_figure()
    fig15.savefig(path_to_plots + '/' + 'Average Technology Revenues per iteration ' + str(first_year) + '.png',
                  bbox_inches='tight', dpi=300)


def plot_future_fuel_prices(future_fuel_prices, path_to_plots):
    plt.figure()
    colors = [fuel_colors[tech] for tech in future_fuel_prices.columns.values]
    axs12 = future_fuel_prices.plot(color=colors)
    axs12.set_axisbelow(True)
    plt.xlabel('Year', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    axs12.annotate('electricity refers to the increase on demand',
                   xy=(1.1, 1.1), xycoords='figure fraction',
                   horizontalalignment='right', verticalalignment='top',
                   fontsize='small')
    plt.grid()
    axs12.set_title('Expected future fuel prices per year (4 years ahead)')
    fig12 = axs12.get_figure()
    fig12.savefig(path_to_plots + '/' + 'Future Fuel prices per year.png', bbox_inches='tight', dpi=300)


def plot_screening_curve(yearly_costs, marginal_costs_per_hour, path_to_plots, test_year):
    colors_unique_techs = [technology_colors[tech] for tech in yearly_costs.columns.values]
    axs13 = yearly_costs.plot(color=colors_unique_techs)
    axs13.set_axisbelow(True)
    axs13.annotate('annual fixed costs + (variable cost + fuel costs + CO2 costs) hours /efficiency',
                   xy=(.025, 1), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='top',
                   fontsize='medium')
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs13.set_title('Screening curve in year ' + str(test_year))
    fig13 = axs13.get_figure()
    fig13.savefig(path_to_plots + '/' + 'Screening curve (with CO2)' + str(test_year) + '.png', bbox_inches='tight',
                  dpi=300)
    plt.close('all')
    axs14 = marginal_costs_per_hour.reset_index().plot.scatter(x="index", y=0)
    axs14.set_axisbelow(True)
    plt.xticks(rotation=90)
    plt.ylabel('Prices (€/MWh per hour', fontsize='medium')
    # axs14.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs14.set_title('Marginal price at year ' + str(test_year))
    fig14 = axs14.get_figure()
    fig14.savefig(path_to_plots + '/' + 'Marginal_price(with CO2)' + str(test_year) + '.png', bbox_inches='tight',
                  dpi=300)


def plot_screening_curve_candidates(yearly_costs_candidates, path_to_plots, future_year):
    colors_unique_techs = [technology_colors[tech] for tech in yearly_costs_candidates.columns.values]
    axs14 = yearly_costs_candidates.plot(color=colors_unique_techs)
    axs14.set_axisbelow(True)
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs14.set_title('Screening curve \n candidate technologies for year ' + str(future_year))
    fig14 = axs14.get_figure()
    fig14.savefig(
        path_to_plots + '/' + 'Screening curve candidate technologies (with CO2)' + str(future_year) + '.png',
        bbox_inches='tight', dpi=300)


def plot_CM_revenues(CM_revenues_per_technology, accepted_pp_per_technology, capacity_mechanisms_per_tech,
                     CM_clearing_price,capacity_market_future_price, CM_clearing_volume,capacity_market_future_volume,
                    total_costs_CM,  SR_operator_revenues, cm_revenues_per_pp, price_cap,
                     path_to_plots, colors_unique_techs):
    # df.plot(x='Team', kind='bar', stacked=True,
    axs26 = accepted_pp_per_technology.plot(kind='bar', stacked=True, color=colors_unique_techs)
    axs26.set_axisbelow(True)
    plt.xlabel('tick', fontsize='medium')
    plt.ylabel('Number awarded', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs26.set_title(reps.capacity_remuneration_mechanism + ' awarded plants')
    fig26 = axs26.get_figure()
    fig26.savefig(path_to_plots + '/' + 'Capacity Mechanisms awarded plants.png', bbox_inches='tight', dpi=300)

    # the CM revenues per technology are retrieved from the financial results
    CM_revenues_per_technology.dropna(how='all', axis=1, inplace=True)
    axs15 = CM_revenues_per_technology.plot(kind='bar', stacked=True, color=colors_unique_techs, legend=None)
    axs15.set_axisbelow(True)
    plt.xlabel('tick', fontsize='medium')
    plt.ylabel('Revenues CM [€]', fontsize='medium')
    #plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs15.set_title(reps.capacity_remuneration_mechanism + ' \n costs per technology')
    fig15 = axs15.get_figure()
    fig15.savefig(path_to_plots + '/' + 'Capacity Mechanisms costs per technology.png', bbox_inches='tight', dpi=300)

    if capacity_mechanisms_per_tech.empty:
        pass
    else:
        axs27 = capacity_mechanisms_per_tech.plot(kind='bar', stacked=True, color=colors_unique_techs)
        axs27.set_axisbelow(True)
        plt.xlabel('tick', fontsize='medium')
        plt.ylabel('Awarded Capacity [MW]', fontsize='medium')
        plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid()
        axs27.set_title(reps.capacity_remuneration_mechanism + '\n capacity per technology')
        fig27 = axs27.get_figure()
        fig27.savefig(path_to_plots + '/' + 'Capacity Mechanism capacity per technology.png', bbox_inches='tight',
                      dpi=300)

    if reps.capacity_remuneration_mechanism == "strategic_reserve_ger":
        axs29 = SR_operator_revenues.plot()
        axs29.set_axisbelow(True)
        plt.xlabel('tick', fontsize='medium')
        plt.ylabel('[€]', fontsize='medium')
        plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid()
        axs29.set_title('Strategic Reserve operator revenues')
        fig29 = axs29.get_figure()
        fig29.savefig(path_to_plots + '/' + 'SR_operator_revenues.png', bbox_inches='tight', dpi=300)

        # cm_revenues_per_pp.replace(0, pd.NA, inplace=True)
        # cm_revenues_per_pp.dropna(how='all', axis=1, inplace=True)
        # axs28 = cm_revenues_per_pp.plot()
        # axs28.set_axisbelow(True)
        # plt.xlabel('tick', fontsize='medium')
        # plt.ylabel('Revenues SR', fontsize='medium')
        # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
        # plt.grid()
        # axs28.set_title('SR_results_per_pp')
        # fig28 = axs28.get_figure()
        # fig28.savefig(path_to_plots + '/' + 'SR_results_per_pp.png', bbox_inches='tight', dpi=300)
    else:
        axs27 = CM_clearing_volume.plot()
        capacity_market_future_volume.plot(ax=axs27,  marker='o', linestyle='--')
        axs27.set_axisbelow(True)
        plt.xlabel('Simulation year', fontsize='medium')
        plt.ylabel('CM clearing volume [MW]  \n in effective year ', fontsize='medium')
        plt.legend(["realized", "estimated"],fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid()
        axs27.set_title(reps.capacity_remuneration_mechanism + '\n clearing volume')
        fig27 = axs27.get_figure()
        fig27.savefig(path_to_plots + '/' + 'Capacity Mechanism clearing volume.png', bbox_inches='tight', dpi=300)
        axs28 = CM_clearing_price.plot()
        capacity_market_future_price.plot(ax=axs28 ,marker='o', linestyle='--')
        axs28.set_axisbelow(True)
        plt.xlabel('Simulation year', fontsize='medium')
        plt.ylabel('CM clearing price [€/MW]', fontsize='medium')
        plt.legend(["realized", "estimated"], fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid()
        if reps.capacity_remuneration_mechanism in [globalNames.capacity_subscription, globalNames.capacity_market]:
            axs28.set_title(reps.capacity_remuneration_mechanism + '\n clearing price. \nPrice cap ' + str(price_cap) + ' €/MW')
        else:
            axs28.set_title(reps.capacity_remuneration_mechanism + '\n clearing price  €/MW' + "\n based on previous year results" )
        fig28 = axs28.get_figure()
        fig28.savefig(path_to_plots + '/' + 'Capacity Mechanism clearing price.png', bbox_inches='tight', dpi=300)

        axs29 = total_costs_CM.plot()
        axs29.set_axisbelow(True)
        plt.xlabel('tick', fontsize='medium')
        plt.ylabel('total costs [€]', fontsize='medium')
        plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid()
        axs29.set_title(reps.capacity_remuneration_mechanism + '\n total costs')
        fig29 = axs29.get_figure()
        fig29.savefig(path_to_plots + '/' + 'Capacity Mechanism total costs.png', bbox_inches='tight', dpi=300)

def plot_irrs_and_npv_per_tech_per_year(irrs_per_tech_per_year, npvs_per_tech_per_MW, profits_with_loans_all,
                                        path_to_plots, technology_colors):
    # irrs_per_tech_per_year.drop("PV_utility_systems",  axis=1,inplace=True)
    # irrs_per_tech_per_year.drop("WTG_onshore", axis=1, inplace=True)
    colors = [technology_colors[tech] for tech in npvs_per_tech_per_MW.columns.values]
    axs16 = irrs_per_tech_per_year.plot(color=colors)
    axs16.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('IRR %', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs16.set_title('IRRs, not including NAN results')
    # plt.ylim(-100, 300)
    fig16 = axs16.get_figure()
    fig16.savefig(path_to_plots + '/' + 'IRRs per year per technology.png', bbox_inches='tight', dpi=300)

    npvs_per_tech_per_MW = npvs_per_tech_per_MW / 1000000
    axs27 = npvs_per_tech_per_MW.plot(color=colors)
    axs27.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('mill. €', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs27.set_title('Average NPVs per MW (discount rate=0%)' + '\n ignoring nan, ')
    fig27 = axs27.get_figure()
    fig27.savefig(path_to_plots + '/' + 'NPVs per capacity per technology.png', bbox_inches='tight', dpi=300)
    plt.close('all')

    axs29 = profits_with_loans_all.plot(color=colors)
    axs29.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('€', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    if write_titles == True:
        axs29.set_title(scenario_name + 'Average profits (with loans) per technology')
    fig29 = axs29.get_figure()
    fig29.savefig(path_to_plots + '/' + 'Profits with loans per MW.png', bbox_inches='tight', dpi=300)
    plt.close('all')

    # test_plant = "112"
    # totalProfits = reps.financialPowerPlantReports[test_plant].totalProfits.sort_index()
    # totalProfitswLoans = reps.financialPowerPlantReports[test_plant].totalProfitswLoans.sort_index()
    # npv = reps.financialPowerPlantReports[test_plant].npv.sort_index()
    # totalCosts = reps.financialPowerPlantReports[test_plant].totalCosts.sort_index()
    # fixedCosts= - reps.financialPowerPlantReports[test_plant].fixedCosts.sort_index()
    # overallRevenue = reps.financialPowerPlantReports[test_plant].overallRevenue.sort_index()
    # axs20 = npv.plot()
    # totalProfits.plot(ax=axs20, label="totalProfits")
    # totalProfitswLoans.plot(ax=axs20, label="totalProfitswLoans ")
    # fixedCosts.plot(ax=axs20, label="fixedCosts")
    # overallRevenue.plot(ax=axs20, label="overallRevenue ")
    # totalCosts.plot(ax=axs20, label="totalCosts ")
    # axs20.set_axisbelow(True)
    # plt.xlabel('hours', fontsize='medium')
    # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    # axs20.set_title('financial report')
    # fig20 = axs20.get_figure()
    # fig20.savefig(path_to_plots + '/' + 'Finanical report for ' + test_plant+'.png', bbox_inches='tight', dpi=300)


def plot_total_profits_per_tech_per_year(average_profits_per_tech_per_year_perMW, path_to_plots, colors):
    # CM revenues + revenues - variable costs - fixed costs
    axs25 = average_profits_per_tech_per_year_perMW.plot(color=colors)
    axs25.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('operational profits [€]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs25.annotate('Annual profits = revenues + CM revenues - variable costs - fixed costs',
                   xy=(0.025, 1), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='top',
                   fontsize='medium')
    axs25.set_title('Average Profits per MW (per Technology)')
    fig25 = axs25.get_figure()
    fig25.savefig(path_to_plots + '/' + 'Operational profits, average per year per technology.png', bbox_inches='tight',
                  dpi=300)
    plt.close('all')


def plot_profits_for_tech_per_year(new_pp_profits_for_tech, path_to_plots, colors):
    axs26 = new_pp_profits_for_tech.plot(color=colors)
    axs26.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('operational profits [€]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1), ncol=5)
    plt.grid()
    axs26.set_title('Operational profits per year \n for ' + test_tech)
    axs26.annotate('Annual profits = revenues + CM revenues - variable costs - fixed costs',
                   xy=(0, 1), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='top',
                   fontsize='medium')
    fig26 = axs26.get_figure()
    fig26.savefig(path_to_plots + '/' + 'Operational profits per year for ' + test_tech + '.png', bbox_inches='tight',
                  dpi=300)
    plt.close('all')


def plot_installed_capacity(all_techs_capacity, path_to_plots, years_to_generate, years_to_generate_initialization,
                            technology_colors, ticks_to_generate
                            ):
    print('plotting installed Capacity per technology ')
    installed_capacity = all_techs_capacity.loc[years_to_generate]
    all_techs_capacity_nozeroes = installed_capacity[installed_capacity > 0]
    all_techs_capacity_nozeroes.dropna(how='all', axis=1, inplace=True)

    colors = [technology_colors[tech] for tech in all_techs_capacity_nozeroes.columns.values]
    all_techs_capacity_nozeroes = all_techs_capacity_nozeroes / 1000
    all_techs_capacity_nozeroes.rename(columns=technology_names, inplace=True)
    # all_techs_capacity_nozeroes.index = all_techs_capacity_nozeroes.index - 2050
    axs17 = all_techs_capacity_nozeroes.plot.area(color=colors, legend=None, figsize=(5, 5))
    plt.legend(fontsize='large', loc='upper left', bbox_to_anchor=(1, 1))
    axs17.set_axisbelow(True)
    plt.xlabel('Years', fontsize='large')
    plt.ylabel('Installed Capacity [GW]', fontsize='large')
    results_file = os.path.join(path_to_plots, 'capacities.csv')
    all_techs_capacity_nozeroes.to_csv(results_file, header=True, sep=';', index=True)
    plt.grid()
    fig17 = axs17.get_figure()
    fig17.savefig(path_to_plots + '/' + 'Annual installed Capacity per technology.png', bbox_inches='tight', dpi=300)
    plt.close('all')
    return all_techs_capacity_nozeroes


def plot_total_demand(reps):
    future_demand = reps.get_peak_future_demand()
    realized_demand = reps.get_realized_peak_demand()
    fig21, axs21 = plt.subplots()
    future_demand.plot(label='future demand')
    realized_demand.plot(label='realized demand')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs21.set_title('peak demand')
    fig21.savefig(path_to_plots + '/' + 'Peak demand.png', bbox_inches='tight', dpi=300)
    plt.close('all')


def plot_capacity_factor_and_full_load_hours(all_techs_capacity_factor, all_techs_full_load_hours, path_to_plots,
                                             colors_unique_techs):
    all_techs_capacity_factornonzero = all_techs_capacity_factor[all_techs_capacity_factor > 0]
    all_techs_capacity_factornonzero.dropna(axis=1, how='all', inplace=True)
    colors = [technology_colors[tech] for tech in all_techs_capacity_factornonzero.columns.values]
    axs23 = all_techs_capacity_factornonzero.plot(color=colors)
    axs23.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity factor [%]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    if write_titles == True:
        axs23.set_title(scenario_name + ' Capacity factor (production/capacity*hoursinyear)')
    fig23 = axs23.get_figure()
    fig23.savefig(path_to_plots + '/' + 'Capacity factor.png', bbox_inches='tight', dpi=300)

    axs24 = all_techs_full_load_hours.plot(color=colors)
    axs24.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Hours', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs24.set_title('Full load hours (production/capacity)')
    fig24 = axs24.get_figure()
    fig24.savefig(path_to_plots + '/' + 'Full load hours.png', bbox_inches='tight', dpi=300)
    plt.close('all')


def plot_annual_generation(all_techs_generation, all_techs_consumption, path_to_plots, technology_colors
                           ):
    """
    ALl technologies after the current simulation year can be wrongly displayed (capacity limits can be passed)
    because decommissions are not considered.
    """
    all_techs_generation_nozeroes = all_techs_generation[all_techs_generation > 0]
    all_techs_generation_nozeroes.dropna(how='all', axis=1, inplace=True)
    all_techs_consumption_nozeroes = all_techs_consumption[all_techs_consumption > 0]
    all_techs_consumption_nozeroes.dropna(how='all', axis=1, inplace=True)
    all_techs_generation_nozeroes = all_techs_generation_nozeroes / 1000000
    all_techs_consumption_nozeroes = all_techs_consumption_nozeroes / 1000000
    colors = [technology_colors[tech] for tech in all_techs_generation_nozeroes.columns.values]
    # if calculate_investments == False:
    #     all_techs_generation_nozeroes = pd.concat([all_techs_generation_nozeroes] * 2, ignore_index=True)
    all_techs_generation_nozeroes.rename(columns=technology_names, inplace=True)
    # all_techs_generation_nozeroes.index = all_techs_generation_nozeroes.index - 2050
    axs18 = all_techs_generation_nozeroes.plot.area(color=colors, figsize=(5, 5))
    axs18.set_axisbelow(True)
    plt.xlabel('Years', fontsize='large')
    plt.ylabel('Annual Generation [TWh]', fontsize='large')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    all_techs_generation_nozeroes.rename(columns=technology_names, inplace=True)
    if write_titles == True:
        axs18.set_title(scenario_name + ' \n Annual Generation')
    fig18 = axs18.get_figure()
    fig18.savefig(path_to_plots + '/' + 'Annual generation per technology.png', bbox_inches='tight', dpi=300)
    plt.close('all')

    results_file = os.path.join(path_to_plots, 'annualGenerationRES.csv')
    all_techs_generation_nozeroes.to_csv(results_file, header=True, sep=';', index=True)
    axs19 = all_techs_consumption_nozeroes.plot.area(color=colors)
    axs19.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Annual Consumption [TWh]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid()
    axs19.set_title(scenario_name + ' \n Annual Consumption')
    fig19 = axs19.get_figure()
    fig19.savefig(path_to_plots + '/' + 'Annual Consumption per technology.png', bbox_inches='tight', dpi=300)
    plt.close('all')
    return all_techs_generation_nozeroes


def plot_supply_ratio(supply_ratio, curtailed_res, yearly_load, path_to_plots):
    print("load and residual load = (minimum of hourly supplied /demand)")
    axs19 = supply_ratio.plot()
    axs19.set_axisbelow(True)
    plt.xlabel('Supply ratio %', fontsize='medium')

    if write_titles == True:
        axs19.set_title(scenario_name + ' \n Supply ratio')
    plt.xlabel('Years', fontsize='medium')
    plt.grid()
    fig19 = axs19.get_figure()
    fig19.savefig(path_to_plots + '/' + 'Supply ratio.png', bbox_inches='tight', dpi=300)

    axs19.annotate("controllable capacity / peak load",
                   xy=(0, 0), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='bottom',
                   fontsize='small')

    curtailed_res_TWh = curtailed_res / 1000000
    axs20 = curtailed_res_TWh.plot()
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Curtailed VRES [TWh]', fontsize='medium')
    axs20.set_title('Curtailed VRES')
    fig20 = axs20.get_figure()
    fig20.savefig(path_to_plots + '/' + 'Curtailed VRES.png', bbox_inches='tight', dpi=300)
    plt.close('all')

    # fig20, axs20 = plt.subplots()
    # n = len(residual_load.columns)
    # rl_sorted = pd.DataFrame()
    # colors = plt.cm.rainbow(np.linspace(0, 1, n))
    # for col in residual_load:
    #     rl_sorted[col] = residual_load[col].sort_values(ignore_index=True, ascending=False, )
    # load = yearly_load[reps.current_year].sort_values(ignore_index=True, ascending=False, )
    # rl_sorted = rl_sorted / 1000
    # load = load / 1000
    # rl_sorted.plot(ax=axs20, label="residual_load", color=colors)
    # load.plot(ax=axs20, label="load in year " + str(reps.current_year))
    # axs20.set_axisbelow(True)
    # plt.xlabel('Hours', fontsize='medium')
    # plt.ylabel('Load [GW]', fontsize='medium')
    # plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(0.2, 1), ncol=5)
    # axs20.set_title('Residual load')
    # fig20 = axs20.get_figure()
    # fig20.savefig(path_to_plots + '/' + 'Load and residual load.png', bbox_inches='tight', dpi=300)
    # plt.close('all')


def plot_shortages_and_ENS(shortages, load_shedded_per_group_MWh, path_to_plots):
    fig3, axs3 = plt.subplots(2, 1)
    fig3.tight_layout()
    ENS_in_simulated_years_gwh = load_shedded_per_group_MWh.sum(axis =1) / 1000
    shortages.plot(ax=axs3[0], grid=True, legend=False)
    ENS_in_simulated_years_gwh.plot(ax=axs3[1], grid=True, legend=False)
    axs3[0].set_ylabel('LOLE [h] ', fontsize='large')
    axs3[0].set_xlabel('Years', fontsize='large')
    axs3[1].set_ylabel('ENS \n [GWh]', fontsize='large')

    fig3.savefig(path_to_plots + '/' + 'LOLE_ENS.png', bbox_inches='tight', dpi=300)
    plt.close()


def plot_yearly_VRES_support(yearl_vres_support, path_to_plots):
    axs33 = yearl_vres_support.plot()
    axs33.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('[€]', fontsize='medium')
    plt.grid()
    for label in axs33.get_xticklabels(which='major'):
        label.set(rotation=45, horizontalalignment='right')
    # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))

    if write_titles == True:
        axs33.set_title(scenario_name + ' \n Yearly VRES support from target investment')
    fig33 = axs33.get_figure()
    fig33.savefig(path_to_plots + '/' + 'VRES support.png', bbox_inches='tight', dpi=300)
    plt.close('all')


def plot_costs_to_society(average_electricity_price, costs_to_society, costs_to_society4000, social_welfare, path_to_plots):
    axs30 = average_electricity_price.plot()
    axs30.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Total price', fontsize='medium')
    plt.grid()
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.ylabel('Price to society [Eur/MWh]', fontsize='medium')

    axs30.set_title(scenario_name + ' \n Price to society (SR costs =- SR revenues')
    fig30 = axs30.get_figure()
    fig30.savefig(path_to_plots + '/' + 'average electricity price.png', bbox_inches='tight', dpi=300)

    axs31 = DispatchSystemCostInEUR.plot()
    axs31.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Total price', fontsize='medium')
    plt.grid()
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs31.set_title('Wholesale market costs to society')
    fig31 = axs31.get_figure()
    fig31.savefig(path_to_plots + '/' + 'Costs to society (Wholesale market).png', bbox_inches='tight', dpi=300)

    axs1 = costs_to_society.plot.area(figsize=(5, 5))
    total_cost = costs_to_society4000.sum(axis=1)
    total_cost.plot(ax=axs1, color='black', linestyle='--',  label='@4000')
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('[Eur]', fontsize='medium')
    plt.grid()
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs1.set_title('Costs to society')
    fig1 = axs1.get_figure()
    fig1.savefig(path_to_plots + '/' + 'Costs to society.png', bbox_inches='tight', dpi=300)

    axs2 = social_welfare.plot()
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('social_welfare', fontsize='medium')
    plt.grid()
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs2.set_title('social_welfare')
    fig2= axs2.get_figure()
    fig2.savefig(path_to_plots + '/' + 'social_welfare.png', bbox_inches='tight', dpi=300)


def plot_average_and_weighted(total_electricity_price, simple_electricity_prices_average, path_to_plots):
    average_weighted = total_electricity_price["wholesale price"]
    fig3, axs3 = plt.subplots(2, 1)
    fig3.tight_layout()
    average_weighted.plot(ax=axs3[0], grid=True, legend=False)
    simple_electricity_prices_average.plot(ax=axs3[1], grid=True, legend=False)
    plt.xlabel('Years', fontsize='medium')
    axs3[0].set_ylabel('weighted average \n electricity price\n €/Mwh', fontsize='large')
    axs3[1].set_ylabel('simple', fontsize='large')
    axs3[0].set_title('Average and weighted average electricity price')
    fig3.savefig(path_to_plots + '/' + 'Electricity price average and weighted.png', bbox_inches='tight', dpi=300)
    plt.close('all')


def plot_market_values_generation(all_techs_capacity, path_to_plots, colors_unique_techs):
    # these market values only include plants if they have been dispatched
    axs21 = all_techs_capacity.plot(color=colors_unique_techs)
    axs21.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    # plt.ylim([-5, 300])
    plt.ylabel('Market value (€/MWh)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    if write_titles == True:
        axs21.set_title(scenario_name + ' \n Market values (Market revenues / Production)')
    fig21 = axs21.get_figure()
    fig21.savefig(path_to_plots + '/' + 'Market values per technology.png', bbox_inches='tight', dpi=300)
    plt.close('all')


def plot_full_load_hours_values(all_techs_full_load_hours, path_to_plots, renewable_technologies, colors_unique_techs):
    # not market values because market values dont consider the installed capacity: only production/capacity
    vRES_full_load_hours = all_techs_full_load_hours[renewable_technologies]
    colors = [technology_colors[tech] for tech in vRES_full_load_hours.columns.values]
    axs21 = vRES_full_load_hours.plot(color=colors)
    axs21.set_axisbelow(True)
    if write_titles == True:
        axs21.set_title(scenario_name + ' \n Full load hours renewables(production/capacity)')
    plt.xlabel('Years', fontsize='medium')
    fig21 = axs21.get_figure()
    fig21.savefig(path_to_plots + '/' + 'RenewablesFullLoadHours.png', bbox_inches='tight', dpi=300)
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.close('all')
    results_file = os.path.join(path_to_plots, 'RenewablesFullLoadHours.csv')
    vRES_full_load_hours.to_csv(results_file, header=True, sep=';', index=True)


def plot_yearly_average_electricity_prices_and_RES_share(electricity_price, share_RES, path_to_plots):
    axs22 = electricity_price.plot(legend=False, figsize=(6, 3), grid=True)
    axs22.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Weighted-average \n electricity prices (€/MWh)', fontsize='large', )
    axs22.set_title('Weighted-average yearly electricity prices')
    fig22 = axs22.get_figure()
    fig22.savefig(path_to_plots + '/' + 'Electricity prices.png', bbox_inches='tight', dpi=300)
    plt.close('all')

    axs21 = share_RES.plot()
    axs21.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Share RES [%]', fontsize='medium')
    plt.grid()
    # axs21.get_legend().remove()
    # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs21.set_title('Share RES( RES generation/total demand)')
    fig21 = axs21.get_figure()
    fig21.savefig(path_to_plots + '/' + 'Share RES.png', bbox_inches='tight', dpi=300)
    plt.close('all')


def plot_price_duration_curve(electricity_prices, path_to_plots):
    sorted_prices = electricity_prices.apply(lambda x: x.sort_values(ascending=False).values)
    n = len(electricity_prices.columns)
    colors = plt.cm.rainbow(np.linspace(0, 1, n))
    fig24, axs24 = plt.subplots(nrows=2, ncols=1)
    sorted_prices.plot(color=colors, ax=axs24[0], legend=None)

    axs24[0].legend(fontsize='small', loc='upper left', ncol=2 ,bbox_to_anchor=(1.1, 1.1))
    axs24[0].set_title('Price duration curve')
    axs24[1] = sorted_prices.plot(color=colors, ax=axs24[1], legend=None)
    plt.ylim([0, 1600])
    plt.xlim([0, 1000])
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Wholesale market price (€/MWh)', fontsize='medium')
    axs24[1].yaxis.set_label_coords(-0.1, 1.02)
    fig24.savefig(path_to_plots + '/' + 'Price duration curve.png', bbox_inches='tight', dpi=300)
    plt.close('all')

    number_SR_prices = pd.Series()
    if reps.capacity_remuneration_mechanism == "strategic_reserve_ger":
        operator = reps.get_strategic_reserve_operator(reps.country)

        '''
        When calculating the SR, we dont consider the variable costs
        '''
        variable_costs = (operator.reservePriceSR  +
                          reps.substances["hydrogen"].simulatedPrice[reps.start_simulation_year]/ reps.power_generating_technologies["hydrogen OCGT"].efficiency ) # Eur/mwh
        rounded_prices = round(sorted_prices)
        SR_prices  = (rounded_prices == round(variable_costs))
        number_SR_prices = SR_prices.sum()
        # axs25 = number_SR_prices.plot(legend=None)
        # plt.xlabel('years', fontsize='medium')
        # plt.ylabel('SR activation hours', fontsize='medium')
        # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
        # fig25 = axs25.get_figure()
        # fig25.savefig(path_to_plots + '/' + 'SR_activation_hours.png', bbox_inches='tight', dpi=300)
        # plt.close('all')
        #3985
    return number_SR_prices


def plot_hourly_electricity_prices_boxplot(electricity_prices, path_to_plots):
    axs25 = sns.boxplot(data=electricity_prices)
    for label in axs25.get_xticklabels(which='major'):
        label.set(rotation=45, horizontalalignment='right')
    plt.xlabel('hours', fontsize='medium')
    plt.ylim([-5, 300])
    plt.ylabel('Wholesale market price (€/MWh)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs25.set_title('Hourly electricity prices [prices limited to 300 €/MWh]')
    fig25 = axs25.get_figure()
    fig25.savefig(path_to_plots + '/' + 'Hourly Electricity prices boxplot.png', bbox_inches='tight', dpi=300)
    plt.close('all')


def plot_cash_flows(cash_flows_with_zeroes, new_plants_loans, calculate_capacity_mechanisms, path_to_plots):
    if calculate_capacity_mechanisms == False:
        cash_flows_with_zeroes.drop(["Capacity Mechanism"], axis=1, inplace=True)
    cash_flows = cash_flows_with_zeroes[cash_flows_with_zeroes != 0]
    cash_flows.dropna(how='all', axis=1, inplace=True)
    cash_flows = cash_flows / 1000000000
    axs29 = cash_flows.plot.area(figsize=(5, 5))
    axs29.set_axisbelow(True)
    # plt.xticks(cash_flows.index, SIMULATION_YEARS)
    # plt.locator_params(nbins=4)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Cash [bn €]', fontsize='medium')
    plt.legend(fontsize='large', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    if write_titles == True:
        axs29.set_title(scenario_name + ' \nTotal Cash Flows')
    fig29 = axs29.get_figure()
    fig29.savefig(path_to_plots + '/' + 'Cash Flows.png', bbox_inches='tight', dpi=300)
    results_file = os.path.join(path_to_plots, 'cash_flows.csv')
    cash_flows.to_csv(results_file, header=True, sep=';', index=True)
    # axs30 = new_plants_loans.plot(y="Downpayments new plants", kind="area")
    axs30 = new_plants_loans.plot.bar()
    axs30.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Cash [bn €]', fontsize='medium')
    plt.grid()
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs30.set_title('Downpayments Energy Producer')
    fig30 = axs30.get_figure()
    fig30.savefig(path_to_plots + '/' + 'Cash Flows Downpayments.png', bbox_inches='tight', dpi=300)
    plt.close('all')
    #
    # axs32 = total_costs.plot()
    # axs32.set_axisbelow(True)
    # plt.xlabel('Years', fontsize='medium')
    # plt.ylabel('Cash [€]', fontsize='medium')
    # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    # axs32.set_title('Total Profits (with loans)')
    # fig32 = axs32.get_figure()
    # fig32.savefig(path_to_plots + '/' + 'Total Profits.png', bbox_inches='tight', dpi=300)


def plot_cost_recovery(cost_recovery, cumulative_cost_recovery, path_to_plots):
    cumulative_cost_recovery = cumulative_cost_recovery / 1000000000
    fig31, axs31 = plt.subplots(2, 1)
    fig31.tight_layout()
    cost_recovery.plot(ax=axs31[0], grid=True, legend=False)
    cumulative_cost_recovery.plot(ax=axs31[1], grid=True, legend=False)
    axs31[0].set_ylabel('Cost recovery [%]', fontsize='large')
    axs31[1].set_ylabel('Cummulative \n cost recovery [bn €]', fontsize='large')
    # axs33.annotate('(Revenues - Costs) Include Capacity Mechanisms',
    #                xy=(1, 1.1), xycoords='figure fraction',
    #                horizontalalignment='right', verticalalignment='bottom',
    #                fontsize='small')
    fig31.savefig(path_to_plots + '/' + 'Cost recovery.png', bbox_inches='tight', dpi=300)
    results_file = os.path.join(path_to_plots, 'cost_recovery.csv')
    cost_recovery.to_csv(results_file, header=True, sep=';', index=True)
    plt.close()


def plot_financial_results_new_plants(overall_NPV_per_technology, overall_IRR_per_technology, path_to_plots):
    fig31, axs31 = plt.subplots(1, 2)
    fig31.tight_layout()
    colors = [technology_colors[tech] for tech in overall_NPV_per_technology.columns.values]
    overall_NPV_per_technology = overall_NPV_per_technology / 1000000
    overall_IRR_per_technology = overall_IRR_per_technology * 100
    overall_NPV_per_technology.plot.bar(ax=axs31[0], grid=True, legend=False, figsize=(4, 4), color=colors)
    overall_IRR_per_technology.plot.bar(ax=axs31[1], grid=True, legend=False, figsize=(4, 4), color=colors)
    # plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs31[0].set_title('NPV r = 7%')
    axs31[1].set_title('IRR %')
    axs31[0].set_xlabel('mill. €')
    axs31[1].set_xlabel('%')
    fig31.tight_layout()

    # fig31.set_figwidth(4)
    # fig31.set_figheight(4)
    # fig31.set_size_inches(2, 4)
    fig31.savefig(path_to_plots + '/' + 'NPV and IRRs new plants.png', bbox_inches='tight', dpi=300)


def plot_strategic_reserve_plants(npvs_per_year_perMW_strategic_reseve, npvs_per_tech_per_MW, path_to_plots):
    fig30, axs30 = plt.subplots()
    # colors = [technology_colors[tech] for tech in npvs_per_tech_per_MW.columns.values]
    # key gives the group name (i.e. category), data gives the actual values
    if npvs_per_year_perMW_strategic_reseve.empty == False:
        npvs_per_year_perMW_strategic_reseve.plot(ax=axs30)
    # npvs_per_tech_per_MW.hydrogen_turbine.plot(ax=axs30)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('€', fontsize='medium')
    plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(1, 1.1), ncol=5)
    if write_titles == True:
        axs30.set_title(scenario_name + ' \n yearly NPV strategic reserve plants')

    axs30.annotate('legend = name, capacity, age',
                   xy=(0, 1), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='bottom',
                   fontsize='small')
    fig30.savefig(path_to_plots + '/' + 'NPV_Strategic reserve.png', bbox_inches='tight', dpi=300)


def plot_npv_new_plants(npvs_per_year_new_plants_perMWall, npv_long_term_market_plants_all, irrs_per_year_new_plants_all,
                        candidate_plants_project_value_per_MW,
                        test_year,
                        future_year, path_to_plots):
    fig30, axs30 = plt.subplots()
    # key gives the group name (i.e. category), data gives the actual values
    for key, data in irrs_per_year_new_plants_all.items():
        if data.size > 0:
            data.plot(ax=axs30, label=key, color=technology_colors[key])
        if key == test_tech:
            test_irrs = data
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('%', fontsize='medium')
    plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(1, 1.1), ncol=5)
    if write_titles == True:
        axs30.set_title(scenario_name + ' \n yearly IRR new plants')
    axs30.annotate('legend = name, capacity, age',
                   xy=(0, 1), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='bottom',
                   fontsize='small')
    fig30.savefig(path_to_plots + '/' + 'IRR new plants.png', bbox_inches='tight', dpi=300)


    fig1, axs1 = plt.subplots()
    for key, data in npv_long_term_market_plants_all.items():
        if data.size > 0:
            data.plot(ax=axs1, label=key, color=technology_colors[key])
    plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(1, 1.1), ncol=5)
    axs1.set_title('NPV per MW for LTCM plants \n  (discount rate = 0)')
    fig1.savefig(path_to_plots + '/' + 'NPV per MW for plants in LTCM.png', bbox_inches='tight', dpi=300)


    fig31, axs31 = plt.subplots()
    for key, data in npvs_per_year_new_plants_perMWall.items():
        if data.size > 0:
            data.plot(ax=axs31, label=key, color=technology_colors[key])
        if key == test_tech:
            test_npvs = data

    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('mill. €', fontsize='medium')
    plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(1, 1.1), ncol=5)
    axs31.set_title('NPV per MW for new plants \n  (discount rate = 0)')
    fig31.savefig(path_to_plots + '/' + 'NPV per MW for new plants.png', bbox_inches='tight', dpi=300)

    if test_tech is not None:
        axs29 = test_irrs.plot()
        plt.xlabel('Years', fontsize='medium')
        plt.ylabel('%', fontsize='medium')
        plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1), ncol=5)
        axs29.set_title('IRR new plants for tech ' + test_tech)
        axs29.annotate('legend = name, capacity, age',
                       xy=(0, 1), xycoords='figure fraction',
                       horizontalalignment='right', verticalalignment='top',
                       fontsize='small')
        fig29 = axs29.get_figure()
        fig29.savefig(path_to_plots + '/' + 'IRR new plants of tech ' + test_tech + ' .png', bbox_inches='tight',
                      dpi=300)

        NPVNewPlants = test_npvs.mean(axis=1)
        NPVNewPlants = NPVNewPlants / 1000000
        axs32 = NPVNewPlants.plot()
        plt.xlabel('Years', fontsize='medium')
        plt.ylabel('mill. €', fontsize='medium')
        plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1), ncol=5)
        axs32.set_title('NPV new plants \n of tech ' + test_tech)
        axs32.annotate('legend = name, capacity, age',
                       xy=(0, 1), xycoords='figure fraction',
                       horizontalalignment='left', verticalalignment='bottom',
                       fontsize='small')
        fig32 = axs32.get_figure()
        fig32.savefig(path_to_plots + '/' + 'NPV new plants of tech ' + test_tech + ' .png', bbox_inches='tight',
                      dpi=300)

        pp_installed_in_test_year = []
        if reps.install_at_look_ahead_year == True:
            installed_year = test_year + reps.lookAhead
            installed_tick = test_tick + reps.lookAhead
        else:
            installed_year = test_year + reps.power_generating_technologies[test_tech].expected_leadtime + \
                             reps.power_generating_technologies[test_tech].expected_permittime
            installed_tick = test_tick + reps.power_generating_technologies[test_tech].expected_leadtime + \
                             reps.power_generating_technologies[test_tech].expected_permittime
        for i in test_npvs.columns:
            pp = i.split()
            pp_name = pp[0]
            if reps.power_plants[pp_name].commissionedYear == installed_year:
                pp_installed_in_test_year.append(i)

        fig33, axs33 = plt.subplots()
        candidate_PV_perMW = candidate_plants_project_value_per_MW[test_tech]
        candidate_PV_perMW.plot(ax=axs33, style='.', label="Expected to be installed in " + str(future_year))
        # Attention ONLY WHEN THERE IS NO DISMANTLING, there are no extra fixed costs along the years
        # AND ONLY ONE PLANT IS INSTALLED PER YEAR, COULD THE EXPECTED AND THE REAL npv BE THE SAME
        if installed_tick <= reps.current_tick:
            npvs_testTech = test_npvs[pp_installed_in_test_year].iloc[installed_tick]
            npvs_testTech.reset_index(inplace=True, drop=True)
            npvs_testTech.plot(ax=axs33, style='.', label="Installed in " + str(installed_year))
            plt.ylabel('[€]/MW', fontsize='medium')
            plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
            for label in axs33.get_xticklabels(which='major'):
                label.set(rotation=30, horizontalalignment='right')

            axs33.annotate('ticks = name, capacity, age',
                           xy=(1, 0), xycoords='figure fraction',
                           horizontalalignment='center', verticalalignment='top',
                           fontsize='medium')
            axs33.set_title('NPV per MW \n for new plants of tech \n' + test_tech)
            fig33.savefig(path_to_plots + '/' + 'NPV expected vs reality ' + test_tech + '-' + str(test_year) + ' .png',
                          bbox_inches='tight', dpi=300)
        else:
            print("future NPV not evaluated yet for year " + str(installed_tick))
    else:
        NPVNewPlants = None
    plt.close('all')
    return NPVNewPlants


def plot_initial_power_plants(path_to_plots, sheetname):
    sns.set_theme(style="whitegrid")
    print("plotted initial power plants")
    sns.set(font_scale=1.2)
    df = pd.read_excel(globalNames.power_plants_path,
                       sheet_name=sheetname)
    colors = [technology_colors[tech] for tech in df["Technology"].unique()]
    fig1 = sns.relplot(x="Age", y="Efficiency", hue="Technology", size="Capacity",
                       sizes=(40, 400), alpha=.5, palette=colors,
                       height=6, data=df)

    plt.xlabel("Age", fontsize="large")
    plt.ylabel("Efficiency", fontsize="large")
    fig1.savefig(path_to_plots + '/' + 'Initial_power_plants_efficiency.png', bbox_inches='tight', dpi=300)
    plt.close('all')


def plot_grouped_monthly_production_per_type(average_yearly_generation):
    new_columns = {
        'conventionals': 'H2 turbine + Nuclear + Biofuel',
        'electrolysis_power_consumption': 'Industrial heat production'
    }
    average_yearly_generation = average_yearly_generation.rename(columns=new_columns)
    average_yearly_generation['monthly'] = (average_yearly_generation.index // 730)
    grouped = average_yearly_generation.groupby(['monthly']).sum()
    grouped = grouped / 1000000
    ax1 = grouped.plot()
    ax1.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.xlabel('Months', fontsize='medium')
    plt.ylabel('TWh', fontsize='medium')
    ax1.set_title("Monthly average production")
    fig1 = ax1.get_figure()
    fig1.savefig(path_to_plots + '/' + 'monthly_production.png', bbox_inches='tight', dpi=300)


def plot_load_shedded(path_to_plots, production_not_shedded_MWh, load_shedded_per_group_MWh,
                      normalized_load_shedded):
    fig37, axs37 = plt.subplots(2, 1)
    fig37.tight_layout()
    production_not_shedded_TWh = production_not_shedded_MWh[["hydrogen_produced", "industrial_heat_demand"]] / 1000000
    production_not_shedded_TWh.plot(ax=axs37[0], legend=False, grid=True)
    axs37[0].set_xlabel('Years', fontsize='medium')
    production_not_shedded_MWh[["hydrogen_percentage_produced", "industrial_percentage_produced"]].plot(ax=axs37[1],
                                                                                                        grid=True,
                                                                                                        legend=False)
    axs37[0].set_ylabel('TWh', fontsize='medium')
    axs37[0].set_xlabel('Years', fontsize='medium')
    axs37[1].set_ylabel('%', fontsize='medium')
    axs37[0].legend(loc='lower center')
    axs37[0].legend(['Electrolyzer', 'Industrial heat'])
    fig37.savefig(path_to_plots + '/' + 'Hydrogen_produced.png', bbox_inches='tight', dpi=300)
    plt.close('all')

    # reorganize columns as specified
    # percentage_load_shedded = percentage_load_shedded[['low', 'mid', 'high', 'base']]
    # load_shedded_per_group_MWh = load_shedded_per_group_MWh[['low', 'mid', 'high', 'base']]
    # dropping hydrogen because it is too
    #load_shedded_per_group_MWh.drop('hydrogen', axis=1, inplace=True)

    melted_dfs = []
    if reps.capacity_remuneration_mechanism == "capacity_subscription":
        for year, df in hourly_load_shedders_per_year.items():
            df.drop(columns=[8888888], inplace=True)
            df_positive = df[df > 0]
            df_filtered = df_positive.dropna(how="all")
            melted_df =  df_filtered.melt(var_name='Type', value_name='Value')
            melted_df['year'] = year
            melted_dfs.append(melted_df)

            # Concatenate all melted DataFrames into one
        result_df = pd.concat(melted_dfs, ignore_index=True)
        load_mapping = {
            100000: 'ENS',
            200000: 'DSR',
        }
        df_replaced = result_df.replace(load_mapping)

        if  df_replaced.empty == False:
            # unsubscribed_volume = reps.get_unsubscribed_volume()
            fig, ax = plt.subplots(figsize=(10, 6))
            catplot = sns.catplot( data=df_replaced, x="year", y="Value",  kind="box", hue="Type", ax= ax)
            ax = catplot.facet_axis(0, 0)
            # unsubscribed_volume.reset_index(drop=True, inplace=True)
            # unsubscribed_volume[:-1].plot(ax= ax, color = "red", linestyle='--', linewidth=3, label = "Unsubscribed volume")
            plt.ylabel('ENS [MW]', fontsize='large')
            plt.xticks(rotation=20, size = 15, ha="right")
            fig = ax.get_figure()
            fig.savefig(path_to_plots + '/' + 'ENS.png', bbox_inches='tight', dpi=300)

    fig38, axs38 = plt.subplots(2, 1)
    fig38.tight_layout()
    load_shedded_per_group_MWh.plot(ax=axs38[0], cmap = "viridis",  legend=False)
    axs38[0].set_title('ENS', fontsize='medium')
    normalized_load_shedded.plot(ax=axs38[1], cmap = "viridis", legend=True)
    axs38[1].set_title('normalized ENS (excluding industrial heating load)', fontsize='medium')
    axs38[0].set_ylabel('[MWh]', fontsize='medium')
    axs38[1].set_xlabel('Years', fontsize='medium')
    axs38[1].set_ylabel('normalized ENS [%]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    fig38.savefig(path_to_plots + '/' + 'Load_shedded.png', bbox_inches='tight', dpi=300)

    plt.close('all')
def plot_non_subscription_costs(CM_clearing_price, cost_non_subcription, load_per_group):
    CM_subsription_cost = CM_clearing_price.values*load_per_group
    cost_non_subcription.plot()
    fig38, axs38 = plt.subplots(3, 1)
    fig38.tight_layout()
    CM_subsription_cost.plot(ax=axs38[0], cmap = "viridis",  legend=True)
    axs38[0].set_title('Subscription costs', fontsize='medium')
    cost_non_subcription.plot(ax=axs38[1], cmap = "viridis", legend=False)
    CM_subsription_cost.sum(axis=1).plot(ax=axs38[2], color = "black", label="subscription costs", legend=True)
    cost_non_subcription.sum(axis=1).plot(ax=axs38[2], color = "red", label="non subscription costs", legend=True)
    axs38[1].set_title('Non subscription costs', fontsize='medium')
    axs38[0].set_ylabel('[Eur]', fontsize='medium')
    axs38[2].set_xlabel('Years', fontsize='medium')
    axs38[1].set_ylabel('[Eur]', fontsize='medium')
    axs38[2].set_ylabel('[Eur]', fontsize='medium')
    fig38.savefig(path_to_plots + '/' + 'Costsnonsubscription.png', bbox_inches='tight', dpi=300)
    plt.close('all')
def plot_lole_per_group(path_to_plots, max_ENS_in_a_row, LOLE_per_group, VOLL_per_year, total_SR_hours):
    # load_mapping = {
    #     '1': 'subscribed',
    #     '2': 'unsubscribed',
    #     '3': 'DSR',
    # }
    # LOLE_per_group.rename(index=load_mapping, inplace=True)
    # VOLL_per_year.rename(index=load_mapping, inplace=True)
    # max_ENS_in_a_row.rename(index=load_mapping, inplace=True)
    LOLE_per_group.drop(inplace=True, index='hydrogen')
    max_ENS_in_a_row.drop(inplace=True, index='hydrogen')
    fig39, axs39 = plt.subplots(3, 1)
    fig39.tight_layout()
    VOLL_per_year.T.plot(ax=axs39[0], legend=False,  cmap='viridis' )
    LOLE_per_group.T.plot(ax=axs39[1], legend=False,  cmap='viridis')
    if total_SR_hours.size >0:
        total_SR_hours.plot(ax=axs39[1],  color="g")
    max_ENS_in_a_row.T.plot(ax=axs39[2], legend=False,  cmap='viridis')
    axs39[0].set_ylabel('Load percentage', fontsize='medium')
    axs39[1].set_ylabel('hours', fontsize='medium')
    axs39[2].set_ylabel('Max continous \n hours in a row', fontsize='medium')
    axs39[2].set_xlabel('year', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    fig39.savefig(path_to_plots + '/' + 'Load_shedded_hours.png', bbox_inches='tight', dpi=300)
    plt.close('all')

# section -----------------------------------------------------------------------------------------------data preparation
def prepare_pp_decommissioned(reps):
    years_to_generate_and_build = list(
        range(reps.start_simulation_year - reps.lookAhead, reps.current_year + 1 + reps.max_permit_build_time))
    plants_decommissioned_per_year = pd.DataFrame(columns=["PPname", "decommissionInYear", "technology", "Capacity"])
    plants_expected_decommissioned = pd.DataFrame(
        columns=["PPname", "decommissionInYear", "technology", "Capacity"])
    for pp in reps.get_power_plants_by_status([globalNames.power_plant_status_decommissioned]):
        plants_decommissioned_per_year.loc[len(plants_decommissioned_per_year)] = [pp.name, pp.decommissionInYear,
                                                                                   pp.technology.name, pp.capacity]
    plants_decommissioned_per_year["color"] = plants_decommissioned_per_year['technology'].apply(
        lambda x: technology_colors[x])

    for expected_decomm_year, power_plants in reps.decommissioned["Expectation"].Expectation.items():
        for pp_name in power_plants:
            pp = reps.get_power_plant_by_name(pp_name)
            plants_expected_decommissioned.loc[len(plants_expected_decommissioned)] = [pp.name,
                                                                                       expected_decomm_year,
                                                                                       pp.technology.name,
                                                                                       pp.capacity]
    plants_expected_decommissioned_per_year = plants_expected_decommissioned[
        plants_expected_decommissioned.groupby('PPname')['decommissionInYear'].transform(
            'idxmin') == plants_expected_decommissioned.index]

    colors = [technology_colors[tech] for tech in plants_expected_decommissioned_per_year["technology"].unique()]
    fig2 = sns.relplot(x="decommissionInYear", y="Capacity", hue="technology",
                       sizes=(40, 400), alpha=.5, palette=colors,
                       height=6, data=plants_expected_decommissioned_per_year)

    for row in plants_decommissioned_per_year.iterrows():
        if len(row[1].PPname) > 4:
            name = row[1].PPname[:3]
        else:
            name = row[1].PPname
        plt.text(x=row[1].decommissionInYear + 0.1, y=row[1].Capacity + 0.4, s=str(name),
                 color=row[1].color,
                 weight='semibold')
    plt.xlabel("decommissionYear", fontsize="large")
    plt.ylabel("Capacity", fontsize="large")
    fig2.savefig(path_to_plots + '/' + 'DecommissionedvsExpected.png', bbox_inches='tight', dpi=300)

    plants_expected_decommissioned_per_year.set_index('decommissionInYear', inplace=True)
    groupeddf1 = plants_expected_decommissioned_per_year.groupby(['decommissionInYear', 'technology'])[
        'Capacity'].sum()
    df1 = groupeddf1.unstack()

    plants_decommissioned_per_year.set_index('decommissionInYear', inplace=True)
    groupeddf2 = plants_decommissioned_per_year.groupby(['decommissionInYear', 'technology'])[
        'Capacity'].sum()

    # df2 = groupeddf2.unstack()
    # df1['category'] = 'expected'
    # df2['category'] = 'decommissioned'
    # combined_df = pd.concat([df1, df2])
    # melted = pd.melt(combined_df, id_vars=['category'], ignore_index=False)
    # melted.index.name = 'year'
    # melted = melted.reset_index()
    # fig = sns.catplot(data=melted, x="year", y="value", hue="category", col="technology", kind="bar", height=4,
    #                   aspect=1.2)
    # [plt.setp(ax.get_xticklabels(), rotation=90) for ax in fig.axes.flat]
    # # fig.set_xticklabels(fig.get_xticklabels(), rotation=90, horizontalalignment='right')
    # fig.savefig(path_to_plots + '/' + 'DecommissionedvsExpected2.png', bbox_inches='tight', dpi=300)


def prepare_pp_lifetime_extension(reps):
    extended_lifetime = pd.DataFrame(columns=["Extension", "Technology", "Capacity", "Age"])
    row = 0
    for pp_name, pp in reps.power_plants.items():
        # some power plants have age higher than tick becuase they were installed during initialization
        if pp.status in [globalNames.power_plant_status_to_be_decommissioned,
                         globalNames.power_plant_status_strategic_reserve,
                         globalNames.power_plant_status_decommissioned
                         ]:
            row = row + 1
            pp.decommissionInYear
            extended_lifetime.at[row, "Extension"] = pp.age - pp.technology.expected_lifetime
            extended_lifetime.at[row, "Technology"] = pp.technology.name
            extended_lifetime.at[row, "Capacity"] = pp.capacity
            extended_lifetime.at[row, "Age"] = pp.age
            extended_lifetime.at[row, "Status"] = pp.status
            extended_lifetime.at[row, "Name"] = pp.name
    extended_lifetime_tech = extended_lifetime.groupby(by=["Technology"]).mean()
    sns.set_theme(style="whitegrid")
    sns.set(font_scale=1.2)
    colors = [technology_colors[tech] for tech in extended_lifetime["Technology"].unique()]
    fig1 = sns.relplot(x="Age", y="Extension", hue="Technology", size="Capacity",
                       sizes=(40, 400), alpha=.5, palette=colors,
                       height=6, data=extended_lifetime)
    for row in extended_lifetime.iterrows():
        plt.text(x=row[1].Age + 0.1, y=row[1].Extension + 0.1, s=row[1].Name,
                 weight='semibold')

    plt.xlabel("Age", fontsize="large")
    plt.ylabel("Extension", fontsize="large")
    if write_titles == True:
        plt.title(scenario_name + ' lifetime extension \n ')
    fig1.savefig(path_to_plots + '/' + 'Initial_power_plants.png', bbox_inches='tight', dpi=300)
    plt.close('all')

    return extended_lifetime_tech


def prepare_pp_status(years_to_generate,unique_technologies,  reps):
    if reps.decommission_from_input == True:  # the initial power plants have negative age to avoid all to be commmissioned in one year
        if reps.current_year + 1 + reps.lookAhead > 2050:
            until = reps.current_year + 1 + reps.lookAhead
        else:
            until = 2050
        years_to_generate_and_build = list(range(reps.start_simulation_year - reps.lookAhead, until))
    else:
        years_to_generate_and_build = list(
            range(reps.start_simulation_year - reps.lookAhead, reps.current_year + 1 + reps.lookAhead))

    annual_decommissioned_capacity = pd.DataFrame(columns=unique_technologies,
                                                  index=years_to_generate_and_build).fillna(0)
    annual_in_pipeline_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate_and_build).fillna(0)
    annual_commissioned_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate_and_build).fillna(
        0)
    initial_power_plants = pd.DataFrame(columns=unique_technologies, index=years_to_generate_and_build).fillna(0)
    last_year = years_to_generate[-1]
    last_year_operational_capacity = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_to_be_decommissioned_capacity = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_strategic_reserve_capacity = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_not_set_status_capacity = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_in_pipeline = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_decommissioned = pd.DataFrame(columns=unique_technologies, index=[last_year]).fillna(0)
    last_year_power_plant_status_decommissioned_from_SR = pd.DataFrame(columns=unique_technologies,
                                                                       index=[last_year]).fillna(0)

    for pp_name, pp in reps.power_plants.items():
        # some power plants have age higher than tick becuase they were installed during initialization

        if reps.install_at_look_ahead_year == True:
            year_investment_decision = pp.commissionedYear - reps.lookAhead
        else:
            year_investment_decision = pp.commissionedYear - pp.technology.expected_leadtime - pp.technology.expected_permittime

        if pp.commissionedYear >= years_to_generate_and_build[0] or pp.is_new_installed():
            # graphed according to commissioned year which is determined by age.
            if year_investment_decision < years_to_generate_and_build[0]:
                pass
            else:
                annual_in_pipeline_capacity.at[year_investment_decision, pp.technology.name] += pp.capacity
            #  the year when the investment entered in operation
            annual_commissioned_capacity.at[pp.commissionedYear, pp.technology.name] += pp.capacity

        # if the age at the start was larger than zero then they count as being installed.
        elif pp.commissionedYear < years_to_generate_and_build[0]:
            initial_power_plants.loc[:, pp.technology.name] += pp.capacity

        if pp.status == globalNames.power_plant_status_decommissioned:
            annual_decommissioned_capacity.at[pp.decommissionInYear, pp.technology.name] += pp.capacity
            # if pp.age + pp.decommissionInYear - reps.start_simulation_year > (reps.current_tick):
            #     initial_power_plants.loc[:, pp.technology.name] += pp.capacity

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
        elif pp.status == globalNames.power_plant_status_decommissioned_from_SR:
            last_year_power_plant_status_decommissioned_from_SR.at[last_year, pp.technology.name] += pp.capacity
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

    decommissioned = np.cumsum(annual_decommissioned_capacity.values, axis=0)
    commissioned = np.cumsum(annual_commissioned_capacity.values, axis=0)
    all_techs_capacity = np.subtract(commissioned, decommissioned)
    all_techs_capacity = initial_power_plants.add(all_techs_capacity, axis=0)

    return annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_commissioned_capacity, \
        all_techs_capacity, last_year_in_pipeline, last_year_decommissioned, \
        last_year_operational_capacity, last_year_to_be_decommissioned_capacity, \
        last_year_strategic_reserve_capacity, number_per_status, number_per_status_last_year



def prepare_capacity_per_iteration(future_year, future_tick, reps, unique_candidate_power_plants):
    # preparing empty df
    pps_invested_in_tick = reps.get_power_plants_invested_in_future_tick(future_tick)
    max_iteration = len(pps_invested_in_tick)
    # for the years in which there are no other investments than this.
    if reps.targetinvestment_per_year == True:
        max_iteration += 1

    #  df_zeros = np.zeros(shape=(max_iteration, len(unique_candidate_power_plants)))
    candidate_plants_project_value_perMW = pd.DataFrame()

    # preparing NPV per MW per iteration
    for name, investment in reps.candidatesNPV.items():
        if len(investment.project_value_year) > 0:
            if str(future_year) in investment.project_value_year.keys():
                a = pd.Series(dict(investment.project_value_year[str(future_year)]))
                # candidate_plants_project_value_perMW[reps.candidatePowerPlants[name].technology.name] = a
                candidate_plants_project_value_perMW = pd.concat(
                    [candidate_plants_project_value_perMW, a.rename(reps.candidatePowerPlants[name].technology.name)],
                    axis=1)
                # candidate_plants_project_value_perMW.insert(loc=len(candidate_plants_project_value_perMW.columns), column=reps.candidatePowerPlants[name].technology.name, value=a)
    installed_capacity_per_iteration = pd.DataFrame(
        columns=unique_candidate_power_plants).fillna(0)
    for pp in pps_invested_in_tick:
        installed_capacity_per_iteration.at[int(str(pp.id)[-4:]), pp.technology.name] = pp.capacity

    installed_capacity_per_iteration.sort_index(ascending=True, inplace=True)
    installed_capacity_per_iteration.reset_index(drop=True, inplace=True)
    installed_capacity_per_iteration.replace(to_replace=0, value=np.nan, inplace=True)
    candidate_plants_project_value_perMW.sort_index(ascending=True, inplace=True)
    return installed_capacity_per_iteration, candidate_plants_project_value_perMW


def prepare_profits_candidates_per_iteration(reps):
    # profits from candidate power plants are from excel sheets operationalProfit = CONTRIBUTION_MARGIN_IN_EURO
    profits = reps.get_profits_per_tick(test_tick)
    #  profits_per_iteration = pd.DataFrame(index=profits.profits_per_iteration_names_candidates[test_tick]).fillna(0)
    # ser = pd.Series(data2, index=list(profits.profits_per_iteration_candidates.items()))
    profits_per_iteration = pd.DataFrame()
    for iteration, profit_per_iteration in list(profits.profits_per_iteration_candidates.items()):
        temporal = pd.Series(profit_per_iteration, index=profits.profits_per_iteration_names_candidates[iteration])
        profits_per_iteration[iteration] = temporal

    tech = []
    capacity_to_be_installed = []
    for pp in profits_per_iteration.index.values:
        tech.append(
            reps.candidatePowerPlants[pp].technology.name + "_tested_" + str(
                reps.candidatePowerPlants[pp].capacity) + "MW")
        capacity_to_be_installed.append(reps.candidatePowerPlants[pp].capacityTobeInstalled)

    profits_per_iteration = profits_per_iteration.mul(capacity_to_be_installed, axis=0)
    profits_per_iteration["tech"] = tech
    profits_per_iteration = np.transpose(profits_per_iteration)
    profits_per_iteration.columns = profits_per_iteration.iloc[-1]
    profits_per_iteration.drop("tech", inplace=True)
    profits_per_iteration.index.map(int)
    profits_per_iteration.sort_index(ascending=True, inplace=True)
    return profits_per_iteration


def prepare_revenues_per_iteration(reps, future_tick, last_year, future_year):
    # expected future operational profits
    profits = reps.get_profits_per_tick(test_tick)
    future_operational_profit_per_iteration = pd.DataFrame()
    future_operational_profit_per_iteration_with_age = pd.DataFrame()
    for iteration, profit_per_iteration in list(profits.profits_per_iteration.items()):
        temporal = pd.Series(profit_per_iteration, index=profits.profits_per_iteration_names[iteration])
        future_operational_profit_per_iteration[int(iteration)] = temporal
        future_operational_profit_per_iteration_with_age[int(iteration)] = temporal
    # adding technology name
    tech = []
    capacity_efficiency_commissionyear = []

    for pp in future_operational_profit_per_iteration.index.values:
        capacity_efficiency_commissionyear.append(
            str(reps.power_plants[pp].capacity) + "MW " + str(reps.power_plants[pp].actualEfficiency)
            + "% " + str(reps.power_plants[pp].commissionedYear))
        tech.append(reps.power_plants[pp].technology.name)
    future_operational_profit_per_iteration["tech"] = tech
    grouped_revenues = future_operational_profit_per_iteration.groupby('tech').mean()
    sorted_average_revenues_per_tech_test_tick = grouped_revenues.T.sort_index()

    future_operational_profit_per_iteration_with_age["tech"] = tech
    future_operational_profit_per_iteration_with_age["tech-commissionedYear"] = capacity_efficiency_commissionyear
    expected_future_operational_profit = future_operational_profit_per_iteration_with_age.loc[
        future_operational_profit_per_iteration_with_age.tech == test_tech]
    expected_future_operational_profit.drop(["tech"], axis=1, inplace=True)
    all_future_operational_profit = expected_future_operational_profit.set_index('tech-commissionedYear').T.sort_index(
        level=0)

    # real obtained operational profits
    if last_year >= future_year:
        # get power plants ids invested in tick from investment decisions
        plants_commissioned_in_future_year = reps.get_power_plants_invested_in_future_tick(future_tick)
        profits_plants_commissioned = pd.DataFrame()
        for pp in plants_commissioned_in_future_year:
            # get operational profits
            profits_plants_commissioned[reps.power_plants[pp].technology.name] = reps.get_operational_profits_pp(pp)
        if profits_plants_commissioned.shape != (0, 0):
            operational_profits_commissioned = profits_plants_commissioned.loc[future_tick]
            operational_profits_commissioned.reset_index(drop=True)
        else:
            operational_profits_commissioned = False
    else:
        operational_profits_commissioned = False

    return sorted_average_revenues_per_tech_test_tick, all_future_operational_profit, operational_profits_commissioned


def prepare_retrospectively_npv_and_irr(reps, unique_technologies):
    overall_NPV_per_technology = pd.DataFrame(columns=unique_technologies)
    overall_IRR_per_technology = pd.DataFrame(columns=unique_technologies)
    for technology_name in unique_technologies:
        powerplants_per_tech = reps.get_power_plants_by_technology(technology_name)
        npvs = []
        irrs = []
        for pp in powerplants_per_tech:
            if pp.is_new_installed() and pp.status == globalNames.power_plant_status_decommissioned:
                CashFlow_no_downpayments = reps.financialPowerPlantReports[pp.name].totalProfitswLoans
                CashFlow_no_downpayments.sort_index(inplace=True)
                nr_downpayments = reps.power_plants[pp.name].downpayment.getTotalNumberOfPayments()
                downpayment = reps.power_plants[pp.name].downpayment.getAmountPerPayment()
                list_downpayments = [- downpayment for item in range(0, int(nr_downpayments))]
                investmentCashFlow = pd.concat([pd.Series(list_downpayments), CashFlow_no_downpayments],
                                               ignore_index=True)
                npv = npf.npv(reps.energy_producers[reps.agent].equityInterestRate, investmentCashFlow)
                irr = npf.irr(investmentCashFlow)
                npvs.append(npv)
                irrs.append(irr)
        if len(powerplants_per_tech) > 0:
            overall_NPV_per_technology.at[0, technology_name] = np.average(npvs)
            overall_IRR_per_technology.at[0, technology_name] = np.average(irrs)
    return overall_NPV_per_technology, overall_IRR_per_technology


def prepare_operational_profit_per_year_per_tech(reps, simulation_years):
    # CM revenues + revenues - variable costs - fixed costs
    average_profits_per_tech_per_year_perMW = pd.DataFrame(index=simulation_years).fillna(0)
    # making df per technology
    for technology_name in unique_technologies:
        powerplants_per_tech = reps.get_power_plants_by_technology(technology_name)
        profits_per_year = pd.DataFrame(index=simulation_years).fillna(0)
        # for the plants of that technology
        for plant in powerplants_per_tech:
            profits_per_plant = reps.get_total_profits_for_plant(plant.name)
            if profits_per_plant is None:
                print("power plant in pipeline", plant.name, plant.id)
            else:
                profits_per_year[plant.name] = profits_per_plant / plant.capacity

        if profits_per_year.size != 0:
            average_profits_per_tech_per_year_perMW[technology_name] = np.nanmean(profits_per_year, axis=1)
        if technology_name == test_tech:
            info = []
            chosen = []
            for pp in profits_per_year.columns:
                age = reps.power_plants[pp].age
                capacity = reps.power_plants[pp].capacity
                actualFixedOperatingCost = reps.power_plants[pp].getActualFixedOperatingCost()
                info.append(
                    str(age) + ' ' + str(capacity) + ' ' + str(pp) + ' ' + str(int(actualFixedOperatingCost / 1000000)))
                if capacity == reps.get_candidate_capacity(test_tech):
                    chosen.append(str(age) + ' ' + str(capacity) + ' ' + str(pp) + ' ' + str(
                        int(actualFixedOperatingCost / 1000000)))
                # chosen.append(str(age) + ' ' + str(capacity) + ' ' + str(pp)  + ' ' + str(int(actualFixedOperatingCost/1000000)))
            profits_for_test_tech_per_year = pd.DataFrame(profits_per_year, columns=info, index=simulation_years)
            if len(chosen) == 0 and test_tech != None:
                raise Exception(
                    "choose other test technology. There could be technologies invested in this year, but plants are still in pipeline")
            new_pp_profits_for_tech = profits_for_test_tech_per_year[chosen]

    if test_tech == None:
        new_pp_profits_for_tech = 0
    return average_profits_per_tech_per_year_perMW, new_pp_profits_for_tech


def prepare_cash_per_agent(reps, simulation_ticks):
    # the cash includes the loans of installed power plants
    costs_to_society =pd.DataFrame()
    cash_per_agent = pd.DataFrame(index=simulation_ticks).fillna(0)
    new_plants_loans = pd.DataFrame(index=simulation_ticks).fillna(0)
    all_info = reps.getCashFlowsForEnergyProducer(reps.agent)
    cash_per_agent["Wholesale market"] = all_info.CF_ELECTRICITY_SPOT
    cash_per_agent["Variable costs"] = all_info.CF_COMMODITY
    cash_per_agent["Fixed costs"] = all_info.CF_FIXEDOMCOST
    cash_per_agent["Capacity Mechanism"] = all_info.CF_CAPMARKETPAYMENT
    cash_per_agent["Loans"] = all_info.CF_LOAN
    cash_per_agent["Loans new plants"] = all_info.CF_LOAN_NEW_PLANTS
    cash_per_agent["Downpayments"] = all_info.CF_DOWNPAYMENT
    cash_per_agent["Downpayments new plants"] = all_info.CF_DOWNPAYMENT_NEW_PLANTS

    if not isinstance(all_info.RETURN_CONSUMERS, int):
        if all_info.RETURN_CONSUMERS.any() < - 10:
            print(all_info.RETURN_CONSUMER[all_info.RETURN_CONSUMER<0])
            raise Exception("consumers payback is too low")
    cash_per_agent["Clawback"] = abs(all_info.RETURN_CONSUMERS)

    new_plants_loans["Downpayments new plants"] = all_info.CF_DOWNPAYMENT_NEW_PLANTS
    new_plants_loans["Loans new plants"] = all_info.CF_LOAN_NEW_PLANTS
    cost_recovery_in_eur = cash_per_agent.sum(axis=1)

    cost_recovery = (all_info.CF_ELECTRICITY_SPOT + all_info.CF_CAPMARKETPAYMENT - all_info.RETURN_CONSUMERS).divide(
        -(all_info.CF_COMMODITY + all_info.CF_LOAN + all_info.CF_FIXEDOMCOST + all_info.CF_DOWNPAYMENT +
          + all_info.CF_DOWNPAYMENT_NEW_PLANTS + all_info.CF_LOAN_NEW_PLANTS)
    )
    # new_index = cost_recovery_in_eur.index.values + reps.start_simulation_year
    cash_per_agent["years"] = cash_per_agent.index.values + reps.start_simulation_year
    cash_per_agent.set_index('years', inplace=True)
    cost_recovery.index = cost_recovery.index + reps.start_simulation_year
    cost_recovery_in_eur.index = cost_recovery_in_eur.index + reps.start_simulation_year
    cost_recovery.sort_index(inplace=True)
    cumulative_cost_recovery = cost_recovery_in_eur.cumsum()
    costs_to_society["OPEX + CAPEX"] =  - all_info.CF_COMMODITY - \
    all_info.CF_LOAN - all_info.CF_FIXEDOMCOST - all_info.CF_DOWNPAYMENT - \
    all_info.CF_DOWNPAYMENT_NEW_PLANTS - all_info.CF_LOAN_NEW_PLANTS
    return cash_per_agent, cost_recovery * 100, cumulative_cost_recovery, new_plants_loans, costs_to_society


def prepare_irr_and_npv_per_technology_per_year(reps, ticks_to_generate, years_to_generate):
    irrs_per_tech_per_year = pd.DataFrame(index=ticks_to_generate).fillna(0)
    npvs_per_tech_per_MW = pd.DataFrame(index=ticks_to_generate).fillna(0)
    profits_with_loans_all = pd.DataFrame(index=ticks_to_generate).fillna(0)
    npvs_per_year_new_plants_perMW_all = dict()
    npv_long_term_market_plants_all = dict()
    irrs_per_year_new_plants_all = dict()
    sr_operator = reps.get_strategic_reserve_operator(reps.country)
    SR_powerplants = [j for i in sr_operator.list_of_plants_all.values() for j in i]
    npvs_per_year_perMW_strategic_reseve = pd.DataFrame(index=ticks_to_generate).fillna(0)
    for technology_name in unique_technologies:
        powerplants_per_tech = reps.get_power_plants_by_technology(technology_name)
        irrs_per_year = pd.DataFrame(index=ticks_to_generate).fillna(0)
        npvs_per_year_perMW = pd.DataFrame(index=ticks_to_generate).fillna(0)
        npvs_per_year_new_plants = pd.DataFrame(index=ticks_to_generate).fillna(0)
        npvs_in_ltcm = pd.DataFrame(index=ticks_to_generate).fillna(0)
        irrs_per_year_new_plants = pd.DataFrame(index=ticks_to_generate).fillna(0)
        totalProfitswLoans = pd.DataFrame(index=ticks_to_generate).fillna(0)
        for plant in powerplants_per_tech:
            irr_per_plant = reps.get_irrs_for_plant(plant.name)
            if irr_per_plant is None:
                pass
                # print("power plant in pipeline", plant.name, plant.id)
            else:
                a = reps.get_npvs_for_plant(plant.name) / plant.capacity
                if plant.is_new_installed():
                    info = plant.name + " " + str(plant.capacity) + " MW " + str(plant.age)
                    irrs_per_year_new_plants[info] = irr_per_plant

                info = plant.name + " " + str(plant.capacity) + " MW " + str(plant.age)
                if reps.power_plant_in_ltcm(plant):
                    npvs_in_ltcm[info] = a
                else:
                    npvs_per_year_new_plants[info] = a

                if plant.name in SR_powerplants:
                    info = plant.name + " " + str(plant.capacity) + " MW " + str(plant.age)
                    npvs_per_year_perMW_strategic_reseve[info] = a
                else:
                    irrs_per_year[plant.name] = irr_per_plant
                    npvs_per_year_perMW[plant.name] = a
                    totalProfitswLoans[plant.name] = reps.get_totalProfitswLoans_for_plant(plant.name) / plant.capacity

        irrs_per_year_new_plants.replace(to_replace=-100, value=np.nan,
                                         inplace=True)  # the -100 was hard coded in the financial reports
        irrs_per_year.replace(to_replace=-100, value=np.nan,
                              inplace=True)

        npvs_per_year_new_plants_perMW_all[technology_name] = npvs_per_year_new_plants
        npv_long_term_market_plants_all[technology_name] = npvs_in_ltcm

        irrs_per_year_new_plants_all[technology_name] = irrs_per_year_new_plants * 100  # making to percent
        if irrs_per_year.size != 0:
            irrs_per_tech_per_year[technology_name] = np.nanmean(irrs_per_year, axis=1)
        if npvs_per_year_perMW.size != 0:
            npvs_per_tech_per_MW[technology_name] = np.nanmean(npvs_per_year_perMW, axis=1)
        if totalProfitswLoans.size != 0:
            profits_with_loans_all[technology_name] = np.nanmean(totalProfitswLoans, axis=1)
    npvs_per_year_perMW_strategic_reseve['years'] = years_to_generate
    npvs_per_year_perMW_strategic_reseve.set_index("years", inplace=True)
    npvs_per_tech_per_MW['years'] = years_to_generate
    npvs_per_tech_per_MW.set_index("years", inplace=True)
    irrs_per_tech_per_year['years'] = years_to_generate
    irrs_per_tech_per_year.set_index("years", inplace=True)

    return irrs_per_tech_per_year * 100, npvs_per_tech_per_MW, npvs_per_year_new_plants_perMW_all, \
        irrs_per_year_new_plants_all, profits_with_loans_all, npvs_per_year_perMW_strategic_reseve, npv_long_term_market_plants_all


def prepare_future_fuel_prices(reps):
    substances_calculated_prices = pd.DataFrame()
    for k, substance in reps.substances.items():
        calculatedPrices = substance.simulatedPrice
        substances_calculated_prices[substance.name] = calculatedPrices
    return substances_calculated_prices


def prepare_screening_curves(reps, year):
    hours = np.array(list(range(1, reps.hours_in_year)))
    agent = reps.energy_producers[reps.agent]

    yearly_costs = pd.DataFrame(index=hours)
    marginal_costs_per_hour = pd.DataFrame()
    co2price = reps.substances["CO2"].simulatedPrice[year]
    for tech_name, tech in reps.power_generating_technologies.items():
        if tech.intermittent == False:
            investment_cost = tech.get_investment_costs_perMW_by_year(year)
            debt = investment_cost * agent.debtRatioOfInvestments
            annual_cost_debt = npf.pmt(agent.loanInterestRate, tech.expected_lifetime, -debt)
            if tech.fuel == "":
                fuel_price = np.int64(0)
                co2_TperMWh = np.int64(0)
            else:
                calculatedPrices = tech.fuel.simulatedPrice
                fuel_price = calculatedPrices.at[(year)]
                # Co2EmissionsInTperMWH / efficiency = CO2 emissions per MWh
                co2_TperMWh = tech.fuel.co2_density  # TperMWH
                # uncomment this if it is the old amiris prices
                # fuel_price = AMIRIS_temporal_fuel[tech.fuel.name]
                # co2price = AMIRIS_temporal_fuel["CO2"]
                # co2_TperMWh = SpecificCo2EmissionsInTperMWH[tech.fuel.name]
            opex = (tech.variable_operating_costs + (fuel_price + co2price * co2_TperMWh) / tech.efficiency) * hours
            total = annual_cost_debt + opex + tech.get_fixed_costs_by_commissioning_year(year)
            yearly_costs[tech_name] = total
            # Eur/Mwh * h = Eur/MW
            marginal_costs_per_hour.at[tech_name, 0] = tech.variable_operating_costs + (
                    fuel_price + co2price * co2_TperMWh) / tech.efficiency
        else:
            pass
    return yearly_costs, marginal_costs_per_hour


def prepare_screening_curves_candidates(reps, year):
    hours = np.array(list(range(1, reps.hours_in_year)))
    agent = reps.energy_producers[reps.agent]
    wacc = (1 - agent.debtRatioOfInvestments) * agent.equityInterestRate \
           + agent.debtRatioOfInvestments * agent.loanInterestRate
    yearly_costs_candidates = pd.DataFrame(index=hours)

    CO2prices_future_prices = reps.substances["CO2"].futurePrice
    # values = [float(i[1]) for i in CO2prices_future_prices["data"]]
    # index = [int(i[0]) for i in CO2prices_future_prices["data"]]
    # co2prices = pd.Series(values, index=index)

    co2price = CO2prices_future_prices[year]
    print("co2price")
    print(co2price)
    for tech in reps.get_unique_candidate_technologies():
        investment_cost = tech.get_investment_costs_perMW_by_year(year)
        annual_cost_capital = npf.pmt(wacc, tech.expected_lifetime, -investment_cost)
        if tech.fuel == "":
            # ton / MWh
            fuel_price = np.int64(0)
            co2_TperMWh = np.int64(0)
        else:
            fuel_price = tech.fuel.futurePrice[year]
            # Co2EmissionsInTperMWH / efficiency = CO2 emissions per MWh
            co2_TperMWh = tech.fuel.co2_density

            # uncomment this if it is the old amiris prices
            # fuel_price = AMIRIS_temporal_fuel[tech.fuel.name]
            # co2price = AMIRIS_temporal_fuel["CO2"]
            # co2_TperMWh = SpecificCo2EmissionsInTperMWH[tech.fuel.name]

        # Eur / MWh * h = EUR/MW
        opex = (tech.variable_operating_costs + (fuel_price + co2price * co2_TperMWh) / tech.efficiency) * hours
        total = annual_cost_capital + opex + tech.get_fixed_costs_by_commissioning_year(year)
        yearly_costs_candidates[tech.name] = total
    return yearly_costs_candidates


def prepare_accepted_CapacityMechanism(reps, ticks_to_generate):
    CM_costs_per_technology = pd.DataFrame(index=ticks_to_generate, columns=unique_technologies)
    number_accepted_pp_per_technology = pd.DataFrame(index=ticks_to_generate, columns=unique_technologies).fillna(0)
    capacity_mechanisms_volume_per_tech = pd.DataFrame(index=ticks_to_generate, columns=unique_technologies)
    CM_clearing_price = pd.DataFrame(index=ticks_to_generate).fillna(0)
    capacity_market_future_price = pd.DataFrame(index=ticks_to_generate).fillna(0)
    CM_clearing_volume = pd.DataFrame(index=ticks_to_generate).fillna(0)
    capacity_market_future_volume = pd.DataFrame(index=ticks_to_generate).fillna(0)
    SR_operator_revenues = pd.DataFrame(index=ticks_to_generate).fillna(0)
    #ticks_to_generate.pop()  # the last year doesnt have the results of the following year #Attention
    # attention: FOR STRATEGIC RESERVES
    sr_operator = reps.get_strategic_reserve_operator(reps.country)

    if reps.capacity_remuneration_mechanism == "strategic_reserve_ger":
        pricecap = None
        for tick in ticks_to_generate:
            if tick in sr_operator.list_of_plants_all:
                accepted_per_tick = sr_operator.list_of_plants_all[tick]
                for technology_name in unique_technologies:
                    for accepted_plant in accepted_per_tick:
                        if reps.power_plants[accepted_plant].technology.name == technology_name:
                            capacity_mechanisms_volume_per_tech.loc[tick, technology_name] += reps.power_plants[
                                accepted_plant].capacity
                # saving
                SR_operator_revenues.at[tick, 0] = sr_operator.revenues_per_year_all[tick]
            else:
                print("no SR in tick" + str(tick))

    # attention: FOR CAPACITY MARKETS
    else:
        if reps.capacity_remuneration_mechanism in ["capacity_market", "capacity_subscription"]:
            market = reps.get_capacity_market_in_country(reps.country, False)
            pricecap = market.PriceCap
        else: # forward enery market is used
            market = reps.get_capacity_market_in_country(reps.country, True)
            pricecap = market.PriceCap
        for tick in ticks_to_generate:
            CM_clearing_price.at[tick, 0] = reps.get_market_clearing_point_price_for_market_and_time(market.name, tick + market.forward_years_CM )
            capacity_market_future_price.at[tick, 0] = reps.get_market_clearing_point_price_for_market_and_time("capacity_market_future", tick + market.forward_years_CM)  # saved according to effective year
            CM_clearing_volume.at[tick, 0] = reps.get_cleared_volume_for_market_and_time(market.name, tick + market.forward_years_CM)
            capacity_market_future_volume.at[tick, 0] = reps.get_cleared_volume_for_market_and_time("capacity_market_future", tick+ market.forward_years_CM)  # saved according to effective year

    cm_revenues_per_pp = pd.DataFrame(index=ticks_to_generate).fillna(0)
    for technology_name in unique_technologies:
        powerplants_per_tech = reps.get_power_plants_by_technology(technology_name)
        temporal = pd.DataFrame(index=ticks_to_generate).fillna(0)
        capacity_awarded = pd.DataFrame(index=ticks_to_generate)
        for pp in powerplants_per_tech:
            CMrevenues = reps.get_CM_revenues(pp.name)  # CM revenues from financial results
            cm_revenues_per_pp[pp.name] = CMrevenues
            temporal[pp.name] = CMrevenues
            if isinstance(CMrevenues, pd.Series):
                df_whereCMawarded = CMrevenues
                df_whereCMawarded[
                    df_whereCMawarded > 0] = pp.capacity * pp.technology.deratingFactor
                capacity_awarded[pp.name] = df_whereCMawarded
            else:
                pass
        capacity_mechanisms_volume_per_tech[technology_name] = capacity_awarded.sum(axis=1, skipna=True)
        number_accepted_pp_per_technology[technology_name] = temporal.gt(0).sum(axis=1)
        total_revenues_per_technology = temporal.sum(axis=1, skipna=True)
        CM_costs_per_technology[technology_name] = total_revenues_per_technology
    total_costs_CM = CM_costs_per_technology.sum(axis=1, skipna=True)
    capacity_mechanisms_volume_per_tech.replace(0, np.nan, inplace=True)
    capacity_mechanisms_volume_per_tech.dropna(axis=1, how='all', inplace=True)
    return (CM_costs_per_technology, number_accepted_pp_per_technology, capacity_mechanisms_volume_per_tech,
            CM_clearing_price, capacity_market_future_price, CM_clearing_volume,capacity_market_future_volume ,total_costs_CM, \
             SR_operator_revenues, cm_revenues_per_pp, pricecap )


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


def prepare_capacity_and_generation_per_technology(reps, renewable_technologies, yearly_load,
                                                   years_to_generate):
    all_techs_consumption = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    all_techs_generation = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    all_techs_full_load_hours = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    all_techs_market_value = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    all_techs_capacity_factor = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    average_electricity_price = pd.DataFrame(index=years_to_generate, columns=["wholesale price"]).fillna(0)
    share_RES = pd.DataFrame(index=years_to_generate).fillna(0)
    #  production_per_year = pd.DataFrame(index=years_to_generate).fillna(0)
    for year in years_to_generate:
        dispatch_per_year = reps.get_all_power_plant_dispatch_plans_by_tick(year)
        totalrevenues = 0
        totalproduction = 0
        for technology_name in unique_technologies:
            generation_per_tech = 0
            consumption_per_tech = 0
            market_value_per_plant = []
            capacity_factor_per_tech = []
            full_load_hours = []
            for id, pp_production_in_MWh in dispatch_per_year.accepted_amount.items():
                power_plant = reps.get_power_plant_by_id(id)
                if power_plant is not None:
                    if power_plant.technology.name == technology_name:
                        generation_per_tech += pp_production_in_MWh
                        capacity_factor_per_tech.append(pp_production_in_MWh / (power_plant.capacity * reps.hours_in_year))
                        full_load_hours.append(pp_production_in_MWh / (power_plant.capacity))
                        totalproduction += pp_production_in_MWh
                        totalrevenues += dispatch_per_year.revenues[id]
                        if pp_production_in_MWh > 0:
                            market_value_per_plant.append(dispatch_per_year.revenues[id] / pp_production_in_MWh)
                        else:
                            market_value_per_plant.append(0)

            for id, pp_consumption_in_MWh in dispatch_per_year.consumed_amount.items():
                power_plant = reps.get_power_plant_by_id(id)
                if power_plant is not None:
                    if power_plant.technology.name == technology_name:
                        consumption_per_tech += pp_consumption_in_MWh
                else:
                    if id == str(99999999999) and electrolyzer_read == True:
                        if technology_name == "electrolyzer":
                            technology_name = "industry"
                            """
                            in reality we model the load shifter as the electrolyzer
                            """
                            consumption_per_tech = pp_consumption_in_MWh
                            electrolyzers_capacity = reps.loadShifterDemand['Industrial_load_shifter'].peakConsumptionInMW
                            capacity_factor_per_tech.append(pp_consumption_in_MWh / (electrolyzers_capacity * reps.hours_in_year))
                            if pp_consumption_in_MWh > 0:
                                market_value_per_plant.append(dispatch_per_year.revenues[id] / pp_consumption_in_MWh)

            all_techs_full_load_hours.loc[technology_name, year] = mean(full_load_hours)
            all_techs_capacity_factor.loc[technology_name, year] = mean(capacity_factor_per_tech)
            all_techs_market_value.loc[technology_name, year] = mean(market_value_per_plant)
            all_techs_generation.loc[technology_name, year] = generation_per_tech
            all_techs_consumption.loc[technology_name, year] = consumption_per_tech
            # if technology_name == "Lithium_ion_battery":
            #     all_techs_generation.loc["Lithium_ion_battery_charge", year] = generation_per_tech_charge
        if totalproduction != 0:
            average_electricity_price.loc[year, "wholesale price"] = totalrevenues / totalproduction

    share_RES= 100 * all_techs_generation.loc[renewable_technologies].sum(axis=0) / all_techs_generation.sum()
    #   production_per_year.loc[year, 1] = totalproduction
    return all_techs_generation, all_techs_consumption, all_techs_market_value.replace(np.nan, 0), \
        all_techs_capacity_factor.replace(np.nan, 0), average_electricity_price, all_techs_full_load_hours, share_RES


def calculating_RES_support(reps, years_to_generate):
    VRES_support = pd.DataFrame()
    for target_invested_plant in reps.get_power_plants_if_target_invested():
        name = target_invested_plant.name
        commissioned_tick = target_invested_plant.commissionedYear - reps.start_simulation_year
        downpayment = target_invested_plant.downpayment

        if target_invested_plant.age > 0:
            financialPowerPlantReport = reps.get_financial_report_for_plant(target_invested_plant.name)
            # filter total profits until end of life
            # end of lifetime = current tick(5) + expected lifetime (30) - age(2) =  33
            last_tick = min(reps.current_tick, target_invested_plant.endOfLife)
            index_years = list(range(commissioned_tick, last_tick + 1))
            totalprofits_until_RES_Support = financialPowerPlantReport.totalProfitswLoans.loc[index_years]
            VRES_support[name] = totalprofits_until_RES_Support

        if downpayment is not None:
            # attention : change this to get number of payments done
            made_downpayments = downpayment.getNumberOfPaymentsDone() * downpayment.getAmountPerPayment()
            # made_downpayments =  downpayment.getTotalNumberOfPayments() * downpayment.getAmountPerPayment()
            VRES_support.at[commissioned_tick - 1, name] = - made_downpayments

    # filtering the positive power plants:
    filtered_VRES_support = - VRES_support[VRES_support < 0]
    # Adding missing profits
    total_vres_support = filtered_VRES_support.sum(axis=1)
    total_vres_support.sort_index(ascending=True, inplace=True)
    new_index = total_vres_support.index.values + reps.start_simulation_year
    total_vres_support.index = new_index
    yearly_vres_support = pd.DataFrame(index=years_to_generate)
    yearly_vres_support["Vres support"] = total_vres_support
    # todo filter for the lifetime of
    yearly_vres_support.fillna(0, inplace=True)
    return yearly_vres_support


def reading_electricity_prices(reps, folder_name, scenario_name, existing_scenario):
    years_to_generate = list(range(reps.start_simulation_year, reps.current_year + 1))
    yearly_electricity_prices = pd.DataFrame()
    TotalAwardedPowerInMW = pd.DataFrame()
    curtailed_res = pd.DataFrame()

    global DispatchSystemCostInEUR
    DispatchSystemCostInEUR = pd.DataFrame()

    global hourly_load_shedded
    hourly_load_shedded = pd.DataFrame()

    global hourly_industrial_heat
    hourly_industrial_heat = pd.DataFrame()

    global average_yearly_generation
    average_yearly_generation = pd.DataFrame()

    global hourly_load_shedders_per_year
    hourly_load_shedders_per_year = dict()

    global production_in_scarcity
    production_in_scarcity = dict()

    dfs = {}
    for year in years_to_generate:
        if existing_scenario == True:
            year_excel = globalNames.scenarios_path + scenario_name + "\\" + str(year) + ".xlsx"
        else:
            year_excel = folder_name + str(year) + ".xlsx"

        df = pd.read_excel(year_excel, sheet_name=["energy_exchange", "residual_load", "hourly_generation"])
        yearly_electricity_prices.at[:, year] = df['energy_exchange']["ElectricityPriceInEURperMWH"]
        TotalAwardedPowerInMW.at[:, year] = df['energy_exchange'].TotalAwardedPowerInMW
        DispatchSystemCostInEUR.at[year, 0] = df['energy_exchange'].DispatchSystemCostInEUR.sum()
        #
        # if "residual_load_actual_infeed" in df['residual_load'].columns:
        #     residual_load.at[:, year] = df['residual_load']['residual_load_actual_infeed']
        # else:
        #     residual_load.at[:, year] = df['residual_load']['residual_load']

        curtailed_res.at[year, 0]  = df['residual_load']['curtailed_res'].sum()

        hourly_load_shedded.at[:, year] = df['hourly_generation'].load_shedding
        hourly_industrial_heat.at[:, year] = df['hourly_generation'].electrolysis_power_consumption

        if calculate_hourly_shedders_new == True:
            hourly_load_shedders = pd.DataFrame()
            for unit in df['hourly_generation'].columns.values:
                if unit[0:4] == "unit":
                    hourly_load_shedders[unit[5:]] = df['hourly_generation'][unit]
            hourly_load_shedders_per_year[year] = hourly_load_shedders

        if calculate_monthly_generation == True:
            name = "yearly_generation" + str(year)
            dfs[name] = df['hourly_generation'][
                ["PV", "WindOff", "WindOn", "storages_discharging",
                 "conventionals", "electrolysis_power_consumption"]]

            LS = hourly_load_shedders.drop(columns=["8888888"]).sum(axis =1)
            scarcity_hours = LS[LS > 0].index
            if len(scarcity_hours)>0:
                production_in_scarcity[year]  = dfs[name].loc[scarcity_hours].mean(axis=0)

    if calculate_monthly_generation == True:
        total_sum = pd.DataFrame(0, index=range(reps.hours_in_year), columns=["PV", "WindOff", "WindOn", "storages_discharging",
                                                                "conventionals", "electrolysis_power_consumption"])
        for df in dfs.values():
            total_sum = total_sum + df
        average_yearly_generation = total_sum / len(years_to_generate)

    return yearly_electricity_prices, curtailed_res, TotalAwardedPowerInMW


def reading_original_load(years_to_generate, list_ticks ):
    if reps.country == "NL" and reps.fix_demand_to_representative_year == False:
        input_data = os.path.join(os.path.dirname(os.getcwd()) , 'data', reps.scenarioWeatheryearsExcel)
        input_yearly_profiles_demand = input_data
        sequence = reps.weatherYears["weatherYears"].sequence[list_ticks]
        allyears_load = pd.read_excel(input_yearly_profiles_demand, index_col=None, sheet_name="Load")
        yearly_load = pd.DataFrame(columns=years_to_generate)
        zipped = zip(years_to_generate, sequence.tolist())
        for y in zipped:
            if y[1] in allyears_load:
                yearly_load[y[0]] = allyears_load[y[1]]
            else:
                yearly_load[y[0]] = allyears_load.iloc[:, y[1]]

    elif reps.country == "NL" and reps.fix_demand_to_representative_year == True:
        input_yearly_profiles_demand = os.path.join(os.path.dirname(os.getcwd()) , 'data', reps.scenarioWeatheryearsExcel)
        all_years = pd.read_excel(input_yearly_profiles_demand, index_col=None, sheet_name="Load")
        load_representative_year = pd.DataFrame(all_years[reps.representative_year])
        # repeat load for all generation years
        number_years = len(years_to_generate)
        yearly_load = pd.concat([load_representative_year] * number_years, axis=1)
        yearly_load.columns = years_to_generate


    elif reps.country == "DE":
        input_yearly_profiles_demand = globalNames.input_load_de
        one_year_load = pd.read_csv(input_yearly_profiles_demand, sep=";")
        yearly_load = pd.DataFrame()
        for y in years_to_generate:
            yearly_load[y] = one_year_load
    else:
        print("which country?")
    print("finish reading  excel")
    return yearly_load

def prepare_percentage_load_shedded_new(reps, years_to_generate):
    total_load_shedded = pd.DataFrame()
    total_load_shedded_per_year = pd.DataFrame()
    max_ENS_in_a_row = pd.DataFrame()
    LOLE_per_group = pd.DataFrame()
    VOLL_per_year = pd.DataFrame()
    for year in years_to_generate:
        for name, values in reps.loadShedders.items():
            selected_df = hourly_load_shedders_per_year[year]
            test_list = [int(i) for i in selected_df.columns.values]
            selected_df.columns = test_list
            if name == "hydrogen":  # hydrogen is the lowest load shedder
                total_load_shedded[name] = selected_df[(8888888)]
            else:
                id_shedder = int(name) * 100000
                if id_shedder in selected_df.columns:
                    total_load_shedded[name] = selected_df[(id_shedder)]
                    if reps.capacity_remuneration_mechanism == "capacity_subscription":
                        VOLL_per_year.at[name, year] = values.percentageLoad[year]
                    else:
                        VOLL_per_year.at[name, year]  = values.percentageLoad[reps.start_simulation_year]
                else:
                    print("---------" + str(year) )
                    print(id_shedder)

        total_load_shedded_per_year[year] = total_load_shedded.sum()
        LOLE_per_group[year] = total_load_shedded[total_load_shedded > 0].count()

        for column_name, column_data in total_load_shedded.iteritems():
            continuous_hours = 0  # Counter for continuous hours
            max_continuous_hours = 0  # Counter for maximum continuous hours
            prev_value = 0  # Variable to store the previous value
            filtered = [column_data > 0]
            for value in filtered[0]:
                if value == True:
                    continuous_hours += 1
                else:
                    continuous_hours = 0
                if continuous_hours > max_continuous_hours:
                    max_continuous_hours = continuous_hours
            max_ENS_in_a_row.at[column_name, year] = max_continuous_hours
    return  max_ENS_in_a_row, LOLE_per_group, total_load_shedded_per_year, VOLL_per_year


def prepareCONE_and_derating_factors(years_to_generate, all_techs_capacity):
    if reps.capacity_remuneration_mechanism == "capacity_market":
        cones = pd.DataFrame()
        netcones = pd.DataFrame()
        for name, i in  reps.capacity_markets.items():
            if i.name in unique_technologies:
                cones[i.name] = i.cone
                netcones[i.name] = i.netcone
        cones.sort_index(inplace=True)
        netcones.sort_index(inplace=True)
        axs21 = cones.plot() # color=colors_unique_techs
        netcones.plot(ax= axs21, linestyle='dashed')
        axs21.set_axisbelow(True)
        plt.xlabel('Years', fontsize='medium')
        plt.ylabel(' (€/MW)', fontsize='medium')
        plt.title("net cone(----) = CONE - market profits ")
        plt.grid()
        fig21 = axs21.get_figure()
        fig21.savefig(path_to_plots + '/' + 'CONEs.png', bbox_inches='tight', dpi=300)

    """
    These are the realized derating factors based on realized weather
    """
    dict = {
        "PV": "Solar PV large", "WindOff": "Wind Offshore", "WindOn": "Wind Onshore", "storages_discharging":"Lithium ion battery 4",
    } #"conventionals", "electrolysis_power_consumption"
    realized_derating_factors = pd.DataFrame()
    for year in years_to_generate:
        if year in production_in_scarcity:
            production = production_in_scarcity[year]
            for tech, energy in production.items():
                if  tech in dict:
                    if dict[tech] in all_techs_capacity.columns:
                        realized_derating_factors.loc[ year, dict[tech]] = energy / all_techs_capacity.loc[ year, dict[tech]]

    initial_derating_factor = pd.DataFrame()
    for name, tech in  reps.power_generating_technologies.items():
        if tech.name in realized_derating_factors.columns:
            initial_derating_factor.loc[2049, tech.name] = tech.deratingFactor

    initial_derating_factor.dropna(axis=1, how='all', inplace=True)

    fig, (ax1, ax2) = plt.subplots(2, 1, sharey=True)
    colors = [technology_colors[tech] for tech in realized_derating_factors.columns.values]
    realized_derating_factors.plot( marker='o', linestyle='dashed', ax = ax1, color = colors) # color=colors_unique_techs
    colors = [technology_colors[tech] for tech in initial_derating_factor.columns.values]
    initial_derating_factor.plot( marker='D', ax = ax1, color = colors)

    n = len(initial_derating_factor.columns)
    handles, labels = ax1.get_legend_handles_labels()
    a = ["realized", "initial"]
    new_labels = [element for element in a for _ in range(n)]
    new_handles = [handle for handle, label in zip(handles, new_labels) if label]
    ax1.legend(new_handles, [label for label in new_labels if label], fontsize='small', loc='upper right', bbox_to_anchor=(1, 1))
    ax1.set_ylabel('realized market', fontsize='medium')
    ax1.grid(True)
    """
    These are the expected derating factors based on future for representative year
    """
    if reps.dynamic_derating_factor == True:
        derating_factor = pd.DataFrame()
        for name, tech in  reps.power_generating_technologies.items():
            if name in unique_technologies:
                derating_factor[tech.name] = tech.deratingFactoryearly
        derating_factor.sort_index(inplace=True)
        derating_factor.dropna(axis=1, how='all', inplace=True)
        derating_factor.index = derating_factor.index + reps.start_simulation_year
        derating_factor_mean = derating_factor.rolling(window= reps.dynamic_derating_factor_window, min_periods=1).mean()
        colors = [technology_colors[tech] for tech in derating_factor_mean.columns.values]
        if derating_factor_mean.size != 0:
            derating_factor_mean.plot(marker='*', ax = ax2, color = colors, label='applied') # color=colors_unique_techs
            derating_factor.plot(marker='s', ax = ax2, color = colors, label='future')
            a = ["mean", "yearly"]
            handles, labels = ax1.get_legend_handles_labels()
            new_labels = [element for element in a for _ in range(n)]
            new_handles = [handle for handle, label in zip(handles, new_labels) if label]
            ax2.legend(new_handles, [label for label in new_labels if label], fontsize='small', loc='upper right', bbox_to_anchor=(1, 1))
            ax2.set_xlabel('Years', fontsize='medium')
            ax2.grid(True)
            ax2.set_ylabel('future market', fontsize='medium')
    #plt.title(" D = initial , o- = realized weather" + "\n  *  = representative year (expected)"  )
    fig.savefig(path_to_plots + '/' + 'Derating factor.png', bbox_inches='tight', dpi=300)
    plt.close('all')


def prepare_subscribed_capacity_new(ticks_to_generate):
    subscribed_yearly_volume = pd.DataFrame()
    for consumer in reps.cs_consumers.values():
        subscribed_yearly_volume[consumer.name] = consumer.subscribed_volume
    subscribed_yearly_volume.sort_index(inplace=True)
    # # fig3, axs3 = plt.subplots(1, 1)
    # fig3.tight_layout()
    names_ordered = reps.get_CS_consumer_descending_WTP_names()
    if "DSR" in subscribed_yearly_volume.columns:
        names_ordered.append("DSR")
    subscribed_yearly_volume = subscribed_yearly_volume[ names_ordered]
    axs3 = subscribed_yearly_volume.plot( kind='bar', stacked=True, grid=True, legend=True ,  cmap='viridis')
    axs3.legend(fontsize='small', loc='upper right', bbox_to_anchor=(1.5, 1))
    axs3.set_ylabel('subscribed \n consumers vol. [MW]', fontsize='large')
    # axs3[0].set_xlabel('CS Bids', fontsize='large')
    # axs3[1].set_ylabel('CS bids \n [Eur/MW - y]', fontsize='large')
    fig = axs3.get_figure()
    fig.savefig(path_to_plots + '/' + 'subscribed_consumers.png', bbox_inches='tight', dpi=300)

    # past_consumer_bids = dict()
    # for tick in ticks_to_generate:
    #     path  = os.path.join(folder_name +  str(tick) +"bid_per_consumer_group.csv")
    #     if os.path.exists(path):
    #         past_consumer_bids[tick] = pd.read_csv(path )
    #     else:
    #         print(path)
    #         raise Exception("File not found")
    # num_iterations  = len(past_consumer_bids)
    # for key, consumers in past_consumer_bids.items():
    #     cumsum = consumers.volume.cumsum()
    #     color=plt.cm.inferno(key / num_iterations)
    #     plt.step( cumsum, consumers.bid, where='post', label = key, color = color)
    # plt.legend(ncol = 3)
    # plt.ylabel('bids')
    # plt.xlabel('volume')
    # plt.savefig(path_to_plots + '/' + 'bids_consumers.png', bbox_inches='tight', dpi=300)
    return subscribed_yearly_volume
def prepare_subscribed_capacity():
    subscribed_yearly = pd.DataFrame()
    bid_yearly = pd.DataFrame()
    for consumer in reps.cs_consumers.values():
        subscribed_yearly[consumer.name] = consumer.subscribed_yearly
        bid_yearly[consumer.name] = consumer.bid
    sorted_bids = bid_yearly.sort_values(by=bid_yearly.index[0], axis=1, ascending=False)
    column_order = sorted_bids.columns
    subscribed_sorted = subscribed_yearly[column_order]
    sorted_bids.sort_index(ascending=False, inplace=True)
    subscribed_sorted.sort_index(ascending=True, inplace=True)

    plt.close('all')
    yearly_peak_demand = reps.get_realized_peak_demand()
    num_iterations = reps.current_tick

    for i in range(num_iterations):
        axs40 = plt.plot( np.cumsum(subscribed_sorted.iloc[i]* yearly_peak_demand.iloc[i] ), \
                          sorted_bids.iloc[i], label = str(i),  color=plt.cm.inferno(i / num_iterations))
    plt.xlabel('Volume [MW]', fontsize='medium')
    plt.ylabel('Bids [Eur/MW]', fontsize='medium')
    plt.title("demand curves per year")
    plt.grid(True, which='minor')
    plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(1, 1), ncol=3)
    axs40[0].figure.savefig(path_to_plots + '/' + 'subscribed_demand_curves.png', bbox_inches='tight', dpi=300)

    fig3, axs3 = plt.subplots(2, 1)
    fig3.tight_layout()
    subscribed_sorted.plot(ax=axs3[0], kind='bar', stacked=True, grid=True, legend=True,  cmap='viridis')
    axs3[0].legend(fontsize='small', loc='upper right', bbox_to_anchor=(1.5, 1))
    sorted_bids.plot(ax=axs3[1], grid=True, legend=False,  cmap='viridis' )
    axs3[0].set_ylabel('subscribed \n consumers', fontsize='large')
   # axs3[0].set_xlabel('CS Bids', fontsize='large')
    axs3[1].set_ylabel('CS bids \n [Eur/MW - y]', fontsize='large')
    fig3.savefig(path_to_plots + '/' + 'subscribed_consumers.png', bbox_inches='tight', dpi=300)
    plt.close()
    return subscribed_sorted
def prepare_percentage_load_shedded(yearly_load, weighted_average_VOLL, years_to_generate):
    production_not_shedded_MWh = pd.DataFrame()
    load_shedded_per_group_MWh = pd.DataFrame()
    cost_non_subcription = pd.DataFrame()
    total_yearly_electrolysis_consumption = pd.DataFrame()
    total_yearly_hydrogen_input_demand = reps.loadShedders["hydrogen"].ShedderCapacityMW * reps.hours_in_year
    hydrogen_input_demand = [reps.loadShedders["hydrogen"].ShedderCapacityMW] * reps.hours_in_year
    input_shifter_demand = reps.loadShifterDemand[
                               'Industrial_load_shifter'].averagemonthlyConsumptionMWh * 12
    total_load_shedded = pd.DataFrame()
    load_per_group =  pd.DataFrame()
    for tick, year in enumerate(years_to_generate):
        for name, LS in reps.loadShedders.items():
            selected_df = hourly_load_shedders_per_year[year]
            test_list = [int(i) for i in selected_df.columns.values]
            selected_df.columns = test_list
            if name == "hydrogen":  # hydrogen is the lowest load shedder
                total_load_shedded[name] = selected_df[(8888888)]
                yearly_hydrogen_shedded = total_load_shedded[name].sum()
                production_not_shedded_MWh.at[year, "hydrogen_produced"] = (total_yearly_hydrogen_input_demand - yearly_hydrogen_shedded)
                production_not_shedded_MWh.at[year, "hydrogen_percentage_produced"] = ((total_yearly_hydrogen_input_demand - yearly_hydrogen_shedded) / total_yearly_hydrogen_input_demand) * 100
                total_yearly_electrolysis_consumption[year] = hydrogen_input_demand - total_load_shedded[name]
            else:
                id_shedder = int(name)* 100000
                total_load_shedded[name] = selected_df[(id_shedder)]
                load_shedded_per_group_MWh.at[year, name] = selected_df[(id_shedder)].sum()
                if LS.VOLL == 1500:
                    cost_non_subcription.at[year, name] = selected_df[(id_shedder)].sum() * LS.VOLL
                else:
                    if reps.capacity_remuneration_mechanism == "capacity_subscription":
                        cost_non_subcription.at[year, name] = selected_df[(id_shedder)].sum() * weighted_average_VOLL[tick]
                    else:
                        cost_non_subcription.at[year, name] = selected_df[(id_shedder)].sum() * weighted_average_VOLL

        if industrial_demand_as_flex_demand_with_cap == True:
            flexconsumer_MWh = hourly_industrial_heat[year].sum()
            production_not_shedded_MWh.at[year, "industrial_heat_demand"] = flexconsumer_MWh
            production_not_shedded_MWh.at[year, "industrial_percentage_produced"] = (flexconsumer_MWh / input_shifter_demand) * 100
        else:
            production_not_shedded_MWh.at[year, "industrial_shedder"] = 0

    if calculate_monthly_generation == True:
        average_yearly_generation["electrolysis consumption"] = total_yearly_electrolysis_consumption.mean(axis=1)

    normalized_load_shedded = pd.DataFrame()
    for year in years_to_generate:
        for lshedder in reps.loadShedders.values():
            if lshedder.name != "hydrogen":
                if reps.capacity_remuneration_mechanism == "capacity_subscription":
                    percentage_load = lshedder.percentageLoad[year]
                    sheddable_load = yearly_load[year].sum() * percentage_load
                else:
                    percentage_load = lshedder.percentageLoad[reps.start_simulation_year]
                    sheddable_load = yearly_load[year].sum() * percentage_load
                load_shedded = load_shedded_per_group_MWh.loc[year, lshedder.name]
                normalized_load_shedded.at[year, lshedder.name] = load_shedded / sheddable_load

                load_per_group.at[year, lshedder.name] = percentage_load * reps.get_realized_peak_demand_by_year( year)
    normalized_load_shedded = normalized_load_shedded * 100
    return (normalized_load_shedded, production_not_shedded_MWh, load_shedded_per_group_MWh,
            average_yearly_generation, cost_non_subcription, load_per_group)


# def get_production_by_consumer(reps, total_load_shedded_per_year, years_to_generate):
#     excel = os.path.join(os.path.dirname(os.getcwd()),'data' , reps.scenarioWeatheryearsExcel + '.xlsx')
#     original_load = pd.read_excel(reps.scenarioWeatheryearsExcel, sheet_name="Load")
#     reps.iteration_weather
#     sequence_year = original_load.values[new_tick]
#
#     for lshedder_name in load_shedders_no_hydrogen:
#         load_shedder = excel['Load'][sequence_year] * load_shedders.loc[lshedder_name, "percentage_load"]
#     load_shedder_file_for_amiris = os.path.join(amiris_worfklow_path, os.path.normpath(
#         load_shedders.loc[lshedder_name, "TimeSeriesFile"]))
#     load_shedder.to_csv(load_shedder_file_for_amiris, header=False, sep=';', index=True)
#     production_per_consumer = pd.DataFrame()
#     for year in years_to_generate:
#         for consumer in reps.cs_consumers.values():
#             production_per_consumer[consumer.name] = consumer.production_yearly
#     return production_per_consumer



def get_shortage_hours_and_power_ratio(reps, years_to_generate, yearly_electricity_prices,
                                       yearly_load, LOLE_per_group):
    simple_electricity_prices_average = yearly_electricity_prices.sum(axis=0) / reps.hours_in_year
    # average electricity prices calculated in prepare capacpity and generation are the same
    shortage_hours = pd.DataFrame(index=years_to_generate)
    inflexible_shedding = hourly_load_shedded - reps.loadShedders["hydrogen"].ShedderCapacityMW
    shortage_hours["all groups"] = LOLE_per_group.loc["1"] #+ LOLE_per_group.loc["2"]

    """
    supply ratio: hour when load is the highest 
    """
    installedCapacity = pd.Series(reps.installedCapacity['All'].yearly)
    maxload = yearly_load.max()  # hour where load is the highest
    a = maxload.loc[installedCapacity.index.values]  # capacity when load is the highest
    supply_ratio = installedCapacity.divide(a, fill_value=np.nan)  # available supply at peak over peak demand.
    """
    reserve margin 
    (available generation capacty - peak demand) / peak demand
    """
    return shortage_hours, supply_ratio, simple_electricity_prices_average


def prepare_monthly_electricity_prices(electricity_prices):
    monthly_electricity_price = electricity_prices.copy(deep=True)
    monthly_electricity_price['monthly'] = (electricity_prices.index // 730)
    grouped = monthly_electricity_price.groupby(['monthly']).mean()
    monthly_electricity_price_grouped = grouped.melt()['value']
    # monthly_electricity_price_grouped = pd.melt(grouped, id_vars='index', value_name='Value')#grouped.melt()['value']

    ax1 = monthly_electricity_price_grouped.plot(  )
    plt.legend(fontsize='small', loc='upper left', ncol=2 ,bbox_to_anchor=(1.1, 1.1))
    plt.xlabel('Months', fontsize='medium')
    plt.ylabel('€/MWh', fontsize='medium')
    ax1.set_title('Monthly electricity prices')
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(60))
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(12))
    ax1.grid(True, which='minor')
    fig1 = ax1.get_figure()
    fig1.savefig(path_to_plots + '/' + 'Monthly_electricity_prices.png', bbox_inches='tight', dpi=300)
    plt.close("all")
    results_file = os.path.join(path_to_plots, 'monthly_electricity_prices.csv')
    monthly_electricity_price_grouped.to_csv(results_file, header=True, sep=';', index=True)

    # axs1 = sns.catplot( data=monthly_electricity_price_grouped, x="variable", y="value",  kind="box")
    # plt.xlabel('sequence', fontsize='large')
    # plt.ylabel('Monthly electricity prices Eur/MWh ', fontsize='large')
    # plt.tight_layout()
    # plt.xticks(rotation=90, size = 15)
    # axs1.savefig(path_to_plots + '/' + 'Monthly_electricity_prices.png', bbox_inches='tight', dpi=300)

    ax1 = grouped.plot(cmap = 'inferno' )
    ax1.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    plt.xlabel('Months', fontsize='medium')
    plt.ylabel('€/MWh', fontsize='medium')
    ax1.set_title('Monthly electricity prices')
    plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(1, 1))
    fig1 = ax1.get_figure()
    fig1.savefig(path_to_plots + '/' + 'Monthly_electricity_prices_by_year.png', bbox_inches='tight', dpi=300)
    return monthly_electricity_price_grouped


def generate_plots(reps, path_to_plots, electricity_prices, curtailed_res, TotalAwardedPowerInMW,
                   calculate_vres_support):
    print("Databases read")
    global unique_technologies
    unique_technologies = reps.get_unique_technologies_names()
    # conventional_technologies = ['Coal PSC', "Fuel oil PGT", 'Lignite PSC', "CCGT_CHP_backpressure_DH", \
    #                             'CCGT', 'OCGT', 'Nuclear', 'fuel_cell', "Pumped_hydro"]
    if reps.capacity_remuneration_mechanism == "none":
        calculate_capacity_mechanisms = False
    else:
        calculate_capacity_mechanisms = True
    renewable_technologies = reps.get_intermittent_technologies_names()
    unique_candidate_power_plants = reps.get_unique_candidate_technologies_names()
    unique_candidate_power_plants += ["Lithium_ion_battery_charge"]  # adding technology for negative production
    start_tick = 0
    global years_to_generate
    years_to_generate = list(range(reps.start_simulation_year, reps.current_year + 1))  # control the current year

    years_to_generate_initialization = list(
        range(reps.start_simulation_year - reps.lookAhead, reps.current_year + 1))  # control the current year
    list_ticks = list(range(0, reps.current_tick + 1))
    ticks_to_generate = list(range(start_tick, reps.current_tick + 1))

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
    first_year = years_to_generate[0]
    test_year = test_tick + reps.start_simulation_year
    future_year = test_year + reps.lookAhead
    future_tick = test_tick + reps.lookAhead
    last_year = years_to_generate[-1]

    if test_year > years_to_generate[-1]:
        raise Exception("Test tick is higher than simulated results, Max year " + str(years_to_generate[-1]))
    if test_tech == None:
        pass
    elif test_tech not in reps.get_unique_candidate_technologies_names():
        raise Exception("Test other technology, this is not installed until year" + str(years_to_generate[-1]))

    yearly_load = reading_original_load(years_to_generate, list_ticks)
    if read_electricity_prices == True:
        monthly_electricity_price_grouped = prepare_monthly_electricity_prices(electricity_prices)

    if calculate_hourly_shedders_new == True:
        max_ENS_in_a_row, LOLE_per_group, total_load_shedded_per_year, VOLL_per_year = prepare_percentage_load_shedded_new(reps, years_to_generate)
    else:
        pass

    if reps.capacity_remuneration_mechanism == "capacity_subscription":
        weighted_average_VOLL = reps.get_weighted_VOLL_unsubscribed()
    else:
        weighted_average_VOLL = reps.get_weighted_VOLL()

    (normalized_load_shedded, production_not_shedded_MWh, load_shedded_per_group_MWh, average_yearly_generation,
     cost_non_subcription, load_per_group) =\
        prepare_percentage_load_shedded(yearly_load, weighted_average_VOLL, years_to_generate)

    subscribed_sorted = pd.DataFrame()
    if reps.capacity_remuneration_mechanism == "capacity_subscription":
        subscribed_sorted = prepare_subscribed_capacity_new(ticks_to_generate)

    plot_load_shedded(path_to_plots, production_not_shedded_MWh, load_shedded_per_group_MWh,
                      normalized_load_shedded)


    if calculate_monthly_generation == True and calculate_hourly_shedders_new == True:
        plot_grouped_monthly_production_per_type(average_yearly_generation)
    overall_NPV_per_technology, overall_IRR_per_technology = prepare_retrospectively_npv_and_irr(reps,
                                                                                                 unique_candidate_power_plants)
    plot_financial_results_new_plants(overall_NPV_per_technology, overall_IRR_per_technology, path_to_plots)

    # # section -----------------------------------------------------------------------------------------------capacities
    prepare_pp_decommissioned(reps)
    all_techs_generation, all_techs_consumption, all_techs_market_value, all_techs_capacity_factor, \
        average_electricity_price, all_techs_full_load_hours, share_RES = prepare_capacity_and_generation_per_technology(
        reps, renewable_technologies, yearly_load,
        years_to_generate)

    plot_total_demand(reps)

    plot_capacity_factor_and_full_load_hours(all_techs_capacity_factor.T, all_techs_full_load_hours.T, path_to_plots,
                                             colors_unique_techs)
    plot_market_values_generation(all_techs_market_value.T, path_to_plots, colors_unique_techs)
    plot_full_load_hours_values(all_techs_full_load_hours.T, path_to_plots, renewable_technologies, colors_unique_techs)
    plot_yearly_average_electricity_prices_and_RES_share(average_electricity_price, share_RES, path_to_plots)
    all_techs_generation_nozeroes = plot_annual_generation(all_techs_generation.T, all_techs_consumption.T, path_to_plots, technology_colors,
                           )

    # section ---------------------------------------------------------------Cash energy producer
    cash_flows_energy_producer, cost_recovery, cumulative_cost_recovery, new_plants_loans , costs_to_society = prepare_cash_per_agent(reps,
                                                                                                                   ticks_to_generate)
    costs_to_society.sort_index(inplace=True)
    social_welfare = pd.DataFrame()
    costs_to_society.index = years_to_generate
    if reps.capacity_remuneration_mechanism == "capacity_subscription":
        "changing index to multiply with load shedded"
        weighted_average_VOLL= weighted_average_VOLL[:-1]
        weighted_average_VOLL.index = years_to_generate
    costs_to_society["ENS"] = total_load_shedded_per_year.loc[["1"]].sum(axis=0)* weighted_average_VOLL + \
                                    total_load_shedded_per_year.loc[["2"]].sum(axis=0)* reps.loadShedders["2"].VOLL # load shedders 2 is the DSR
    costs_to_society4000 = costs_to_society.copy(deep=True)
    costs_to_society4000["ENS"] = total_load_shedded_per_year.loc[["1"]].sum(axis=0)* 4000 + \
                              total_load_shedded_per_year.loc[["2"]].sum(axis=0)* reps.loadShedders["2"].VOLL
    social_welfare["OPEX+CAPEX+ENS"] =  - costs_to_society.sum(axis=1)
    plot_cash_flows(cash_flows_energy_producer, new_plants_loans, calculate_capacity_mechanisms, path_to_plots)

    # #section -----------------------------------------------------------------------------------------------capacities installed
    annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_commissioned, \
        all_techs_capacity, last_year_in_pipeline, last_year_decommissioned, \
        last_year_operational_capacity, last_year_to_be_decommissioned_capacity, \
        last_year_strategic_reserve_capacity, capacity_per_status, number_per_status_last_year = \
        prepare_pp_status(years_to_generate, unique_technologies, reps)
    if calculate_investments != False:
        plot_investments(annual_in_pipeline_capacity, annual_commissioned, annual_decommissioned_capacity,
                         path_to_plots, colors_unique_techs)
    all_techs_capacity_nozeroes = plot_installed_capacity(all_techs_capacity, path_to_plots, years_to_generate, years_to_generate_initialization,
                            technology_colors, ticks_to_generate)
    plot_power_plants_status(capacity_per_status, path_to_plots)
    plot_power_plants_last_year_status(number_per_status_last_year, path_to_plots, last_year)
    # section -----------------------------------------------------------------------------------------------NPV and investments per iteration
    irrs_per_tech_per_year, npvs_per_tech_per_MW, npvs_per_year_new_plants_all, irrs_per_year_new_plants_all, \
        profits_with_loans_all, npvs_per_year_perMW_strategic_reseve, npv_long_term_market_plants_all = \
        prepare_irr_and_npv_per_technology_per_year(reps, ticks_to_generate, years_to_generate)

    plot_irrs_and_npv_per_tech_per_year(irrs_per_tech_per_year, npvs_per_tech_per_MW, profits_with_loans_all,
                                        path_to_plots,
                                        technology_colors)

    installed_capacity_per_iteration, candidate_plants_project_value_per_MW = prepare_capacity_per_iteration(
        future_year, future_tick, reps, unique_candidate_power_plants)

    if candidate_plants_project_value_per_MW.shape[0] == 0:
        print("----------------------------------------------------no installable capacity in this test year")
    else:
        plot_investments_and_NPV_per_iteration(candidate_plants_project_value_per_MW, installed_capacity_per_iteration,
                                               future_year, path_to_plots, colors_unique_candidates)

    # ATTENTION: FOR TEST TECH
    average_profits_per_tech_per_year_perMW, new_pp_profits_for_tech = prepare_operational_profit_per_year_per_tech(
        reps, ticks_to_generate)

    plot_total_profits_per_tech_per_year(average_profits_per_tech_per_year_perMW, path_to_plots, colors_unique_techs)
    if test_tech != None:
        plot_profits_for_tech_per_year(new_pp_profits_for_tech, path_to_plots, colors_unique_techs)
    # reality vs expectation

    NPVNewPlants = plot_npv_new_plants(npvs_per_year_new_plants_all, npv_long_term_market_plants_all, irrs_per_year_new_plants_all,
                                       candidate_plants_project_value_per_MW, test_year,
                                       future_year, path_to_plots)

    # #section -----------------------------------------------------------------------------------------------revenues per iteration
    '''
    decommissioning is plotted according to the year when it is decided to get decommissioned
    '''
    if calculate_investments_per_iteration != False:
        candidates_profits_per_iteration = prepare_profits_candidates_per_iteration(reps)

        sorted_average_revenues_per_iteration_test_tick, all_future_operational_profit, operational_profits_commissioned = prepare_revenues_per_iteration(
            reps, future_tick, last_year, future_year)
        plot_revenues_per_iteration_for_one_tech(all_future_operational_profit, path_to_plots, future_year
                                                 )

        if isinstance(operational_profits_commissioned, pd.Series):
            plot_expected_candidate_profits_real_profits(candidates_profits_per_iteration,
                                                         operational_profits_commissioned,
                                                         path_to_plots, future_year,
                                                         )

    if calculate_profits_candidates_per_iteration != False:
        plot_average_revenues_per_iteration(sorted_average_revenues_per_iteration_test_tick, path_to_plots, first_year,
                                            colors_unique_techs)

    # # #  ---------------------------------------------------------------------- section Capacity Mechanisms
    if calculate_capacity_mechanisms == True:

        """
        The total CM costs already have reduced revenues due to the clawback mechanism
        """
        CM_costs_per_technology, accepted_pp_per_technology, capacity_mechanisms_per_tech, CM_clearing_price, \
            capacity_market_future_price, CM_clearing_volume,capacity_market_future_volume, total_costs_CM, \
            SR_operator_revenues, cm_revenues_per_pp, price_cap = \
            prepare_accepted_CapacityMechanism(
            reps, ticks_to_generate)
        plot_CM_revenues(CM_costs_per_technology, accepted_pp_per_technology, capacity_mechanisms_per_tech,
                         CM_clearing_price,capacity_market_future_price, CM_clearing_volume,capacity_market_future_volume ,
                         total_costs_CM, SR_operator_revenues, cm_revenues_per_pp, price_cap , path_to_plots,
                         colors_unique_techs)

        if reps.capacity_remuneration_mechanism == "strategic_reserve_ger":
            plot_strategic_reserve_plants(npvs_per_year_perMW_strategic_reseve, npvs_per_tech_per_MW, path_to_plots)
        else:
            plot_non_subscription_costs(CM_clearing_price,cost_non_subcription, load_per_group )


    prepareCONE_and_derating_factors(years_to_generate, all_techs_capacity)


    if calculate_vres_support == True:
        yearly_vres_support = calculating_RES_support(reps, years_to_generate)
        plot_yearly_VRES_support(yearly_vres_support, path_to_plots)

    if electricity_prices is not None:
        total_SR_hours = plot_price_duration_curve(electricity_prices, path_to_plots)
        plot_hourly_electricity_prices_boxplot(electricity_prices, path_to_plots)
        shortages, supply_ratio, simple_electricity_prices_average \
            = get_shortage_hours_and_power_ratio(reps, years_to_generate, electricity_prices, yearly_load, LOLE_per_group)
        plot_average_and_weighted(average_electricity_price, simple_electricity_prices_average, path_to_plots)
        plot_supply_ratio(supply_ratio, curtailed_res, yearly_load, path_to_plots)
        plot_shortages_and_ENS(shortages, load_shedded_per_group_MWh, path_to_plots)

        # plotting costs to society
        annual_generation = all_techs_generation.sum().values
        if calculate_vres_support == True:
            VRES_price = yearly_vres_support["Vres support"] / annual_generation.T
            average_electricity_price['VRES support'] = VRES_price.values
        if calculate_capacity_mechanisms == True:
            if reps.capacity_remuneration_mechanism == "capacity_subscription":
                total_costs_CM = total_costs_CM - cash_flows_energy_producer["Clawback"].values
            CM_price = total_costs_CM / annual_generation
            average_electricity_price['CRM_Costs'] = CM_price.values
            if reps.capacity_remuneration_mechanism == "strategic_reserve_ger":
                revenues_SR = SR_operator_revenues[0] / annual_generation
                average_electricity_price['SR_revenues'] = - revenues_SR.values

    plot_lole_per_group(path_to_plots, max_ENS_in_a_row, LOLE_per_group, VOLL_per_year, total_SR_hours)

    # #  section ---------------------------------------------------------------------------------------revenues per iteration

    yearly_costs, marginal_costs_per_hour = prepare_screening_curves(reps, test_year)
    if calculate_investments != False:
        yearly_costs_candidates = prepare_screening_curves_candidates(reps, future_year)
        plot_screening_curve_candidates(yearly_costs_candidates, path_to_plots, test_year + reps.lookAhead)
    plot_screening_curve(yearly_costs, marginal_costs_per_hour, path_to_plots, test_year)
    future_fuel_prices = prepare_future_fuel_prices(reps)
    plot_future_fuel_prices(future_fuel_prices, path_to_plots)
    plot_cost_recovery(cost_recovery, cumulative_cost_recovery, path_to_plots)
   # social_welfare["consumers"] =
    social_welfare["hydrogen_and_heat"] = (production_not_shedded_MWh["hydrogen_produced"]* future_fuel_prices["hydrogen"][2050] \
                                * reps.power_generating_technologies["electrolyzer"].efficiency + \
                                #  not inclusing industrial load becuase the demand is the same
                                reps.calculate_marginal_costs_by_technology( "central gas boiler", 0 , ) * production_not_shedded_MWh["industrial_heat_demand"])
    social_welfare["load"] = (yearly_load.sum(axis = 0)*3750 -
                              load_shedded_per_group_MWh[["1"]].sum(axis=1)*4000 -
                              load_shedded_per_group_MWh["2"]*1500)

# get_production_by_consumer(reps, total_load_shedded_per_year, years_to_generate)
    plot_costs_to_society(average_electricity_price, costs_to_society , costs_to_society4000,social_welfare, path_to_plots)
    extended_lifetime_tech = prepare_pp_lifetime_extension(reps)
    # section -----------------------------------------------------------------------------------------------Write Excel
    if save_excel == True:
        path_to_results = os.path.join(os.getcwd(), "plots", "Scenarios", results_excel)
        CostRecovery_data = pd.read_excel(path_to_results, sheet_name='CostRecovery', index_col=0)
        LOLvoluntary_data = pd.read_excel(path_to_results, sheet_name='LOLvoluntary', index_col=0)
        LOL_data = pd.read_excel(path_to_results, sheet_name='LOL', index_col=0)
        ENS_data = pd.read_excel(path_to_results, sheet_name='ENS', index_col=0)
        Inflexible_load = pd.read_excel(path_to_results, sheet_name='Inflexible_load', index_col=0)
        SupplyRatio_data = pd.read_excel(path_to_results, sheet_name='SupplyRatio', index_col=0)
        ElectricityPrices_data = pd.read_excel(path_to_results, sheet_name='ElectricityPrices', index_col=0)
        lifeextension_data = pd.read_excel(path_to_results, sheet_name='lifeextension', index_col=0)
        TotalSystemCosts_data = pd.read_excel(path_to_results, sheet_name='TotalSystemCosts', index_col=0)
        Monthly_electricity_data = pd.read_excel(path_to_results, sheet_name='MonthlyElectricityPrices', index_col=0)
        H2_production_data = pd.read_excel(path_to_results, sheet_name='H2Production', index_col=0)
        IndustrialHeat_data = pd.read_excel(path_to_results, sheet_name='IndustrialHeat', index_col=0)
        CRM_data = pd.read_excel(path_to_results, sheet_name='CRM', index_col=0)  # costs per total energy
        SRhours_data = pd.read_excel(path_to_results, sheet_name='SRhours', index_col=0)
        SR_data = pd.read_excel(path_to_results, sheet_name='SR', index_col=0)  # revenues per total energy
        VRES_data = pd.read_excel(path_to_results, sheet_name='VRES', index_col=0)
        ShareRES_data = pd.read_excel(path_to_results, sheet_name='ShareRES', index_col=0)
        last_year_operational_capacity_data = pd.read_excel(path_to_results, sheet_name='last_year_capacity',
                                                            index_col=0)
        median_annual_production_data = pd.read_excel(path_to_results, sheet_name='median_annual_production',
                                                            index_col=0)
        NPVNewPlants_data = pd.read_excel(path_to_results, sheet_name='NPVNewPlants', index_col=0)
        Overall_NPV_data = pd.read_excel(path_to_results, sheet_name='overallNPV', index_col=0)
        Overall_IRR_data = pd.read_excel(path_to_results, sheet_name='overallIRR', index_col=0)
        Installed_capacity_data = pd.read_excel(path_to_results, sheet_name='InstalledCapacity', index_col=0)
        Commissioned_capacity_data = pd.read_excel(path_to_results, sheet_name='Invested', index_col=0)
        Dismantled_capacity_data = pd.read_excel(path_to_results, sheet_name='Dismantled', index_col=0)
        Last_year_PDC_data = pd.read_excel(path_to_results, sheet_name='Last_year_pdc', index_col=0)
        costs_to_society_data = pd.read_excel(path_to_results, sheet_name='costs_to_society', index_col=0)
        costs_to_society4000_data = pd.read_excel(path_to_results, sheet_name='costs_to_society4000', index_col=0)

        social_welfare_data = pd.read_excel(path_to_results, sheet_name='social_welfare', index_col=0)
        total_subscribed_consumers = pd.read_excel(path_to_results, sheet_name='subscribedCons', index_col=0)
        curtailment_data = pd.read_excel(path_to_results, sheet_name='VREScurtailed', index_col=0)
        curtailment_data[scenario_name]  = curtailed_res
        total_subscribed_consumers[scenario_name]  = subscribed_sorted.sum(axis=1)
        costs_to_society_data[scenario_name]  = costs_to_society.sum(axis=1)
        costs_to_society4000_data[scenario_name]  = costs_to_society4000.sum(axis=1)
        social_welfare_data[scenario_name]  = social_welfare.sum(axis=1)
        all_techs_capacity_peryear = all_techs_capacity.sum(axis=1)
        df1 = pd.DataFrame(all_techs_capacity_peryear, columns=[scenario_name])
        Installed_capacity_data = pd.concat([Installed_capacity_data, df1], axis=1)
        df2 = pd.DataFrame(NPVNewPlants, columns=[scenario_name])
        NPVNewPlants_data = pd.concat([NPVNewPlants_data, df2], axis=1)

        voluntaryENS_data = pd.read_excel(path_to_results, sheet_name='voluntaryENS', header=[0,1], index_col=0)
        IRRS_yearly_data = pd.read_excel(path_to_results, sheet_name='yearlyIRRs', header=[0,1], index_col=0)
        consumers_data =  pd.read_excel(path_to_results, sheet_name='consumers', header=[0,1], index_col=0)
        AverageNPVpertechnology_data = pd.read_excel(path_to_results, sheet_name='AverageNPVpertechnology',   header=[0,1], index_col=0)
        Profits_with_loans_data = pd.read_excel(path_to_results, sheet_name='Profits',  header=[0,1], index_col=0)
        capacities_data = pd.read_excel(path_to_results, sheet_name='capacities',  header=[0,1], index_col=0)
        npvs_per_tech_per_MW = pd.DataFrame(npvs_per_tech_per_MW)
        multi_index = pd.MultiIndex.from_product([[scenario_name], npvs_per_tech_per_MW.columns], names=['scenario_name', "technology"])
        npvs_per_tech_per_MW.columns = multi_index
        AverageNPVpertechnology_data = pd.concat([AverageNPVpertechnology_data, npvs_per_tech_per_MW],  axis=1)

        multi_index = pd.MultiIndex.from_product([[scenario_name], all_techs_capacity_nozeroes.columns], names=['scenario_name', "technology"])
        all_techs_capacity_nozeroes.columns = multi_index
        capacities_data = pd.concat([capacities_data, all_techs_capacity_nozeroes],  axis=1)

        LS_pergroup= pd.DataFrame(load_shedded_per_group_MWh)
        multi_index = pd.MultiIndex.from_product([[scenario_name], LS_pergroup.columns], names=['scenario_name', "load_type"])
        LS_pergroup.columns = multi_index
        voluntaryENS_data = pd.concat([voluntaryENS_data, LS_pergroup],  axis=1)

        multi_index = pd.MultiIndex.from_product([[scenario_name], irrs_per_tech_per_year.columns], names=['scenario_name', "technology"])
        irrs_per_tech_per_year.columns = multi_index
        IRRS_yearly_data = pd.concat([IRRS_yearly_data, irrs_per_tech_per_year],  axis=1)

        multi_index = pd.MultiIndex.from_product([[scenario_name], profits_with_loans_all.columns], names=['scenario_name', "technology"])
        profits_with_loans_all.columns = multi_index
        Profits_with_loans_data = pd.concat([Profits_with_loans_data, profits_with_loans_all],  axis=1)
        #
        if subscribed_sorted.size>0:
                multi_index = pd.MultiIndex.from_product([[scenario_name], subscribed_sorted.columns], names=['scenario_name', None])
                subscribed_sorted.columns = multi_index
                consumers_data = pd.concat([consumers_data, subscribed_sorted],  axis=1)

        if calculate_capacity_mechanisms == True:
            clearing_price_capacity_market_data = pd.read_excel(path_to_results, sheet_name='CM_clearing_price',
                                                                index_col=0)
            capacity_market_capacity_data = pd.read_excel(path_to_results, sheet_name='CM_capacity', index_col=0)

            capacity_mechanisms_per_tech.at["scenario_name", :] = scenario_name
            last_row = capacity_mechanisms_per_tech.iloc[-1]
            df = capacity_mechanisms_per_tech.iloc[:-1]
            df = pd.concat([last_row.to_frame().T, df], ignore_index=True)
            capacity_market_capacity_data = pd.concat([capacity_market_capacity_data, df], axis=1)

        total_costs_capacity_market_data = pd.read_excel(path_to_results, sheet_name='CM_total_costs', index_col=0)
        if extended_lifetime_tech.size>0:
            lifeextension_data[scenario_name]  = extended_lifetime_tech["Extension"]
        Last_year_PDC_data[scenario_name] = electricity_prices[years_to_generate[-1]]
        CostRecovery_data[scenario_name] = cost_recovery
        LOL_data[scenario_name] = LOLE_per_group.T[["1"]].sum(axis =1) # involutary shedding comparison
        LOLvoluntary_data[scenario_name] = LOLE_per_group.T["2"] # volutary shedding comparison
        SupplyRatio_data[scenario_name] = supply_ratio
        Monthly_electricity_data[scenario_name] = monthly_electricity_price_grouped
        H2_production_data[scenario_name] = production_not_shedded_MWh["hydrogen_produced"]
        IndustrialHeat_data[scenario_name] = production_not_shedded_MWh["industrial_heat_demand"]
        Overall_NPV_data[scenario_name] = overall_NPV_per_technology.T # plants that were installed and decommissioned during simulation
        Overall_IRR_data[scenario_name] = overall_IRR_per_technology.T # plants that were installed and decommissioned during simulation
        ElectricityPrices_data[scenario_name] = average_electricity_price["wholesale price"]
        TotalSystemCosts_data[scenario_name] = DispatchSystemCostInEUR
        ENS_data[scenario_name] = load_shedded_per_group_MWh.sum(axis=1)
        Inflexible_load[scenario_name] = yearly_load.sum(axis=0)
        ShareRES_data[scenario_name] = share_RES
        Dismantled_capacity_data[scenario_name] = capacity_per_status.Decommissioned
        Commissioned_capacity_data[scenario_name] = capacity_per_status.InPipeline

        if calculate_capacity_mechanisms == True:
            total_costs_capacity_market_data[scenario_name] = total_costs_CM
            CRM_data[scenario_name]  = CM_price #= pd.concat([CRM_data, CM_price], ignore_index=True, axis=1)

            if reps.capacity_remuneration_mechanism == "strategic_reserve_ger":
                SR_data[scenario_name] = revenues_SR.values
                SRhours_data[scenario_name]  = total_SR_hours
            else:
                clearing_price_capacity_market_data[scenario_name] = CM_clearing_price

        if calculate_vres_support == True:
            VRES_data[scenario_name] = average_electricity_price['VRES support']
        last_year_operational_capacity_data[scenario_name] = all_techs_capacity.loc[years_to_generate[-1]].T
        print("last year " + str(years_to_generate[-1]))
        median_annual_production_data[scenario_name] = all_techs_generation_nozeroes.loc[years_to_generate[-1]].T

        with pd.ExcelWriter(path_to_results,
                            mode="a",
                            engine="openpyxl",
                            if_sheet_exists="overlay") as writer:
            costs_to_society_data.to_excel(writer, sheet_name='costs_to_society')
            costs_to_society4000_data.to_excel(writer, sheet_name='costs_to_society4000')
            social_welfare_data.to_excel(writer, sheet_name='social_welfare')
            Last_year_PDC_data.to_excel(writer, sheet_name="Last_year_pdc")
            Inflexible_load.to_excel(writer, sheet_name="Inflexible_load")
            CostRecovery_data.to_excel(writer, sheet_name='CostRecovery')
            LOL_data.to_excel(writer, sheet_name='LOL')
            LOLvoluntary_data.to_excel(writer, sheet_name='LOLvoluntary')
            ENS_data.to_excel(writer, sheet_name='ENS')
            voluntaryENS_data.to_excel(writer, sheet_name='voluntaryENS')
            SupplyRatio_data.to_excel(writer, sheet_name='SupplyRatio')
            capacities_data.to_excel(writer, sheet_name='capacities')
            ElectricityPrices_data.to_excel(writer, sheet_name='ElectricityPrices')
            TotalSystemCosts_data.to_excel(writer, sheet_name='TotalSystemCosts')
            Monthly_electricity_data.to_excel(writer, sheet_name='MonthlyElectricityPrices')
            NPVNewPlants_data.to_excel(writer, sheet_name='NPVNewPlants')
            AverageNPVpertechnology_data.to_excel(writer, sheet_name='AverageNPVpertechnology')
            Overall_NPV_data.to_excel(writer, sheet_name='overallNPV')
            Overall_IRR_data.to_excel(writer, sheet_name='overallIRR')
            IRRS_yearly_data.to_excel(writer, sheet_name='yearlyIRRs')
            Installed_capacity_data.to_excel(writer, sheet_name='InstalledCapacity')
            lifeextension_data.to_excel(writer, sheet_name='lifeextension')
            H2_production_data.to_excel(writer, sheet_name='H2Production')
            IndustrialHeat_data.to_excel(writer, sheet_name='IndustrialHeat')
            Commissioned_capacity_data.to_excel(writer, sheet_name='Invested')
            Dismantled_capacity_data.to_excel(writer, sheet_name='Dismantled')
            SRhours_data.to_excel(writer, sheet_name='SRhours')
            curtailment_data.to_excel(writer, sheet_name='VREScurtailed')
            Profits_with_loans_data.to_excel(writer, sheet_name='Profits')
            total_subscribed_consumers.to_excel(writer, sheet_name='subscribedCons')
            consumers_data.to_excel(writer, sheet_name='consumers')
            if calculate_capacity_mechanisms == True:
                CRM_data.to_excel(writer, sheet_name='CRM')
                clearing_price_capacity_market_data.to_excel(writer, sheet_name='CM_clearing_price')
                total_costs_capacity_market_data.to_excel(writer, sheet_name='CM_total_costs')
                capacity_market_capacity_data.to_excel(writer, sheet_name='CM_capacity')
                SR_data.to_excel(writer, sheet_name='SR')
            if calculate_vres_support == True:
                VRES_data.to_excel(writer, sheet_name='VRES')
            ShareRES_data.to_excel(writer, sheet_name='ShareRES')
            last_year_operational_capacity_data.to_excel(writer, sheet_name='last_year_capacity')
            median_annual_production_data.to_excel(writer, sheet_name='median_annual_production')
            writer.save()

    # section -----------------------------------------------------------------------------------------------Capacity Markets
    # # # #check extension of power plants.

    print('Showing plots...')
    plt.close('all')


def writeInfo(reps, path_to_plots, scenario_name):
    file = open(path_to_plots + "/info.txt", "w")
    number_of_power_plants = len(reps.power_plants)
    info = []
    print("Number of power plants " + str(number_of_power_plants))
    file.write("Number of power plants " + str(number_of_power_plants) + "\n")
    info.append("Number of power plants " + str(number_of_power_plants))

    print("Test_tick " + str(test_tick) + " Test tech " + str(test_tech))
    file.write("Test_tick " + str(test_tick) + " Test tech " + str(test_tech) + "\n")
    info.append("Test_tick " + str(test_tick) + " Test tech " + str(test_tech))
    print("pastTimeHorizon " + str(reps.pastTimeHorizon) + " start_tick_dismantling" + str(
        reps.start_dismantling_tick))
    file.write(
        "pastTimeHorizon " + str(reps.pastTimeHorizon) + " start_tick_dismantling " + str(
            reps.start_dismantling_tick))
    info.append("pastTimeHorizon " + str(reps.pastTimeHorizon) + "\n")
    info.append("start_tick_dismantling" + str(reps.start_dismantling_tick) + "\n")
    file.write("look ahead " + str(reps.lookAhead) + "\n")
    info.append("look ahead " + str(reps.lookAhead) + "\n")
    file.write("start_tick_fuel_trends " + str(reps.start_tick_fuel_trends) + "\n")
    info.append("start_tick_fuel_trends " + str(reps.start_tick_fuel_trends) + "\n")
    Strategic_operator = reps.get_strategic_reserve_operator(reps.country)

    file.write(
        "SR " + str(Strategic_operator.reservePriceSR) + " " + str(Strategic_operator.reserveVolumePercentSR) + "\n")
    info.append(
        "SR " + str(Strategic_operator.reservePriceSR) + " " + str(Strategic_operator.reserveVolumePercentSR) + "\n")
    file.write(json.dumps(Strategic_operator.list_of_plants_all))

    file.write("representative year " + str(reps.representative_year) + "\n")
    info.append("representative year " + str(reps.representative_year) + "\n")

    file.write("capacity mechanism " + str(reps.capacity_remuneration_mechanism) + "\n")
    info.append("capacity mechanism " + str(reps.capacity_remuneration_mechanism) + "\n")

    file.write("group power plants" + str(reps.groups_plants_per_installed_year) + "\n")
    info.append("group power plants" + str(reps.groups_plants_per_installed_year) + "\n")

    if reps.fix_fuel_prices_to_year != False:
        print("fix_prices_to_2020")
        file.write("fix_fuel_prices_to_year \n")
        info.append("fix_fuel_prices_to_year")

    if reps.fix_profiles_to_representative_year == True:
        print("fix_profiles_to_initial_year")
        file.write("fix_profiles_to_initial_year \n")
        info.append("fix_profiles_to_initial_year")
    else:
        print(reps.iteration_weather)
        file.write(str(reps.iteration_weather) + "\n")
        info.append(reps.iteration_weather)

    if reps.fix_demand_to_representative_year == True:
        print("fix_demand_to_initial_year")
        file.write("fix_demand_to_initial_year \n")
        info.append("fix_demand_to_initial_year")

    if reps.yearly_CO2_prices == True:
        print("yearly CO2 prices")
        file.write("yearly_CO2_prices \n")
        info.append("yearly_CO2_prices")
    if reps.install_at_look_ahead_year == True:
        print("install_at_look_ahead_year")
        file.write("install_at_look_ahead_year \n")
        info.append("install_at_look_ahead_year")
    if reps.Power_plants_from_year:
        print("Power_plants_from_year" + str(reps.Power_plants_from_year))
        file.write("Power_plants_from_year" + str(reps.Power_plants_from_year))
        info.append("Power_plants_from_year" + str(reps.Power_plants_from_year))

    if save_excel == True:
        path_to_results = os.path.join(os.getcwd(), "plots", "Scenarios", results_excel)
        InfoOriginal = pd.read_excel(path_to_results, sheet_name='Info', index_col=0)
        df2 = pd.DataFrame(info, columns=[scenario_name])
        Info = pd.concat([InfoOriginal, df2], axis=1)
        with pd.ExcelWriter(path_to_results,
                            mode="a",
                            engine="openpyxl",
                            if_sheet_exists="overlay") as writer:
            Info.to_excel(writer, sheet_name="Info")
            writer.save()

    for candidate in reps.candidatePowerPlants.values():
        print(candidate.name + " " + candidate.technology.name + " Tested: " + str(
            candidate.capacity) + " and to be installed: " + str(candidate.capacityTobeInstalled) + "\n")
        file.write(candidate.name + " " + candidate.technology.name + " Tested: " + str(
            candidate.capacity) + " and to be installed: " + str(candidate.capacityTobeInstalled) + "\n")
    file.close()


print('===== Start Generating Plots =====')


fuel_colors = {
    'CO2': "black",
    'biomethane': "green",
    'BiogasRetro': "green",
    "collectable_residues": "gray",
    'LNG': "darkgoldenrod",
    'hard_coal': "indianred",
    'oil': "gray",
    'heavy_oil': "gray",
    'light_oil': "lightsteelblue",
    "oil_shale": "mediumpurple",
    "Oil": "mediumpurple",
    'lignite': "darkgoldenrod",
    'natural_gas': "darkred",
    'Derived Gas': "darkred",
    "bioliquids": "lime",
    "electricity": "yellow",
    "hydrogen": "navy",
    "nuclear": "mediumorchid",
    "processing_residues": "mediumseagreen",
    "wood_pellets": "springgreen",
    "OTHER": "darkred"
}

AMIRIS_temporal_fuel = {
    'CO2': 93,
    'biomethane': 0,  # saved as Biogas
    "collectable_residues": 0,
    'LNG': 0,
    'hard_coal': 11,
    'heavy_oil': 37,
    'light_oil': 37,
    "oil_shale": 37,
    'lignite': 5,
    'natural_gas': 17,
    "bioliquids": 0,
    "electricity": 1,
    "hydrogen": 0,
    "nuclear": 2,
    "wood_pellets": 0,
}

SpecificCo2EmissionsInTperMWH = {
    'hard_coal': 0.34055972755,
    'heavy_oil': 0.26676,
    'lignite': 0.364,
    'natural_gas': 0.2019598384,
    "nuclear": 0,
    "collectable_residues": 0,
    'biomethane': 0,  # saved as Biogas
    "oil_shale": 0,
    'light_oil': 0,
    "wood_pellets": 0
}
vRES = ['PV_utility_systems', 'WTG_onshore', 'WTG_offshore', 'PV']

technology_colors = {
    'Biomass_CHP_wood_pellets_DH': "green",
    'Biofuel': "green",
    "Biomass_CHP_wood_pellets_PH": "greenyellow",
    'Hard Coal': "black",
    "Oil": "gray",
    'Lignite': "darkgoldenrod",
    'CCGT': "indianred",
    "CCS gas": "indianred",
    'OCGT': "gray",
    'Gas': "gray",
    'PV_utility_systems': "gold",
    "Solar PV large": "gold",
    "Solar CSP": "gold",
    'PV': "gold",
    'Solar PV rooftop': "khaki",
    'Wind Onshore': "cornflowerblue",
    "Wind Offshore": "navy",
    "central gas boiler": "black",
    "Nuclear": "mediumorchid",
    "Hydropower ROR": "aquamarine",
    'Hydro Reservoir': "darkcyan",
    "Hydropower": "darkcyan",
    "Lithium ion battery": "hotpink",
    "Lithium_ion_battery_charge": "hotpink",
    "Lithium ion battery 4": "pink",
    "PHS Discharge": "darkcyan",
    "CCGT_CHP_backpressure_DH": "orange",
    "CCGT_CHP_backpressure_PH": "orange",
    "CCS": "orange",
    "fuel_cell": "gold",
    "industry": "black",
    "electrolyzer": "gray",
    "hydrogen turbine": "darkred",
    "hydrogen CCGT": "darkred",
    "hydrogen OCGT": "indianred",
    "hydrogen CHP": "indianred",
    "hydrogen_combined_cycle": "coral",
    "hydrogen combined cycle": "coral"
}

technology_names = {
    'Biomass_CHP_wood_pellets_DH': "Biomass",
    "Biomass_CHP_wood_pellets_PH": "Biomass",
    'Hydropower_reservoir_medium': "Hydro",
    'PV_utility_systems': "PV utility",
    'PV_residential': "PV residential",
    'WTG_onshore': "Wind onshore",
    "WTG_offshore": "Wind offhore",
    "Lithium_ion_battery": "Lithium battery",
    "Lithium_ion_battery_charge": "Lithium battery charge",
    "Pumped_hydro": "Pumped hydro",
    "CCGT_CHP_backpressure_DH": "CCGT CHP",
    "hydrogen_turbine": "Hydrogen turbine",
}

def  plotting(SCENARIOS, results_excel, emlab_url, amiris_url, existing_scenario):
    global save_excel
    save_excel = False
    global scenario_name
    global calculate_hourly_shedders_new
    global calculate_monthly_generation
    global test_tick
    global test_tech
    global industrial_demand_as_flex_demand_with_cap
    global read_electricity_prices
    global calculate_investments
    global calculate_investments_per_iteration
    global calculate_profits_candidates_per_iteration
    global calculate_capacity_mechanisms
    global calculate_vres_support
    global electrolyzer_read
    global reps
    global path_to_plots
    global path_to_excel
    global write_titles
    global template_excel

    write_titles = False

    test_tick = 0
    # write None is no investment is expected,g
    test_tech = None  # None, 'Lithium_ion_battery'  # "hydrogen OCGT" #" #None #"WTG_offshore"   # "WTG_onshore" ##"CCGT"# "hydrogen_turbine"

    industrial_demand_as_flex_demand_with_cap = True
    read_electricity_prices = True  # write False if not wished to graph electricity prices"
    calculate_hourly_shedders_new = True
    calculate_monthly_generation = True  # !!!!!!!!!!!!!!For the new plots
    calculate_investments = True
    calculate_investments_per_iteration = False  # ProfitsC
    calculate_profits_candidates_per_iteration = False
    calculate_vres_support = False
    electrolyzer_read = True

    if save_excel == True:
        path_to_excel = os.path.join(os.getcwd(), "plots", "Scenarios", results_excel)
        template_excel = os.path.join(os.getcwd(), "plots", "Scenarios", "ScenariosComparisonTEMPLATE.xlsx")
        if not os.path.exists(path_to_excel):
            shutil.copy(template_excel, path_to_excel)

    for scenario_name in SCENARIOS:
        try:
            if scenario_name == "":
                raise Exception("Name needed")

            if read_electricity_prices == False:
                electricity_prices = None  # dont read if not necessary
                curtailed_res = None
                TotalAwardedPowerInMW = None

            if existing_scenario == False:
                print("Plots for NEW scenario  " + scenario_name)
                # use "Amiris" if this should be read
                spinedb_reader_writer = SpineDBReaderWriter("Amiris", emlab_url, amiris_url)
                reps = spinedb_reader_writer.read_db_and_create_repository("plotting")

                pre_name = reps.country + str(reps.end_simulation_year) + str(len(reps.power_plants))  + reps.capacity_remuneration_mechanism
                if reps.realistic_candidate_capacities_to_test == True:
                    pre_name = pre_name + "testRealC"
                if reps.realistic_candidate_capacities_tobe_installed == True:
                    pre_name = pre_name + "instalRealC"
                complete_name = pre_name + scenario_name

                if read_electricity_prices == True:
                    electricity_prices, curtailed_res, TotalAwardedPowerInMW = reading_electricity_prices(reps,
                                                                                                          os.path.join(os.path.dirname(os.getcwd()),'amiris_workflow\\output\\'),
                                                                                                          "none", existing_scenario)

            elif existing_scenario == True:
                print("Plots for EXISTING scenario " + scenario_name)
                first = "sqlite:///" + globalNames.scenarios_path
                emlab_sql = "\\EmlabDB.sqlite"
                amiris_sql = "\\AMIRIS db.sqlite"
                energy_exchange_url_sql = "\\energy exchange.sqlite"
                emlab_url = first + scenario_name + emlab_sql
                amiris_url = first + scenario_name + amiris_sql

                spinedb_reader_writer = SpineDBReaderWriter("Amiris", emlab_url, amiris_url)
                reps = spinedb_reader_writer.read_db_and_create_repository("plotting")
                folder_name = first + scenario_name

                if read_electricity_prices == True:
                    electricity_prices, curtailed_res, TotalAwardedPowerInMW = reading_electricity_prices(reps,
                                                                                                          "none",
                                                                                                          scenario_name, existing_scenario)
                complete_name = scenario_name
                splitname = complete_name.split("-")
                scenario_name = splitname[1]

            for p, power_plant in reps.power_plants.items():
                power_plant.specifyPowerPlantsInstalled(reps, False)

            print(reps.country + str(reps.end_simulation_year) + "_SD" + str(
                reps.start_dismantling_tick) + "_PH" + str(
                reps.pastTimeHorizon) + "_MI" + str(
                reps.maximum_investment_capacity_per_year) + "_" + reps.typeofProfitforPastHorizon + "_")
            path_to_plots = os.path.join(os.getcwd(), "plots", "Scenarios", complete_name)

            if not os.path.exists(path_to_plots):
                os.makedirs(path_to_plots)
            # plot_initial_power_plants(path_to_plots, "futureDecarbonizedNL") # other options are "extendedDE" extendedNL, groupedNL, groupedNLprePP

            writeInfo(reps, path_to_plots, scenario_name)

            generate_plots(reps, path_to_plots, electricity_prices, curtailed_res, TotalAwardedPowerInMW,
                           calculate_vres_support)

        except Exception as e:
            logging.error('Exception occurred: ' + str(e))
            raise
        finally:
            spinedb_reader_writer.db.close_connection()
            spinedb_reader_writer.amirisdb.close_connection()
            print("finished emlab")

if __name__ == '__main__':
    # SCENARIOS =   ["final3-EOM",'final3-EOM_inflexibleelectrolyzer',"final3-EOM_halfelectrolyzers","final3-EOM_halfFlexIndustry"]
    # SCENARIOS =  ["final3-EOM", "final3-CM", "final3-CM_VRES_BESS", "final3-CM_VRES_BESS_lowTV","final3-CM_endogen_lowTV"]
    # SCENARIOS =  ["final3-EOM", "final3-CM", "final3-CS","final3-SR"]
    # SCENARIOS =  ["final3-EOM", "final3-CM", "final3-CM_RO", "final3-CM_VRES_BESS", "final3-CM_endogen"]
    SCENARIOS =  ["test-test"]
    results_excel = "comparisonCM_ROandhighTV.xlsx"
    # results_excel = "comparisonCS9-noConsumersMemory.xlsx"
    existing_scenario = False
    if isinstance(SCENARIOS, (list, tuple)):
        pass
    else:
        raise Exception

    plotting(SCENARIOS, results_excel, sys.argv[1], sys.argv[2], existing_scenario)
    print('===== End Generating Plots =====')

# write the name of the existing scenario or the new scenario
# The short name from the scenario will start from "-"


# amirisdb = SpineDB(sys.argv[2])
# db_amirisdata = amirisdb.export_data()
# object_parameter_values = db_amirisdata['object_parameter_values']
# plot_decommissions(annual_decommissioned_capacity, years_to_generate, path_to_plots, colors_unique_techs)

# plot_annual_operational_capacity(last_year_operational_capacity, path_to_plots, colors_unique_techs)
# plot_annual_to_be_decommissioned_capacity(last_year_to_be_decommissioned_capacity, years_to_generate, path_to_plots,
#                                           colors_unique_techs)

#
# def plot_annual_to_be_decommissioned_capacity(plot_annual_to_be_decommissioned_capacity, years_to_generate,
#                                               path_to_plots, colors):
#     fig4, axs5 = plt.subplots()
#     axs4 = plot_annual_to_be_decommissioned_capacity.plot.bar(stacked=True, rot=0, color=colors, grid=True,
#                                                               legend=False)
#     axs4.set_axisbelow(True)
#     axs4.set_xlabel('Years', fontsize='medium')
#     axs4.set_ylabel('Capacity (MW)', fontsize='medium')
#     # plt.ylim([-4.3e5, 5.5e5])
#     axs4.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
#     axs4.set_title('Capacity per Technology to be decommissioned')\
#     # fig4 = a.get_figure()
#     fig4.savefig(path_to_plots + '/' + 'Capacity to be decommissioned.png', bbox_inches='tight', dpi=300)
#     plt.show()

# def reading_electricity_prices(raw_results_url, reps):
#     db_raw = SpineDB(raw_results_url)
#     db_electricity_prices = db_raw.query_object_parameter_values_by_object_class('Results')
#     db_raw.close_connection()
#     years_to_generate = list(range(reps.start_simulation_year, reps.current_year + 1))
#     globalNames.amiris_ouput_path
#     yearly_electricity_prices = pd.DataFrame()
#     for yearly in db_electricity_prices:
#         year = int(yearly["object_name"])
#         electricity_prices = yearly['parameter_value'].to_dict()
#         a = pd.Series(i[1] for i in electricity_prices["data"])
#         yearly_electricity_prices.at[:, year] = a
#     return yearly_electricity_prices

# this is already graphed in plot_expected_candidate_profits_real_profits
# plot_candidate_profits_per_iteration(candidates_profits_per_iteration, path_to_plots,
#                                      colors_unique_candidates)
