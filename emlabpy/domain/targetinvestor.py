import pandas as pd

from domain.energyproducer import EnergyProducer

class TargetInvestor(EnergyProducer):
    def __init__(self, name):
        super().__init__(name)
        self.targetTechnology = None
        self.targetCountry = None
        self.yearly_increment = pd.Series()
        self.trend = None
        self.start_capacity = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'targetTechnology':
            self.targetTechnology = parameter_value
        elif parameter_name == 'targetCountry':
            self.targetCountry = parameter_value
        elif parameter_name == 'start_capacity':
            self.start_capacity = parameter_value
        else:
            year = parameter_name[0:4]
            self.yearly_increment.at[int(year)] = parameter_value
            #self.yearly_increment.set_value(parameter_value)

    def set_start_capacity(self, start_capacity):
        self.start_capacity = start_capacity

    def get_cummulative_capacity(self, from_year, to_year):
        list_years = list(range(from_year,to_year))
        increment_in_years  = self.yearly_increment[list_years]
        cummulative = increment_in_years.cumsum()
        return self.start_capacity + cummulative[to_year-1]