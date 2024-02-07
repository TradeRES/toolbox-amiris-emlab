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
        if reps.current_tick == 0:
            reps.dbrw.stage_init_financial_results_structure()
            reps.dbrw.stage_init_cash_agent()

    def act(self):
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

            if powerplant.status == globalNames.power_plant_status_strategic_reserve: # power plants in reserve dont get the dispatch revenues
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

            if powerplant.status == globalNames.power_plant_status_strategic_reserve: # power plants in reserve dont get the dispatch revenues
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
        self.modifyIRR()
        # saving
        self.reps.dbrw.stage_financial_results(financialPowerPlantReports)
        self.reps.dbrw.stage_cash_agent(self.agent, self.reps.current_tick)

        if self.reps.capacity_remuneration_mechanism in ["strategic_reserve_ger","strategic_reserve_swe", "strategic_reserve"] :
            # Save the SR operator variables to the SR operator of the country
            self.reps.update_StrategicReserveOperator( self.reps.get_strategic_reserve_operator(self.reps.country))


    def modifyIRR(self):
        if  self.reps.current_tick < 5:
            pass
        else:
            start = self.reps.current_tick -4
            ticks_to_generate = list(range(start, self.reps.current_tick ))
            irrs_per_tech_per_year = pd.DataFrame(index=ticks_to_generate).fillna(0)
            for technology_name in globalNames.used_technologies:
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
                if  pd.isna(averageirr):
                    pass
                else:
                    decrease = (averageirr-0.1) * 0.1
                    old_value = self.reps.power_generating_technologies[technology_name].interestRate
                    if averageirr < 0.01:
                        pass # and IRR of 10% is normal
                    elif old_value - decrease < 0:
                        pass
                    elif old_value - decrease > 0.2:
                        pass
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

    # def addingMarketClearingIncome(self):
    #     print("adding again dispatch revenues????")
    #     all_dispatch = self.reps.power_plant_dispatch_plans_in_year
    #     SRO = self.reps.get_strategic_reserve_operator(self.reps.country)
    #     all_revenues = 0
    #     for k, dispatch in all_dispatch.items():
    #         if k not in SRO.list_of_plants:
    #             all_revenues += dispatch.revenues
    #             self.agent.CF_ELECTRICITY_SPOT += dispatch.revenues

        # adding market revenues to energy producer
        # wholesale_market = self.reps.get_electricity_spot_market_for_country(self.reps.country)
        # self.reps.createCashFlow(wholesale_market, self.agent, all_revenues,
        #                          globalNames.CF_ELECTRICITY_SPOT, self.reps.current_tick, "all")

        # TODO add CO2 costs
        # financialPowerPlantReport.setVariableCosts(financialPowerPlantReport.getCommodityCosts() + financialPowerPlantReport.getCo2Costs())
        # financialPowerPlantReport.setOverallRevenue(financialPowerPlantReport.getCapacityMarketRevenue() + financialPowerPlantReport.getCo2HedgingRevenue() + financialPowerPlantReport.getSpotMarketRevenue() + financialPowerPlantReport.getStrategicReserveRevenue())
