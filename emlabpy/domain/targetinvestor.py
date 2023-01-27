import pandas as pd

from domain.energyproducer import EnergyProducer

class TargetInvestor(EnergyProducer):
    def __init__(self, name):
        super().__init__(name)
        self.targetTechnology = None
        self.targetCountry = None
        self.yearly_increment = pd.Series(dtype='float64')
        self.trend = None


    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'targetTechnology':
            self.targetTechnology = parameter_value
        elif parameter_name == 'targetCountry' or parameter_name == 'targetNode':
            self.targetCountry = parameter_value
        elif parameter_name == 'start_capacity':
            pass
           # self.start_capacity = parameter_value
        else: # todo improve this condition
            year = parameter_name[0:4]
            self.yearly_increment.at[int(year)] = parameter_value

    def get_cummulative_capacity(self, from_year, to_year, last_year):
        if to_year > last_year: # erase this if there are capacity targets after 2050
            to_year = last_year
        list_years = list(range(from_year,to_year))
        increment_in_years  = self.yearly_increment[list_years]
        cummulative = increment_in_years.cumsum()
        return cummulative[to_year-1]