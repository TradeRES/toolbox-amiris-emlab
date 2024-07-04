import logging
from domain.import_object import *
from domain.energyproducer import *

class PowerPlantDispatchPlan(ImportObject):
    """"
    This module is read for each year, not all years are needed
    """
    def __init__(self, name):
        super().__init__(name)
        self.power_plant_id = None
        self.accepted_amount = 0
        self.revenues = 0
        self.variable_costs = 0
        self.consumed_amount = 0
        self.plant = None
        self.tick = 0
        self.status = 'Awaiting confirmation'
        self.capped_revenues = 0
    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        self.tick = reps.current_year # alternative
        # the power plant dispatch plan name correspond to the id of the power plant
        if parameter_name == 'PRODUCTION_IN_MWH':
            self.accepted_amount = float(parameter_value)
        if parameter_name == 'REVENUES_IN_EURO':
            self.revenues = float(parameter_value)
        if parameter_name == 'VARIABLE_COSTS_IN_EURO':
            self.variable_costs = float(parameter_value)
            self.power_plant_id = self.name
        if parameter_name == 'CONSUMPTION_IN_MWH':
            self.consumed_amount = float(parameter_value)
            self.power_plant_id = self.name
        elif  parameter_name == 'CAPPED_REVENUES':
            self.capped_revenues = float(parameter_value)
        # the CONTRIBUTION_MARGIN_IN_EURO is equal to revenues - variable costs in euro


class PowerPlantDispatchPlansALL(ImportObject):
    """"
    This module is read for plotting
    """
    def __init__(self, name):
        super().__init__(name)
        self.accepted_amount = dict()
        self.consumed_amount = dict()
        self.revenues = dict()
        self.variable_costs = dict()

    def add_parameter_value(self, reps, parameter_name, parameter_value, plant_id):
        # the power plant dispatch plan name correspond to the YEAR
        if parameter_name == 'PRODUCTION_IN_MWH':
            self.accepted_amount[plant_id] = float(parameter_value)
        if parameter_name == 'REVENUES_IN_EURO':
            self.revenues[plant_id] = float(parameter_value)
        if parameter_name == 'VARIABLE_COSTS_IN_EURO':
            self.variable_costs[plant_id] = float(parameter_value)
        if parameter_name == 'CONSUMPTION_IN_MWH':
            self.consumed_amount[plant_id] = float(parameter_value)