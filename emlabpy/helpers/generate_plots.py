import matplotlib.pyplot as plt
import os
import pandas
import numpy as np
from spinedb import SpineDB
import pandas as pd


def get_participating_technologies_in_capacity_market(db_emlab_powerplantdispatchplans, years_to_generate, years_emlab,
                                                      db_emlab_powerplants):
    """
    This function returns all participating technologies that get revenue from the Capacity Market.
    It returns a set so all values are distinct.

    :param db_emlab_powerplantdispatchplans: PPDPs as queried from SpineDB EMLab
    :return: Set of technology names
    """
    capacity_market_aggregated_per_tech = pd.DataFrame()
    for year in years_emlab:
        capacity_market_ppdps = [row['object_name'] for row in db_emlab_powerplantdispatchplans if
                                 row['parameter_name'] == 'Market' and
                                 row['parameter_value'] == 'DutchCapacityMarket' and
                                 row['alternative'] == str(year)]
        capacity_market_accepted_ppdps = [row['object_name'] for row in db_emlab_powerplantdispatchplans if
                                          row['object_name'] in capacity_market_ppdps and
                                          row['parameter_name'] == 'AcceptedAmount' and
                                          row['parameter_value'] > 0]

        list_of_tech_fuel_cominations = []
        capacity_market_participating_capacities = []
        for ppdp in capacity_market_accepted_ppdps:
            plant_name = next(row['parameter_value'] for row in db_emlab_powerplantdispatchplans if
                              row['object_name'] == ppdp and
                              row['parameter_name'] == 'Plant')
            plant_accepted_amount = next(row['parameter_value'] for row in db_emlab_powerplantdispatchplans if
                                  row['object_name'] == ppdp and
                                  row['parameter_name'] == 'AcceptedAmount')
            plant_technology = next(row['parameter_value'] for row in db_emlab_powerplants if
                                    row['object_name'] == plant_name and
                                    row['parameter_name'] == 'TECHTYPENL')
            plant_fuel = next(row['parameter_value'] for row in db_emlab_powerplants if
                              row['object_name'] == plant_name and
                              row['parameter_name'] == 'FUELNL')
            list_of_tech_fuel_cominations.append(plant_technology + ', ' + plant_fuel)
            capacity_market_participating_capacities.append(plant_accepted_amount)

        df_year = pd.DataFrame({'technology_fuel': list_of_tech_fuel_cominations,
                                'capacity': capacity_market_participating_capacities})
        capacity_market_aggregated_per_tech[year] = df_year.groupby('technology_fuel').sum()
    years_dictionary = dict(zip(years_emlab, years_to_generate))
    capacity_market_aggregated_per_tech.rename(columns=years_dictionary,
                                               inplace=True)
    return capacity_market_aggregated_per_tech.fillna(0)


def plot_mcps_with_filter(db_mcps, market, years_to_generate, path_to_plots, title, file_name, yl, ylim):
    # MCP Plots
    filtered_mcps = [i['object_name'] for i in db_mcps if
                     i['parameter_name'] == 'Market' and i['parameter_value'] == market]
    mcp_x = []
    mcp_y = []

    print('Creating ' + str(market) + ' MCP plot')
    for row in [i for i in db_mcps if i['object_name'] in filtered_mcps]:
        if row['parameter_name'] == 'Price':
            mcp_x.append(int(row['alternative']) + years_to_generate[0])
            mcp_y.append(row['parameter_value'])

    fig7 = plt.figure()
    axs7 = plt.axes()
    plt.grid(b=True)
    axs7.plot(mcp_x, mcp_y, 'o')
    axs7.set_axisbelow(True)
    plt.xlabel('Years')
    plt.ylabel(yl)
    plt.ylim(ylim)
    axs7.set_title(title)
    fig7.savefig(path_to_plots + '/' + file_name, bbox_inches='tight', dpi=300)


