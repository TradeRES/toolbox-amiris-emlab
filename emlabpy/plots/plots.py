import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy_financial as npf
from util.spinedb_reader_writer import *

# # from copy import deepcopy
# # df = deepcopy(annual_operational_capacity)
import numpy as np
logging.basicConfig(level=logging.ERROR)
def plot_investments_and_NPV_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration,
                                           test_year,
                                           path_to_plots):
    print('investments and NPV')
    fig1, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(candidate_plants_project_value)
    ax2.plot(installed_capacity_per_iteration, 'o')
    ax1.set_xlabel('Iterations', fontsize='medium')
    ax1.set_ylabel('Project value', fontsize='medium')
    ax2.set_ylabel('Investments', fontsize='medium')
    ax1.set_title('Investments and NPV per iterations')
    ax1.legend(candidate_plants_project_value.columns.values.tolist(), fontsize='medium', loc='upper left',
               bbox_to_anchor=(1, 1.1))
    fig1.savefig(path_to_plots + '/' + 'Investments and NPV per iterations' + str(test_year)+ '.png', bbox_inches='tight', dpi=300)


def plot_annual_to_be_decommissioned_capacity(plot_annual_to_be_decommissioned_capacity, years_to_generate,
                                              path_to_plots):
    fig4, axs5 = plt.subplots()
    axs4 = plot_annual_to_be_decommissioned_capacity.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True,
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


