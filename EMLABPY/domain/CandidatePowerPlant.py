from emlabpy.domain.powerplant import *
import logging

class CandidatePowerPlant(PowerPlant):
    def __init__(self, name):
        super().__init__(name)
        # results from Amiris
        self.AwardedPowerinMWh = 0
        self.CostsinEUR = 0
        self.OfferedPowerinMWH = 0
        self.ReceivedMoneyinEUR = 0
        self.Profit = 0
        # scenario from amiris
        # self.technology = None
        # self.location = None
        # self.age = 0
        # self.owner = None
        # self.efficiency = 0
        # self.capacity = 0
        # self.constructionStartTime = 0
        # scenario from artificial emlab parameters
        self.Leadtime = 0
        self.Permittime = 0
        self.Lifetime = 0
        self.InvestedCapital = 0
        self.FixedOperatingCost = 0

        self.viableInvestment = False
        self.expectedEndOfLife = 0
        self.actualNominalCapacity = 0
        self.historicalCvarDummyPlant = 0
        self.electricityOutput = 0
        self.flagOutputChanged = True


    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'AwardedPowerInMWH':
            self.AwardedPowerinMWh = parameter_value
        elif parameter_name == 'CostsInEUR':
            self.CostsinEUR = float(parameter_value)
        elif parameter_name == 'OfferedPowerInMW':
            self.OfferedPowerinMW = float(parameter_value)
        elif parameter_name == 'ReceivedMoneyInEUR':
            self.ReceivedMoneyinEUR = float(parameter_value)
        elif parameter_name == 'Id':
            self.name = parameter_value
        elif parameter_name == 'Technology':
            self.technology = reps.power_generating_technologies[parameter_value]
        elif parameter_name == 'InstalledPowerInMW':
            self.capacity = parameter_value
        elif parameter_name == 'Owner':
            self.owner = parameter_value
        elif parameter_name == 'ComissionedYear':
            self.age = reps.current_tick + reps.start_simulation_year - int(parameter_value)
        elif parameter_name == 'Maximal':
            self.efficiency = float(parameter_value)


    def get_technology(self, time):
        return self.technology

    def get_Profit(self):
        if not self.Profit:
            Profit = self.ReceivedMoneyinEUR - self.CostsinEUR
        return Profit

    def setInvestedCapital(self):
        pass

    def specifyTemporaryPowerPlant(self, tick, energyProducer, location):
        self.setOwner(energyProducer)
        self.setLocation(location)
        self.setConstructionStartTime()
        self.setActualLeadtime(self.technology.getExpectedLeadtime())
        self.setActualPermittime(self.technology.getExpectedPermittime())
        #self.setHistoricalCvarDummyPlant(False)
        self.setActualNominalCapacity(self.getCapacity())
        self.setDismantleTime(1000)
        #self.calculateAndSetActualInvestedCapital(tick)
        self.calculateAndSetActualFixedOperatingCosts(tick)
        print("tick", tick,  "permit", self.getActualPermittime() ,"actuallead" ,self.getActualLeadtime() ,"lifetirme",  self.getTechnology().getExpectedLifetime())

        self.setExpectedEndOfLife(tick + self.getActualPermittime() + self.getActualLeadtime() + self.getTechnology().getExpectedLifetime())
        print("setExpectedEndOfLife", self.expectedEndOfLife)
        return self

    def setConstructionStartTime(self):
        self.constructionStartTime = - (self.technology.expected_leadtime +
                                        self.technology.expected_permittime +
                                        round(random() * self.technology.expected_lifetime)) + 2



class FutureStorageTrader(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.AwardedChargePower = 0
        self.AwardedDischargePower = 0
        self.AwardedPower = 0
        self.StoredMWh = 0
        self.Profit = 0
        #self.OfferedChargePrice = None
        #self.OfferedDischargePrice = None
        #self.OfferedPowerinMW

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'AwardedPowerinMWh':
            self.AwardedPowerinMWh = float(parameter_value)
        elif parameter_name == 'AwardedDischargePower':
            self.AwardedDischargePower = float(parameter_value)
        elif parameter_name == 'AwardedPower':
            self.AwardedPower = float(parameter_value)
        elif parameter_name == 'StoredMWh':
            self.StoredMWh = float(parameter_value)
        elif parameter_name == 'Profit':
            self.Profit = float(parameter_value)


