from domain.import_object import *

class Investments(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.invested_in_iteration = dict()
       # self.invested_times_per_year = dict()
        self.project_value_year = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        """"
        This function is being read for the plotting. The investment decisions  are saved in the invest module
        """
        future_year, iteration = parameter_name.split('-')
        if alternative == "InvestmentDecisions":
            if future_year not in self.invested_in_iteration.keys():
                self.invested_in_iteration[future_year] = [iteration]
            else:
                self.invested_in_iteration[future_year].append(iteration)
        else: #                                                     information from the  CandidatePlantsNPV class
            if future_year not in self.project_value_year.keys():
                self.project_value_year[future_year] = [parameter_value]
            else:
                # print(iteration)
                # print(parameter_value)
                self.project_value_year[future_year].append((iteration, parameter_value))

