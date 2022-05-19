from domain.import_object import *

class YearlyEmissions(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.emissions = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if int(alternative) not in self.emissions.keys():
            self.emissions[int(alternative)] = dict()
        self.emissions[int(alternative)][parameter_name] = parameter_value