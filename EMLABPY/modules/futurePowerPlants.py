from emlabpy.domain.CandidatePowerPlant import *
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
        self.newTechnologies = None
        self.lastrenewableId = 0
        self.lastconventionalId = 0
        self.laststorageId = 0
        self.RESLabel = "VariableRenewableOperator"
        self.conventionalLabel = "ConventionalPlantOperator"
        self.storageLabel = "StorageTrader"

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
        self.getlastIds()
        for key, candidateTechnology in self.reps.newTechnology.items():
            if candidateTechnology.type == self.RESLabel:
                self.lastrenewableId+=1
                object_name = self.lastrenewableId
            elif candidateTechnology.type == self.conventionalLabel:
                self.lastconventionalId+=1
                object_name = self.lastconventionalId
            elif candidateTechnology.type == self.storageLabel:
                self.laststorageId+=1
                object_name = self.laststorageId
            self.reps.candidatePowerPlants[object_name] = CandidatePowerPlant(object_name)
            self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, "type", candidateTechnology.type, 0)
            self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, "technology", candidateTechnology.technology, 0)
            self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, "InstalledPowerInMW", candidateTechnology.InstalledPowerInMW, 0)
            # parameternames = [Technology, Status, CommissionedYear, InstalledPowerInMW, FuelType, Label]

    def getlastIds(self):
        # get maximum number of power plan
        lastbuiltrenewable = []
        lastbuiltconventional = []
        lastbuiltstorage = []
        for id, pp in self.reps.power_plants.items():
            if pp.label == self.RESLabel:
                lastbuiltrenewable.append(int(id))
            elif pp.label == self.conventionalLabel:
                lastbuiltconventional.append(int(id))
            elif pp.label == self.storageLabel:
                lastbuiltstorage.append(int(id))
        lastbuiltrenewable.sort()
        lastbuiltconventional.sort()
        lastbuiltstorage.sort()
        self.lastrenewableId = lastbuiltrenewable[-1]
        self.lastconventionalId = lastbuiltconventional[-1]
        if len(lastbuiltstorage) >0: # TODO: give numeration to storage so that it doesnt overlap with renewables
            self.laststorageId = lastbuiltstorage[-1]

