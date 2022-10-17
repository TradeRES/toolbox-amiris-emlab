from domain.import_object import *

class InvestmentDecisions(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.invested_in_iteration = dict()
        self.invested_in_tick = dict()

    def add_parameter_value(self, reps, parameter_name: str, id, alternative: str):
        """"
        object name = candidate technology
        In the DB objectname = str(futureYear) + "-" + str(iteration)
        This function is being read for the plotting. The investment decisions are saved in the invest module
        """
        future_year, iteration = parameter_name.split('-')
        decision_year = alternative
        if future_year not in self.invested_in_iteration.keys():
            self.invested_in_iteration[future_year] = [iteration]
            # todo: better save this as strings
            self.invested_in_tick[decision_year] = [str(int(id))]
        else:
            self.invested_in_iteration[future_year].append(iteration)
            self.invested_in_tick[decision_year].append( str(int(id)))


class Investments(ImportObject):
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

