"""
This file contains all Market and Market operation classes.
Jim Hommes - 13-5-2021
Sanchez 5-22
"""
from domain.actors import EMLabAgent
from domain.import_object import *
import numpy as np
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
        self.realized_demand_peak = None
        self.future_demand_peak = None
        self.peak_load_fixed = None  # fixed from input
        self.country = ""
        self.hourlyDemand = None
        self.future_hourly_demand = None

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'country':
            self.country = str(parameter_value)
        elif parameter_name == 'futuredemand_peak':
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            self.future_demand_peak = pd.Series(values, index=index)
        elif parameter_name == 'next_year_demand_peak':
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            self.realized_demand_peak = pd.Series(values, index=index)
        elif parameter_name == 'peakLoadFixed':
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            self.peak_load_fixed = pd.Series(values, index=index)

    def get_peak_load_per_year(self, year):
        """
        NOT CONSIDERING LOAD SHIFTER or hydrogen, not in use
        :param year:
        :return:
        """
        if year in self.peak_load_fixed.index.values:  # value is present
            return self.peak_load_fixed[year]
        elif self.peak_load_fixed.index.min() > year:  # if the year is lower than data, take first year
            self.peak_load_fixed.sort_index(ascending=True, inplace=True)
            return self.peak_load_fixed.iloc[0]
        else:  # interpolate years. If the year is larger, the maximum value is taken
            self.peak_load_fixed.at[year] = np.nan
            self.peak_load_fixed.sort_index(ascending=True, inplace=True)
            self.peak_load_fixed.interpolate(method='linear', inplace=True)
            return self.peak_load_fixed[year]

        # elif parameter_name == 'totalDemand':
        #     load_path = globalNames.load_file_for_amiris
        #     if reps.available_years_data == False:
        #         self.hourlyDemand = pd.read_csv(load_path,  delimiter= ";", header=None)
        #         self.future_hourly_demand = self.hourlyDemand # no dynamic load for other cases yet
        #     else:
        #         future_load_path = globalNames.future_load_file_for_amiris
        #         self.hourlyDemand = pd.read_csv(load_path,  delimiter= ";", header=None) # inflexible load
        #         self.future_hourly_demand = pd.read_csv(future_load_path, delimiter=";", header=None) # inflexible load


class LoadShedder(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.VOLL = None
        self.TimeSeriesFile = 0
        self.TimeSeriesFileFuture = 0
        self.ShedderCapacityMW = 0
        self.percentageLoad = 0
        self.reliability_standard = 0
        self.price = 0
        self.realized_LOLE = pd.Series()

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'TimeSeriesFile':
            self.TimeSeriesFile = str(parameter_value)
        elif parameter_name == 'TimeSeriesFileFuture':
            self.TimeSeriesFileFuture = str(parameter_value)
        elif parameter_name == 'VOLL':
            if self.name == "hydrogen":
                self.VOLL = reps.substances[self.name].initialPrice.loc[reps.start_simulation_year2050]  # this is mainly for plotting, in prepare market real price is being read.
            else:
                self.VOLL = parameter_value
        elif parameter_name == 'ShedderCapacityMW':
            self.ShedderCapacityMW = parameter_value
        elif parameter_name == 'ShedderCapacityMWyearly' and reps.runningModule == "plotting":
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            self.ShedderCapacityMW = pd.Series(values, index=index)
        elif parameter_name == 'percentage_load':
            if self.name == "hydrogen":
                pass
            else:
                array = parameter_value.to_dict()
                values = [float(i[1]) for i in array["data"]]
                index = [int(i[0]) for i in array["data"]]
                pd_series = pd.Series(values, index=index)
                if reps.runningModule == "plotting":
                    self.percentageLoad = pd_series
                elif reps.capacity_remuneration_mechanism == globalNames.capacity_subscription:
                    self.percentageLoad = round(pd_series[reps.current_year],3)
                else:
                    self.percentageLoad = round(pd_series[reps.start_simulation_year],3)
        # elif parameter_name == 'reliability_standard':
        #     self.reliability_standard = parameter_value
        elif parameter_name == 'realized_LOLE':
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index=index)
            self.realized_LOLE = pd_series


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
        self.forward_years_CM = 0
        self.PriceCapTimesCONE = 0
        self.allowed_technologies_capacity_market = []
        self.long_term = False
        self.years_long_term_market = 15
        self.TargetCapacity = 0
        self.net_cone = 0
        self.InitialPrice = 0


    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if parameter_name == 'forward_years_CM':
            self.forward_years_CM = int(parameter_value)
        elif parameter_name == 'years_long_term_market':
            self.years_long_term_market = int(parameter_value)
        elif parameter_name == 'allowed_technologies':
            self.allowed_technologies_capacity_market = parameter_value.split(",")
        else:
            setattr(self, parameter_name, parameter_value)

    def get_sloping_demand_curve(self, target_volume):
        return SlopingDemandCurve(self.InstalledReserveMargin,
                                  self.LowerMargin,
                                  self.UpperMargin, target_volume, self.net_cone, self.PriceCap)

