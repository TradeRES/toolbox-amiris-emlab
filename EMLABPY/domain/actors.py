"""
This file contains all lifeforms or actors in the energy world.

Jim Hommes - 13-5-2021
"""
from domain.import_object import *


class EnergyProducer(ImportObject):
    pass


class NationalGovernment(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.governed_zone = None
        self.min_national_co2_price_trend = None

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'governedZone':
            self.governed_zone = reps.zones[parameter_value]
        elif parameter_name == 'minNationalCo2PriceTrend':
            self.min_national_co2_price_trend = reps.trends[parameter_value]


class Government(ImportObject):
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
