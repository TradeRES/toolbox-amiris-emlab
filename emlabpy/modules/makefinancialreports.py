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

        total_load_shedded = self.prepare_percentage_load_shedded()
        # if self.reps.capacity_remuneration_mechanism == globalNames.capacity_subscription :#and self.reps.current_tick >0:
        #     self.assign_LOLE_by_subscription(total_load_shedded)
        # else:
        #     # load percentage doesnt change
        self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, self.reps.current_year + 1)
        self.createFinancialReportsForPowerPlantsAndTick()
        # modifying the IRR by technology
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
            ticks_to_generate = list(range(self.reps.current_tick - 4, self.reps.current_tick))
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
                    decrease = (averageirr)/ 10
                    old_irr = self.reps.power_generating_technologies[technology_name].interestRate
                    if averageirr < 0.01:
                        continue   # and IRR of 10% is normal
                    elif old_irr - decrease < 0.04:
                        new_value = 0.04
                    elif old_irr - decrease > 0.15:
                        new_value = 0.15
                    else:
                        new_value = old_irr - decrease
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

        npv = npf.npv(agent.equityInterestRate, investmentCashFlow)

        IRR = npf.irr(investmentCashFlow)
        if pd.isna(IRR):
            return IRR, npv
        else:
            return round(IRR, 4), npv

    def prepare_percentage_load_shedded(self):
        """
        calculate LOLE by load shedder.
        """
        df = pd.read_csv(globalNames.hourly_generation_per_group_path)
        hourly_load_shedders = pd.DataFrame()
        for unit in df.columns.values:
            if unit[0:4] == "unit":
                hourly_load_shedders[unit[5:]] = df[unit]

        total_load_shedded = pd.DataFrame()
        for name, values in self.reps.loadShedders.items():
            test_list = [int(i) for i in hourly_load_shedders.columns.values]
            hourly_load_shedders.columns = test_list
            if name == "hydrogen":  # hydrogen is the lowest load shedder
                pass
            else:
                id_shedder = int(name) * 100000
                total_load_shedded[name] = hourly_load_shedders[(id_shedder)]

        realized_LOLE = total_load_shedded.where(total_load_shedded > 0).sum()
        print(realized_LOLE)
        self.reps.dbrw.stage_load_shedders_realized_lole(realized_LOLE, self.reps.current_tick)

        return total_load_shedded

    def assign_LOLE_by_subscription(self, total_load_shedded):
        """
        CS consumer descending by WTP
        """
        ENS_per_LS = total_load_shedded.sum(axis=0)
        if ENS_per_LS["1"] > 0:
            print("subscribed consumers are curtailed!!!!!!!!!!!")
        ENS_per_LS.drop("1", inplace=True)  # the first year there could be too much ENS due to no capacity market.
        ENS = ENS_per_LS.sum()
        peak_demand = self.reps.get_realized_peak_demand_by_year(self.reps.current_year)
        unsubcribed_volume = sum([i.percentageLoad for i in self.reps.loadShedders.values() if i.name != "1"])
        volume_unsubscribed = unsubcribed_volume * peak_demand
        if volume_unsubscribed == 0:
            average_LOLE_unsubscribed = ENS
        else:
            average_LOLE_unsubscribed = ENS / volume_unsubscribed
        # MWH/MW
        print("average_LOLE_unsubscribed [h]" + str(average_LOLE_unsubscribed))
        if average_LOLE_unsubscribed > 1.5:
            average_LOLE_unsubscribed = 1.5
        elif average_LOLE_unsubscribed < 0.5:
            average_LOLE_unsubscribed = 0.5
        else:
            pass
        subscribed_percentage = []
        for consumer in self.reps.get_CS_consumer_descending_WTP():
            print("--------------------------"+consumer.name)
            avoided_costs_non_subscription =  consumer.WTP  *  average_LOLE_unsubscribed    # H * Eur/MWH = Eur/MW
            """
            estimating bids with intertia
            In the first year the bid is the avoided costs, in the next years the bids are changed with inertia
            """
            if self.reps.current_tick == 0:
                bid = avoided_costs_non_subscription # reducing to half bids because of initializing the last year bids were 0
                self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, self.reps.current_year + 1)
                self.reps.dbrw.stage_consumer_subscribed_yearly(consumer.name, consumer.subscribed_yearly[self.reps.current_tick] , self.reps.current_tick + 1)
                #self.reps.dbrw.stage_consumers_bids(consumer.name, bid, self.reps.current_tick)

            else:
                last_year_bid  =  self.reps.get_last_year_bid(consumer.name)
                bid = last_year_bid + 0.2 * ( avoided_costs_non_subscription - last_year_bid)
                #bid = avoided_costs_non_subscription
                consumer.bid = bid
                #self.reps.dbrw.stage_consumers_bids(consumer.name, consumer.bid, self.reps.current_tick)
                """
                changing consumer subscription percentage 
                for the first year there is no estimation of a change in next year subcription
                """
                capacity_market = self.reps.get_capacity_market_in_country(self.reps.country, long_term=False)
                capacity_market_price = self.reps.get_market_clearing_point_price_for_market_and_time(capacity_market.name,
                                                                                                  self.reps.current_tick - 1 + capacity_market.forward_years_CM)
                if capacity_market_price == 0 and bid ==0:
                    increase = 0
                elif capacity_market_price == 0 and bid !=0:
                    increase = 1
                else:
                    increase = (bid - capacity_market_price)/(capacity_market_price)
                if pd.isna(increase):
                    raise Exception
                print("increase" + str(increase) )
                next_year_subscription = round(consumer.subscribed_yearly[self.reps.current_tick - 1]  +  increase,2)
                if next_year_subscription >  consumer.max_subscribed_percentage:
                    next_year_subscription = consumer.max_subscribed_percentage
                    print("passed max subscribed percentage")
                elif next_year_subscription < 0:
                    next_year_subscription = 0
                    print("passed min subscribed percentage")
                    print("percentage_load")
                print(next_year_subscription)
                subscribed_percentage.append(next_year_subscription)
                self.reps.dbrw.stage_consumer_subscribed_yearly(consumer.name, next_year_subscription, self.reps.current_tick + 1)

        if self.reps.current_tick > 0:
            load_shedders_not_hydrogen = self.reps.get_load_shedders_not_hydrogen()
            voluntary_consumers = sum([i.percentageLoad for i in load_shedders_not_hydrogen if i.VOLL < 4000])
            total_subcribed_percentage = round(sum(subscribed_percentage),2)
            percentage_unsubscribed = 1 - total_subcribed_percentage - voluntary_consumers
            if percentage_unsubscribed < -0.01:
                print("percentage_unsubscribed is negative")
                raise Exception
            self.reps.loadShedders["1"].percentageLoad = round(total_subcribed_percentage, 2)
            print("subscribed")
            print(total_subcribed_percentage)
            self.reps.loadShedders["2"].percentageLoad = round(percentage_unsubscribed, 2)
            print("unsubscribed")
            print(percentage_unsubscribed)
            self.saving_load_shedders_percentage(self.reps.current_year + 1)

    def saving_load_shedders_percentage(self, year ):
        """
        checking that the percentage of load shedded is not higher than 100%
        """
        lst = []
        for load_shedder_name, load_shedder in self.reps.loadShedders.items():
            print(load_shedder.name + "-------------" + str(load_shedder.percentageLoad))
            lst.append(load_shedder.percentageLoad)
        if sum(lst) > 1.01:
            print("percentage of load shedded is higher than 101%")
            raise Exception
        elif sum(lst) < .99:
            print("percentage of load shedded is lower than 99%")
            raise Exception
        else:
            pass

        self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, year )

    # def modify_CS_parameter_by_RS(self):
    #     if self.reps.current_tick < self.start_tick_CS:
    #         self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, self.reps.current_year + 1)
    #     else:
    #         """
    #         increase the percentage of load shedded by the difference between the realized LOLE and the reliability standard
    #         """
    #         ticks_to_generate = list(range(self.reps.current_tick - 1, self.reps.current_tick))
    #         ascending_load_shedders_no_hydrogen = self.reps.get_sorted_load_shedders_by_increasing_VOLL_no_hydrogen(
    #             reverse=False)
    #         last = len(ascending_load_shedders_no_hydrogen) - 1
    #         minimumvalue_per_group = 0.01
    #         for count, load_shedder in enumerate(ascending_load_shedders_no_hydrogen):
    #             if count < last:
    #                 print(load_shedder.name + "+++++++++++++++++++++++++++++++" + str(load_shedder.percentageLoad))
    #                 averageLOLE = load_shedder.realized_LOLE[ticks_to_generate].mean()
    #                 reliability_standard = load_shedder.reliability_standard
    #                 if pd.isna(averageLOLE):
    #                     pass
    #                 else:
    #                     unsubscribe = round((averageLOLE - reliability_standard) / reliability_standard / 10, 2)
    #                     if unsubscribe <= 0:
    #                         pass  # does not want to subscribe more.
    #                     else:  # unsubscribe is positive
    #                         print(unsubscribe)
    #                         new_value = load_shedder.percentageLoad - unsubscribe  # smaller load percentage
    #                         if new_value < minimumvalue_per_group:  # cannot decrease more than the available value
    #                             unsubscribe = load_shedder.percentageLoad - minimumvalue_per_group
    #                             new_value = minimumvalue_per_group
    #                         else:
    #                             pass
    #                         load_shedder.percentageLoad = new_value
    #                         ascending_load_shedders_no_hydrogen[last].percentageLoad = \
    #                             ascending_load_shedders_no_hydrogen[last].percentageLoad + unsubscribe
    #                         print(ascending_load_shedders_no_hydrogen[last].name + " new value " + str(
    #                             ascending_load_shedders_no_hydrogen[last].percentageLoad))
    #
    #         for count, load_shedder in enumerate(ascending_load_shedders_no_hydrogen):
    #             if count < last:
    #                 print(load_shedder.name + "---------------------------------" + str(load_shedder.percentageLoad))
    #                 averageLOLE = load_shedder.realized_LOLE[ticks_to_generate].mean()
    #                 reliability_standard = load_shedder.reliability_standard
    #                 if pd.isna(averageLOLE):
    #                     pass
    #                 else:
    #                     unsubscribe = round((averageLOLE - reliability_standard) / reliability_standard / 100, 2)
    #                     if unsubscribe <= 0:
    #                         new_value = load_shedder.percentageLoad - unsubscribe  # larger load percentage
    #                     else:  # unsubscribe is positive
    #                         continue
    #                     print("addSubscribed" + str(unsubscribe))
    #                     load_shedder.percentageLoad = new_value
    #                     print(
    #                         load_shedder.name + "---------------------------------" + str(load_shedder.percentageLoad))
    #                     """
    #                     if there subscription load is lower than the needed load, then take the difference from the next load shedder
    #                     """
    #                     if unsubscribe > 0:
    #                         print(ascending_load_shedders_no_hydrogen[last].name + " adding group " + str(
    #                             ascending_load_shedders_no_hydrogen[last].percentageLoad))
    #                         ascending_load_shedders_no_hydrogen[last].percentageLoad = \
    #                             ascending_load_shedders_no_hydrogen[last].percentageLoad + unsubscribe
    #                     else:
    #                         if ascending_load_shedders_no_hydrogen[
    #                             last].percentageLoad + unsubscribe < minimumvalue_per_group:
    #                             descending_load_shedders_no_hydrogen = self.reps.get_sorted_load_shedders_by_increasing_VOLL_no_hydrogen(
    #                                 reverse=True)
    #                             last = len(descending_load_shedders_no_hydrogen) - 1
    #                             for countdescending, descending_load_shedder in enumerate(
    #                                     descending_load_shedders_no_hydrogen):
    #                                 if descending_load_shedder.percentageLoad + unsubscribe < minimumvalue_per_group:
    #                                     unsubscribe = unsubscribe + descending_load_shedder.percentageLoad - minimumvalue_per_group
    #                                     ascending_load_shedders_no_hydrogen[
    #                                         last].percentageLoad = minimumvalue_per_group
    #                                     print(
    #                                         str(descending_load_shedder.percentageLoad) + " part from group " + descending_load_shedder.name)
    #                                     last = last - 1
    #                                 else:
    #                                     ascending_load_shedders_no_hydrogen[
    #                                         last].percentageLoad = descending_load_shedder.percentageLoad + unsubscribe
    #                                     print(
    #                                         str(ascending_load_shedders_no_hydrogen[last].percentageLoad) + "  group " +
    #                                         ascending_load_shedders_no_hydrogen[last].name)
    #                                     break
    #                         else:
    #                             print(str(
    #                                 ascending_load_shedders_no_hydrogen[last].percentageLoad) + " from  group enough " +
    #                                   ascending_load_shedders_no_hydrogen[last].name)
    #                             ascending_load_shedders_no_hydrogen[last].percentageLoad = \
    #                                 ascending_load_shedders_no_hydrogen[last].percentageLoad + unsubscribe
    #
    #         """
    #         checking that the percentage of load shedded is not higher than 100%
    #         """
    #         lst = []
    #         for load_shedder_name, load_shedder in self.reps.loadShedders.items():
    #             print(load_shedder.name + "-------------" + str(load_shedder.percentageLoad))
    #             lst.append(load_shedder.percentageLoad)
    #         if sum(lst) > 1.02:
    #             print("percentage of load shedded is higher than 101%")
    #             raise Exception
    #         elif sum(lst) < .98:
    #             print("percentage of load shedded is lower than 99%")
    #             raise Exception
    #         else:
    #             pass
    #
    #         self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, self.reps.current_year + 1)

    def modify_CS_parameter_by_costs(self):
        """
        modify load percentage for Capacity Subscription according to the difference of costs of subscribing and not subscribing
        """
        if self.reps.current_tick < self.start_tick_CS:
            self.reps.dbrw.stage_load_shedders_voll_not_hydrogen(self.reps.loadShedders, self.reps.current_year + 1)
        else:
            ticks_to_generate = list(range(self.reps.current_tick - 1, self.reps.current_tick))
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
                    averageENS = load_shedder.realized_LOLE[ticks_to_generate].mean()
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
                                (non_subscription_costs - Capacity_market_costs) / (Capacity_market_costs) * 10,
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
                    averageENS = load_shedder.realized_LOLE[ticks_to_generate].mean()
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