def plot_annual_balances(annual_balance, years_to_generate, path_to_plots):
    # Annual Balance
    print('Create Annual Balance plot')
    plt.figure()
    annual_balance_df = pd.DataFrame(annual_balance, index=years_to_generate)
    axs125 = annual_balance_df.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Supply or Demand (MWh)', fontsize='medium')
    axs125.set_title('NL Annual Balance per Technology')
    axs125.set_axisbelow(True)
    plt.ylim([-0.6e8, 1.75e8])
    fig125 = axs125.get_figure()
    fig125.savefig(path_to_plots + '/' + 'NL Annual Balance.png', bbox_inches='tight', dpi=300)


def plot_vre_nl_installed_capacity(vre_investment_sums, years_to_generate, path_to_plots):
    # VRE Investments plot
    print('Create VRE Investments plot')
    plt.figure()
    vre_investments_df = pd.DataFrame(vre_investment_sums, index=years_to_generate)
    axs5 = vre_investments_df.plot.bar(stacked=True, rot=0, colormap='tab20', legend=False)
    axs5.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity (MW)', fontsize='medium')
    axs5.set_title('NL VRE Installed Capacity')
    fig5 = axs5.get_figure()
    fig5.savefig(path_to_plots + '/' + 'NL Installed Capacity.png', bbox_inches='tight', dpi=300)


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


def plot_nl_investments(investment_sums, years_to_generate, path_to_plots, look_ahead):
    # NL Investments plot
    print('Create NL Investments plot')
    plt.figure()
    investments_df = pd.DataFrame(investment_sums,
                                  index=list(range(years_to_generate[0], years_to_generate[-1] + look_ahead + 1)))
    axs6 = investments_df.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity (MW)', fontsize='medium')
    # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs6.set_title('NL Capacity Investments per Technology')
    axs6.set_axisbelow(True)
    plt.ylim([-20e3, 33e3])
    fig6 = axs6.get_figure()
    fig6.savefig(path_to_plots + '/' + 'NL Investments.png', bbox_inches='tight', dpi=300)


def plot_co2_emissions(co2_emission_sums, years_to_generate, path_to_plots):
    # CO2 emissions plot
    print('Create annual CO2 Emission per tech plot')
    plt.figure()
    co2_df = pd.DataFrame(co2_emission_sums, index=years_to_generate)
    axs4 = co2_df.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Emissions (ton CO2)', fontsize='medium')
    axs4.set_title('NL CO2 Emissions per Technology')
    axs4.set_axisbelow(True)
    plt.ylim([0, 3.5e7])
    # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    fig4 = axs4.get_figure()
    fig4.savefig(path_to_plots + '/' + 'NL CO2 Emissions.png', bbox_inches='tight', dpi=300)


