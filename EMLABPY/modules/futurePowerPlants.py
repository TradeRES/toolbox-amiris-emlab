from emlabpy.domain import CandidatePowerPlant
from emlabpy.domain.trends import TriangularTrend
from emlabpy.modules.defaultmodule import DefaultModule
from emlabpy.domain.substances import Substance
import numpy as np
import logging
class FuturePowerPlants(DefaultModule):

    def __init__(self, reps):
        super().__init__("Clearing the market", reps)
        self.newPowerPlant = None
        self.nextTimePoint = 0
        self.futureInvestmentyear = 0
        self.expectedFuelPrices = None
        self.expectedDemand = None
        reps.dbrw.stage_init_expected_prices_structure()

    def act(self):
        self.setTimeHorizon()
        self.setExpectations()
        self.createCandidatePowerPlants()

    def setTimeHorizon(self):
        self.nextTimePoint = self.reps.current_tick

    def setExpectations(self):
        for k, substance in self.reps.substances.items():
            substance.get_price_for_tick(self.nextTimePoint, substance)
            self.reps.dbrw.stage_fuel_prices(substance)
        #self.nextDemand()

    def createCandidatePowerPlants(self):
        # get maximum number of power plan
        lastrenewable = []
        lastconventional = []
        for powerplant, info in self.reps.power_plants.items():
            if info.label == "VariableRenewableOperator":
                lastrenewable.append(int(powerplant))
            else:
                lastconventional.append(int(powerplant))
        # 
        # newrenewable = max(lastrenewable) + 1
        # print(newrenewable)
        # newConventional = max(lastconventional) + 1
        # print(newConventional)

        # parameternames = [Technology, Status, CommissionedYear, InstalledPowerInMW, Label ]
        # parameternames = [Technology, Status, CommissionedYear, InstalledPowerInMW, FuelType, Label]
        #
        # parameter_alt = 0
        # for candidateTechnology in candidateTechnologies:
        #     if candidateTechnology.label == "VariableRenewableOperator":
        #         object_name = newrenewable
        #         parameter_name
        #         self.reps.candidatePowerPlants[object_name] = CandidatePowerPlant(object_name)
        #         self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, parameter_name, parameter_value, parameter_alt)
        #
        #         to_dict[object_name] = class_to_create(object_name)
        #
        #         newrenewable+=1


           # self.add_parameter_value_to_repository(self.reps, db_line, self.reps.candidatePowerPlants, CandidatePowerPlant)


        def add_parameter_value_to_repository(self, reps , db_line , to_dict , class_to_create):
            object_name = db_line[1]
            parameter_name = db_line[2]
            parameter_value = db_line[3]
            parameter_alt = db_line[4]
            if object_name not in to_dict.keys():
                to_dict[object_name] = class_to_create(object_name)
            to_dict[object_name].add_parameter_value(reps, parameter_name, parameter_value, parameter_alt)
    #
