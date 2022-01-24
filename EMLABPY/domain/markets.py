"""
This file contains all Market and Market operation classes.

Jim Hommes - 13-5-2021
"""
from domain.import_object import *


class Market(ImportObject):
    """
    The parent class of all markets.
    """
    pass


class ElectricitySpotMarket(Market):
    pass


class CapacityMarket(Market):
    """"""
    def __init__(self, name: str):
        """"""
        super().__init__(name)
        self.sloping_demand_curve = None

    def get_sloping_demand_curve(self, d_peak):
        return SlopingDemandCurve(float(self.parameters['InstalledReserveMargin']),
                                  float(self.parameters['LowerMargin']),
                                  float(self.parameters['UpperMargin']), d_peak, float(self.parameters['PriceCap']))


class CO2Market(Market):
    pass


class MarketClearingPoint(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.market = None
        self.price = 0
        self.capacity = 0
        self.tick = -1

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        self.tick = int(alternative)
        if parameter_name == 'Price':
            self.price = float(parameter_value)
        if parameter_name == 'Market':
            if parameter_value in reps.capacity_markets.keys():
                self.market = reps.capacity_markets[parameter_value]
            elif parameter_value in reps.electricity_spot_markets.keys():
                self.market = reps.electricity_spot_markets[parameter_value]
            else:
                self.market = reps.co2_markets[parameter_value]
        if parameter_name == 'TotalCapacity':
            self.capacity = float(parameter_value)


class SlopingDemandCurve:
    """
    The SlopingDemandCurve as required in the CapacityMarket.
    """
    def __init__(self, irm, lm, um, d_peak, price_cap):
        self.irm = irm
        self.lm = lm
        self.lm_volume = d_peak * (1 + irm - lm)
        self.um = um
        self.um_volume = d_peak * (1 + irm + um)
        self.d_peak = d_peak
        self.price_cap = price_cap

    def get_price_at_volume(self, volume):
        m = self.price_cap / (self.um_volume - self.lm_volume)
        if volume < self.lm_volume:
            return self.price_cap
        elif self.lm_volume <= volume <= self.um_volume:
            return self.price_cap - m * (volume - self.lm_volume)
        elif self.um_volume < volume:
            return 0

    def get_volume_at_price(self, price):
        m = self.price_cap / (self.um_volume - self.lm_volume)
        if price >= self.price_cap:
            return None
        elif price == 0:
            return None
        else:
            return ((self.price_cap - price) / m) + self.lm_volume


class MarketStabilityReserve(ImportObject):
    """
    The MarketStabilityReserve as part of the CO2 Market.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.reserve = [0 for i in range(100)]
        self.upper_trigger_trend = None
        self.lower_trigger_trend = None
        self.release_trend = None
        self.zone = None
        self.flow = 0

    def add_parameter_value(self, reps, parameter_name: str, parameter_value: str, alternative: str):
        if parameter_name == 'UpperTriggerTrend':
            self.upper_trigger_trend = reps.trends[parameter_value]
        elif parameter_name == 'LowerTriggerTrend':
            self.lower_trigger_trend = reps.trends[parameter_value]
        elif parameter_name == 'ReleaseTrend':
            self.release_trend = reps.trends[parameter_value]
        elif parameter_name == 'Zone':
            self.zone = reps.zones[parameter_value]
