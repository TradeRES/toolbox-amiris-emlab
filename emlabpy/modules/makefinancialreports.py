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
        self.agent = reps.energy_producers[reps.agent]

    def act(self):
        # TODO WHY findAllPowerPlantsWhichAreNotDismantledBeforeTick(self.reps.current_tick - 2)
        self.addingMarketClearingIncome()
        self.createFinancialReportsForPowerPlantsAndTick()
        print("finished financial report")

    def addingMarketClearingIncome(self):
        all_dispatch = self.reps.power_plant_dispatch_plans_in_year
        wholesale_market = self.reps.get_electricity_spot_market_for_country(self.reps.country)
        SRO = self.reps.get_strategic_reserve_operator(self.reps.country)
        all_revenues = 0
        for k, dispatch in all_dispatch.items():
            if k not in SRO.list_of_plants:
                all_revenues += dispatch.revenues
        self.reps.createCashFlow(wholesale_market, self.agent, all_revenues,
                                 globalNames.CF_ELECTRICITY_SPOT, self.reps.current_tick, "all")
        self.reps.dbrw.stage_cash_agent(self.agent)

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
            fixed_on_m_cost = powerplant.getActualFixedOperatingCost()
            financialPowerPlantReport.setTime(self.reps.current_tick)
            financialPowerPlantReport.setPowerPlant(powerplant.name)  # this can be ignored, its already in the name
            financialPowerPlantReport.setPowerPlantStatus(powerplant.status)
            financialPowerPlantReport.setFixedCosts(fixed_on_m_cost)

            if dispatch != None:
                yearly_costs = - dispatch.variable_costs - fixed_on_m_cost
                accepted_amount = dispatch.accepted_amount
                revenues = dispatch.revenues
                variable_costs = dispatch.variable_costs   # these include already fuel, O&M, CO2 costs from AMIRIS
            else:
                yearly_costs = - fixed_on_m_cost
                accepted_amount = 0
                revenues = 0
                variable_costs = 0
                raise

            loans = powerplant.loan_payments_in_year
            financialPowerPlantReport.setVariableCosts(variable_costs)
            financialPowerPlantReport.setTotalCosts(yearly_costs)
            financialPowerPlantReport.setProduction(accepted_amount)
            financialPowerPlantReport.setSpotMarketRevenue(revenues)

            # yearly_costs = - dispatch.variable_costs - fixed_on_m_cost  # without loans
            # financialPowerPlantReport.setTotalCosts(yearly_costs)
            # financialPowerPlantReport.setProduction(dispatch.accepted_amount)
            # financialPowerPlantReport.setSpotMarketRevenue(dispatch.revenues)
            financialPowerPlantReport.setOverallRevenue(
                financialPowerPlantReport.capacityMarketRevenues_in_year +  revenues)

            operational_profit = financialPowerPlantReport.capacityMarketRevenues_in_year + revenues + yearly_costs
            operational_profit_with_loans = operational_profit - loans
            financialPowerPlantReport.totalProfitswLoans = operational_profit_with_loans
            financialPowerPlantReport.setTotalYearlyProfit(operational_profit)
            irr = self.getProjectIRR(powerplant, operational_profit_with_loans, self.agent)
            financialPowerPlantReport.irr = irr
            financialPowerPlantReports.append(financialPowerPlantReport)
        self.reps.dbrw.stage_financial_results(financialPowerPlantReports)

    def getProjectIRR(self, pp, operational_profit_with_loans, agent):
        totalInvestment = pp.getActualInvestedCapital()
        depreciationTime = pp.technology.depreciation_time
        technical_lifetime = pp.technology.expected_lifetime
        buildingTime = pp.technology.expected_leadtime
        # get average profits per technology
        equalTotalDownPaymentInstallment = (totalInvestment * agent.debtRatioOfInvestments) / buildingTime
        # the rest payment is considered in the loans
        # restPayment = totalInvestment * (1 - agent.debtRatioOfInvestments) / depreciationTime

        investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]
        for i in range(0, buildingTime):
            investmentCashFlow[i] = - equalTotalDownPaymentInstallment
        for i in range(buildingTime, depreciationTime + buildingTime):
            investmentCashFlow[i] = operational_profit_with_loans
        IRR = npf.irr(investmentCashFlow)
        if pd.isna(IRR):
            return -100
        else:
            return round(IRR, 4)
            # if plant.getFuelMix() is None:
            #     plant.setFuelMix(java.util.HashSet())
            # for share in plant.getFuelMix():
            #     amount = share.getShare() * totalSupply
            #     substance = share.getSubstance()
            #     substanceCost = findLastKnownPriceForSubstance(substance) * amount
            #     financialPowerPlantReport.setCommodityCosts(financialPowerPlantReport.getCommodityCosts() + substanceCost)
            # TODO add cash flows
            # cashFlows = self.reps.getCashFlowsForPowerPlant(plant, tick)
            # financialPowerPlantReport.setCo2Costs(self.calculateCO2CostsOfPowerPlant(cashFlows))
            # financialPowerPlantReport.setVariableCosts(financialPowerPlantReport.getCommodityCosts() + financialPowerPlantReport.getCo2Costs())
            # Determine fixed costs
            # financialPowerPlantReport.setFixedCosts(self.calculateFixedCostsOfPowerPlant(cashFlows))
            # financialPowerPlantReport.setFixedOMCosts(self.calculateFixedOMCostsOfPowerPlant(cashFlows))
            # financialPowerPlantReport.setStrategicReserveRevenue(self.calculateStrategicReserveRevenueOfPowerPlant(cashFlows))
            # financialPowerPlantReport.setCapacityMarketRevenue(self.calculateCapacityMarketRevenueOfPowerPlant(cashFlows))
            # financialPowerPlantReport.setCo2HedgingRevenue(self.calculateCO2HedgingRevenueOfPowerPlant(cashFlows))
            # financialPowerPlantReport.setOverallRevenue(financialPowerPlantReport.getCapacityMarketRevenue() + financialPowerPlantReport.getCo2HedgingRevenue() + financialPowerPlantReport.getSpotMarketRevenue() + financialPowerPlantReport.getStrategicReserveRevenue())
            # Calculate Full load hours
            # financialPowerPlantReport.setFullLoadHours(self.reps.calculateFullLoadHoursOfPowerPlant(plant, tick))

    # def createFinancialReportsForNewInvestments(self):
    #     self.createFinancialReportsForPowerPlantsAndTick(
    #         self.reps.findAllPowerPlantsWithConstructionStartTimeInTick(self.reps.current_tick), self.reps.current_tick)

    #
    # def calculateSpotMarketRevenueOfPowerPlant(self, cashFlows):
    #     toReturn = cashFlows.stream().filter(lambda p : p.getType() == emlab.gen.domain.contract.CashFlow.ELECTRICITY_SPOT).collect(java.util.stream.Collectors.summarizingDouble(emlab.gen.domain.contract.CashFlow::getMoney)).getSum()
    #     java.util.logging.Logger.getGlobal().finer("Income Spot " + toReturn)
    #     return toReturn
    #
    # def calculateLongTermContractRevenueOfPowerPlant(self, cashFlows):
    #     toReturn = cashFlows.stream().filter(lambda p : p.getType() == emlab.gen.domain.contract.CashFlow.ELECTRICITY_LONGTERM).collect(java.util.stream.Collectors.summarizingDouble(emlab.gen.domain.contract.CashFlow::getMoney)).getSum()
    #     java.util.logging.Logger.getGlobal().finer("Income LT " + toReturn)
    #     return toReturn
    #
    # def calculateStrategicReserveRevenueOfPowerPlant(self, cashFlows):
    #     toReturn = cashFlows.stream().filter(lambda p : p.getType() == emlab.gen.domain.contract.CashFlow.STRRESPAYMENT).collect(java.util.stream.Collectors.summarizingDouble(emlab.gen.domain.contract.CashFlow::getMoney)).getSum()
    #     java.util.logging.Logger.getGlobal().finer("Income strategic reserve " + toReturn)
    #     return toReturn
    #
    # def calculateCapacityMarketRevenueOfPowerPlant(self, cashFlows):
    #     toReturn = cashFlows.stream().filter(lambda p : p.getType() == emlab.gen.domain.contract.CashFlow.CAPMARKETPAYMENT).collect(java.util.stream.Collectors.summarizingDouble(emlab.gen.domain.contract.CashFlow::getMoney)).getSum()
    #     java.util.logging.Logger.getGlobal().finer("Income Capacity market " + toReturn)
    #     return toReturn
    #
    # def calculateCO2HedgingRevenueOfPowerPlant(self, cashFlows):
    #     toReturn = cashFlows.stream().filter(lambda p : p.getType() == emlab.gen.domain.contract.CashFlow.CO2HEDGING).collect(java.util.stream.Collectors.summarizingDouble(emlab.gen.domain.contract.CashFlow::getMoney)).getSum()
    #     java.util.logging.Logger.getGlobal().finer("Income CO2 Hedging" + toReturn)
    #     return toReturn
    #
    # def calculateCO2CostsOfPowerPlant(self, list):
    #     return list.stream().filter(lambda p : (p.getType() == emlab.gen.domain.contract.CashFlow.CO2TAX) or (p.getType() == emlab.gen.domain.contract.CashFlow.CO2AUCTION) or (p.getType() == emlab.gen.domain.contract.CashFlow.NATIONALMINCO2)).mapToDouble(lambda p : p.getMoney()).sum()

    # def calculateFixedCostsOfPowerPlant(self, list):
    #     pass
    #     #return list.stream().filter(lambda p : (p.getType() ==  CashFlow.FIXEDOMCOST) or (p.getType() == CashFlow.LOAN) or (p.getType() == CashFlow.DOWNPAYMENT)).mapToDouble(lambda p : p.getMoney()).sum()
    #
    # def calculateFixedOMCostsOfPowerPlant(self, list):
    #     pass
    #     #return list.stream().filter(lambda p : (p.getType() == CashFlow.FIXEDOMCOST)).mapToDouble(lambda p : p.getMoney()).sum()
