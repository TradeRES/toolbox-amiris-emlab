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
            if reps.current_year not in pd_series.index:
                pd_series[reps.current_year] = np.nan
                pd_series = pd_series.sort_index()
                interpolated_data = pd_series.interpolate(method='index')
                self.peakConsumptionInMW  = int(interpolated_data[reps.current_year])
            else:
                self.peakConsumptionInMW = pd_series[reps.current_year]

        elif parameter_name == 'averagemonthlyConsumptionMWhyearly':
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index=index)
            if reps.runningModule == "plotting":
                self.averagemonthlyConsumptionMWh = pd_series
            else:
                if reps.current_year not in pd_series.index:
                    pd_series[reps.current_year] = np.nan
                    pd_series = pd_series.sort_index()
                    interpolated_data = pd_series.interpolate( method="index")
                    self.averagemonthlyConsumptionMWh = int(interpolated_data[reps.current_year])
                else:
                    self.averagemonthlyConsumptionMWh =  pd_series[reps.current_year]