def plot_nl_unit_generation(path_and_filename_dispatch, year, path_to_plots):
    print('Plot NL Unit Generation')
    # Plot 3 NL Unit Generation curve
    nl_unit_generation_df = pandas.read_excel(path_and_filename_dispatch, 'NL Unit Generation', skiprows=1, index_col=0,
                                              header=0).transpose()

    plt.figure()
    axs3 = nl_unit_generation_df.plot()
    axs3.set_axisbelow(True)
    plt.xlabel('Hours', fontsize='medium')
    plt.ylabel('Generation (MWh)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs3.set_title('NL Unit Generation ' + str(year))
    fig3 = axs3.get_figure()
    fig3.savefig(path_to_plots + '/' + 'NL Unit Generation ' + str(year) + '.png', bbox_inches='tight', dpi=300)


def plot_and_prepare_hourly_nodal_price_duration_curve(hourly_nodal_prices_df, year, path_to_plots,
                                                       price_duration_curves):
    # Plot 2.5 Hourly Market Price Duration Curve
    print('Create Hourly Nodal Price duration curve')
    plt.figure()
    axs25 = hourly_nodal_prices_df['NED'].sort_values(ascending=False).plot(use_index=False, grid=True, legend=False)
    plt.xlabel('Hours')
    plt.ylabel('Price (Euro / MWh)')
    axs25.set_title('NL Hourly Electricity Spot Market Price Duration Curve ' + str(year))
    axs25.set_axisbelow(True)
    plt.ylim([0, min(hourly_nodal_prices_df['NED'].max() + 50, 250)])
    fig25 = axs25.get_figure()
    fig25.savefig(path_to_plots + '/' + 'NL Nodal Prices Duration Curve ' + str(year) + '.png', bbox_inches='tight', dpi=300)

    price_duration_curves[year] = hourly_nodal_prices_df['NED'].sort_values(ascending=False).values
    return price_duration_curves


def plot_hourly_nodal_prices(path_and_filename_dispatch, year, path_to_plots):
    # Plot 2 Hourly Nodal Prices
    print('Read and create hourly nodal prices plot')
    hourly_nodal_prices_df = pandas.read_excel(path_and_filename_dispatch, 'Hourly Nodal Prices', skiprows=1,
                                               index_col=0)
    # hourly_nodal_prices_df[hourly_nodal_prices_df > 250] = 250

    plt.figure()
    axs2 = hourly_nodal_prices_df['NED'].plot(grid=True)
    axs2.set_axisbelow(True)
    plt.xlabel('Hours')
    plt.ylabel('Price (Euro / MWh)')
    plt.xlim([0, 8760])
    plt.ylim([0, min(hourly_nodal_prices_df['NED'].max() + 50, 250)])
    axs2.set_title('NL Hourly Electricity Spot Market Prices ' + str(year))
    fig2 = axs2.get_figure()
    fig2.savefig(path_to_plots + '/' + 'NL Nodal Prices ' + str(year) + '.png', bbox_inches='tight', dpi=300)

    return hourly_nodal_prices_df


def plot_and_prepare_residual_load_duration_curve(hourly_nl_balance_demand, hourly_nl_balance_df, year, path_to_plots,
                                                  residual_load_curves):
    # Plot 1.75: Residual Load Curve
    print('Create Res Load duration curve')
    plt.figure()
    hourly_nl_balance_residual_load = hourly_nl_balance_demand.subtract(hourly_nl_balance_df['Wind Onshore']) \
        .subtract(hourly_nl_balance_df['Wind Offshore']) \
        .subtract(hourly_nl_balance_df['Sun']) \
        .subtract(hourly_nl_balance_df['Hydro Conv.'])
    axs175 = hourly_nl_balance_residual_load.sort_values(ascending=False).plot(use_index=False, grid=True, legend=False)
    axs175.set_title('NL Residual Load Duration Curve ' + str(year))
    axs175.set_axisbelow(True)
    plt.xlabel('Hours')
    plt.ylabel('Residual Load (MWh)')
    plt.xlim([0, 8760])
    fig175 = axs175.get_figure()
    fig175.savefig(path_to_plots + '/' + 'NL Residual Load Duration Curve ' + str(year) + '.png', bbox_inches='tight', dpi=300)

    residual_load_curves[year] = hourly_nl_balance_residual_load.sort_values(ascending=False).values
    return residual_load_curves


def plot_and_prepare_load_duration_curve(hourly_nl_balance_demand, year, path_to_plots, load_duration_curves):
    # Plot 1.5: Load duration curve
    print('Create Load duration curve plot')
    plt.figure()
    axs15 = hourly_nl_balance_demand.sort_values(ascending=False).plot(use_index=False, grid=True, legend=False)
    axs15.set_title('NL Load Duration Curve ' + str(year))
    axs15.set_axisbelow(True)
    plt.xlabel('Hours')
    plt.ylabel('Load (MWh)')
    plt.xlim([0, 8760])
    fig15 = axs15.get_figure()
    fig15.savefig(path_to_plots + '/' + 'NL Load Duration Curve ' + str(year) + '.png', bbox_inches='tight', dpi=300)

    load_duration_curves[year] = hourly_nl_balance_demand.sort_values(ascending=False).values
    return load_duration_curves


def prepare_annual_nl_balance(hourly_nl_balance_df, annual_balance, years_to_generate, year):
    print('Prepare Annual NL Balance plot data')
    hourly_nl_annual = hourly_nl_balance_df.sum()
    for index, col in hourly_nl_annual.iteritems():
        if index in annual_balance.keys():
            annual_balance[index].append(col)
        else:
            annual_balance[index] = [0] * years_to_generate.index(year) + [col]
    return annual_balance


def plot_hourly_nl_balance(path_and_filename_dispatch, path_to_plots, year):
    # Plot 1 Hourly NL Balance (per year)
    print('Read and Create Hourly NL Balance plot')
    hourly_nl_balance_df = pandas.read_excel(path_and_filename_dispatch, 'Hourly NL Balance', skiprows=1, index_col=0,
                                             skipfooter=2, usecols='A:W').replace(np.nan, 0)
    hourly_nl_balance_demand = hourly_nl_balance_df['Demand']
    hourly_nl_balance_df = hourly_nl_balance_df.drop(['Demand'], axis=1)
    hourly_nl_balance_df['Exports'] = -1 * hourly_nl_balance_df['Exports']
    hourly_nl_balance_df['H2'] = -1 * hourly_nl_balance_df['H2']
    hourly_nl_balance_df['Heat'] = -1 * hourly_nl_balance_df['Heat']
    hourly_nl_balance_df['HP'] = -1 * hourly_nl_balance_df['HP']
    hourly_nl_balance_df['EVs'] = -1 * hourly_nl_balance_df['EVs']
    hourly_nl_balance_df['Storage cons.'] = -1 * hourly_nl_balance_df['Storage cons.']
    hourly_nl_balance_df_resampled = hourly_nl_balance_df.copy()

    hourly_nl_balance_df_resampled['T'] = hourly_nl_balance_df_resampled.sum(axis=1)
    hourly_nl_balance_df_resampled.index = pandas.to_timedelta(hourly_nl_balance_df_resampled.index, unit='H')
    hourly_nl_balance_df_resampled = hourly_nl_balance_df_resampled.resample('50H').mean()
    hourly_nl_balance_df_resampled = hourly_nl_balance_df_resampled.drop(['T'], axis=1)
    hourly_nl_balance_df_resampled = hourly_nl_balance_df_resampled.interpolate(method='cubic')
    hourly_nl_balance_df_resampled.index = [i * 50 for i in range(0, len(hourly_nl_balance_df_resampled))]
    axs = hourly_nl_balance_df_resampled.plot.area(colormap='tab20', linewidth=0, legend=False)
    axs.set_title('Hourly NL Balance - All Technologies ' + str(year))
    axs.set_axisbelow(True)
    plt.xlabel('Hours', fontsize='medium')
    plt.ylabel('Supply or Demand (MWh)', fontsize='medium')
    plt.xlim([0, 8760])
    # plt.legend(fontsize='medium', loc='best', bbox_to_anchor=(1, 1.1))
    fig = axs.get_figure()
    fig.savefig(path_to_plots + '/' + 'NL Hourly Balance ' + str(year) + '.png', bbox_inches='tight', dpi=300)
    return hourly_nl_balance_df, hourly_nl_balance_demand


def prepare_co2_emission_data(path_and_filename_dispatch, co2_emission_sums, years_to_generate, year):
    # Preparing values for CO2 Emissions plot, plot after years iterations
    print('Prepare CO2 Emission plot data')
    co2_emissions = pandas.read_excel(path_and_filename_dispatch, 'CO2 Emissions tech', skiprows=1, index_col=0)
    co2_emissions.columns = [i[0] + ',' + i[1] for i in zip(co2_emissions.columns.values, co2_emissions.iloc[0].values)]

    for index, value in co2_emissions.loc['NED'].iteritems():
        if index in co2_emission_sums.keys():
            co2_emission_sums[index].append(value)
        else:
            co2_emission_sums[index] = [0] * years_to_generate.index(year) + [value]
    # Add 0 to values if not in COMPETES results
    for key in co2_emission_sums.keys():
        if key not in co2_emissions.columns.values:
            co2_emission_sums[key].append(0)
    return co2_emission_sums


def prepare_vre_investment_data(path_and_filename_investments, vre_investment_sums, years_to_generate, year):
    # Preparing values for VRE Investments plot, plot after years iterations
    print('Preparing VRE Investment data')
    vre_investments = pandas.read_excel(path_and_filename_investments, 'VRE investment', skiprows=2)
    for index, row in vre_investments[vre_investments['Bus'] == 'NED'].iterrows():
        if row['WindOn'] in vre_investment_sums.keys():
            vre_investment_sums[row['WindOn']].append(row['Initial'])
        else:
            vre_investment_sums[row['WindOn']] = [0] * years_to_generate.index(year) + [row['Initial']]
    # Add 0 to values if not in COMPETES results
    for key in vre_investment_sums.keys():
        if key not in vre_investments[vre_investments['Bus'] == 'NED']['WindOn'].values:
            vre_investment_sums[key].append(0)
    return vre_investment_sums


def prepare_investment_and_decom_data(path_and_filename_investments, investment_sums, years_to_generate, year,
                                      emlab_spine_powerplants_tech_dict, emlab_spine_powerplants_fuel_dict,
                                      emlab_spine_technologies, look_ahead, nl_investment_sums):
    print('Loading investment and decom data')
    decommissioning = pandas.read_excel(path_and_filename_investments, 'Decommissioning', skiprows=2, usecols='A:C')
    decommissioning = decommissioning.dropna()
    nl_decommissioning = decommissioning[decommissioning['node'] == 'NED'].copy()
    investments = pandas.read_excel(path_and_filename_investments, 'New Generation Capacity', skiprows=2, usecols="A:D")
    investments = investments.dropna()
    nl_investments = investments[investments['Node'] == 'NED'].copy()

    investment_sums, investments = prepare_investment_data(investments, investment_sums, years_to_generate, year,
                                                           emlab_spine_technologies, look_ahead)
    nl_investment_sums, nl_investments = prepare_investment_data(nl_investments, nl_investment_sums, years_to_generate,
                                                                 year, emlab_spine_technologies, look_ahead)

    investment_sums = prepare_decom_data(decommissioning, emlab_spine_powerplants_tech_dict, investment_sums,
                                         years_to_generate, year, investments, emlab_spine_powerplants_fuel_dict,
                                         look_ahead)
    nl_investment_sums = prepare_decom_data(nl_decommissioning, emlab_spine_powerplants_tech_dict, nl_investment_sums,
                                            years_to_generate, year, nl_investments, emlab_spine_powerplants_fuel_dict,
                                            look_ahead)

    return investment_sums, nl_investment_sums


def prepare_decom_data(decommissioning, emlab_spine_powerplants_tech_dict, investment_sums, years_to_generate, year,
                       investments, emlab_spine_powerplants_fuel_dict, look_ahead):
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


def get_year_online_by_technology(db_emlab_technologies, fuel, techtype, current_competes_tick):
    technologies_by_fuel = [i['object_name'] for i in db_emlab_technologies if
                            i['parameter_name'] == 'FUELNEW' and i['parameter_value'] == fuel]
    technologies_by_techtype = [i['object_name'] for i in db_emlab_technologies if
                                i['parameter_name'] == 'FUELTYPENEW' and i['parameter_value'] == techtype]
    technology = next(name for name in technologies_by_fuel if name in technologies_by_techtype)
    expected_permit_time = next(int(i['parameter_value']) for i in db_emlab_technologies if
                                i['object_name'] == technology and i['parameter_name'] == 'expectedPermittime')
    expected_lead_time = next(int(i['parameter_value']) for i in db_emlab_technologies if
                              i['object_name'] == technology and i['parameter_name'] == 'expectedLeadtime')
    build_time = expected_permit_time + expected_lead_time
    return current_competes_tick + build_time


def prepare_investment_data(investments, investment_sums, years_to_generate, year, emlab_spine_technologies,
                            look_ahead):
    # Preparing values for Investments plot, plot after years iterations
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

    return investment_sums, investments


def prepare_annual_installed_capacity(path_and_filename_dispatch, emlab_spine_powerplants_tech_dict,
                                      annual_installed_capacity, year, years_to_generate):
    installed_capacity_df = pandas.read_excel(path_and_filename_dispatch, 'Initial generation capacity', skiprows=2)
    installed_capacity_df = installed_capacity_df[installed_capacity_df['i'] == 'NED']
    installed_capacity_df['Technology'] = [emlab_spine_powerplants_tech_dict[i] for i in
                                           installed_capacity_df['h'].values]
    installed_capacity_df = installed_capacity_df.groupby(['Technology']).sum()
    for tech, row in installed_capacity_df.iterrows():
        if tech in annual_installed_capacity.keys():
            annual_installed_capacity[tech].append(row['MW'])
        else:
            annual_installed_capacity[tech] = [0] * years_to_generate.index(year) + [row['MW']]
    return annual_installed_capacity


def plot_annual_installed_capacity(annual_installed_capacity, years_to_generate, path_to_plots):
    print('Annual installed capacity NL')
    plt.figure()
    annual_installed_capacity_df = pd.DataFrame(annual_installed_capacity, index=years_to_generate)
    axs10 = annual_installed_capacity_df.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs10.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity (MW)', fontsize='medium')
    # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs10.set_title('NL Installed Capacity per Technology')
    fig10 = axs10.get_figure()
    fig10.savefig(path_to_plots + '/' + 'NL Installed Capacity per Technology.png', bbox_inches='tight', dpi=300)


def plot_combined_curves(df, title, yl, path_to_plots, ymax):
    if len(df.index) > 0:
        plt.figure()
        axs = df.plot(grid=True, use_index=False, legend=False)
        axs.set_axisbelow(True)
        plt.xlabel('Hours', fontsize='medium')
        plt.ylabel(yl, fontsize='medium')
        plt.xlim([-100, 8760])
        plt.ylim([df.min(axis=1).min(), min(df.max(axis=1).max(), ymax)])
        # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
        axs.set_title(title)
        fig = axs.get_figure()
        fig.savefig(path_to_plots + '/' + title + '.png', bbox_inches='tight', dpi=300)


def plot_capacity_market_technologies(capacity_market_participating_technologies_peryear, path_to_plots,
                                      years_to_generate, title, file_name, yl):
    if len(capacity_market_participating_technologies_peryear.index) > 0:
        fig1 = capacity_market_participating_technologies_peryear.T.plot.bar(stacked=True, grid=True, legend=False)
        fig1.set_axisbelow(True)
        plt.xlabel('Years', fontsize='medium')
        plt.ylabel(yl, fontsize='medium')
        plt.ylim([0, 30e3])
        # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
        plt.title(title)
        plt.savefig(path_to_plots + '/' + file_name, bbox_inches='tight', dpi=300)


def plot_capacity_market_revenues(capacity_market_participating_technologies_peryear, db_mcps, path_to_plots,
                                  years_to_generate, years_emlab, title, file_name, yl):
    if len(capacity_market_participating_technologies_peryear.index) > 0:
        filtered_mcps = [i['object_name'] for i in db_mcps if
                         i['parameter_name'] == 'Market' and i['parameter_value'] == 'DutchCapacityMarket']

        years_dictionary = dict(zip(years_emlab, years_to_generate))
        for row in [i for i in db_mcps if i['object_name'] in filtered_mcps]:
            for yearemlab, yearreal in years_dictionary.items():
                if int(row['alternative']) == yearemlab and row['parameter_name'] == 'Price':
                    capacity_market_participating_technologies_peryear[yearreal] = \
                    capacity_market_participating_technologies_peryear[yearreal].multiply(row['parameter_value'] / 1000000)

        fig2 = capacity_market_participating_technologies_peryear.T.plot.bar(stacked=True, grid=True, legend=False)
        fig2.set_axisbelow(True)
        plt.xlabel('Years', fontsize='medium')
        plt.ylabel(yl, fontsize='medium')
        # plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
        plt.title(title)
        plt.savefig(path_to_plots + '/' + file_name, bbox_inches='tight', dpi=300)


def generate_plots():
    # Select what years you want to generate plots for
    path_to_competes_results = '../../COMPETES/Results/Run 20210730 10M CO2 Cap, discountr 2.5, hedging 1, no exports, no VOLL'
    filename_to_load_dispatch = 'Output_Dynamic_Gen&Trans_?_Dispatch.xlsx'
    filename_to_load_investment = 'Output_Dynamic_Gen&Trans_?_Investments.xlsx'

    # Create plots directory if it does not exist yet
    path_to_plots = path_to_competes_results + '/plots'
    if not os.path.exists(path_to_plots):
        os.makedirs(path_to_plots)

    years_to_generate = [2020, 2021, 2022, 2023, 2024, 2025]
    start_simulation_year = 2020
    years_emlab = [i - start_simulation_year for i in years_to_generate]
    look_ahead = 7

    static_fuel_technology_legend = sorted(['GAS, CCGT', 'COAL, PC (D)', 'LIGNITE, PC (D)', 'RESE, others (D)', 'GAS, CCS CCGT', 'NUCLEAR, -', 'BIOMASS, Cofiring (D)', 'BIOMASS, Standalone (D)', 'Derived GAS, CHP (D)', 'Derived GAS, IC (D)', 'GAS, CCGT (D)', 'GAS, CHP (D)', 'OIL, - (D)', 'GAS, GT (D)', 'GAS, CCS CCGT (D)', 'NUCLEAR, - (D)'])

    co2_emission_sums = dict()
    vre_nl_installed_capacity = dict()
    nl_investment_sums = {i: [0] * len(range(years_to_generate[0], years_to_generate[-1] + look_ahead + 1)) for i in static_fuel_technology_legend}
    investment_sums = {i: [0] * len(range(years_to_generate[0], years_to_generate[-1] + look_ahead + 1)) for i in static_fuel_technology_legend}
    annual_balance = dict()
    annual_installed_capacity = dict()
    residual_load_curves = pd.DataFrame()
    load_duration_curves = pd.DataFrame()
    price_duration_curves = pd.DataFrame()

    # EMLab Plots
    print('Establishing and querying SpineDB...')
    sqlite_prepend = "sqlite:///"
    emlab_spinedb = SpineDB(sqlite_prepend + path_to_competes_results + '/db.sqlite')
    competes_spinedb = SpineDB(sqlite_prepend + path_to_competes_results + '/db competes.sqlite')
    try:
        emlab_spine_powerplants = emlab_spinedb.query_object_parameter_values_by_object_class('PowerPlants')
        competes_spine_powerplants = competes_spinedb.query_object_parameter_values_by_object_classes(
            ['Installed Capacity Abroad', 'Installed Capacity-RES Abroad'])
        spine_powerplants_tech_dict = dict(list({str(i['object_name']): str(i['parameter_value']) for i in
                                                 emlab_spine_powerplants if
                                                 i['parameter_name'] == 'TECHTYPENL'}.items()) +
                                           list({str(i['object_name']): str(i['parameter_value'].decode()).replace("\"",
                                                                                                                   '')
                                                 for i in
                                                 competes_spine_powerplants
                                                 if i['parameter_name'] == 'TECHTYPEU'}.items()))
        spine_powerplants_fuel_dict = dict(list({str(i['object_name']): str(i['parameter_value']) for i in
                                                 emlab_spine_powerplants if i['parameter_name'] == 'FUELNL'}.items()) +
                                           list({str(i['object_name']): str(i['parameter_value'].decode()).replace("\"",
                                                                                                                   '')
                                                 for i in
                                                 competes_spine_powerplants
                                                 if i['parameter_name'] == 'FUELEU'}.items()))
        emlab_spine_technologies = emlab_spinedb.query_object_parameter_values_by_object_class(
            'PowerGeneratingTechnologies')
        db_mcps = emlab_spinedb.query_object_parameter_values_by_object_class('MarketClearingPoints')
        db_emlab_powerplantdispatchplans = emlab_spinedb.query_object_parameter_values_by_object_class(
            'PowerPlantDispatchPlans')
        capacity_market_participating_technologies_peryear = get_participating_technologies_in_capacity_market(
            db_emlab_powerplantdispatchplans, years_to_generate, years_emlab, emlab_spine_powerplants)
    finally:
        competes_spinedb.close_connection()
        emlab_spinedb.close_connection()
    print('Done')

    # Generate plots
    print('Start generating plots per year')
    for year in years_to_generate:
        print('Preparing and plotting for year ' + str(year))
        path_and_filename_dispatch = path_to_competes_results + '/' + filename_to_load_dispatch.replace('?', str(year))
        path_and_filename_investments = path_to_competes_results + '/' + filename_to_load_investment.replace('?',
                                                                                                             str(year + look_ahead))

        # Preparing Data
        investment_sums, nl_investment_sums = prepare_investment_and_decom_data(path_and_filename_investments,
                                                                                investment_sums,
                                                                                years_to_generate, year,
                                                                                spine_powerplants_tech_dict,
                                                                                spine_powerplants_fuel_dict,
                                                                                emlab_spine_technologies,
                                                                                look_ahead, nl_investment_sums)
        vre_nl_installed_capacity = prepare_vre_investment_data(path_and_filename_investments,
                                                                vre_nl_installed_capacity,
                                                                years_to_generate, year)
        co2_emission_sums = prepare_co2_emission_data(path_and_filename_dispatch, co2_emission_sums, years_to_generate,
                                                      year)
        annual_installed_capacity = prepare_annual_installed_capacity(path_and_filename_dispatch,
                                                                      spine_powerplants_tech_dict,
                                                                      annual_installed_capacity, year,
                                                                      years_to_generate)

        # Plots
        hourly_nl_balance_df, hourly_nl_balance_demand = plot_hourly_nl_balance(path_and_filename_dispatch,
                                                                                path_to_plots, year)

        # Another prepare data
        annual_balance = prepare_annual_nl_balance(hourly_nl_balance_df, annual_balance, years_to_generate, year)

        # More plots
        load_duration_curves = plot_and_prepare_load_duration_curve(hourly_nl_balance_demand, year, path_to_plots,
                                                                    load_duration_curves)
        residual_load_curves = plot_and_prepare_residual_load_duration_curve(hourly_nl_balance_demand,
                                                                             hourly_nl_balance_df, year,
                                                                             path_to_plots, residual_load_curves)
        hourly_nodal_prices_df = plot_hourly_nodal_prices(path_and_filename_dispatch, year, path_to_plots)
        price_duration_curves = plot_and_prepare_hourly_nodal_price_duration_curve(hourly_nodal_prices_df, year,
                                                                                   path_to_plots,
                                                                                   price_duration_curves)
        # plot_nl_unit_generation(path_and_filename_dispatch, year, path_to_plots)
        plt.close('all')

    print('Plotting prepared data')
    plot_co2_emissions(co2_emission_sums, years_to_generate, path_to_plots)
    plot_nl_investments(nl_investment_sums, years_to_generate, path_to_plots, look_ahead)
    plot_investments(investment_sums, years_to_generate, path_to_plots, look_ahead)
    plot_vre_nl_installed_capacity(vre_nl_installed_capacity, years_to_generate, path_to_plots)
    plot_annual_balances(annual_balance, years_to_generate, path_to_plots)
    plot_annual_installed_capacity(annual_installed_capacity, years_to_generate, path_to_plots)
    plot_mcps_with_filter(db_mcps, 'CO2Auction', years_to_generate, path_to_plots, 'NL CO2 Market Clearing Prices',
                          'NL CO2 Market Clearing Prices.png', 'Price (Euro / ton CO2)', None)
    plot_mcps_with_filter(db_mcps, 'DutchCapacityMarket', years_to_generate, path_to_plots, 'NL Capacity Market Prices',
                          'NL Capacity Market Prices.png', 'Price (Euro / MW)', [0, 75e3])

    plot_combined_curves(residual_load_curves, 'NL Residual Load Duration Curves', 'Residual Load (MWh)', path_to_plots,
                         2000000)
    plot_combined_curves(load_duration_curves, 'NL Load Duration Curves', 'Load (MWh)', path_to_plots, 2000000)
    plot_combined_curves(price_duration_curves, 'NL Hourly Market Price Duration Curves', 'Price (Euro / MWh)',
                         path_to_plots, 250)

    plot_capacity_market_technologies(capacity_market_participating_technologies_peryear, path_to_plots,
                                      years_to_generate, 'NL Capacity Market technologies',
                                     'NL Capacity Market Technologies.png', 'Awarded capacity (MW)')
    plot_capacity_market_revenues(capacity_market_participating_technologies_peryear, db_mcps, path_to_plots,
                                  years_to_generate, years_emlab, 'NL Capacity Market Revenues',
                                 'NL Capacity Market revenues.png', 'CM Revenues (Million Euro)')

    # print('Showing plots...')
    # plt.show()
    plt.close('all')


print('===== Start Generating Plots =====')
generate_plots()
print('===== End Generating Plots =====')
