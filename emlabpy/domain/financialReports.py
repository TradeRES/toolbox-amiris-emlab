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
        self.totalProfitswLoans = 0
        self.tick = 0
        self.iteration = 0
        self.schedule = None
        self.fullLoadHours = [] # [0 for i in range(reps.simulation_length)]
        self.longTermMarketRevenue = 0
        self.capacityMarketRevenues_in_year = 0
        self.capacityMarketRevenues = 0
        self.strategicReserveRevenue = 0
        self.co2HedgingRevenue = 0
        self.commodityCosts = 0
        self.co2Costs = 0
        self.variableCosts = 0
        self.totalCosts = 0
        self.fixedCosts = 0
        self.fixedOMCosts = 0
        self.irr = 0.0
        self.irr_in_year = 0.0
        self.npv = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, iteration):
        # -----------------------------CM revenues from financial Reports classname
        if reps.runningModule == "plotting" and  parameter_name in ['irr','npv',  'totalProfitswLoans', 'totalProfits', 'capacityMechanismRevenues']:
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index = index)
            if parameter_name == 'irr':
                self.irr = pd_series
            elif parameter_name == 'npv':
                self.npv = pd_series
            elif parameter_name == 'totalProfitswLoans':
                self.totalProfitswLoans = pd_series
            elif parameter_name == 'totalProfits':
                self.totalProfits = pd_series
            elif  parameter_name == 'capacityMechanismRevenues':
                # for plotting import all capacity mechanisms
                self.capacityMarketRevenues = pd_series

        elif parameter_name == 'capacityMechanismRevenues':
            # to making financial results, only retrieve the CM of that year
            array = parameter_value.to_dict()
            df = pd.DataFrame(array['data'])
            df.set_index(0, inplace=True)
            if str(reps.current_tick) in df.index:
                self.capacityMarketRevenues_in_year = df.loc[str(reps.current_tick)][1]
            else:
                self.capacityMarketRevenues_in_year = 0

    def getTime(self):
        return self.tick

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

    # def getCapacityMarketRevenue(self):
    #     return self.capacityMarketRevenues

    # def setCapacityMarketRevenue(self, capacityMarketRevenue):
    #     self.capacityMarketRevenues = capacityMarketRevenue

    def getStrategicReserveRevenue(self):
        return self.strategicReserveRevenue

    def setStrategicReserveRevenue(self, strategicReserveRevenue):
        self.strategicReserveRevenue = strategicReserveRevenue

    def getCo2HedgingRevenue(self):
        return self.co2HedgingRevenue

    def setCo2HedgingRevenue(self, co2HedgingRevenue):
        self.co2HedgingRevenue = co2HedgingRevenue