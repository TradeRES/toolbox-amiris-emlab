from domain.import_object import *

class Investments(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.invested_in_iteration = dict()
       # self.invested_times_per_year = dict()
        self.project_value_year = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        year, iteration = parameter_name.split('-')
        if alternative == "InvestmentDecisions":
            if year not in self.invested_in_iteration.keys():
                self.invested_in_iteration[year] = [iteration]
            else:
                self.invested_in_iteration[year].append(iteration)
        else: # here is the information from the  CandidatePlantsNPV class read
            if year not in self.project_value_year.keys():
                self.project_value_year[year] = [parameter_value]
            else:
                self.project_value_year[year].append(parameter_value)

    def get_project_value_year(self):
        return self.project_value_year
