from domain.import_object import *

class Investments(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.invested = dict()
        self.project_value_year = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        year, iteration = parameter_name.split('-')
        if alternative == "Invested":
            if year not in self.invested.keys():
                self.invested[year] = 1
            else:
                self.invested[year] += 1
        else:
            if year not in self.project_value_year.keys():
                self.project_value_year[year] = [parameter_value]
            else:
                self.project_value_year[year].append(parameter_value)

