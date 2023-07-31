"""
This file contains all lifeforms or actors in the energy world.
EnergyProducer
NationalGovernment
Government
"""
from domain.import_object import *

class EMLabAgent(ImportObject):

    def __init__(self, name):
        super().__init__(name)
        self.cash = 0
        self.co2Allowances = 0
        self.lastYearsCo2Allowances = 0

    def setCash(self, cash):
        self.cash = cash

    def getCash(self):
        return self.cash

class BigBank(EMLabAgent):

    def __init__(self, name):
        super().__init__(name)



class PowerPlantManufacturer(EMLabAgent):
    def __init__(self, name):
        super().__init__(name)


class NationalGovernment(EMLabAgent):
    def __init__(self, name):
        super().__init__(name)
        self.governed_zone = None
        self.min_national_co2_price_trend = None

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'governedZone':
            self.governed_zone = reps.zones[parameter_value]
        elif parameter_name == 'minNationalCo2PriceTrend':
            self.min_national_co2_price_trend = reps.trends[parameter_value]

class Government(EMLabAgent):
    def __init__(self, name):
        super().__init__(name)
        self.co2_penalty = 0
        self.co2_cap_trend = None
        self.co2_min_price_trend = None

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'co2Penalty':
            self.co2_penalty = int(parameter_value)
        elif parameter_name == 'co2CapTrend':
            self.co2_cap_trend = reps.trends[parameter_value]
        elif parameter_name == 'minCo2PriceTrend':
            self.co2_min_price_trend = reps.trends[parameter_value]