def plot_investments(annual_installed_capacity, annual_invested_capacity, years_to_generate, path_to_plots):
    print('Create Investments plot')
    fig6, axs6 = plt.subplots(2, 1)
    annual_installed_capacity.plot.bar(ax=axs6[0],stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    annual_invested_capacity.plot.bar(ax=axs6[1],stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs6[0].set_axisbelow(True)
    axs6[1].set_xlabel('Years', fontsize='medium')
    axs6[0].set_ylabel('Invested capacity (MW)', fontsize='small')
    axs6[1].set_ylabel('Investments installed (MW)', fontsize='small')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs6[0].set_title('Capacity Investments per Technology')
    fig6.savefig(path_to_plots + '/' + 'Capacity Investments.png', bbox_inches='tight', dpi=300)


def plot_candidate_pp_project_value(candidate_plants_project_value, years_to_generate, path_to_plots):
    print('candidate project value')
    axs7 = candidate_plants_project_value.plot.line()
    axs7.set_axisbelow(True)
    plt.xlabel('Iterations', fontsize='medium')
    plt.ylabel('Project value', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs7.set_title('NPV Candidate power plants')
    fig7 = axs7.get_figure()
    fig7.savefig(path_to_plots + '/' + 'NPV Candidate power plants.png', bbox_inches='tight', dpi=300)

def power_plants_status(number_per_status , path_to_plots):
    print("power plants status")
    axs8 = number_per_status.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs8.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity per status (MW)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs8.set_title('Power plants status')
    fig8 = axs8.get_figure()
    fig8.savefig(path_to_plots + '/' + 'Power plants status per year.png', bbox_inches='tight', dpi=300)

def power_plants_last_year_status(power_plants_last_year_status , path_to_plots, last_year):
    plt.figure()
    axs9 = power_plants_last_year_status.plot.bar(stacked=True, rot=0, colormap='tab20', grid=True, legend=False)
    axs9.set_axisbelow(True)
    plt.xlabel('Years', fontsize='medium')
    plt.ylabel('Capacity per status (MW)', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs9.set_title('Power plants status' +str(last_year))
    fig9 = axs9.get_figure()
    fig9.savefig(path_to_plots + '/' + 'Power plants status ' +str(last_year) +'.png', bbox_inches='tight', dpi=300)

def plot_annual_operational_capacity(annual_operational_capacity, path_to_plots):
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

def plot_revenues_per_iteration(revenues_iteration, path_to_plots, last_year):
    print('Revenues per iteration')
    plt.figure()
    axs11 = revenues_iteration.plot()
    axs11.set_axisbelow(True)
    plt.xlabel('Iterations', fontsize='medium')
    plt.ylabel('Revenues', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs11.set_title('Average revenues per technologies for year'+str(last_year))
    fig11 = axs11.get_figure()
    fig11.savefig(path_to_plots + '/' + 'Technology Revenues per iteration ' +str(last_year) +'.png', bbox_inches='tight', dpi=300)

def plot_future_fuel_prices(future_fuel_prices,  path_to_plots):
    plt.figure()
    axs12 = future_fuel_prices.plot()
    axs12.set_axisbelow(True)
    plt.xlabel('years', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs12.set_title('Future Fuel prices per year')
    fig12 = axs12.get_figure()
    fig12.savefig(path_to_plots + '/' + 'Future Fuel prices per year.png', bbox_inches='tight', dpi=300)

def plot_screening_curve(yearly_costs,  path_to_plots, test_year):
    axs13 = yearly_costs.plot()
    axs13.set_axisbelow(True)
    plt.xlabel('years', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs13.set_title('Screening curve')
    fig13 = axs13.get_figure()
    fig13.savefig(path_to_plots + '/' + 'Screening curve (no CO2) ' +str(test_year) +'.png', bbox_inches='tight', dpi=300)

def plot_screening_curve_candidates(yearly_costs_candidates,  path_to_plots, future_year):
    axs14 = yearly_costs_candidates.plot()
    axs14.set_axisbelow(True)
    plt.xlabel('years', fontsize='medium')
    plt.ylabel('Prices', fontsize='medium')
    plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.grid()
    axs14.set_title('Screening curve candidate technologies')
    fig14 = axs14.get_figure()
    fig14.savefig(path_to_plots + '/' + 'Screening curve candidate technologies (no CO2) ' +str(future_year) +'.png', bbox_inches='tight', dpi=300)

def prepare_pp_status(years_to_generate,years_to_generate_and_build, reps, unique_technologies):
    annual_decommissioned_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate_and_build).fillna(0)
    annual_in_pipeline_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate_and_build).fillna(0)
    annual_invested_capacity = pd.DataFrame(columns=unique_technologies, index=years_to_generate_and_build).fillna(0)
    last_year =  years_to_generate[-1]

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
        elif pp.status == globalNames.power_plant_status_inPipeline:
            year = pp.commissionedYear - pp.technology.expected_leadtime - pp.technology.expected_permittime
            annual_in_pipeline_capacity.at[year, pp.technology.name] += pp.capacity
            annual_invested_capacity.at[pp.commissionedYear, pp.technology.name] += pp.capacity

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
        globalNames.power_plant_status_decommissioned: (annual_decommissioned_capacity).sum(axis = 1),
        globalNames.power_plant_status_inPipeline: (annual_in_pipeline_capacity).sum(axis = 1),
    }

    data_last_year = {
        globalNames.power_plant_status_decommissioned: (last_year_decommissioned).sum(axis = 1),
        globalNames.power_plant_status_inPipeline: (last_year_in_pipeline).sum(axis = 1),
        globalNames.power_plant_status_operational: (last_year_operational_capacity).sum(axis = 1),
        globalNames.power_plant_status_to_be_decommissioned: (last_year_to_be_decommissioned_capacity).sum(axis = 1),
        globalNames.power_plant_status_strategic_reserve: (last_year_strategic_reserve_capacity).sum(axis = 1),
        globalNames.power_plant_status_not_set: (last_year_not_set_status_capacity).sum(axis = 1)
    }

    number_per_status = pd.DataFrame(data_per_year)
    number_per_status_last_year =  pd.DataFrame(data_last_year)

    return  annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_invested_capacity, last_year_in_pipeline, last_year_decommissioned, \
            last_year_operational_capacity,last_year_to_be_decommissioned_capacity, \
           last_year_strategic_reserve_capacity,    number_per_status, number_per_status_last_year

def prepare_capacity_per_iteration(future_year, reps):
    unique_candidate_power_plants = reps.get_unique_candidate_technologies()
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
                candidate_plants_project_value[reps.candidatePowerPlants[name].technology.name] = pd.Series(
                    investment.project_value_year[str(future_year)])

    # preparing investments per iteration
    df_zeros = np.zeros(shape=(max_iteration, len(unique_candidate_power_plants)))
    installed_capacity_per_iteration = pd.DataFrame(df_zeros, columns=unique_candidate_power_plants)
    for invest_name, investment in reps.investments.items():
        if len(investment.invested_in_iteration) > 0:
            if str(future_year) in investment.invested_in_iteration.keys():
                index_invested_iteration = list(map(int, investment.invested_in_iteration[str(future_year)]))
                installed_capacity_per_iteration.loc[
                    index_invested_iteration, reps.candidatePowerPlants[invest_name].technology.name] = \
                    reps.candidatePowerPlants[invest_name].capacityTobeInstalled

    return installed_capacity_per_iteration, candidate_plants_project_value

def prepare_revenues_per_iteration(reps):
    for name_profits, profits in reps.financialPowerPlantReports.items():
        # each item is an iteration
        power_plants_revenues_per_iteration = pd.DataFrame(index = profits.profits_per_iteration_pp[str(0)], columns= ["zero"]).fillna(0)
        for iteration , profit_per_iteration in profits.profits_per_iteration.items():
            temporal = pd.DataFrame( profit_per_iteration, index = profits.profits_per_iteration_pp[iteration], columns= [int(iteration)])
            power_plants_revenues_per_iteration = power_plants_revenues_per_iteration.join(temporal)
        power_plants_revenues_per_iteration.drop("zero", axis=1, inplace=True)
        break #attention break after a year. each object is a year - > remove if more years are desired

    tech = []
    for pp in power_plants_revenues_per_iteration.index.values:
        tech.append(reps.power_plants[pp].technology.name)
    power_plants_revenues_per_iteration["tech"] = tech
    grouped = power_plants_revenues_per_iteration.groupby('tech').mean()
    return grouped

def prepare_future_fuel_prices(reps, years_to_generate):
    substances_calculated_prices = pd.DataFrame(index = years_to_generate, columns= ["zero"]).fillna(0)
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
    hours = np.array(list(range(1,8760)))
    agent = reps.energy_producers[reps.agent]
    wacc = (1 - agent.debtRatioOfInvestments) *  agent.equityInterestRate \
           + agent.debtRatioOfInvestments *  agent.loanInterestRate
    yearly_costs = pd.DataFrame(index = hours)
    for tech_name, tech in reps.power_generating_technologies.items():
        annual_cost_capital = npf.pmt(wacc, tech.expected_lifetime, -tech.investment_cost_eur_MW)
        capex =  annual_cost_capital + tech.fixed_operating_costs
        if tech.fuel == "":
            fuel_price = np.int64(0)
        else:
            calculatedPrices = tech.fuel.simulatedPrice.to_dict()
            df = pd.DataFrame(calculatedPrices['data'])
            df.set_index(0, inplace=True)
            fuel_price = df.at[str(year),1]
        opex = tech.variable_operating_costs*hours + fuel_price*hours
        total = capex + opex
        yearly_costs[tech_name] = total
    return yearly_costs

def prepare_screening_curves_candidates(reps, year):
    hours = np.array(list(range(1,8760)))
    agent = reps.energy_producers[reps.agent]
    wacc = (1 - agent.debtRatioOfInvestments) *  agent.equityInterestRate \
           + agent.debtRatioOfInvestments *  agent.loanInterestRate
    yearly_costs_candidates = pd.DataFrame(index = hours)
    candidate_technologies =  [i.technology.name for i in reps.candidatePowerPlants.values()]

    for tech_name, tech in reps.power_generating_technologies.items():
        if tech_name in candidate_technologies:
            annual_cost_capital = npf.pmt(wacc, tech.expected_lifetime, -tech.investment_cost_eur_MW)
            capex =  annual_cost_capital + tech.fixed_operating_costs
            if tech.fuel == "":
                fuel_price = np.int64(0)
            else:
                future_prices = tech.fuel.futurePrice.to_dict()
                df = pd.DataFrame(future_prices['data'])
                df.set_index(0, inplace=True)
                fuel_price = df.at[str(year),1]
            opex = tech.variable_operating_costs*hours + fuel_price*hours
            total = capex + opex
            yearly_costs_candidates[tech_name] = total
    return yearly_costs_candidates

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

    years_to_generate = list(range(reps.start_simulation_year, reps.current_year))
    years_to_generate_and_build =  list(range(reps.start_simulation_year, reps.current_year + reps.max_permit_build_time))
    years_ahead_to_generate = [x + reps.lookAhead for x in years_to_generate]
    df_zeros = np.zeros(shape=(len(years_to_generate), len(unique_technologies)))
    ticks = [i - reps.start_simulation_year for i in years_to_generate]
    annual_balance = dict()

    residual_load_curves = pd.DataFrame()
    load_duration_curves = pd.DataFrame()
    price_duration_curves = pd.DataFrame()

    spinedb_reader_writer.db.close_connection()
    print('Done')

    print('Start generating plots for first year')
    # graphs for the first year
    test_year = years_to_generate[0]
    future_year = test_year  + reps.lookAhead
    last_year = years_to_generate[-1]
    yearly_costs_candidates = prepare_screening_curves_candidates(reps, future_year)
    yearly_costs = prepare_screening_curves(reps, test_year)
    installed_capacity_per_iteration, candidate_plants_project_value = prepare_capacity_per_iteration(
        future_year, reps)
    print('Start generating plots for all years')
    #Preparing power plants revenues
    power_plants_revenues_per_iteration = prepare_revenues_per_iteration(reps)
    sorted_revenues_per_iteration = power_plants_revenues_per_iteration.T.sort_index()
    #Preparing power plants status
    # decommissioning is plotted according to the year when it is decided to get decommissioned

    annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_invested_capacity,\
    last_year_in_pipeline, last_year_decommissioned, \
    last_year_operational_capacity,last_year_to_be_decommissioned_capacity, \
    last_year_strategic_reserve_capacity,    number_per_status, number_per_status_last_year = \
        prepare_pp_status(years_to_generate, years_to_generate_and_build, reps, unique_technologies)

    # preparing fuel prices
    future_fuel_prices = prepare_future_fuel_prices(reps, years_to_generate)

    print('Plotting prepared data')
    plot_investments(annual_in_pipeline_capacity, annual_invested_capacity ,years_to_generate, path_to_plots)
    # plot_screening_curve_candidates(yearly_costs_candidates,  path_to_plots, test_year + + reps.lookAhead)
    # plot_screening_curve(yearly_costs,  path_to_plots, test_year)
    # plot_future_fuel_prices(future_fuel_prices,  path_to_plots)
    # plot_revenues_per_iteration(sorted_revenues_per_iteration,  path_to_plots, last_year)
    # plot_investments_and_NPV_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration,
    #                                        test_year,
    #                                        path_to_plots)
    #
    #
    # plot_decommissions(annual_decommissioned_capacity, years_to_generate, path_to_plots)
    # # last_year_strategic_reserve_capacity
    # plot_annual_operational_capacity(last_year_operational_capacity, path_to_plots)
    # plot_annual_to_be_decommissioned_capacity(last_year_to_be_decommissioned_capacity, years_to_generate, path_to_plots)
    # plot_candidate_pp_project_value(candidate_plants_project_value, years_to_generate, path_to_plots)
    # power_plants_status(number_per_status , path_to_plots)
    # power_plants_last_year_status(number_per_status_last_year , path_to_plots, last_year)

    print('Showing plots...')
    plt.show()
    plt.close('all')

print('===== Start Generating Plots =====')
generate_plots()
print('===== End Generating Plots =====')
