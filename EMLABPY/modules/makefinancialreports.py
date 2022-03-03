from emlabpy.domain.import_object import *
from emlabpy.modules.defaultmodule import DefaultModule
from emlabpy.domain.financialReports import FinancialPowerPlantReport
from emlabpy.domain.powerplant import PowerPlant
from emlabpy.domain.cashflow import CashFlow
from emlabpy.domain.technologies import *

import logging
class CreatingFinancialReports(DefaultModule):

    def __init__(self, reps):
        super().__init__("Creating Financial Reports",reps)
        reps.dbrw.stage_init_power_plant_dispatch_plan_structure()

    def act(self):
        # fuelPriceMap = {}
        # for substance in self.reps.substances:
        #     fuelPriceMap.update({substance: findLastKnownPriceForSubstance(substance)})
        #TODO WHY findAllPowerPlantsWhichAreNotDismantledBeforeTick(self.reps.current_tick - 2)
        self.createFinancialReportsForPowerPlantsAndTick(self.reps.findAllPowerPlantsWhichAreNotDismantledBeforeTick(self.reps.current_tick), self.reps.current_tick)

    def createFinancialReportsForNewInvestments(self):
        self.createFinancialReportsForPowerPlantsAndTick(self.reps.findAllPowerPlantsWithConstructionStartTimeInTick(self.reps.current_tick), self.reps.current_tick)

    def createFinancialReportsForPowerPlantsAndTick(self, plants, tick):
        for plant in plants:
            financialPowerPlantReport = FinancialPowerPlantReport()

            #financialPowerPlantReport.setTime(tick)
            financialPowerPlantReport.setPowerPlant(plant.name)
            totalSupply = plant.getAwardedPowerinMWh()
            financialPowerPlantReport.setProduction(totalSupply, tick)
            # #TODO fix this:
            # if plant.getFuelMix() is None:
            #     plant.setFuelMix(java.util.HashSet())
            # for share in plant.getFuelMix():
            #     amount = share.getShare() * totalSupply
            #     substance = share.getSubstance()
            #     substanceCost = findLastKnownPriceForSubstance(substance) * amount
            #     financialPowerPlantReport.setCommodityCosts(financialPowerPlantReport.getCommodityCosts() + substanceCost)
            #TODO add cash flows
            #cashFlows = self.reps.getCashFlowsForPowerPlant(plant, tick)
            #financialPowerPlantReport.setCo2Costs(self.calculateCO2CostsOfPowerPlant(cashFlows))
            #financialPowerPlantReport.setVariableCosts(financialPowerPlantReport.getCommodityCosts() + financialPowerPlantReport.getCo2Costs())
            #Determine fixed costs
            #financialPowerPlantReport.setFixedCosts(self.calculateFixedCostsOfPowerPlant(cashFlows))
            #financialPowerPlantReport.setFixedOMCosts(self.calculateFixedOMCostsOfPowerPlant(cashFlows))
            financialPowerPlantReport.setSpotMarketRevenue(plant.ReceivedMoneyinEUR, tick)
            financialPowerPlantReport.setProfit(plant.Profit, tick)
            #financialPowerPlantReport.setStrategicReserveRevenue(self.calculateStrategicReserveRevenueOfPowerPlant(cashFlows))
            #financialPowerPlantReport.setCapacityMarketRevenue(self.calculateCapacityMarketRevenueOfPowerPlant(cashFlows))
            #financialPowerPlantReport.setCo2HedgingRevenue(self.calculateCO2HedgingRevenueOfPowerPlant(cashFlows))
            #financialPowerPlantReport.setOverallRevenue(financialPowerPlantReport.getCapacityMarketRevenue() + financialPowerPlantReport.getCo2HedgingRevenue() + financialPowerPlantReport.getSpotMarketRevenue() + financialPowerPlantReport.getStrategicReserveRevenue())

            # Calculate Full load hours
            #financialPowerPlantReport.setFullLoadHours(self.reps.calculateFullLoadHoursOfPowerPlant(plant, tick))

            operationalStatus = None
            if plant.isOperational(tick):
                operationalStatus = 1
            elif plant.isInPipeline(tick):
                operationalStatus = 0
            else:
                operationalStatus = 2

            financialPowerPlantReport.setPowerPlantStatus(operationalStatus, tick)

            self.reps.financialPowerPlantReports.add(financialPowerPlantReport)

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
