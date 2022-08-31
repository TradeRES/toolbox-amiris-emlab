import numpy_financial as npf
import pandas as pd
from modules.defaultmodule import DefaultModule
from domain.financialReports import FinancialPowerPlantReport
from domain.powerplant import PowerPlant
from domain.cashflow import CashFlow
from domain.technologies import *
import logging

from util import globalNames


class CreatingFinancialReports(DefaultModule):

    def __init__(self, reps):
        super().__init__("Creating Financial Reports", reps)
        reps.dbrw.stage_init_financial_results_structure()
       # reps.dbrw.stage_init_cash_agent()
        self.agent = reps.energy_producers[reps.agent]

    def act(self):
        # TODO WHY findAllPowerPlantsWhichAreNotDismantledBeforeTick(self.reps.current_tick - 2)
        self.createFinancialReportsForPowerPlantsAndTick()
        self.addingMarketClearingIncome()
        print("finished financial report")

    def createFinancialReportsForPowerPlantsAndTick(self):
        financialPowerPlantReports = []
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
                print("no dispatch found for ", powerplant.id)
                raise
            fixed_on_m_cost = powerplant.getActualFixedOperatingCost()
            financialPowerPlantReport.setTime(self.reps.current_tick)
            financialPowerPlantReport.setPowerPlant(powerplant.name)  # this can be ignored, its already in the name
            financialPowerPlantReport.setPowerPlantStatus(powerplant.status)
            financialPowerPlantReport.setFixedCosts(fixed_on_m_cost)
            self.agent.CF_FIXEDOMCOST -= fixed_on_m_cost

            loans = powerplant.loan_payments_in_year
            print(powerplant.name,  "---->" ,loans)
            yearly_costs = - dispatch.variable_costs - fixed_on_m_cost  # without loans

            financialPowerPlantReport.setVariableCosts(dispatch.variable_costs)
            self.agent.CF_COMMODITY -= dispatch.variable_costs

            financialPowerPlantReport.setTotalCosts( yearly_costs)
            financialPowerPlantReport.setProduction(dispatch.accepted_amount)

            financialPowerPlantReport.setSpotMarketRevenue(dispatch.revenues)
            self.agent.CF_ELECTRICITY_SPOT += dispatch.revenues

            financialPowerPlantReport.setOverallRevenue(
                financialPowerPlantReport.capacityMarketRevenues_in_year +  dispatch.revenues)

            self.agent.CF_CAPMARKETPAYMENT += financialPowerPlantReport.capacityMarketRevenues_in_year

            operational_profit = financialPowerPlantReport.capacityMarketRevenues_in_year + dispatch.revenues +  yearly_costs
            operational_profit_with_loans = operational_profit - loans
            financialPowerPlantReport.totalProfitswLoans = operational_profit_with_loans
            financialPowerPlantReport.setTotalYearlyProfit(operational_profit)
            irr = self.getProjectIRR(powerplant, operational_profit_with_loans, self.agent)
            financialPowerPlantReport.irr = irr
            financialPowerPlantReports.append(financialPowerPlantReport)
        self.reps.dbrw.stage_financial_results(financialPowerPlantReports)
        self.reps.dbrw.stage_cash_agent(self.agent, self.reps.current_tick)
    def getProjectIRR(self, pp, operational_profit_with_loans, agent):
        totalInvestment = pp.getActualInvestedCapital()
        depreciationTime = pp.technology.depreciation_time
        technical_lifetime = pp.technology.expected_lifetime
        buildingTime = pp.technology.expected_leadtime
        # get average profits per technology
        equalTotalDownPaymentInstallment = (totalInvestment * (1 -agent.debtRatioOfInvestments)) / buildingTime
        # the rest payment is considered in the loans
        # restPayment = totalInvestment * (1 - agent.debtRatioOfInvestments) / depreciationTime

        investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]
        for i in range(0, buildingTime):
            investmentCashFlow[i] = - equalTotalDownPaymentInstallment * (1 + agent.equityInterestRate)
        for i in range(buildingTime, depreciationTime + buildingTime):
            investmentCashFlow[i] = operational_profit_with_loans
        IRR = npf.irr(investmentCashFlow)
        if pd.isna(IRR):
            return -100
        else:
            return round(IRR, 4)


    def addingMarketClearingIncome(self):
        all_dispatch = self.reps.power_plant_dispatch_plans_in_year
        SRO = self.reps.get_strategic_reserve_operator(self.reps.country)
        all_revenues = 0
        for k, dispatch in all_dispatch.items():
            if k not in SRO.list_of_plants:
                all_revenues += dispatch.revenues
                self.agent.CF_ELECTRICITY_SPOT += dispatch.revenues

        # adding market revenues to energy producer
        # wholesale_market = self.reps.get_electricity_spot_market_for_country(self.reps.country)
        # self.reps.createCashFlow(wholesale_market, self.agent, all_revenues,
        #                          globalNames.CF_ELECTRICITY_SPOT, self.reps.current_tick, "all")


            # TODO add cash flows
            # financialPowerPlantReport.setVariableCosts(financialPowerPlantReport.getCommodityCosts() + financialPowerPlantReport.getCo2Costs())
            # financialPowerPlantReport.setOverallRevenue(financialPowerPlantReport.getCapacityMarketRevenue() + financialPowerPlantReport.getCo2HedgingRevenue() + financialPowerPlantReport.getSpotMarketRevenue() + financialPowerPlantReport.getStrategicReserveRevenue())
