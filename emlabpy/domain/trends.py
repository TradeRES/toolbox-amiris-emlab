"""
This file contains all Trend classes: mathematical definitions of functions.

Jim Hommes - 13-5-2021
Ingrid Sanchez 02-03-22
"""
from random import random

from domain.import_object import *

import math
import numpy as np
from sklearn import linear_model


class Trend(ImportObject):
    """
    This class is the parent class of all Trend classes.
    """

    def __init__(self, name):
        super().__init__(name)

    def get_value(self, time):
        pass


class GeometricTrend(Trend):
    """
    The GeometricTrend is an exponential growth trend. It requires a start value and the growth percentage (0 - 1)
    This is for the technology efficiency
    """

    def __init__(self, name):
        super().__init__(name)
        self.start = 0
        self.growth_rate = 0.0
        # the start can be taken the fixed costs

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'start':
            self.start = float(parameter_value)
        elif parameter_name == 'growthRate':
            self.growth_rate = float(parameter_value)

    def get_value(self, time):
        return pow(1 + self.growth_rate, time) * self.start


class StepTrend(Trend):
    """
    The StepTrend is a linear growth trend. It will grow by a fixed increment.
    """

    def __init__(self, name):
        super().__init__(name)
        self.duration = 0
        self.start = 0
        self.min_value = 0
        self.increment = 0

    def get_value(self, time):
        return max(self.min_value, self.start + math.floor(time / self.duration) * self.increment)

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'duration':
            self.duration = int(parameter_value)
        elif parameter_name == 'start':
            self.start = int(parameter_value)
        elif parameter_name == 'minValue':
            self.min_value = int(parameter_value)
        elif parameter_name == 'increment':
            self.increment = int(parameter_value)


class TriangularTrend(Trend):
    """
    The TriangularTrend grows according to a Triangular distribution.
    Because of the random nature of this trend, values are saved in self.values so that once generated, the value \
    does not change.
    """

    def __init__(self, name):
        super().__init__(name)
        self.top = 0
        self.max = 0
        self.min = 0
        self.values = []

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'Top':
            self.top = float(parameter_value)
        elif parameter_name == 'Max':
            self.max = float(parameter_value)
        elif parameter_name == 'Min':
            self.min = float(parameter_value)
        #elif parameter_name == 'Start': # the EMLAB value was  the start in the Fuel Price Trends table
        #    self.values.append(float(parameter_value))

    def get_value(self, time, substance):
        try:
            fuels =  self.dbrw.query_object_parameter_values_by_object_class("node")
            self.values = [i['parameter_value'] for i in fuels
                       if i['object_name'] == substance
                       and i['parameter_name'] == "expected price"]
        except StopIteration:
            return None

        while len(self.values) <= time:
            last_value = self.values[-1]
            random_number = random.triangular(-1, 0, 1) # TODO this was (-1,  1, 0 ) for competes integration
            if random_number < 0:
                self.values.append(last_value * (self.top + (random_number * (self.top - self.min))))
            else:
                self.values.append(last_value * (self.top + (random_number * (self.max - self.top))))

        self.reps.dbrw.stage_fuel_prices(self.values)
        return self.values[time]

class TimeSeriesImpl():

    def __init__(self):
        self.timeSeries = []
        self.startingYear = 0

    #     * Index of double array corresponds to the tick, unless a
    #     * {@link startingYear} is defined to shift the index.
    #     * Gives the starting year of the time series (probably a negative number) ,
    #     * is relevant for all implementations with an array.

    def getValue(self, time):
        return self.timeSeries[int(time) - int(self.startingYear)]

    def setValue(self, time, value):
        self.timeSeries[int(time) - int(self.startingYear)] = value

    def getTimeSeries(self):
        return self.timeSeries

    def setTimeSeries(self, timeSeries):
        self.timeSeries = timeSeries

    def getStartingYear(self):
        return self.startingYear

    def setStartingYear(self, startingYear):
        self.startingYear = startingYear


class GeometricTrendRegression(Trend):
    def __init__(self, name):
        super().__init__(name)
        self.X = None
        self.Y = None

    def addData(self, x, y):
        #logy = [math.log(y2) for y2 in y] # this was causing error
        self.X = np.array(x).reshape(-1, 1)
        self.Y = np.array(y).reshape(-1, 1)
        #self.X = np.array(x)
        #self.Y = np.array(logy)

    def predict(self, predictedYear):
        regr = linear_model.LinearRegression()
        regr.fit(self.X, self.Y)
        y_pred = regr.predict([[predictedYear]])
        #print(self.X, self.Y, "predictedYear", predictedYear, 'y_pred', y_pred[0][0])
        return  y_pred[0][0]# todo is this correct? before it was with exponent

    # def removeData(self, x, y):
    #     list.remove(x, math.log(y))

    # def addData(self, x, y):
    #     super().addData(x, math.log(y))
    #
    # def removeData(self, x, y):
    #     super().removeData(x, math.log(y))

    # def addData(self, data):
    #     for d in data:
    #         self.addData(d[0], d[1])
    #
    # def removeData(self, data):
    #     i = 0
    #     while i < len(data) and super().getN() > 0:
    #         self.removeData(data[i][0], math.log(data[i][1]))
    #         i += 1

# class HourlyLoad(ImportObject):
#     """
#     The hourly demand per year. The object name is the same as the bus.
#     """
#
#     def __init__(self, name: str):
#         super().__init__(name)
#         self.demand_map = dict()
#
#     def add_parameter_value(self, reps, parameter_name: str, parameter_value: str, alternative: str):
#         if parameter_name == 'Hourly Demand':
#             for line in parameter_value.to_dict()['data']:
#                 resdict = dict()
#                 for subline in line[1]['data']:
#                     resdict[subline[0]] = subline[1]
#                 self.demand_map[line[0]] = resdict
#
#     def get_hourly_demand_by_year(self, year):
#         return self.demand_map[str(year)]