from domain.import_object import *

class Profits(ImportObject):

    def __init__(self, name):
        super().__init__(name)
        self.profits_per_iteration_names  = dict()
        self.profits_per_iteration = dict()
        self.profits_per_iteration_names_candidates  = dict()
        self.profits_per_iteration_candidates = dict()

    def add_parameter_value(self, reps, parameter_name, parameter_value, iteration):
        """"
        This function is being read for the plotting. The totalProfits are being saved in the module Investmentdecision
        # object name =  year
        # alternative = iteration
        The data is stored in db investment with the object name "tick - iteration"
        """
        # -----------------------------Profits and PowerPlants are read from the Profits classname
        if parameter_name == 'PowerPlants':
            # object name is year and alternative is the iteration.
            self.profits_per_iteration_names[iteration] = parameter_value
        elif parameter_name == 'Profits':
            self.profits_per_iteration[iteration] = parameter_value
        elif parameter_name == 'PowerPlantsC':
            # object name is year and alternative is the iteration.
            self.profits_per_iteration_names_candidates[iteration] = parameter_value
        elif parameter_name == 'ProfitsC':
            self.profits_per_iteration_candidates[iteration] = parameter_value