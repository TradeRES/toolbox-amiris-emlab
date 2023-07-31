from domain.import_object import *
class LoadShifterwCap(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.peakConsumptionInMW = 0
        self.averagemonthlyConsumptionMWh = 0
        self.monthlyTimeSeriesFile = None
    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'peakConsumptionInMW':
            self.peakConsumptionInMW = int(parameter_value)
        elif parameter_name == 'averagemonthlyConsumptionMWh':
            self.averagemonthlyConsumptionMWh = int(parameter_value)
        elif parameter_name == 'monthlyTimeSeriesFile':
            self.monthlyTimeSeriesFile = str(parameter_value)