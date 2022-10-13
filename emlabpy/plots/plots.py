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
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
from util.spinedb_reader_writer import *
from util.spinedb import SpineDB
from copy import deepcopy
from matplotlib.offsetbox import AnchoredText
import numpy as np

logging.basicConfig(level=logging.ERROR)


def plot_investments_and_NPV_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration,
                                           future_year, path_to_plots, colors_unique_candidates):
    print('investments and NPV')
    fig1, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    candidate_plants_project_value.plot(ax=ax1, color=colors_unique_candidates)
    installed_capacity_per_iteration.plot(ax=ax2, color=colors_unique_candidates, linestyle='None', marker='o')
    ax1.set_xlabel('Iterations', fontsize='medium')
    ax1.set_ylabel('NPV [Eur] (lines)', fontsize='medium')
    ax2.set_ylabel('Investments MW (dotted)', fontsize='medium')
    ax1.set_title('Investments and NPV per iterations for future year ' + str(future_year))

    ax2.set_ylim(bottom=2) # void showing zero investments

    ax1.legend(candidate_plants_project_value.columns.values.tolist(), fontsize='medium', loc='upper left',
               bbox_to_anchor=(1.2, 1.1))
    ax2.legend(installed_capacity_per_iteration.columns.values.tolist(), fontsize='medium', loc='upper left',
               bbox_to_anchor=(1.2, 0.5))
    fig1.savefig(path_to_plots + '/' + 'Candidate power plants NPV and Investment decisions' + str(
        future_year) + '.png', bbox_inches='tight', dpi=300)


def plot_candidate_profits_per_iteration(profits_per_iteration, path_to_plots, test_tick, colors_unique_candidates):
    print('profits per iteration')
    axs13 = profits_per_iteration.plot(color=colors_unique_candidates)
    axs13.set_axisbelow(True)
    plt.xlabel('iterations', fontsize='medium')
    plt.ylabel('Profits Eur', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs13.set_title('Profits candidates in ' + str(test_tick))
    fig13 = axs13.get_figure()
    fig13.savefig(path_to_plots + '/' + 'Profits Candidates in ' + str(test_tick) + '.png', bbox_inches='tight',
                  dpi=300)


def plot_decommissions(annual_decommissioned_capacity, years_to_generate, path_to_plots, colors):
    print('Create decommissioning plot')
    fig5, axs5 = plt.subplots()
    axs5 = annual_decommissioned_capacity.plot.bar(stacked=True, rot=0, color=colors, grid=True, legend=False)
    axs5.set_axisbelow(True)
    axs5.set_xlabel('Years', fontsize='medium')
    for label in axs5.get_xticklabels(which='major'):
        label.set(rotation=50, horizontalalignment='right')
    axs5.set_ylabel('Capacity (MW)', fontsize='medium')
    axs5.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs5.set_title('Dismantled Capacity per Technology')
    fig5 = axs5.get_figure()
    fig5.savefig(path_to_plots + '/' + 'Dismantled.png', bbox_inches='tight', dpi=300)
    plt.show()


def plot_investments(annual_installed_capacity, annual_commissioned, annual_decommissioned_capacity,
                     path_to_plots, colors):
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
    axs6[2].set_ylabel('Decommissioned MW', fontsize='small')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.5))
    axs6[0].set_title('Investments by decision year (up) and by commissioning year (down) Maximum ' +
                      str(reps.maximum_investment_capacity_per_year / 1000) + 'GW')
    fig6.savefig(path_to_plots + '/' + 'Capacity Investments.png', bbox_inches='tight', dpi=300)


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