class PlantsinCM(Market):
    """"""

    def __init__(self, name: str):
        """"""
        super().__init__(name)
        self.plantsinCM = []
    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        setattr(self, parameter_name, parameter_value)


class Cone(ImportObject):
    """
    The Cone as part of the CapacityMarket.
    """

    def __init__(self, name: str):
        """"""
        super().__init__(name)
    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        array = parameter_value.to_dict()
        values = [float(i[1]) for i in array["data"]]
        index = [int(i[0]) for i in array["data"]]
        pd_series = pd.Series(values, index=index)
        setattr(self, parameter_name, pd_series)

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
            elif parameter_value in reps.co2_markets.keys():
                self.market = reps.co2_markets[parameter_value]
            else:
                self.market = CapacityMarket(parameter_value)
        if parameter_name == 'TotalCapacity':
            self.capacity = float(parameter_value)
        if parameter_name == 'Tick':
            self.tick = int(parameter_value)
        if parameter_name == 'Volume':

            if pd.isna(parameter_value):
                self.volume = 0
            else:
                self.volume = int(parameter_value)


class SlopingDemandCurve:
    """
    The SlopingDemandCurve as required in the CapacityMarket.
    """

    def __init__(self, irm, lm, um, target_volume,net_cone,  price_cap ):
        self.irm = irm
        self.lm = lm
        self.lm_volume = target_volume * (1 + irm - lm)
        self.um = um
        self.um_volume = target_volume * (1 + irm + um)
        self.target_volume = target_volume
        self.price_cap = price_cap
        self.m = (self.price_cap - self.price_cap/1.5) / (target_volume - self.lm_volume)
        self.net_cone = net_cone

    def get_price_at_volume(self, volume):
        if volume < self.lm_volume:
            return self.price_cap
        elif self.lm_volume <= volume < self.target_volume : # inflexible demand after clearing point
            return self.price_cap - ((self.price_cap - self.net_cone ) / (self.target_volume -  self.lm_volume)) * (volume -  self.lm_volume)
        elif self.target_volume <= volume < self.um_volume : # inflexible demand after clearing point
            return self.net_cone - ((self.net_cone) / ( self.um_volume - self.target_volume)) * (volume -  self.target_volume)
        else:
            return 0


    # def get_price_at_volume(self, volume):
    #     m = self.price_cap / (self.um_volume - self.lm_volume)
    #     if volume < self.lm_volume:
    #         return self.price_cap
    #     elif self.lm_volume <= volume <= self.um_volume:
    #         return self.price_cap - m * (volume - self.lm_volume)
    #     elif self.um_volume < volume:
    #         return 0

    # def get_volume_at_price(self, price):
    #     m = self.price_cap / (self.um_volume - self.lm_volume)
    #     if price >= self.price_cap:
    #         raise Exception
    #     elif price == 0:
    #         print("BID PRICE IS ZERO")
    #         raise Exception
    #         # return None
    #     else:
    #         return ((self.price_cap - price) / m) + self.lm_volume


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
