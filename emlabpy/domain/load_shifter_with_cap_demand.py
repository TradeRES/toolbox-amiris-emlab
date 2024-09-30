from domain.import_object import *
import pandas as pd
import numpy as np
class LoadShifterwCap(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.peakConsumptionInMW = 0
        self.averagemonthlyConsumptionMWh = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'peakConsumptionInMW':
            self.peakConsumptionInMW = int(parameter_value)
        elif parameter_name == 'averagemonthlyConsumptionMWh':
            self.averagemonthlyConsumptionMWh = int(parameter_value)

        elif parameter_name == 'peakConsumptionInMWyearly':
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index=index)
            self.peakConsumptionInMW = pd_series

        elif parameter_name == 'averagemonthlyConsumptionMWhyearly':
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index=index)
            self.averagemonthlyConsumptionMWh = pd_series


    def get_average_monthly_consumption(self, year):
        if isinstance(self.averagemonthlyConsumptionMWh, int):
            return self.averagemonthlyConsumptionMWh
        else:
            if year not in self.averagemonthlyConsumptionMWh.index:
                self.averagemonthlyConsumptionMWh[year] = np.nan
                pd_series = self.averagemonthlyConsumptionMWh.sort_index()
                interpolated_data = pd_series.interpolate( method="index")
                averagemonthlyConsumptionMWh = int(interpolated_data[year])
            else:
                averagemonthlyConsumptionMWh =  self.averagemonthlyConsumptionMWh[year]
            return averagemonthlyConsumptionMWh


    def get_yearly_peak_consumption(self, year):
        if isinstance( self.peakConsumptionInMW, int):
            return  self.peakConsumptionInMW
        else:
            if year not in  self.peakConsumptionInMW.index:
                self.peakConsumptionInMW[year] = np.nan
                pd_series =  self.peakConsumptionInMW.sort_index()
                interpolated_data = pd_series.interpolate( method="index")
                averagemonthlyConsumptionMWh = int(interpolated_data[year])
            else:
                averagemonthlyConsumptionMWh =   self.peakConsumptionInMW[year]
            return averagemonthlyConsumptionMWh