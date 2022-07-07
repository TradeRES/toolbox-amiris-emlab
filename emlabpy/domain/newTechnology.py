from domain.trends import *

class NewTechnology(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.type = ""
        self.capacity = 0
        self.technology = None

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'type':
            self.type = parameter_value
        elif parameter_name == 'Unit size':
            self.capacity = int(parameter_value)
        elif parameter_name == 'Technology':
            self.technology = reps.power_generating_technologies[parameter_value]

