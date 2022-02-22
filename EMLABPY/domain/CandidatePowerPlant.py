from emlabpy.domain.import_object import *
import logging


class FuturePowerPlant(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.AwardedPowerinMWh = 0
        self.CostsinEUR = 0
        self.OfferedPowerinMWH = 0
        self.ReceivedMoneyinEUR = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'AwardedPowerinMWh':
            self.AwardedPowerinMWh = float(parameter_value)
        elif parameter_name == 'CostsinEUR':
            self.CostsinEUR = float(parameter_value)
        elif parameter_name == 'OfferedPowerinMWH':
            self.OfferedPowerinMWH = float(parameter_value)
        elif parameter_name == 'ReceivedMoneyinEUR':
            self.ReceivedMoneyinEUR = float(parameter_value)

class FutureStorageTrader(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.AwardedChargePower = 0
        self.AwardedDischargePower = 0
        self.AwardedPower = 0
        self.StoredMWh = 0
        self.Profit = 0
        #self.Revenues = None
        #self.Costs = None
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