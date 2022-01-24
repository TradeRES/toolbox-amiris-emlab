"""
This file contains all Trend classes: mathematical definitions of functions.

Jim Hommes - 13-5-2021
"""
from domain.import_object import *
import random
import math


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
    """
    def __init__(self, name):
        super().__init__(name)
        self.start = 0
        self.growth_rate = 0

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
        elif parameter_name == 'Start':
            self.values.append(float(parameter_value))

    def get_value(self, time):
        while len(self.values) <= time:
            last_value = self.values[-1]
            random_number = random.triangular(-1, 1, 0)
            if random_number < 0:
                self.values.append(last_value * (self.top + (random_number * (self.top - self.min))))
            else:
                self.values.append(last_value * (self.top + (random_number * (self.max - self.top))))
        return self.values[time]


class HourlyLoad(ImportObject):
    """
    The hourly demand per year. The object name is the same as the bus.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.demand_map = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value: str, alternative: str):
        if parameter_name == 'Hourly Demand':
            for line in parameter_value.to_dict()['data']:
                resdict = dict()
                for subline in line[1]['data']:
                    resdict[subline[0]] = subline[1]
                self.demand_map[line[0]] = resdict

    def get_hourly_demand_by_year(self, year):
        return self.demand_map[str(year)]
