"""
This file contains all Market and Market operation classes.
Jim Hommes - 13-5-2021
Sanchez 5-22
"""
from domain.actors import EMLabAgent
from domain.import_object import *
import os
import pandas as pd
from util import globalNames

class Market(EMLabAgent):
    """
    The parent class of all markets.
    """
    def __init__(self, name):
        super().__init__(name)

class ElectricitySpotMarket(Market):
    def __init__(self, name):
        super().__init__(name)
        self.valueOfLostLoad = 0
        self.hourlyDemand = None
        self.future_demand = None
        self.demandGrowthTrend = 0.0
        self.country = ""

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'valueOfLostLoad':
            self.valueOfLostLoad = int(parameter_value)
        elif parameter_name == 'country':
            self.country = str(parameter_value)
        elif parameter_name == 'growthTrend':
            self.demandGrowthTrend = str(parameter_value)
            load_path = globalNames.load_file_for_amiris
            if reps.available_years_data == False:
                self.hourlyDemand = pd.read_csv(load_path,  delimiter= ";", header=None)
                self.future_demand = self.hourlyDemand # no dynamic load for other cases yet
            else:
                future_load_path = globalNames.future_load_file_for_amiris
                self.hourlyDemand = pd.read_csv(load_path,  delimiter= ";", header=None)
                self.future_demand = pd.read_csv(future_load_path,  delimiter= ";", header=None)

class LoadShedder(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.VOLL = None
        self.TimeSeriesFile = 0
        self.TimeSeriesFileFuture = 0
        self.ShedderCapacityMW = 0
        self.percentageLoad = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'TimeSeriesFile':
            self.TimeSeriesFile = str(parameter_value)
        elif parameter_name == 'TimeSeriesFileFuture':
            self.TimeSeriesFileFuture =  str(parameter_value)
        elif parameter_name == 'VOLL':
            self.VOLL = int(parameter_value)
        elif parameter_name == 'ShedderCapacityMW':
            self.ShedderCapacityMW = parameter_value
        elif parameter_name == 'percentage_load':
            self.percentageLoad = parameter_value

class CapacityMarket(Market):
    """"""
    def __init__(self, name: str):
        """"""
        super().__init__(name)
        self.sloping_demand_curve = None
        self.country = ""
        self.InstalledReserveMargin = 0.0
        self.LowerMargin = 0.0
        self.UpperMargin = 0.0
        self.PriceCap = 0

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        setattr(self, parameter_name, parameter_value)

    def get_sloping_demand_curve(self, d_peak):
        return SlopingDemandCurve(self.InstalledReserveMargin,
                                  self.LowerMargin,
                                  self.UpperMargin, d_peak, self.PriceCap)

class CO2Market(Market):
    pass


class MarketClearingPoint(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.market = None
        self.price = 0
        self.capacity = 0
        self.volume = 0
        self.time = 0
        self.tick = -1

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
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
        if parameter_name == 'Tick':
            self.tick = int(parameter_value)
        if parameter_name == 'Volume':
            self.volume = int(parameter_value)

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
        self.m = self.price_cap / (self.um_volume - self.lm_volume)

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
            print("BID PRICE IS ZERO")
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

