from domain.powerplant import *

import logging

class CandidatePowerPlant(PowerPlant):
    def __init__(self, name):
        super().__init__(name)
        # results from Amiris
        self.AwardedPowerinMWh = 0
        self.CostsinEUR = 0
        self.OfferedPowerinMWH = 0
        self.ReceivedMoneyinEUR = 0
        self.Profit = 0 # operational profits
        # scenario from artificial emlab parameters
        self.Leadtime = 0
        self.Permittime = 0
        self.Lifetime = 0
        self.InvestedCapital = 0
        self.FixedOperatingCost = 0
        self.viableInvestment = True # initially all candidate power plants should be investable
        self.expectedEndOfLife = 0
        self.actualNominalCapacity = 0

        self.historicalCvarDummyPlant = 0
        self.electricityOutput = 0
        self.flagOutputChanged = True
        self.capacity = 1 # all power plants are first tested for a capacity of 1 # capacity is the one being tested
        self.capacityTobeInstalled = 0
        self.capacityRealistic = 1

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'Id':
            self.id = parameter_value
        elif parameter_name == 'Technology':
            self.technology = reps.power_generating_technologies[parameter_value]
            self.actualEfficiency = self.technology.efficiency
        elif parameter_name == 'ViableInvestment':
            self.viableInvestment = bool(parameter_value)
        # capacityTobeInstalled is the one being really installed, after the test of dummy capacity has been tested
        elif parameter_name == "Realistic_capacity":
            self.capacityRealistic = int(parameter_value)
            if reps.last_investable_technology == True:
                self.capacityTobeInstalled = int(parameter_value)
                self.capacity = int(parameter_value)
            else:
                if reps.realistic_candidate_capacities_tobe_installed == True:
                    self.capacityTobeInstalled = int(parameter_value)
                elif reps.realistic_candidate_capacities_tobe_installed == False:
                    self.capacityTobeInstalled = reps.dummy_capacity_to_be_installed
            # capacity is the one being tested
                if reps.realistic_candidate_capacities_to_test == True :
                    self.capacity = int(parameter_value)
                elif reps.realistic_candidate_capacities_to_test == False:
                    self.capacity = reps.dummy_capacity_to_test

    def specifyCandidatePPCapacityLocationOwner(self, reps, energyProducer):
        self.setOwner(energyProducer)
        self.setLocation(reps.country)
        self.setActualNominalCapacity(self.capacity)  # capacity is the one being tested
        return self

    def setConstructionStartTick(self):
        self.constructionStartTime = - (self.technology.expected_leadtime +
                                    self.technology.expected_permittime +
                                    self.technology.expected_lifetime)


    def setViableInvestment(self, viableInvestment):
        self.viableInvestment = viableInvestment


class FutureStorageTrader(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.AwardedChargePower = 0
        self.AwardedDischargePower = 0
        self.AwardedPower = 0
        self.StoredMWh = 0
        self.Profit = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'AwardedPowerinMWh':
            self.AwardedPowerinMWh = float(parameter_value)
        elif parameter_name == 'AwardedDischargePower':
            self.AwardedDischargePower = float(parameter_value)
        elif parameter_name == 'AwardedPower':
            self.AwardedPower = float(parameter_value)
        elif parameter_name == 'StoredMWh':
            self.StoredMWh = float(parameter_value)
        elif parameter_name == 'operationalProfit':
            self.Profit = float(parameter_value)


