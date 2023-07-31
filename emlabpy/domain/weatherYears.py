import pandas as pd

from domain.import_object import *
class WeatherYears(ImportObject):

    def __init__(self, name):
        super().__init__(name)
        self.sequence = None
    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == reps.iteration_weather:
            array = parameter_value.to_dict()
            values = [int(i) for i in array["data"]]
            pd_series = pd.Series(values)
            self.sequence = pd_series