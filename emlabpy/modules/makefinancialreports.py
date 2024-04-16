import os

import numpy_financial as npf
import pandas as pd
from domain.powerplantDispatchPlan import PowerPlantDispatchPlan
from modules.defaultmodule import DefaultModule
from domain.financialReports import FinancialPowerPlantReport
from modules.strategicreserve_ger import StrategicReserveAssignment_ger
from modules.invest import Investmentdecision
from util import globalNames

import numpy as np


class CreatingFinancialReports(DefaultModule):
    """
    for for non decommissioned power plants calculate and save:
    spot market revenue, overall revenue, production, total costs, fixed costs,
    total profits, total profits with loans, irr, npv (considering results of current year)
    per agent also save
    fixed costs, commodity costs (variable costs), loans and downpayment costs,
    spot market revenues, capacity market revenues, strategic reserve payments
    """

    def __init__(self, reps):
        super().__init__("Creating Financial Reports", reps)
        self.agent = reps.energy_producers[reps.agent]
        self.start_tick_CS = 1
        if reps.current_tick == 0:
            reps.dbrw.stage_init_financial_results_structure()
            reps.dbrw.stage_init_cash_agent()
            reps.dbrw.stage_init_load_shedded()

    def act(self):
        self.prepare_percentage_load_shedded()
        self.createFinancialReportsForPowerPlantsAndTick()
        print("finished financial report")

    def createFinancialReportsForPowerPlantsAndTick(self):
        financialPowerPlantReports = []
        # for non decommissioned power plants
        for powerplant in self.reps.get_power_plants_by_status([globalNames.power_plant_status_operational,
                                                                globalNames.power_plant_status_to_be_decommissioned,
                                                                globalNames.power_plant_status_strategic_reserve,
                                                                ]):

            financialPowerPlantReport = self.reps.get_financial_report_for_plant(powerplant.name)
            if financialPowerPlantReport is None:
                # PowerPlantDispatchPlan not found, so create a new one
                financialPowerPlantReport = FinancialPowerPlantReport(powerplant.name)

            dispatch = self.reps.get_power_plant_electricity_dispatch(powerplant.id)
            if dispatch == None:
                dispatch = PowerPlantDispatchPlan(powerplant.id)
                dispatch.variable_costs = 0
                dispatch.accepted_amount = 0
                dispatch.revenues = 0

            financialPowerPlantReport.setTime(self.reps.current_tick)
            financialPowerPlantReport.setPowerPlant(powerplant.name)  # this can be ignored, its already in the name

            fixed_on_m_cost = powerplant.getActualFixedOperatingCost()
            financialPowerPlantReport.setFixedCosts(fixed_on_m_cost)  # saved as fixedCosts

            if powerplant.status == globalNames.power_plant_status_strategic_reserve:  # power plants in reserve dont get the dispatch revenues
                operator = self.reps.get_strategic_reserve_operator(self.reps.country)
                dispatch.variable_costs = StrategicReserveAssignment_ger.createCashFlowforSR(self, powerplant, operator)
            else:
                pass
            self.agent.CF_COMMODITY -= dispatch.variable_costs
            self.agent.CF_FIXEDOMCOST -= fixed_on_m_cost

            loans = powerplant.loan_payments_in_year + powerplant.downpayment_in_year
            # todo: there are no downpayments because its only for operational plants
            # # attention: this is only to check
            # if powerplant.downpayment_in_year> 0:
            #     print("downpayment is paid during construction. why is it paid here")
            fixed_and_variable_costs = - dispatch.variable_costs - fixed_on_m_cost  # without loans

            financialPowerPlantReport.setVariableCosts(dispatch.variable_costs)  # saved as variableCosts

            financialPowerPlantReport.totalCosts = fixed_and_variable_costs  # saved as totalCosts
            financialPowerPlantReport.setProduction(dispatch.accepted_amount)

            financialPowerPlantReport.setSpotMarketRevenue(dispatch.revenues)
            self.agent.CF_ELECTRICITY_SPOT += dispatch.revenues

            financialPowerPlantReport.setOverallRevenue(  # saved as overallRevenue
                financialPowerPlantReport.capacityMarketRevenues_in_year + dispatch.revenues)
            # total profits are used to decide for decommissioning saved as totalProfits

            if powerplant.status == globalNames.power_plant_status_strategic_reserve:  # power plants in reserve dont get the dispatch revenues
                operational_profit = financialPowerPlantReport.capacityMarketRevenues_in_year + fixed_and_variable_costs
                operational_profit_with_loans = operational_profit - loans
                if abs(operational_profit_with_loans) > 10:
                    print("WRONG CRM ")
                    print(operational_profit_with_loans)
                    raise Exception
            else:
                operational_profit = financialPowerPlantReport.capacityMarketRevenues_in_year + dispatch.revenues + fixed_and_variable_costs
                operational_profit_with_loans = operational_profit - loans

            self.agent.CF_CAPMARKETPAYMENT += financialPowerPlantReport.capacityMarketRevenues_in_year
            financialPowerPlantReport.totalProfits = operational_profit  # saved as totalProfits
            # total profits with loans are to calculate RES support. saved as totalProfitswLoans
            financialPowerPlantReport.totalProfitswLoans = operational_profit_with_loans
            irr, npv = self.getProjectIRR(powerplant, operational_profit, loans, self.agent)
            financialPowerPlantReport.irr = irr
            financialPowerPlantReport.npv = npv
            financialPowerPlantReports.append(financialPowerPlantReport)

        # modifying the IRR by technology
        if self.reps.change_IRR == True:
            self.modifyIRR()
            # modifying the IRR by technology
        if self.reps.capacity_remuneration_mechanism == "capacity_subscription":
            self.modify_CS_parameter_by_costs()
        # saving
        self.reps.dbrw.stage_financial_results(financialPowerPlantReports)
        self.reps.dbrw.stage_cash_agent(self.agent, self.reps.current_tick)

        if self.reps.capacity_remuneration_mechanism in ["strategic_reserve_ger", "strategic_reserve_swe",
                                                         "strategic_reserve"]:
            # Save the SR operator variables to the SR operator of the country
            self.reps.update_StrategicReserveOperator(self.reps.get_strategic_reserve_operator(self.reps.country))

    def modifyIRR(self):
        if self.reps.current_tick < 5:
            pass
        else:
            start = self.reps.current_tick - 4
            ticks_to_generate = list(range(start, self.reps.current_tick))
            irrs_per_tech_per_year = pd.DataFrame(index=ticks_to_generate).fillna(0)
            for technology_name, technology in self.reps.power_generating_technologies.items():
                powerplants_per_tech = self.reps.get_power_plants_by_technology(technology_name)
                irrs_per_year = pd.DataFrame(index=ticks_to_generate).fillna(0)
                for plant in powerplants_per_tech:
                    irr_per_plant = self.reps.get_irrs_for_plant(plant.name)
                    if irr_per_plant is None:
                        pass
                    else:
                        irrs_per_year[plant.name] = irr_per_plant

                if irrs_per_year.size != 0:
                    irrs_per_tech_per_year[technology_name] = np.nanmean(irrs_per_year, axis=1)

            irrs_in_last_years = irrs_per_tech_per_year.mean()
            for technology_name, averageirr in irrs_in_last_years.items():
                if pd.isna(averageirr):
                    pass
                else:
                    decrease = (averageirr - 0.1) * 0.1
                    old_value = self.reps.power_generating_technologies[technology_name].interestRate
                    if averageirr < 0.01:
                        pass  # and IRR of 10% is normal
                    elif old_value - decrease < 0:
                        new_value = 0.05
                    elif old_value - decrease > 0.15:
                        new_value = 0.15
                    else:
                        new_value = old_value - decrease
                    print("decrease IRR of " + technology_name + " by " + str(decrease))
                    self.reps.power_generating_technologies[technology_name].interestRate = new_value
                    self.reps.dbrw.stage_new_irr(self.reps.power_generating_technologies[technology_name])

    def getProjectIRR(self, pp, operational_profit_withFixedCosts, loans, agent):
        totalInvestment = pp.getActualInvestedCapital()
        depreciationTime = pp.technology.depreciation_time
        buildingTime = pp.technology.expected_leadtime
        # get average profits per technology
        equity = (1 - agent.debtRatioOfInvestments)
        if equity == 0:
            equalTotalDownPaymentInstallment = 0
        else:
            equalTotalDownPaymentInstallment = (totalInvestment * equity) / buildingTime
        # the rest payment was considered in the loans
        debt = totalInvestment * (agent.debtRatioOfInvestments)
        restPayment = debt / depreciationTime
        investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]

        # print("total investment cost in MIll", totalInvestment / 1000000)
        if self.reps.npv_with_annuity == True:
            for i in range(0, buildingTime):
                investmentCashFlow[i] = - equalTotalDownPaymentInstallment
            for i in range(buildingTime, depreciationTime + buildingTime):
                investmentCashFlow[i] = operational_profit_withFixedCosts - loans
        else:
            for i in range(0, buildingTime):
                investmentCashFlow[i] = - equalTotalDownPaymentInstallment
            for i in range(buildingTime, depreciationTime + buildingTime):
                investmentCashFlow[i] = operational_profit_withFixedCosts - restPayment

        npv = npf.npv(pp.technology.interestRate, investmentCashFlow)

        IRR = npf.irr(investmentCashFlow)
        if pd.isna(IRR):
            return IRR, npv
        else:
            return round(IRR, 4), npv

    def prepare_percentage_load_shedded(self):
        """
        prepare the percentage of load shedded for each load shedder. reading results for current year.
        :return:
        """
        df = pd.read_csv(globalNames.hourly_generation_per_group_path)
        hourly_load_shedders = pd.DataFrame()
        for unit in df.columns.values:
            if unit[0:4] == "unit":
                hourly_load_shedders[unit[5:]] = df[unit]

        production_not_shedded_MWh = pd.DataFrame()
        total_yearly_electrolysis_consumption = pd.DataFrame()
        total_yearly_hydrogen_input_demand = self.reps.loadShedders[
                                                 "hydrogen"].ShedderCapacityMW * self.reps.hours_in_year
        hydrogen_input_demand = [self.reps.loadShedders["hydrogen"].ShedderCapacityMW] * self.reps.hours_in_year
        total_load_shedded = pd.DataFrame()
        year = self.reps.current_year
        for name, values in self.reps.loadShedders.items():
            test_list = [int(i) for i in hourly_load_shedders.columns.values]
            hourly_load_shedders.columns = test_list
            if name == "hydrogen":  # hydrogen is the lowest load shedder
                id_shedder = 8888888
                total_load_shedded[name] = hourly_load_shedders[(id_shedder)]
                yearly_hydrogen_shedded = total_load_shedded[name].sum()
                production_not_shedded_MWh.at[year, "hydrogen_produced"] = (
                            total_yearly_hydrogen_input_demand - yearly_hydrogen_shedded)
                production_not_shedded_MWh.at[year, "hydrogen_percentage_produced"] = ((
                                                                                                   total_yearly_hydrogen_input_demand - yearly_hydrogen_shedded) / total_yearly_hydrogen_input_demand) * 100
                total_yearly_electrolysis_consumption[year] = hydrogen_input_demand - total_load_shedded[name]
            else:
                id_shedder = int(name) * 100000
                total_load_shedded[name] = hourly_load_shedders[(id_shedder)]
        #        load_shedded_per_group_MWh.at[year, name] = hourly_load_shedders[(id_shedder)].sum()
        #        load_shedded_per_group_percentage.at[year, name] = (hourly_load_shedders[(id_shedder)].sum() / total_yearly_electrolysis_consumption[year].sum()) * 10
        print(total_load_shedded.where(total_load_shedded > 0).count())
        realized_curtailments = total_load_shedded.where(total_load_shedded > 0).sum()
        self.reps.dbrw.stage_load_shedders_realized_lole(realized_curtailments, self.reps.current_tick)
        if self.reps.current_tick >= self.start_tick_CS:
            for name, values in self.reps.loadShedders.items():
                print(name + "-" + str(realized_curtailments[name]))
                self.reps.loadShedders[name].realized_rs[self.reps.current_tick] = realized_curtailments[name]

    def modify_CS_parameter_by_RS(self):
        if self.reps.current_tick < self.start_tick_CS:
            self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, self.reps.current_year + 1)
        else:
            """
            increase the percentage of load shedded by the difference between the realized LOLE and the reliability standard
            """
            ticks_to_generate = list(range(self.reps.current_tick - 1, self.reps.current_tick + 1))
            ascending_load_shedders_no_hydrogen = self.reps.get_sorted_load_shedders_by_increasing_VOLL_no_hydrogen(
                reverse=False)
            last = len(ascending_load_shedders_no_hydrogen) - 1
            minimumvalue_per_group = 0.01
            for count, load_shedder in enumerate(ascending_load_shedders_no_hydrogen):
                if count < last:
                    print(load_shedder.name + "+++++++++++++++++++++++++++++++" + str(load_shedder.percentageLoad))
                    averageLOLE = load_shedder.realized_rs[ticks_to_generate].mean()
                    reliability_standard = load_shedder.reliability_standard
                    if pd.isna(averageLOLE):
                        pass
                    else:
                        unsubscribe = round((averageLOLE - reliability_standard) / reliability_standard / 10, 2)
                        if unsubscribe <= 0:
                            pass # does not want to subscribe more.
                        else:  # unsubscribe is positive
                            print(unsubscribe)
                            new_value = load_shedder.percentageLoad - unsubscribe  # smaller load percentage
                            if new_value < minimumvalue_per_group:  # cannot decrease more than the available value
                                unsubscribe = load_shedder.percentageLoad - minimumvalue_per_group
                                new_value = minimumvalue_per_group
                            else:
                                pass
                            load_shedder.percentageLoad = new_value
                            ascending_load_shedders_no_hydrogen[last].percentageLoad = \
                            ascending_load_shedders_no_hydrogen[last].percentageLoad + unsubscribe
                            print(ascending_load_shedders_no_hydrogen[last].name + " new value " + str( ascending_load_shedders_no_hydrogen[last].percentageLoad))

            for count, load_shedder in enumerate(ascending_load_shedders_no_hydrogen):
                if count < last:
                    print(load_shedder.name + "---------------------------------" + str(load_shedder.percentageLoad))
                    averageLOLE = load_shedder.realized_rs[ticks_to_generate].mean()
                    reliability_standard = load_shedder.reliability_standard
                    if pd.isna(averageLOLE):
                        pass
                    else:
                        unsubscribe = round((averageLOLE - reliability_standard) / reliability_standard / 100, 2)
                        if unsubscribe <= 0:
                            new_value = load_shedder.percentageLoad - unsubscribe  # larger load percentage
                        else:  # unsubscribe is positive
                            continue
                        print("addSubscribed" + str(unsubscribe))
                        load_shedder.percentageLoad = new_value
                        print(
                            load_shedder.name + "---------------------------------" + str(load_shedder.percentageLoad))
                        """
                        if there subscription load is lower than the needed load, then take the difference from the next load shedder
                        """
                        if unsubscribe > 0:
                            print(ascending_load_shedders_no_hydrogen[last].name + " adding group " + str(  ascending_load_shedders_no_hydrogen[last].percentageLoad))
                            ascending_load_shedders_no_hydrogen[last].percentageLoad = \
                            ascending_load_shedders_no_hydrogen[last].percentageLoad + unsubscribe
                        else:
                            if ascending_load_shedders_no_hydrogen[
                                last].percentageLoad + unsubscribe < minimumvalue_per_group:
                                descending_load_shedders_no_hydrogen = self.reps.get_sorted_load_shedders_by_increasing_VOLL_no_hydrogen(
                                    reverse=True)
                                last = len(descending_load_shedders_no_hydrogen) - 1
                                for countdescending, descending_load_shedder in enumerate(
                                        descending_load_shedders_no_hydrogen):
                                    if descending_load_shedder.percentageLoad + unsubscribe < minimumvalue_per_group:
                                        unsubscribe = unsubscribe + descending_load_shedder.percentageLoad - minimumvalue_per_group
                                        ascending_load_shedders_no_hydrogen[
                                            last].percentageLoad = minimumvalue_per_group
                                        print(str(descending_load_shedder.percentageLoad) + " part from group " + descending_load_shedder.name)
                                        last = last - 1
                                    else:
                                        ascending_load_shedders_no_hydrogen[
                                            last].percentageLoad = descending_load_shedder.percentageLoad + unsubscribe
                                        print(str(ascending_load_shedders_no_hydrogen[last].percentageLoad) + "  group " +
                                            ascending_load_shedders_no_hydrogen[last].name)
                                        break
                            else:
                                print(str(
                                    ascending_load_shedders_no_hydrogen[last].percentageLoad) + " from  group enough " +
                                      ascending_load_shedders_no_hydrogen[last].name)
                                ascending_load_shedders_no_hydrogen[last].percentageLoad = \
                                ascending_load_shedders_no_hydrogen[last].percentageLoad + unsubscribe

            """
            checking that the percentage of load shedded is not higher than 100%
            """
            lst = []
            for load_shedder_name, load_shedder in self.reps.loadShedders.items():
                print(load_shedder.name + "-------------" + str(load_shedder.percentageLoad))
                lst.append(load_shedder.percentageLoad)
            if sum(lst) > 1.02:
                print("percentage of load shedded is higher than 101%")
                raise Exception
            elif sum(lst) < .98:
                print("percentage of load shedded is lower than 99%")
                raise Exception
            else:
                pass

            self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, self.reps.current_year + 1)

    def modify_CS_parameter_by_costs(self):
        """
        modify load percentage for Capacity Subscription according to the difference of costs of subscribing and not subscribing
        """
        if self.reps.current_tick < self.start_tick_CS:
            self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, self.reps.current_year + 1)
        else:
            ticks_to_generate = list(range(self.reps.current_tick - 1, self.reps.current_tick + 1))
            capacity_market = self.reps.get_capacity_market_in_country(self.reps.country, long_term=False)
            last_year_prices = []
            for t in ticks_to_generate:
                last_year_prices.append(
                    self.reps.get_market_clearing_point_price_for_market_and_time(capacity_market.name,
                                                                                  t + capacity_market.forward_years_CM))
            capacity_market_price = np.mean(last_year_prices)
            peak_demand = self.reps.get_peak_future_demand_by_year(self.reps.current_year)
            ascending_load_shedders_no_hydrogen = self.reps.get_sorted_load_shedders_by_increasing_VOLL_no_hydrogen(
                reverse=False)
            last = len(ascending_load_shedders_no_hydrogen) - 1
            minimumvalue_per_group = 0.01
            for count, load_shedder in enumerate(ascending_load_shedders_no_hydrogen):
                if count < last:
                    print(load_shedder.name + "+++++++++++++++++++++++++++++++" + str(load_shedder.percentageLoad))
                    averageENS = load_shedder.realized_rs[ticks_to_generate].mean()
                    Capacity_market_costs = capacity_market_price * peak_demand * load_shedder.percentageLoad

                    if pd.isna(load_shedder.percentageLoad):
                        raise Exception
                    if Capacity_market_costs == 0:
                        continue
                    else:
                        non_subscription_costs = averageENS * load_shedder.VOLL * self.reps.factor_fromVOLL
                        if pd.isna(averageENS):
                            continue
                        else:
                            unsubscribe = round(
                                (non_subscription_costs - Capacity_market_costs) / (Capacity_market_costs)*10,
                                3)  # Eur/Mwh
                            if unsubscribe <= 0:
                                pass
                            else:  # higher costs of non subscription
                                new_value = load_shedder.percentageLoad - unsubscribe  # smaller load percentage
                                if new_value < minimumvalue_per_group:  # cannot decrease more than the available value
                                    unsubscribe = load_shedder.percentageLoad - minimumvalue_per_group
                                    new_value = minimumvalue_per_group
                                else:
                                    pass
                                load_shedder.percentageLoad = new_value
                                ascending_load_shedders_no_hydrogen[last].percentageLoad = \
                                ascending_load_shedders_no_hydrogen[last].percentageLoad + unsubscribe



            for count, load_shedder in enumerate(ascending_load_shedders_no_hydrogen):
                if count < last:
                    print(load_shedder.name + "---------------------------------" + str(load_shedder.percentageLoad))
                    averageENS = load_shedder.realized_rs[ticks_to_generate].mean()
                    Capacity_market_costs = capacity_market_price * peak_demand * load_shedder.percentageLoad
                    if pd.isna(load_shedder.percentageLoad):
                        raise Exception
                    if Capacity_market_costs == 0:
                        continue
                    else:
                        non_subscription_costs = averageENS * load_shedder.VOLL * self.reps.factor_fromVOLL
                        if pd.isna(averageENS):
                            continue
                        else:
                            unsubscribe = (non_subscription_costs - Capacity_market_costs) / Capacity_market_costs
                            if unsubscribe <= 0:
                                unsubscribe = round(unsubscribe / 10,
                                                    3)  # when there are less shortages the consumers unsubscribe slower
                                new_value = load_shedder.percentageLoad - unsubscribe  # larger load percentage
                            else:  # unsubscribe is positive
                                continue
                            load_shedder.percentageLoad = new_value
                            print(load_shedder.name + "---------------------------------" + str(
                                load_shedder.percentageLoad))
                            """
                            if there subscription load is lower than the needed load, then take the difference from the next load shedder
                            """
                            if unsubscribe > 0:
                                ascending_load_shedders_no_hydrogen[last].percentageLoad = \
                                ascending_load_shedders_no_hydrogen[last].percentageLoad + unsubscribe
                            else:
                                if ascending_load_shedders_no_hydrogen[
                                    last].percentageLoad + unsubscribe < minimumvalue_per_group:
                                    descending_load_shedders_no_hydrogen = self.reps.get_sorted_load_shedders_by_increasing_VOLL_no_hydrogen(
                                        reverse=True)
                                    last = len(descending_load_shedders_no_hydrogen) - 1
                                    for countdescending, descending_load_shedder in enumerate(
                                            descending_load_shedders_no_hydrogen):
                                        if descending_load_shedder.percentageLoad + unsubscribe < minimumvalue_per_group:
                                            unsubscribe = unsubscribe + descending_load_shedder.percentageLoad - minimumvalue_per_group
                                            ascending_load_shedders_no_hydrogen[
                                                last].percentageLoad = minimumvalue_per_group
                                            last = last - 1
                                        else:
                                            ascending_load_shedders_no_hydrogen[
                                                last].percentageLoad = descending_load_shedder.percentageLoad + unsubscribe
                                            break
                                else:
                                    ascending_load_shedders_no_hydrogen[last].percentageLoad = \
                                    ascending_load_shedders_no_hydrogen[last].percentageLoad + unsubscribe

            """
            checking that the percentage of load shedded is not higher than 100%
            """
            lst = []
            for load_shedder_name, load_shedder in self.reps.loadShedders.items():
                print(load_shedder.name + "-------------" + str(load_shedder.percentageLoad))
                lst.append(load_shedder.percentageLoad)
            if sum(lst) > 1.02:
                print("percentage of load shedded is higher than 101%")
                raise Exception
            elif sum(lst) < .98:
                print("percentage of load shedded is lower than 99%")
                raise Exception
            else:
                pass

            self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, self.reps.current_year + 1)
