from domain.import_object import *
from modules.defaultmodule import DefaultModule
from util.repository import Repository
from domain.technologies import *
import pandas as pd
import logging
class FinancialPowerPlantReport(ImportObject):

    def __init__(self, name):
        super().__init__(name)
        self.powerPlant = None
        self.spotMarketRevenue = 0
        self.overallRevenue = 0
        self.production = 0
        self.powerPlantStatus = 0
        self.totalProfits = 0
        self.profits_per_iteration_pp  = dict()
        self.profits_per_iteration = dict()
        self.time = 0
        self.iteration = 0
        self.schedule = None
        self.fullLoadHours = [] # [0 for i in range(reps.simulation_length)]
        self.longTermMarketRevenue = 0
        self.capacityMarketRevenues = dict()
        self.strategicReserveRevenue = 0
        self.co2HedgingRevenue = 0
        self.commodityCosts = 0
        self.co2Costs = 0
        self.variableCosts = 0
        self.totalCosts = 0
        self.fixedCosts = 0
        self.fixedOMCosts = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        """"
        This function is being read for the plotting. The totalProfits are being saved in the module Investmentdecision
        # object name =  year
        # alternative = iteration
        The data is stored in db investment with the object name "tick  - iteration"
        """
        # -----------------------------Profits and PowerPlants are read from the Profits
        if parameter_name == 'PowerPlants':
            # object name is year and alternative is the iteration.
            self.profits_per_iteration_pp[alternative] = parameter_value
        elif parameter_name == 'Profits':
            self.profits_per_iteration[alternative] = parameter_value
        # -----------------------------CM revenues from financial Reports
        elif parameter_name == 'capacityMechanismRevenues':
            array = parameter_value.to_dict()
            df = pd.DataFrame(array['data'])
            df.set_index(0, inplace=True)
            self.capacityMarketRevenues = df.loc[str(reps.current_tick)][1]

    # UNDERCONSTRUCTION = 0
    # OPERATIONAL = 1
    # DISMANTLED = 2

    def getTime(self):
        return self.time

    def getIteration(self):
        return self.iteration

    def setTime(self, tick):
        self.tick = tick

    def setIteration(self, iteration):
        self.iteration = iteration

    def getPowerPlant(self):
        return self.powerPlant

    def setPowerPlant(self, powerPlant):
        self.powerPlant = powerPlant

    def getSpotMarketRevenue(self, tick):
        return self.spotMarketRevenue[tick]

    def setSpotMarketRevenue(self, spotMarketRevenue):
        self.spotMarketRevenue = spotMarketRevenue

    def getOverallRevenue(self, tick):
        return self.overallRevenue[tick]

    def setOverallRevenue(self, overallRevenue):
        self.overallRevenue = overallRevenue

    def getProduction(self, tick):
        return self.production[tick]

    def setProduction(self, production):
        self.production = production

    def getPowerPlantStatus(self, tick):
        return self.powerPlantStatus[tick]

    def setPowerPlantStatus(self, powerPlantStatus):
        self.powerPlantStatus= powerPlantStatus

    def getTotalYearlyProfit(self, tick):
        return self.totalProfits

    def setTotalYearlyProfit(self, profit):
        self.totalProfits= profit

    def getCommodityCosts(self):
        return self.commodityCosts

    def setCommodityCosts(self, commodityCosts):
        self.commodityCosts = commodityCosts

    def getCo2Costs(self):
        return self.co2Costs

    def setCo2Costs(self, co2Costs):
        self.co2Costs = co2Costs

    def setTotalCosts(self, totalCosts):
        self.totalCosts = totalCosts


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
        return self.capacityMarketRevenues

    def setCapacityMarketRevenue(self, capacityMarketRevenue):
        self.capacityMarketRevenues = capacityMarketRevenue

    def getStrategicReserveRevenue(self):
        return self.strategicReserveRevenue

    def setStrategicReserveRevenue(self, strategicReserveRevenue):
        self.strategicReserveRevenue = strategicReserveRevenue

    def getCo2HedgingRevenue(self):
        return self.co2HedgingRevenue

    def setCo2HedgingRevenue(self, co2HedgingRevenue):
        self.co2HedgingRevenue = co2HedgingRevenue