def plot_revenues_per_iteration_for_one_tech(all_future_operational_profit, tech_name, path_to_plots, test_tick):
    plt.figure()
    axs11 = all_future_operational_profit.plot()
    axs11.set_axisbelow(True)
    plt.xlabel('Iterations', fontsize='medium')
    plt.ylabel('Revenues - Operational Costs [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1))
    axs11.set_title('Expected future operational (wholesale market) profits in tick '
                    + str(test_tick) + ' \n and technology ' + tech_name )
    axs11.annotate('legend = age, capacity, efficiency',
                   xy=(1, 1), xycoords='figure fraction',
                   horizontalalignment='right', verticalalignment='top',
                   fontsize='small')
    fig11 = axs11.get_figure()

    fig11.savefig(
        path_to_plots + '/' + ' Expected future profit ' + str(
            test_tick) + ' ' + tech_name + '.png',
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
    fig15.savefig(path_to_plots + '/' + 'Average Technology Revenues per iteration ' + str(first_year) + '.png',
                  bbox_inches='tight', dpi=300)


def plot_future_fuel_prices(future_fuel_prices, path_to_plots):
    plt.figure()
    axs12 = future_fuel_prices.plot()
    axs12.set_axisbelow(True)
    plt.xlabel('Year', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs12.set_title('Expecetd future fuel prices per year (4 years ahead)')
    fig12 = axs12.get_figure()
    fig12.savefig(path_to_plots + '/' + 'Future Fuel prices per year.png', bbox_inches='tight', dpi=300)


def plot_screening_curve(yearly_costs, path_to_plots, test_year, colors_unique_techs):
    axs13 = yearly_costs.plot(color=colors_unique_techs)
    axs13.set_axisbelow(True)
    axs13.annotate('annual fixed costs + (variable cost + fuel costs + CO2 costs) hours /efficiency',
                   xy=(.025, 1), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='top',
                   fontsize='medium')
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs13.set_title('Screening curve in year ' + str(test_year))
    fig13 = axs13.get_figure()
    fig13.savefig(path_to_plots + '/' + 'Screening curve (with CO2) ' + str(test_year) + '.png', bbox_inches='tight',
                  dpi=300)


def plot_screening_curve_candidates(yearly_costs_candidates, path_to_plots, future_year, colors_unique_candidates):
    axs14 = yearly_costs_candidates.plot(color=colors_unique_candidates)
    axs14.set_axisbelow(True)
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs14.set_title('Screening curve candidate technologies for year ' + str(future_year))
    fig14 = axs14.get_figure()
    fig14.savefig(
        path_to_plots + '/' + 'Screening curve candidate technologies (with CO2) ' + str(future_year) + '.png',
        bbox_inches='tight', dpi=300)


def plot_CM_revenues(CM_revenues_per_technology, accepted_pp_per_technology, capacity_mechanisms_per_tech,
                     CM_clearing_price, total_costs_CM, ran_capacity_market, path_to_plots, colors_unique_techs):
    # df.plot(x='Team', kind='bar', stacked=True,
    axs26 = accepted_pp_per_technology.plot(kind='bar', stacked=True, color=colors_unique_techs)
    axs26.set_axisbelow(True)
    plt.xlabel('tick', fontsize='medium')
    plt.ylabel('Number awarded', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs26.set_title('Capacity Mechanism awarded plants')
    fig26 = axs26.get_figure()
    fig26.savefig(path_to_plots + '/' + 'Capacity Mechanisms awarded plants.png', bbox_inches='tight', dpi=300)
    # the CM revenues per technology are retrieved from the financial results
    axs15 = CM_revenues_per_technology.plot(kind='bar', stacked=True, color=colors_unique_techs)
    axs15.set_axisbelow(True)
    plt.xlabel('tick', fontsize='medium')
    plt.ylabel('Revenues CM [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs15.set_title('Capacity Mechanisms revenues per technology')
    fig15 = axs15.get_figure()
    fig15.savefig(path_to_plots + '/' + 'Capacity Mechanisms revenues per technology.png', bbox_inches='tight', dpi=300)

    axs27 = capacity_mechanisms_per_tech.plot(kind='bar', stacked=True, color=colors_unique_techs)
    axs27.set_axisbelow(True)
    plt.xlabel('tick', fontsize='medium')
    plt.ylabel('Awarded Capacity [MW]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs27.set_title('Capacity Mechanism capacity per technology')
    fig27 = axs27.get_figure()
    fig27.savefig(path_to_plots + '/' + 'Capacity Mechanism capacity per technology.png', bbox_inches='tight', dpi=300)

    if ran_capacity_market == True:
        axs28 = CM_clearing_price.plot()
        axs28.set_axisbelow(True)
        plt.xlabel('Simulation year', fontsize='medium')
        plt.ylabel('CM clearing price [Eur/MW]', fontsize='medium')
        plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
        plt.grid()
        axs28.set_title('Capacity Mechanism clearing price')
        fig28 = axs28.get_figure()
        fig28.savefig(path_to_plots + '/' + 'Capacity Mechanism clearing price.png', bbox_inches='tight', dpi=300)

    axs29 = total_costs_CM.plot()
    axs29.set_axisbelow(True)
    plt.xlabel('tick', fontsize='medium')
    plt.ylabel('total costs [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs29.set_title('Capacity Mechanism total costs')
    fig29 = axs29.get_figure()
    fig29.savefig(path_to_plots + '/' + 'Capacity Mechanism total costs.png', bbox_inches='tight', dpi=300)


def plot_irrs_and_npv_per_tech_per_year(irrs_per_tech_per_year, npvs_per_tech_per_MW, path_to_plots, colors):
    # irrs_per_tech_per_year.drop("PV_utility_systems",  axis=1,inplace=True)
    # irrs_per_tech_per_year.drop("WTG_onshore", axis=1, inplace=True)
    axs16 = irrs_per_tech_per_year.plot(color=colors)
    axs16.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('IRR %', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs16.set_title('IRRs')
    # plt.ylim(-60,20)
    fig16 = axs16.get_figure()
    fig16.savefig(path_to_plots + '/' + 'IRRs per year per technology.png', bbox_inches='tight', dpi=300)

    axs27 = npvs_per_tech_per_MW.plot(color=colors)
    axs27.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('EUR/MW', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs27.set_title('Average NPVs per capacity')
    fig27 = axs27.get_figure()
    fig27.savefig(path_to_plots + '/' + 'NPVs per capacity per technology.png', bbox_inches='tight', dpi=300)


def plot_total_profits_per_tech_per_year(average_profits_per_tech_per_year, path_to_plots, colors):
    # CM revenues + revenues - variable costs - fixed costs
    axs25 = average_profits_per_tech_per_year.plot(color=colors)
    axs25.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('operational profits [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs25.annotate('Annual profits = revenues + CM revenues - variable costs - fixed costs',
                   xy=(0, 0), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='bottom',
                   fontsize='medium')
    axs25.set_title('Average Profits per technology')
    fig25 = axs25.get_figure()
    fig25.savefig(path_to_plots + '/' + 'Operational profits, average per year per technology.png', bbox_inches='tight',
                  dpi=300)


def plot_profits_for_tech_per_year(new_pp_profits_for_tech, test_tech, path_to_plots, colors):
    axs26 = new_pp_profits_for_tech.plot(color=colors)
    axs26.set_axisbelow(True)
    plt.xlabel('Simulation years', fontsize='medium')
    plt.ylabel('operational profits [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs26.set_title('Operational profits per year for ' + test_tech)
    axs26.annotate('Annual profits = revenues + CM revenues - variable costs - fixed costs',
                   xy=(0, 1), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='top',
                   fontsize='medium')
    fig26 = axs26.get_figure()
    fig26.savefig(path_to_plots + '/' + 'Operational profits per year for ' + test_tech + '.png', bbox_inches='tight',
                  dpi=300)


def plot_installed_capacity(all_techs_capacity, path_to_plots, colors_unique_techs):
    print('plotting installed Capacity per technology ')
    axs17 = all_techs_capacity.plot.area(color=colors_unique_techs)
    axs17.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Installed Capacity [MW]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs17.set_title('Installed Capacity')
    fig17 = axs17.get_figure()
    fig17.savefig(path_to_plots + '/' + 'Annual installed Capacity per technology.png', bbox_inches='tight', dpi=300)


def plot_capacity_factor(all_techs_capacity_factor, path_to_plots, colors_unique_techs):
    axs23 = all_techs_capacity_factor.plot(color=colors_unique_techs)
    axs23.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity factor [%]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs23.set_title('Capacity factor (production/capacity*8760)')
    fig23 = axs23.get_figure()
    fig23.savefig(path_to_plots + '/' + 'All technologies capacity factor new.png', bbox_inches='tight', dpi=300)


def plot_annual_generation(all_techs_generation, path_to_plots, colors_unique_techs):
    axs18 = all_techs_generation.plot.area(color=colors_unique_techs)
    axs18.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Annual Generation [MWh]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs18.set_title('Annual Generation')
    fig18 = axs18.get_figure()
    fig18.savefig(path_to_plots + '/' + 'Annual generation per technology.png', bbox_inches='tight', dpi=300)


def plot_supply_ratio(supply_ratio, residual_load, path_to_plots):
    axs19 = supply_ratio.plot()
    axs19.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('peak demand  / Total controllable capacity', fontsize='medium')
    axs19.set_title('Supply ratio')
    fig19 = axs19.get_figure()
    fig19.savefig(path_to_plots + '/' + 'Supply ratio.png', bbox_inches='tight', dpi=300)

    axs19.annotate("controllable capacity / peak load",
                   xy=(0, 0), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='bottom',
                   fontsize='small')
    fig20, axs20 = plt.subplots()
    rl_sorted = residual_load.sort_values(by=residual_load.columns[0], ascending=False, ignore_index=True)
    load = reps.get_hourly_demand_by_country(reps.country)[1].sort_values(ascending=False, ignore_index=True)
    rl_sorted.plot(ax=axs20, label="residual_load")
    load.plot(ax=axs20, label="load")
    axs20.set_axisbelow(True)
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('load MW', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs20.set_title('Load and residual load')
    fig20 = axs20.get_figure()
    fig20.savefig(path_to_plots + '/' + 'Load and residual load.png', bbox_inches='tight', dpi=300)


def plot_shortages(shortages, path_to_plots):
    axs20 = shortages.plot()
    axs20.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Number of shortage hours', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs20.set_title('Number of shortages')
    fig20 = axs20.get_figure()
    fig20.savefig(path_to_plots + '/' + 'Shortages.png', bbox_inches='tight', dpi=300)


def plot_costs_to_society(total_electricity_price, path_to_plots):
    axs30 = total_electricity_price.plot()
    axs30.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Total price', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs30.set_title('Total costs to society')
    fig30 = axs30.get_figure()
    fig30.savefig(path_to_plots + '/' + 'Costs to society.png', bbox_inches='tight', dpi=300)


def plot_market_values_generation(all_techs_capacity, path_to_plots, colors_unique_techs):
    # these market values only include plants if they have been dispatched
    axs21 = all_techs_capacity.plot(color=colors_unique_techs)
    axs21.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Market value (Euro/MWh)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs21.set_title('Market values (Market revenues / Production)')
    fig21 = axs21.get_figure()
    fig21.savefig(path_to_plots + '/' + 'Market values per technology.png', bbox_inches='tight', dpi=300)


def plot_yearly_average_electricity_prices(electricity_price, path_to_plots):
    axs22 = electricity_price.plot()
    axs22.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Market price (Eur/MWh)', fontsize='medium')
    #plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs22.set_title('Average yearly electricity prices')
    fig22 = axs22.get_figure()
    fig22.savefig(path_to_plots + '/' + 'Electricity prices.png', bbox_inches='tight', dpi=300)


def plot_hourly_electricity_prices(electricity_prices, path_to_plots):
    axs24 = electricity_prices.plot()
    axs24.set_axisbelow(True)
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Wholesale market price (Eur/MWh)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    for label in axs24.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')
    axs24.set_title('hourly electricity prices')
    fig24 = axs24.get_figure()
    fig24.savefig(path_to_plots + '/' + 'Hourly Electricity prices.png', bbox_inches='tight', dpi=300)


def plot_hourly_electricity_prices_boxplot(electricity_prices, path_to_plots):
    axs25 = sns.boxplot(data=electricity_prices)
    plt.xlabel('hours', fontsize='medium')
    plt.ylabel('Wholesale market price (Eur/MWh)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs25.set_title('Hourly electricity prices')
    fig25 = axs25.get_figure()
    fig25.savefig(path_to_plots + '/' + 'Hourly Electricity prices boxplot.png', bbox_inches='tight', dpi=300)


def plot_cash_flows(cash_flows, new_plants_loans, path_to_plots):
    axs29 = cash_flows.plot.area()
    axs29.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Cash [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs29.set_title('Cash Flow Energy Producer')
    fig29 = axs29.get_figure()
    fig29.savefig(path_to_plots + '/' + 'Cash Flows.png', bbox_inches='tight', dpi=300)

    # axs30 = new_plants_loans.plot(y="Downpayments new plants", kind="area")
    axs30 = new_plants_loans.plot.area()
    axs30.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Cash [Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs30.set_title('Downpayments Energy Producer')
    fig30 = axs30.get_figure()
    fig30.savefig(path_to_plots + '/' + 'Cash Flows Downpayments.png', bbox_inches='tight', dpi=300)
    #
    # axs32 = total_costs.plot()
    # axs32.set_axisbelow(True)
    # plt.xlabel('Years', fontsize='medium')
    # plt.ylabel('Cash [Eur]', fontsize='medium')
    # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    # axs32.set_title('Total Profits (with loans)')
    # fig32 = axs32.get_figure()
    # fig32.savefig(path_to_plots + '/' + 'Total Profits.png', bbox_inches='tight', dpi=300)


def plot_cost_recovery(cost_recovery, path_to_plots):
    axs33 = cost_recovery.plot()
    axs33.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('%', fontsize='medium')
    #plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 0.9))
    axs33.set_title('Cost recovery ')
    axs33.annotate('(Revenues/Costs) Include Capacity Mechanisms',
                   xy=(1, 1.1), xycoords='figure fraction',
                   horizontalalignment='right', verticalalignment='bottom',
                   fontsize='small')
    fig33 = axs33.get_figure()
    fig33.savefig(path_to_plots + '/' + 'Cost recovery.png', bbox_inches='tight', dpi=300)


def plot_npv_new_plants(npvs_per_year_new_plants_all, irrs_per_year_new_plants_all, candidate_plants_project_value, test_tech, test_year, test_tick,
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
    axs30.set_title('IRR new plants')
    axs30.annotate('legend = name, capacity, age',
                   xy=(0, 1), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='bottom',
                   fontsize='small')
    fig30.savefig(path_to_plots + '/' + 'IRR new plants.png', bbox_inches='tight', dpi=300)

    axs29 = test_irrs.plot()
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('[Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs29.set_title('IRR new plants for tech ' + test_tech + '(name, capacity, age)')
    fig29 = axs29.get_figure()
    fig29.savefig(path_to_plots + '/' + 'IRR new plants of tech ' + test_tech + ' .png', bbox_inches='tight', dpi=300)

    fig31, axs31 = plt.subplots()
    # key gives the group name (i.e. category), data gives the actual values
    for key, data in npvs_per_year_new_plants_all.items():
        if data.size > 0:
            data.plot(ax=axs31, label=key, color=technology_colors[key])
        if key == test_tech:
            test_npvs = data
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('[Eur]', fontsize='medium')
    plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(1, 1.1), ncol=5)
    axs31.set_title('NPV new plants')
    fig31.savefig(path_to_plots + '/' + 'NPV new plants.png', bbox_inches='tight', dpi=300)

    axs32 = test_npvs.plot()
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('[Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs32.set_title('NPV new plants for tech ' + test_tech + '(name, capacity, age)')
    fig32 = axs32.get_figure()
    fig32.savefig(path_to_plots + '/' + 'NPV new plants of tech ' + test_tech + ' .png', bbox_inches='tight', dpi=300)


    pp_installed_in_test_year = []
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
    candidate_plants_project_value[test_tech].plot(ax=axs33, label="Expected in year " + str(future_year))
    test_npvs[pp_installed_in_test_year].iloc[installed_tick].plot(ax=axs33,
                                                                   label="Reality in year " + str(installed_year))

    plt.ylabel('[Eur]', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    for label in axs33.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')

    axs33.annotate('ticks = name, capacity, age',
                   xy=(0.1, 0), xycoords='figure fraction',
                   horizontalalignment='right', verticalalignment='bottom',
                   fontsize='medium')
    axs33.set_title('NPV new plants for tech ' + test_tech)
    fig33.savefig(path_to_plots + '/' + 'NPV expected vs reality ' + test_tech + ' .png', bbox_inches='tight', dpi=300)


def plot_initial_power_plants(path_to_plots, sheetname):
    import seaborn as sns
    sns.set_theme(style="white")
    # pfad = r"C:\Users\isanchezjimene\Documents\TraderesCode\toolbox-amiris-emlab\data\Power_plants.xlsx"
    df = pd.read_excel(globalNames.power_plants_path,
                       sheet_name=sheetname)
    fig1 = sns.relplot(x="Age", y="Efficiency", hue="Technology", size="Capacity",
                       sizes=(40, 400), alpha=.5, palette="muted",
                       height=6, data=df)
    fig1.savefig(path_to_plots + '/' + 'Initial_power_plants.png', bbox_inches='tight', dpi=300)


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
    initial_power_plants = pd.DataFrame(columns=unique_technologies, index=years_to_generate_and_build).fillna(0)
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
            if pp.age + pp.dismantleTime > (reps.current_year - reps.start_simulation_year):
                initial_power_plants.loc[:, pp.technology.name] += pp.capacity

        elif pp.age > (reps.current_year - reps.start_simulation_year):
            initial_power_plants.loc[:, pp.technology.name] += pp.capacity
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

    decommissioned = np.cumsum(annual_decommissioned_capacity.values, axis=0)
    commissioned = np.cumsum(annual_commissioned_capacity.values, axis=0)
    all_techs_capacity = np.subtract(commissioned, decommissioned)
    all_techs_capacity = initial_power_plants.add(all_techs_capacity, axis=0)

    return initial_power_plants, annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_commissioned_capacity, \
           all_techs_capacity, last_year_in_pipeline, last_year_decommissioned, \
           last_year_operational_capacity, last_year_to_be_decommissioned_capacity, \
           last_year_strategic_reserve_capacity, number_per_status, number_per_status_last_year


def prepare_capacity_per_iteration(future_year, reps, unique_candidate_power_plants):
    max_iteration = 0
    # preparing empty df

    for name, investment in reps.investments.items():
        if str(future_year) in investment.project_value_year.keys():
            if len(investment.project_value_year[str(future_year)]) > max_iteration:
                max_iteration = len(investment.project_value_year[str(future_year)])
                # for i in investment.project_value_year[str(future_year)]:
                #
                #     max_iteration += len(i)

    df_zeros = np.zeros(shape=(max_iteration, len(unique_candidate_power_plants)))
    candidate_plants_project_value = pd.DataFrame(df_zeros, columns=unique_candidate_power_plants)
    # preparing NPV per iteration
    for name, investment in reps.investments.items():
        if len(investment.project_value_year) > 0:
            if str(future_year) in investment.project_value_year.keys():
                candidate_plants_project_value[reps.candidatePowerPlants[name].technology.name] = \
                    pd.Series(dict(investment.project_value_year[str(future_year)]))

    # preparing investments per iteration

    installed_capacity_per_iteration = pd.DataFrame(index=list(range(0, max_iteration)),
                                                    columns=unique_candidate_power_plants).fillna(0)

    for invest_name, investment in reps.investmentDecisions.items():
        if len(investment.invested_in_iteration) > 0:
            if str(future_year) in investment.invested_in_iteration.keys():
                index_invested_iteration = list(map(int, investment.invested_in_iteration[str(future_year)]))
                # print("name ", invest_name)
                # print(index_invested_iteration)
                # print(reps.candidatePowerPlants[invest_name].technology.name)
                # print(reps.candidatePowerPlants[invest_name].capacityTobeInstalled)
                installed_capacity_per_iteration.loc[
                    index_invested_iteration, reps.candidatePowerPlants[invest_name].technology.name] = \
                    reps.candidatePowerPlants[invest_name].capacityTobeInstalled
    return installed_capacity_per_iteration, candidate_plants_project_value


def prepare_profits_candidates_per_iteration(reps, test_tick):
    profits = reps.get_profits_per_tick(test_tick)
    #  profits_per_iteration = pd.DataFrame(index=profits.profits_per_iteration_names_candidates[test_tick]).fillna(0)
    # ser = pd.Series(data2, index=list(profits.profits_per_iteration_candidates.items()))
    profits_per_iteration = pd.DataFrame()
    for iteration, profit_per_iteration in list(profits.profits_per_iteration_candidates.items()):
        temporal = pd.Series(profit_per_iteration, index=profits.profits_per_iteration_names_candidates[iteration])
        profits_per_iteration[iteration] = temporal
    tech = []
    for pp in profits_per_iteration.index.values:
        tech.append(reps.candidatePowerPlants[pp].technology.name)
    profits_per_iteration["tech"] = tech
    profits_per_iteration = np.transpose(profits_per_iteration)
    profits_per_iteration.columns = profits_per_iteration.iloc[-1]
    profits_per_iteration.drop("tech", inplace=True)
    profits_per_iteration.index.map(int)
    profits_per_iteration.sort_index(ascending=True, inplace=True)
    return profits_per_iteration


def prepare_revenues_per_iteration(reps, tick, test_tech):
    profits = reps.get_profits_per_tick(tick)
    future_operational_profit_per_iteration = pd.DataFrame()
    future_operational_profit_per_iteration_with_age = pd.DataFrame()
    for iteration, profit_per_iteration in list(profits.profits_per_iteration.items()):
        temporal = pd.DataFrame(profit_per_iteration, index=profits.profits_per_iteration_names[iteration],
                                columns=[int(iteration)])
        future_operational_profit_per_iteration = future_operational_profit_per_iteration.join(temporal, how='right')
        future_operational_profit_per_iteration_with_age = future_operational_profit_per_iteration_with_age.join(
            temporal, how='right')
    # adding technology name
    tech = []
    age = []
    capacity = []
    efficiency = []
    for pp in future_operational_profit_per_iteration.index.values:
        tech.append(reps.power_plants[pp].technology.name)
        age.append(reps.power_plants[pp].age)
        capacity.append(reps.power_plants[pp].capacity)
        efficiency.append(reps.power_plants[pp].actualEfficiency)
    future_operational_profit_per_iteration["tech"] = tech
    grouped_revenues = future_operational_profit_per_iteration.groupby('tech').mean()
    sorted_average_revenues_per_iteration_test_tick = grouped_revenues.T.sort_index()

    tech_age = list(zip(age, capacity, efficiency))
    future_operational_profit_per_iteration_with_age["tech"] = tech
    future_operational_profit_per_iteration_with_age["tech-age"] = tech_age
    expected_future_operational_profit = future_operational_profit_per_iteration_with_age.loc[
        future_operational_profit_per_iteration_with_age.tech == test_tech]
    expected_future_operational_profit.drop(["tech"], axis=1, inplace=True)
    all_future_operational_profit = expected_future_operational_profit.set_index('tech-age').T.sort_index(level=0)
    return sorted_average_revenues_per_iteration_test_tick, all_future_operational_profit


def prepare_operational_profit_per_year_per_tech(reps, unique_technologies, simulation_years, test_tech):
    # CM revenues + revenues - variable costs - fixed costs
    average_profits_per_tech_per_year = pd.DataFrame(index=simulation_years).fillna(0)
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
                profits_per_year[plant.name] = profits_per_plant
        numeric = profits_per_year.values.astype('float64')
        average_profits_per_tech_per_year[technology_name] = np.nanmean(numeric, axis=1)
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
            profits_for_test_tech_per_year = pd.DataFrame(numeric, columns=info, index=simulation_years)
            if len(chosen) == 0:
                raise Exception("choose other test technology")
            new_pp_profits_for_tech = profits_for_test_tech_per_year[chosen]
    return average_profits_per_tech_per_year, new_pp_profits_for_tech


def prepare_cash_per_agent(reps, simulation_ticks):
    # the cash includes the loans of installed power plants
    cash_per_agent = pd.DataFrame(index=simulation_ticks).fillna(0)
    new_plants_loans = pd.DataFrame(index=simulation_ticks).fillna(0)
    all_info = reps.getCashFlowsForEnergyProducer(reps.agent)
    cash_per_agent["Wholesale market"] = all_info.CF_ELECTRICITY_SPOT
    cash_per_agent["Commodities"] = all_info.CF_COMMODITY
    cash_per_agent["Fixed costs"] = all_info.CF_FIXEDOMCOST
    cash_per_agent["Capacity Market"] = all_info.CF_CAPMARKETPAYMENT
    cash_per_agent["Loans"] = all_info.CF_LOAN
    cash_per_agent["Loans new plants"] = all_info.CF_LOAN_NEW_PLANTS
    cash_per_agent["Downpayments"] = all_info.CF_DOWNPAYMENT
    cash_per_agent["Downpayments new plants"] = all_info.CF_DOWNPAYMENT_NEW_PLANTS

    new_plants_loans["Downpayments new plants"] = all_info.CF_DOWNPAYMENT_NEW_PLANTS
    new_plants_loans["Loans new plants"] = all_info.CF_LOAN_NEW_PLANTS
    total_costs = cash_per_agent.sum(axis=1)
    cost_recovery = all_info.CF_ELECTRICITY_SPOT / -(
            all_info.CF_COMMODITY + all_info.CF_LOAN + all_info.CF_FIXEDOMCOST + all_info.CF_DOWNPAYMENT +
            all_info.CF_CAPMARKETPAYMENT + all_info.CF_DOWNPAYMENT_NEW_PLANTS + all_info.CF_LOAN_NEW_PLANTS
    )
    cr = cost_recovery.sort_index()
    return cash_per_agent, total_costs, cr, new_plants_loans


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


def prepare_irr_and_npv_per_technology_per_year(reps, unique_technologies, simulation_years):
    irrs_per_tech_per_year = pd.DataFrame(index=simulation_years).fillna(0)
    npvs_per_tech_per_MW = pd.DataFrame(index=simulation_years).fillna(0)
    npvs_per_year_new_plants_all = dict()
    irrs_per_year_new_plants_all  = dict()
    for technology_name in unique_technologies:
        powerplants_per_tech = reps.get_power_plants_by_technology(technology_name)
        irrs_per_year = pd.DataFrame(index=simulation_years).fillna(0)
        npvs_per_year = pd.DataFrame(index=simulation_years).fillna(0)
        npvs_per_year_new_plants = pd.DataFrame(index=simulation_years).fillna(0)
        irrs_per_year_new_plants = pd.DataFrame(index=simulation_years).fillna(0)
        for plant in powerplants_per_tech:
            irr_per_plant = reps.get_irrs_for_plant(plant.name)
            if irr_per_plant is None:
                pass
                # print("power plant in pipeline", plant.name, plant.id)
            else:
                npv_per_plant = reps.get_npvs_for_plant(plant.name) / plant.capacity
                irrs_per_year[plant.name] = irr_per_plant
                npvs_per_year[plant.name] = npv_per_plant
                if int(plant.name) > 10000:
                    info = plant.name + " " + str(plant.capacity) + " MW " + str(plant.age)
                    npvs_per_year_new_plants[info] = npv_per_plant
                    irrs_per_year_new_plants[info] = irr_per_plant

        irrs_per_year_new_plants.replace(to_replace=-100, value=np.nan, inplace=True) # the -100 was hard coded in the financial reports
        npvs_per_year_new_plants_all[technology_name] = npvs_per_year_new_plants
        irrs_per_year_new_plants_all[technology_name] = irrs_per_year_new_plants
        irrs_per_tech_per_year[technology_name] = np.nanmean(irrs_per_year, axis=1)
        npvs_per_tech_per_MW[technology_name] = np.nanmean(npvs_per_year, axis=1)





    return irrs_per_tech_per_year,  npvs_per_tech_per_MW, npvs_per_year_new_plants_all, irrs_per_year_new_plants_all


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
    CO2prices_future_prices = reps.substances["CO2"].simulatedPrice.to_dict()
    values = [float(i[1]) for i in CO2prices_future_prices["data"]]
    index = [int(i[0]) for i in CO2prices_future_prices["data"]]
    co2prices = pd.Series(values, index=index)
    co2price = co2prices[year]
    for tech_name, tech in reps.power_generating_technologies.items():
        if tech.intermittent == False:
            annual_cost_capital = npf.pmt(wacc, tech.expected_lifetime, -tech.investment_cost_eur_MW)
            if tech.fuel == "":
                fuel_price = np.int64(0)
                fuel_perMWh = np.int64(0)
            else:
                calculatedPrices = tech.fuel.simulatedPrice.to_dict()
                df = pd.DataFrame(calculatedPrices['data'])
                df.set_index(0, inplace=True)
                fuel_price = df.at[str(year), 1]
                # Co2EmissionsInTperMWH / efficiency = CO2 emissions per MWh
                fuel_perMWh = tech.fuel.co2_density

            opex = (tech.variable_operating_costs + fuel_price + co2price * fuel_perMWh) * hours / tech.efficiency
            total = annual_cost_capital + opex + tech.fixed_operating_costs
            yearly_costs[tech_name] = total
        else:
            pass
            # print("dont graph renewables", tech_name)
    return yearly_costs


def prepare_screening_curves_candidates(reps, year):
    hours = np.array(list(range(1, 8760)))
    agent = reps.energy_producers[reps.agent]
    wacc = (1 - agent.debtRatioOfInvestments) * agent.equityInterestRate \
           + agent.debtRatioOfInvestments * agent.loanInterestRate
    yearly_costs_candidates = pd.DataFrame(index=hours)

    CO2prices_future_prices = reps.substances["CO2"].futurePrice.to_dict()
    values = [float(i[1]) for i in CO2prices_future_prices["data"]]
    index = [int(i[0]) for i in CO2prices_future_prices["data"]]
    co2prices = pd.Series(values, index=index)
    co2price = co2prices[year]

    for tech in reps.get_unique_candidate_technologies():
        annual_cost_capital = npf.pmt(wacc, tech.expected_lifetime, -tech.investment_cost_eur_MW)
        if tech.fuel == "":
            # ton / MWh
            fuel_price = np.int64(0)
            fuel_perMWh = np.int64(0)
        else:
            future_prices = tech.fuel.futurePrice.to_dict()
            df = pd.DataFrame(future_prices['data'])
            df.set_index(0, inplace=True)
            fuel_price = df.at[str(year), 1]
            # Co2EmissionsInTperMWH / efficiency = CO2 emissions per MWh
            fuel_perMWh = tech.fuel.co2_density / tech.efficiency

            # CO2 intensity from AMIRIS in Emissions in tons/MWh
        opex = (tech.variable_operating_costs + fuel_price + co2price * fuel_perMWh) * hours / tech.efficiency
        total = annual_cost_capital + opex + tech.fixed_operating_costs
        yearly_costs_candidates[tech.name] = total
    return yearly_costs_candidates


def prepare_accepted_CapacityMechanism(reps, unique_technologies, ticks_to_generate):
    CM_revenues_per_technology = pd.DataFrame(index=ticks_to_generate, columns=unique_technologies).fillna(0)
    accepted_pp_per_technology = pd.DataFrame(index=ticks_to_generate, columns=unique_technologies).fillna(0)
    capacity_mechanisms_per_tech = pd.DataFrame(index=ticks_to_generate, columns=unique_technologies).fillna(0)
    CM_clearing_price = pd.DataFrame(index=ticks_to_generate).fillna(0)
    revenues_from_market = pd.DataFrame(index=ticks_to_generate).fillna(0)

    # attention: FOR STRATEGIC RESERVES
    sr_operator = reps.get_strategic_reserve_operator(reps.country)
    if sr_operator.cash != 0:
        ran_capacity_market = False
        for tick in ticks_to_generate:
            accepted_per_tick = sr_operator.list_of_plants_all[tick]
            for technology_name in unique_technologies:
                for accepted_plant in accepted_per_tick:
                    if reps.power_plants[accepted_plant].technology.name == technology_name:
                        capacity_mechanisms_per_tech.loc[tick, technology_name] += reps.power_plants[
                            accepted_plant].capacity
            # todo: finish the revenues
            # revenues_from_market.at[tick,0] = sr_operator.revenues_per_year[tick]
    # attention: FOR CAPACITY MARKETS
    else:
        ran_capacity_market = True
        market = reps.get_capacity_market_in_country(reps.country)
        for tick in ticks_to_generate:
            accepted_per_tick = reps.get_accepted_CM_bids(tick)  # accepted amount from bids todo change to erase bids
            for technology_name in unique_technologies:
                for accepted_plant in accepted_per_tick:
                    if reps.power_plants[accepted_plant.plant].technology.name == technology_name:
                        capacity_mechanisms_per_tech.loc[tick, technology_name] += accepted_plant.amount
            CM_clearing_price.at[tick, 0] = reps.get_market_clearing_point_price_for_market_and_time(market.name, tick)

    for technology_name in unique_technologies:
        cm_revenues_per_pp = pd.DataFrame(index=ticks_to_generate).fillna(0)
        powerplants_per_tech = reps.get_power_plants_by_technology(technology_name)

        for pp in powerplants_per_tech:
            CMrevenues = reps.get_CM_revenues(pp.name)  # CM revenues from financial results
            cm_revenues_per_pp[pp.name] = CMrevenues  # matrix with CM revenues)
        accepted_pp_per_technology[technology_name] = cm_revenues_per_pp.gt(0).sum(axis=1)
        total_revenues_per_technology = cm_revenues_per_pp.sum(axis=1, skipna=True)
        CM_revenues_per_technology[technology_name] = total_revenues_per_technology
    total_costs_CM = CM_revenues_per_technology.sum(axis=1, skipna=True)

    return CM_revenues_per_technology, accepted_pp_per_technology, capacity_mechanisms_per_tech, CM_clearing_price, total_costs_CM, ran_capacity_market


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
    all_techs_generation = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    all_techs_market_value = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    all_techs_capacity_factor = pd.DataFrame(index=unique_technologies, columns=years_to_generate).fillna(0)
    average_electricity_price = pd.DataFrame(index=years_to_generate).fillna(0)
    production_per_year = pd.DataFrame(index=years_to_generate).fillna(0)
    for year in years_to_generate:
        dispatch_per_year = reps.get_all_power_plant_dispatch_plans_by_tick(year)
        totalrevenues = 0
        totalproduction = 0
        for technology_name in unique_technologies:
            generation_per_tech = 0
            market_value_per_tech = []
            capacity_factor_per_tech = []
            for id, pp_production_in_MWh in dispatch_per_year.accepted_amount.items():
                power_plant = reps.get_power_plant_by_id(id)
                if power_plant is not None:
                    if power_plant.technology.name == technology_name:
                        generation_per_tech += pp_production_in_MWh
                        capacity_factor_per_tech.append(pp_production_in_MWh / (power_plant.capacity * 8760))
                        totalproduction += pp_production_in_MWh
                        totalrevenues += dispatch_per_year.revenues[id]
                        market_value_per_tech.append(dispatch_per_year.revenues[id] / pp_production_in_MWh)
                else:
                    print("power plant is none", id)

            all_techs_capacity_factor.loc[technology_name, year] = mean(capacity_factor_per_tech)
            all_techs_market_value.loc[technology_name, year] = mean(market_value_per_tech)
            all_techs_generation.loc[technology_name, year] = generation_per_tech

        average_electricity_price.loc[year, 1] = totalrevenues / totalproduction
        production_per_year.loc[year, 1] = totalproduction
    return all_techs_generation, all_techs_market_value.replace(np.nan, 0), all_techs_capacity_factor.replace(np.nan,
                                                                                                              0), average_electricity_price, production_per_year


def reading_electricity_prices(reps, existing_scenario, folder_name):
    years_to_generate = list(range(reps.start_simulation_year, reps.current_year + 1))
    yearly_electricity_prices = pd.DataFrame()
    residual_load = pd.DataFrame()
    for year in years_to_generate:
        if existing_scenario == True:
            year_excel = globalNames.amiris_ouput_path + "\\" + str(year) + ".xlsx"
        else:
            year_excel = folder_name + str(year) + ".xlsx"
        df = pd.read_excel(year_excel, sheet_name=["energy_exchange", "residual_load"])
        yearly_electricity_prices.at[:, year] = df['energy_exchange'].ElectricityPriceInEURperMWH
        residual_load.at[:, year] = df['residual_load']["0"]
    return yearly_electricity_prices, residual_load


def get_shortage_hours_and_power_ratio(reps, years_to_generate, yearly_electricity_prices, all_techs_capacity):
    total_capacity = all_techs_capacity.sum(axis=0)
    controllable_capacity = all_techs_capacity.sum(axis=0)
    shortage_hours = pd.DataFrame(index=years_to_generate)
    supply_ratio = pd.DataFrame(index=years_to_generate)
    voll = reps.get_electricity_voll()
    shortage_hours["from prices >3000"] = yearly_electricity_prices.eq(3000).sum()

    #shortage_from_capacity = []
    for year in years_to_generate:
        trend = reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity", globalNames.simulated_prices,
                                                                       year)
        load = reps.get_hourly_demand_by_country(reps.country)[1]
        peak_load_without_trend = max(load)
        peak_load_volume = peak_load_without_trend * trend
        # load_volume = residual_load[year]
        # peak_load_volume = max(load_volume)
        count = 0
        for i in load:
            x = i * trend
            if x > total_capacity.loc[year]:
                count += 1
        # the peak load without renewables could be slightly lower, so the residual load could slightly increase the suuply ratio
        supply_ratio.loc[year, 0] = controllable_capacity.loc[year] / peak_load_volume
       # shortage_from_capacity.append(count)

    #shortage_hours["demand> capacity"] = shortage_from_capacity
    return shortage_hours, supply_ratio


def generate_plots(reps, path_to_plots, electricity_prices, residual_load, test_tick, test_tech):
    print("Databases read")
    unique_technologies = reps.get_unique_technologies_names()
    unique_candidate_power_plants = reps.get_unique_candidate_technologies_names()
    years_to_generate = list(range(reps.start_simulation_year, reps.current_year + 1))  # control the current year
    ticks_to_generate = list(range(0, reps.current_tick + 1))
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
    last_year = years_to_generate[-1]
    # # #check extension of power plants.
    # # extension = prepare_extension_lifetime_per_tech(reps, unique_technologies)
    # CM_revenues_per_technology, accepted_pp_per_technology, capacity_mechanisms_per_tech, CM_clearing_price, total_costs_CM,  ran_capacity_market = prepare_accepted_CapacityMechanism(
    #     reps, unique_technologies,
    #     ticks_to_generate)
    # plot_CM_revenues(CM_revenues_per_technology, accepted_pp_per_technology, capacity_mechanisms_per_tech,
    #                  CM_clearing_price, total_costs_CM,  ran_capacity_market ,  path_to_plots, colors_unique_techs)
    # section -----------------------------------------------------------------------------------------------Capacity Markets

    # section ---------------------------------------------------------------Cash energy producer
    #
    cash_flows_energy_producer, total_costs, cost_recovery, new_plants_loans = prepare_cash_per_agent(reps,
                                                                                                      ticks_to_generate)
    plot_cost_recovery(cost_recovery, path_to_plots)
    plot_cash_flows(cash_flows_energy_producer, new_plants_loans, path_to_plots)
    # #section -----------------------------------------------------------------------------------------------capacities
    #
    all_techs_generation, all_techs_market_value, all_techs_capacity_factor, \
    average_electricity_price, production_per_year = prepare_capacity_and_generation_per_technology(
        reps, unique_technologies,
        years_to_generate)
    plot_capacity_factor(all_techs_capacity_factor.T, path_to_plots, colors_unique_techs)
    plot_market_values_generation(all_techs_market_value.T, path_to_plots, colors_unique_techs)
    plot_yearly_average_electricity_prices(average_electricity_price, path_to_plots)
    plot_annual_generation(all_techs_generation.T, path_to_plots, colors_unique_techs)

    # section -----------------------------------------------------------------------------------------------NPV and investments per iteration

    profits_per_iteration = prepare_profits_candidates_per_iteration(reps, test_tick)
    plot_candidate_profits_per_iteration(profits_per_iteration, path_to_plots, test_tick, colors_unique_candidates)

    irrs_per_tech_per_year, npvs_per_tech_per_MW, npvs_per_year_new_plants_all, irrs_per_year_new_plants_all = \
        prepare_irr_and_npv_per_technology_per_year(reps, unique_technologies, ticks_to_generate)

    plot_irrs_and_npv_per_tech_per_year(irrs_per_tech_per_year, npvs_per_tech_per_MW, path_to_plots,
                                        colors_unique_techs)

    installed_capacity_per_iteration, candidate_plants_project_value = prepare_capacity_per_iteration(
        future_year, reps, unique_candidate_power_plants)
    if candidate_plants_project_value.shape[0] == 0:
        raise Exception("no installable capacity in this test year")
    else:
        plot_investments_and_NPV_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration,
                                               future_year, path_to_plots, colors_unique_candidates)
    # ATTENTION: FOR TEST TECH
    average_profits_per_tech_per_year, new_pp_profits_for_tech = prepare_operational_profit_per_year_per_tech(
        reps, unique_technologies, ticks_to_generate, test_tech)

    plot_total_profits_per_tech_per_year(average_profits_per_tech_per_year, path_to_plots, colors_unique_techs)
    plot_profits_for_tech_per_year(new_pp_profits_for_tech, test_tech, path_to_plots, colors_unique_techs)
    # reality vs expectation
    plot_npv_new_plants(npvs_per_year_new_plants_all, irrs_per_year_new_plants_all, candidate_plants_project_value, test_tech, test_year, test_tick,
                        future_year, path_to_plots)

    ##section -----------------------------------------------------------------------------------------------revenues per iteration
    # '''
    # decommissioning is plotted according to the year when it is decided to get decommissioned
    # '''
    sorted_average_revenues_per_iteration_test_tick, all_future_operational_profit = prepare_revenues_per_iteration(
        reps, test_tick, test_tech)
    plot_revenues_per_iteration_for_one_tech(all_future_operational_profit, test_tech, path_to_plots, test_tick)

    plot_average_revenues_per_iteration(sorted_average_revenues_per_iteration_test_tick, path_to_plots, first_year,
                                        colors_unique_techs)

    initial_power_plants, annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_commissioned, \
    all_techs_capacity, last_year_in_pipeline, last_year_decommissioned, \
    last_year_operational_capacity, last_year_to_be_decommissioned_capacity, \
    last_year_strategic_reserve_capacity, number_per_status, number_per_status_last_year = \
        prepare_pp_status(years_to_generate, years_to_generate_and_build, reps, unique_technologies)

    plot_investments(annual_in_pipeline_capacity, annual_commissioned, annual_decommissioned_capacity,
                     path_to_plots,
                     colors_unique_techs)

    plot_installed_capacity(all_techs_capacity, path_to_plots, colors_unique_techs)

    power_plants_status(number_per_status, path_to_plots)
    power_plants_last_year_status(number_per_status_last_year, path_to_plots, last_year)
    if electricity_prices is not None:
        plot_hourly_electricity_prices(electricity_prices, path_to_plots)
        plot_hourly_electricity_prices_boxplot(electricity_prices, path_to_plots)
        shortages, supply_ratio = get_shortage_hours_and_power_ratio(reps, years_to_generate, electricity_prices,
                                                                     all_techs_capacity.T)
        plot_supply_ratio(supply_ratio, residual_load, path_to_plots)

        plot_shortages(shortages, path_to_plots)
        # plotting costs to society
        annual_generation = all_techs_generation.sum().values
        # CM_price =  total_costs_CM/annual_generation
        # average_electricity_price['CM price'] = CM_price.values
        # plot_costs_to_society(average_electricity_price, path_to_plots)

    # #  section -----------------------------------------------------------------------------------------------revenues per iteration

    yearly_costs = prepare_screening_curves(reps, test_year)
    yearly_costs_candidates = prepare_screening_curves_candidates(reps, future_year)
    # candidates = reps.get_unique_candidate_technologies_names()
    # yearly_costs_candidates_for_test_year = yearly_costs[candidates]
    plot_screening_curve_candidates(yearly_costs_candidates, path_to_plots, first_year + reps.lookAhead,
                                    colors_unique_candidates)
    plot_screening_curve(yearly_costs, path_to_plots, test_year, colors_unique_techs)
    future_fuel_prices = prepare_future_fuel_prices(reps, years_to_generate)
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
    #plt.show()
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
    # write the name of the exiisting scenario or the new scenario
    name = "grouped_unlimited"
    existing_scenario = False
    electricity_prices = True  # write False if not wished to graph electricity prices"

    if name == "":
        raise Exception("Name needed")

    if electricity_prices == False:
        electricity_prices = None  # dont read if not necessary
        residual_load = None

    if existing_scenario == False:
        print("Plots for new scenario  " + name)
        # if there is no scenario available
        emlab_url = sys.argv[1]
        amiris_url = sys.argv[2]
        # use "Amiris" if this should be read
        spinedb_reader_writer = SpineDBReaderWriter("Amiris", emlab_url, amiris_url)
        reps = spinedb_reader_writer.read_db_and_create_repository("plotting")

        complete_name = reps.country + str(reps.end_simulation_year) \
                        + "_SD" + str(reps.start_year_dismantling) \
                        + "_PH" + str(reps.pastTimeHorizon) + "_MI" + str(reps.maximum_investment_capacity_per_year) \
                        + "_" + reps.typeofProfitforPastHorizon + "_"
        if reps.realistic_candidate_capacities_for_future == True:
            complete_name = complete_name + "future1"
        if reps.realistic_candidate_capacities_tobe_installed == True:
            complete_name = complete_name + "installed1"
        name = complete_name + name

        if electricity_prices == True:
            electricity_prices, residual_load = reading_electricity_prices(reps, existing_scenario,
                                                                           globalNames.amiris_ouput_path)

    elif existing_scenario == True:
        print("Plots for existing scenario " + name)

        first = globalNames.scenarios_path
        emlab_sql = "\\EmlabDB.sqlite"
        amiris_sql = "\\AMIRIS db.sqlite"
        energy_exchange_url_sql = "\\energy exchange.sqlite"
        emlab_url = first + name + emlab_sql
        amiris_url = first + name + amiris_sql
        spinedb_reader_writer = SpineDBReaderWriter("Amiris", emlab_url, amiris_url)
        reps = spinedb_reader_writer.read_db_and_create_repository("plotting")
        folder_name = first + name
        if electricity_prices == True:
            electricity_prices, residual_load = reading_electricity_prices(reps, existing_scenario, folder_name)

    for p, power_plant in reps.power_plants.items():
        power_plant.specifyPowerPlantsInstalled(reps.current_tick)

    test_tick = 4
    # test_tech = "OCGT"
    test_tech = "CCGT"
    path_to_plots = os.path.join(os.getcwd(), "plots", "Scenarios", name)

    if not os.path.exists(path_to_plots):
        os.makedirs(path_to_plots)

    # plot_initial_power_plants(path_to_plots, "powerplants_grouped") #"extendedDE"
    generate_plots(reps, path_to_plots, electricity_prices, residual_load, test_tick, test_tech)

except Exception as e:
    logging.error('Exception occurred: ' + str(e))
    raise
finally:
    spinedb_reader_writer.db.close_connection()
    spinedb_reader_writer.amirisdb.close_connection()
    print("finished emlab")

print('===== End Generating Plots =====')

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
#     axs4.set_title('Capacity per Technology to be decommissioned')
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
