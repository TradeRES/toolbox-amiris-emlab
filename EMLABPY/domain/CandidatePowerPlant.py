from emlabpy.domain.import_object import *
import logging


class CandidatePowerPlant(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        # results from Amiris
        self.AwardedPowerinMWh = 0
        self.CostsinEUR = 0
        self.OfferedPowerinMWH = 0
        self.ReceivedMoneyinEUR = 0
        self.Profit = 0
        # scenario from Amiris
        self.name = ""
        self.technology = None
        self.location = None
        self.age = 0
        self.owner = None
        self.capacity = 0
        self.efficiency = 0
        # scenario from Amiris
        self.constructionStartTime = 0
        self.Leadtime = 0
        self.Permittime = 0
        self.Lifetime = 0
        self.InvestedCapital = 0
        self.FixedOperatingCost = 0
        self.Efficiency = 0
        self.expectedEndOfLife = 0
        self.actualNominalCapacity = 0
        self.historicalCvarDummyPlant = 0
        self.electricityOutput = 0
        self.flagOutputChanged = True


    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'AwardedPowerInMWH':
            self.AwardedPowerinMWh = float(parameter_value)
        elif parameter_name == 'CostsInEUR':
            self.CostsinEUR = float(parameter_value)
        elif parameter_name == 'OfferedPowerInMW':
            self.OfferedPowerinMW = float(parameter_value)
        elif parameter_name == 'ReceivedMoneyInEUR':
            self.ReceivedMoneyinEUR = float(parameter_value)
        elif parameter_name == 'Id':
            self.name = parameter_value
        elif parameter_name == 'Technology':
            self.technology = parameter_value
        elif parameter_name == 'InstalledPowerInMW':
            self.capacity = parameter_value
        elif parameter_name == 'Owner':
            self.owner = parameter_value
        elif parameter_name == 'ComissionedYear':
            print(reps.current_tick, "start year", reps.start_simulation_year, "commisioned" ,  parameter_value)
            self.age = reps.current_tick + reps.start_simulation_year - int(parameter_value)
        elif parameter_name == 'Maximal':
            self.efficiency = float(parameter_value)


    def get_technology(self, time):
        return self.technology

    def CalculateProfit(self):
        self.Profit = self.ReceivedMoneyinEUR - self.CostsinEUR




class FutureStorageTrader(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.AwardedChargePower = 0
        self.AwardedDischargePower = 0
        self.AwardedPower = 0
        self.StoredMWh = 0
        self.Profit = 0

        #self.OfferedChargePrice = None
        #self.OfferedDischargePrice = None
        #self.OfferedPowerinMW


    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'AwardedPowerinMWh':
            self.AwardedPowerinMWh = float(parameter_value)
        elif parameter_name == 'AwardedDischargePower':
            self.AwardedDischargePower = float(parameter_value)
        elif parameter_name == 'AwardedPower':
            self.AwardedPower = float(parameter_value)
        elif parameter_name == 'StoredMWh':
            self.StoredMWh = float(parameter_value)
        elif parameter_name == 'Profit':
            self.Profit = float(parameter_value)

