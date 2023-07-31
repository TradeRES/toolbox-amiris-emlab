from domain.import_object import *

class InvestmentDecisions(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.invested_in_iteration = dict()


    def add_parameter_value(self, reps, parameter_name: str, id, alternative: str):
        """"
       # object name = candidate technology
        In the DB:
        objectname = str(tick)
        parameter  = str(iteration)
        This function is being read for the plotting. The investment decisions are saved in the invest module
        """
        self.invested_in_iteration[int(parameter_name)] = str(int(id))



class CandidatesNPV(ImportObject):
    def __init__(self, name):
        super().__init__(name)
       # self.invested_times_per_year = dict()
        self.project_value_year = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        """"
        This function is being read for the plotting from object name CandidatePlantsNPV
        name = cnadidate power plants
        The investment decisions  are saved in the invest module
        """
        future_year, iteration = parameter_name.split('-')
        # information from the  CandidatePlantsNPV class
        if future_year not in self.project_value_year.keys():
            self.project_value_year[future_year] = [(int(iteration), parameter_value)]
        else:

            self.project_value_year[future_year].append((int(iteration), parameter_value))

class InstalledCapacity(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.yearly = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        self.yearly[int(parameter_name)] = int(parameter_value)


class InstalledFuturePowerPlants(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.installed_ids = dict()
        # storing as ids because the candidate power plants could have same name
        # these are saved to calculate expecetd capacity and to calculate profits of non dispatched plants
    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        self.installed_ids[int(parameter_name)] = parameter_value