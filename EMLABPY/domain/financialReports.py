from emlabpy.domain.import_object import *
from emlabpy.modules.defaultmodule import DefaultModule
from emlabpy.util.repository import Repository
from emlabpy.domain.technologies import *

import logging
class FinancialPowerPlantReport(DefaultModule):

    def __init__(self, reps):
        super().__init__(reps)
        self.reps = reps
        self.__powerPlant = None
        self.time = 0
        self.iteration = 0
        self.schedule = None
        self.spotMarketRevenue = [0 for i in range(self.simulation_length)]
        self.overallRevenue = [0 for i in range(self.simulation_length)]
        self.fullLoadHours = [0 for i in range(self.simulation_length)]
        self.production = [0 for i in range(self.simulation_length)]
        self.powerPlantStatus = [0 for i in range(self.simulation_length)]
        self.longTermMarketRevenue = 0
        self.capacityMarketRevenue = 0
        self.strategicReserveRevenue = 0
        self.co2HedgingRevenue = 0
        self.commodityCosts = 0
        self.co2Costs = 0
        self.variableCosts = 0
        self.fixedCosts = 0
        self.fixedOMCosts = 0


    # UNDERCONSTRUCTION = 0
    # OPERATIONAL = 1
    # DISMANTLED = 2

    def getTime(self):
        return self.time

    def getIteration(self):
        return self.iteration

    def setTime(self, time):
        self.time = time

    def setIteration(self, iteration):
        self.iteration = iteration

    def getPowerPlant(self):
        return self.__powerPlant

    def setPowerPlant(self, powerPlant):
        self.__powerPlant = powerPlant

    def getSpotMarketRevenue(self, tick):
        return self.spotMarketRevenue[tick]

    def setSpotMarketRevenue(self, spotMarketRevenue, tick):
        self.spotMarketRevenue[tick] = spotMarketRevenue

    def getOverallRevenue(self, tick):
        return self.overallRevenue[tick]

    def setOverallRevenue(self, overallRevenue, tick):
        self.overallRevenue[tick] = overallRevenue

    def getProduction(self, tick):
        return self.production[tick]

    def setProduction(self, production, tick):
        self.production[tick] = production

    def getPowerPlantStatus(self, tick):
        return self.powerPlantStatus[tick]

    def setPowerPlantStatus(self, powerPlantStatus, tick):
        self.powerPlantStatus[tick] = powerPlantStatus

    def getProfit(self, tick):
        return self.profit[tick]

    def setProfit(self, profit, tick):
        self.profit[tick] = profit

    def getCommodityCosts(self):
        return self.commodityCosts

    def setCommodityCosts(self, commodityCosts):
        self.commodityCosts = commodityCosts

    def getCo2Costs(self):
        return self.co2Costs

    def setCo2Costs(self, co2Costs):
        self.co2Costs = co2Costs

    def getFullLoadHours(self):
        return self.fullLoadHours

    def setFullLoadHours(self, fullLoadHours):
        self.fullLoadHours = fullLoadHours

    def getVariableCosts(self):
        return self.variableCosts

    def setVariableCosts(self, variableCosts):
        self.variableCosts = variableCosts

    def getFixedCosts(self):
        return self.fixedCosts

    def setFixedCosts(self, fixedCosts):
        self.fixedCosts = fixedCosts

    def getFixedOMCosts(self):
        return self.fixedOMCosts

    def setFixedOMCosts(self, fixedOMCosts):
        self.fixedOMCosts = fixedOMCosts

    def getLongTermMarketRevenue(self):
        return self.longTermMarketRevenue

    def setLongTermMarketRevenue(self, longTermMarketRevenue):
        self.longTermMarketRevenue = longTermMarketRevenue

    def getCapacityMarketRevenue(self):
        return self.capacityMarketRevenue

    def setCapacityMarketRevenue(self, capacityMarketRevenue):
        self.capacityMarketRevenue = capacityMarketRevenue

    def getStrategicReserveRevenue(self):
        return self.strategicReserveRevenue

    def setStrategicReserveRevenue(self, strategicReserveRevenue):
        self.strategicReserveRevenue = strategicReserveRevenue

    def getCo2HedgingRevenue(self):
        return self.co2HedgingRevenue

    def setCo2HedgingRevenue(self, co2HedgingRevenue):
        self.co2HedgingRevenue = co2HedgingRevenue