import pandas as pd

from domain.import_object import *

class WeatherYears(ImportObject):
    """
    This class is the parent class of all Trend classes.
    """

    def __init__(self, name):
        super().__init__(name)
        self.yearly = pd.DataFrame()

    def add_parameter_value(self, reps, parameter_name , parameter_value, alternative ):
        self.yearly = pd.DataFrame(parameter_value.values, index=parameter_value.indexes)