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
        if reps.runningModule == "plotting" and  parameter_name in \
            ['irr','npv',  'totalProfitswLoans', 'totalProfits', 'spotMarketRevenue', 'variableCosts','capacityMechanismRevenues']:
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
            elif parameter_name == 'totalProfits': # todo: can be deleted - > only for plots
                self.totalProfits = pd_series
            elif  parameter_name == 'capacityMechanismRevenues':
                self.capacityMarketRevenues = pd_series
            elif parameter_name == 'variableCosts': # todo: can be deleted - > only for plots real obtained operational profits
                self.variableCosts = pd_series
            elif  parameter_name == 'spotMarketRevenue':
                self.spotMarketRevenue = pd_series

        if reps.runningModule == "run_future_market" and  parameter_name in \
                ['irr','npv', 'totalProfitswLoans', 'totalProfits' ]:
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

        elif parameter_name == 'capacityMechanismRevenues':
            # to making financial results, only retrieve the CM of that year
            array = parameter_value.to_dict()
            df = pd.DataFrame(array['data'])
            df.set_index(0, inplace=True)
            if str(reps.current_tick) in df.index:
                self.capacityMarketRevenues_in_year = df.loc[str(reps.current_tick)][1]
            else:
                self.capacityMarketRevenues_in_year = 0

    def setTime(self, tick):
        self.tick = tick

    def setPowerPlant(self, powerPlant):
        self.powerPlant = powerPlant

    def setSpotMarketRevenue(self, spotMarketRevenue):
        self.spotMarketRevenue = spotMarketRevenue

    def setOverallRevenue(self, overallRevenue):
        self.overallRevenue = overallRevenue

    def setProduction(self, production):
        self.production = production

    def setPowerPlantStatus(self, powerPlantStatus):
        self.powerPlantStatus= powerPlantStatus

    def setCommodityCosts(self, commodityCosts):
        self.commodityCosts = commodityCosts

    def setCo2Costs(self, co2Costs):
        self.co2Costs = co2Costs

    def setVariableCosts(self, variableCosts):
        self.variableCosts = variableCosts

    def setFixedCosts(self, fixedCosts):
        self.fixedCosts = fixedCosts