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
        elif parameter_name == 'targetCountry' :
            self.targetCountry = parameter_value
        elif parameter_name == 'yearlyIncrease' :
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index = index)
            self.yearly_increment= pd_series.sort_values(ascending=True)

    def get_cummulative_capacity(self, from_year, to_year, last_year):
        if to_year > last_year: # erase this if there are capacity targets after 2050
            to_year = last_year
        list_years = list(range(from_year,to_year))
        increment_in_years  = self.yearly_increment[list_years]
        cummulative = increment_in_years.cumsum()
        return cummulative[to_year-1]