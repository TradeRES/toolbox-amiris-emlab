"""
This file contains all classes directly related to
PowerPlant
"""
from domain.energyproducer import EnergyProducer
from domain.import_object import *
from random import random
import logging

from domain.loans import Loan
from util import globalNames


class PowerPlant(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.id = 0
        self.technology = None
        self.location = ""
        self.age = None
        self.owner = None # change if there are more energyproducers
        self.capacity = 0
        self.efficiency = 0
        # TODO: Implement GetActualEfficiency
        self.banked_allowances = [0 for i in range(100)]
        self.status = globalNames.power_plant_status_not_set  # 'Operational' , 'InPipeline', 'Decommissioned', 'TobeDecommissioned'
        self.fictional_status = globalNames.power_plant_status_not_set
        self.loan = None
        self.downpayment = None
        self.dismantleTime = 0  # in terms of tick
        self.expectedEndOfLife = 0  # in terms of tick
        # scenario from artificial emlab parameters
        self.constructionStartTime = 0
        self.actualLeadtime = 0
        self.actualPermittime = 0 # todo clear this functionalities
        self.actualLifetime = 0
        self.commissionedYear = 0
        self.label = ""
        self.actualInvestedCapital = 0
        self.actualFixedOperatingCost = 0
        self.actualEfficiency = 0
        self.actualNominalCapacity = 0
        self.historicalCvarDummyPlant = 0
        self.electricityOutput = 0
        self.flagOutputChanged = True
        # from Amiris results
        self.subsidized = False
        self.AwardedPowerinMWh = 0
        self.CostsinEUR = 0
        self.OfferedPowerinMWH = 0
        self.ReceivedMoneyinEUR = 0
        self.Profit = 0
        self.chargingEfficiency = 0
        self.dischargingEfficiency = 0
        self.energyToPowerRatio = 0
        self.initialEnergyLevelInMWH = 0
        self.selfDischargeRatePerHour = 0
        self.actualDischargingEfficiency = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        # do not import decommissioned power plants to the repository if it is not the plotting step
        if reps.dbrw.read_investments == False and self.name in (
                reps.decommissioned["Decommissioned"]).Decommissioned:
            return
        elif parameter_name == 'Status':
            self.status = parameter_value
        elif parameter_name == 'Efficiency':  # the efficiency stored in the DB is the actual one
            self.actualEfficiency = float(parameter_value)
        elif parameter_name == 'DischargingEfficiency':  # the efficiency stored in the DB is the actual one
            self.actualDischargingEfficiency = float(parameter_value)
        elif parameter_name == 'Location':
            self.location = parameter_value
        elif parameter_name == 'Id':
            self.id = int(parameter_value)
        if parameter_name == 'Technology':
            self.technology = reps.power_generating_technologies[parameter_value]
        elif parameter_name == 'Capacity':
            self.capacity = parameter_value
        elif parameter_name == 'Owner':
            self.owner = reps.energy_producers[parameter_value]
        elif parameter_name == 'Age':
            self.age = int(parameter_value) # for emlab data the commissioned year can be read from the age
            self.commissionedYear = reps.current_year - int(parameter_value)
        elif parameter_name == 'dismantleTime':
            self.dismantleTime = int(parameter_value)
        elif parameter_name == 'ComissionedYear':
            # for amiris data the age can be read from the commisioned year
            print(self.name, "assigned age by commissioned year ")
            self.commissionedYear = int(parameter_value)
            self.age = reps.current_tick + reps.start_simulation_year - int(parameter_value)
        elif parameter_name == 'Maximal':
            self.efficiency = float(parameter_value)
        elif parameter_name == 'AwardedPowerInMWH':
            self.AwardedPowerinMWh = parameter_value
        elif parameter_name == 'CostsInEUR':
            self.CostsinEUR = float(parameter_value)
        elif parameter_name == 'OfferedPowerInMW':
            self.OfferedPowerinMW = float(parameter_value)
        elif parameter_name == 'ReceivedMoneyInEUR':
            self.ReceivedMoneyinEUR = float(parameter_value)
        elif parameter_name == 'label':
            self.label = parameter_value
        elif parameter_name == 'ChargingEfficiency':
            self.chargingEfficiency = float(parameter_value)
        elif parameter_name == 'DischargingEfficiency':
            self.dischargingEfficiency = float(parameter_value)
        elif parameter_name == 'EnergyToPowerRatio':
            self.energyToPowerRatio = float(parameter_value)
        elif parameter_name == 'InitialEnergyLevelInMWH':
            self.initialEnergyLevelInMWH = float(parameter_value)
        elif parameter_name == 'SelfDischargeRatePerHour':
            self.selfDischargeRatePerHour = float(parameter_value)

    def calculate_emission_intensity(self, reps):
        # emission = 0
        # substance_in_fuel_mix_object = reps.get_substances_in_fuel_mix_by_plant(self)
        # for substance_in_fuel_mix in substance_in_fuel_mix_object.substances:
        #     # CO2 Density is a ton CO2 / MWh
        #     co2_density = substance_in_fuel_mix.co2_density * (1 - float(
        #         self.technology.co2_capture_efficiency))
        #
        #     # Returned value is ton CO2 / MWh
        #     emission_for_this_fuel = substance_in_fuel_mix_object.share * co2_density / self.efficiency
        #     emission += emission_for_this_fuel
        # return emission
        if self.technology.fuel != '':
            co2_density = self.technology.fuel.co2_density * (1 - float(
                self.technology.co2_capture_efficiency))
            emission = co2_density / self.technology.efficiency
        else:
            emission = 0
        return emission

    def get_actual_fixed_operating_cost(self):
        per_mw = self.technology.get_fixed_operating_cost(self.constructionStartTime +
                                                          int(self.technology.expected_leadtime) +
                                                          int(self.technology.expected_permittime))
        capacity = self.get_actual_nominal_capacity()
        return per_mw * capacity

    def get_Profit(self):
        if not self.Profit:
            self.Profit = self.ReceivedMoneyinEUR - self.CostsinEUR
        return self.Profit

    def get_actual_nominal_capacity(self):
        return self.capacity
        # if self.capacity == 0:
        #     return self.technology.capacity * float(self.location.parameters['CapacityMultiplicationFactor'])
        # else:
        #     return self.capacity

    def calculate_marginal_fuel_cost_per_mw_by_tick(self, reps, time):
        # fc = 0
        # substance_in_fuel_mix_object = reps.get_substances_in_fuel_mix_by_plant(self)
        # for substance_in_fuel_mix in substance_in_fuel_mix_object.substances:
        #     # Fuel price is Euro / MWh
        #     fc += substance_in_fuel_mix_object.share * substance_in_fuel_mix.get_price_for_tick(time) / self.efficiency
        # return fc
        if self.technology.fuel != '':
            # fc = ((self.technology.fuel.futurePrice.values[0] + self.technology.fuel.futurePrice.values[1]) / 2) / \
            #      self.technology.efficiency
            fc = self.technology.fuel.futurePrice.values[0] / self.technology.efficiency
        else:
            fc = 0
        return fc

    def calculate_co2_tax_marginal_cost(self, reps):
        co2_intensity = self.calculate_emission_intensity(reps)
        co2_tax = 0  # TODO: Retrieve CO2 Market Price
        return co2_intensity * co2_tax

    def calculate_marginal_cost_excl_co2_market_cost(self, reps, time):
        mc = 0
        mc += self.calculate_marginal_fuel_cost_per_mw_by_tick(reps, time)
        mc += self.calculate_co2_tax_marginal_cost(reps)
        return mc

    def get_load_factor_for_production(self, production):
        if self.capacity != 0:
            return production / self.capacity
        else:
            return 0

    def add_values_from_df(self, results):
        self.AwardedPowerinMWh = results.PRODUCTION_IN_MWH
        self.CostsinEUR = results.VARIABLE_COSTS_IN_EURO
        self.ReceivedMoneyinEUR = results.REVENUES_IN_EURO
        self.Profit = results.CONTRIBUTION_MARGIN_IN_EURO

    # createPowerPlant from target investment or from investment algorithm chosen power plant
    def specifyPowerPlant(self, tick, year, energyProducer, location, capacity, pgt):
        self.dischargingEfficiency = 0
        self.setCapacity(capacity)
        self.setTechnology(pgt)
        self.setOwner(energyProducer)
        self.setLocation(location)
        self.setActualLeadtime(self.technology.getExpectedLeadtime())
        self.setActualPermittime(self.technology.getExpectedPermittime())
        self.commissionedYear = year + pgt.getExpectedLeadtime() + pgt.getExpectedPermittime()
        self.age = - pgt.getExpectedLeadtime() - pgt.getExpectedPermittime()
        self.constructionStartTime = tick
        self.calculateAndSetActualEfficiency(self.getConstructionStartTime())
        self.calculateAndSetActualFixedOperatingCosts(self.getConstructionStartTime())
        self.calculateAndSetActualInvestedCapital(self.getConstructionStartTime())
        self.setDismantleTime(1000)
        self.setExpectedEndOfLife(
            tick + self.getActualPermittime() + self.getActualLeadtime() + self.getTechnology().getExpectedLifetime())
        self.status = globalNames.power_plant_status_inPipeline

    # createPowerPlant from initial database
    def specifyPowerPlantsInstalled(self, tick):  # TODO add this information to the database
        self.setActualLeadtime(self.technology.getExpectedLeadtime())
        self.setActualPermittime(self.technology.getExpectedPermittime())
        self.setActualNominalCapacity(self.getCapacity())
        self.setConstructionStartTime()  # minus years, considering the age, permit and lead time
        self.calculateAndSetActualInvestedCapital(self.getConstructionStartTime())
        self.calculateAndSetActualEfficiency(self.getConstructionStartTime())
        self.calculateAndSetActualFixedOperatingCosts(self.getConstructionStartTime())
        self.setDismantleTime(1000)  # TODO set this first to 1000 and then it changes in later stage?
        # as a default the expected end of life is assigned by the technology expected lifetime
        if self.dismantleTime < 1000:
            self.setExpectedEndOfLife = self.dismantleTime
        else:
            self.setExpectedEndOfLife(  # set in terms of tick
                tick + self.getActualPermittime() + self.getActualLeadtime() + self.getTechnology().getExpectedLifetime())
        self.setloan(self.owner)
        self.setPowerPlantsStatusforInstalledPowerPlants()
        return self

    def setloan(self, energyProducer):
        loan = Loan()
        loan.setFrom(energyProducer.name)
        loan.setTo(None)  # TODO check if this is really so or ot should be bank
        amountPerPayment = loan.determineLoanAnnuities(
            self.getActualInvestedCapital() * energyProducer.getDebtRatioOfInvestments(),
            self.getTechnology().getDepreciationTime(), energyProducer.getLoanInterestRate())
        loan.setAmountPerPayment(amountPerPayment)
        loan.setTotalNumberOfPayments(self.getTechnology().getDepreciationTime())
        loan.setLoanStartTime(self.getConstructionStartTime())  # minus years
        loan.setNumberOfPaymentsDone(-self.getConstructionStartTime())
        loan.setRegardingPowerPlant(self.name)
        self.setLoan(loan)

    def setPowerPlantsStatusforInstalledPowerPlants(self):
        if self.age is not None:
            if self.age >= self.technology.expected_lifetime:
                self.status = globalNames.power_plant_status_to_be_decommissioned
            elif self.age < 0:
                self.status = globalNames.power_plant_status_inPipeline
            else:
                self.status = globalNames.power_plant_status_operational
        else:
            print("power plant dont have an age ", self.name)

    def isOperational(self, currentTick):
        finishedConstruction = self.getConstructionStartTime() + self.calculateActualPermittime() + self.calculateActualLeadtime()
        if finishedConstruction <= currentTick:
            # finished construction
            if self.getDismantleTime() == 1000:
                # No dismantletime set, therefore must be not yet dismantled.
                return True
            elif self.getDismantleTime() > currentTick:
                # Dismantle time set, but not yet reached
                return True
            elif self.getDismantleTime() <= currentTick:
                # Dismantle time passed so not operational
                return False
        # Construction not yet finished.
        return False

    def isExpectedToBeOperational(self, futuretick, futureyear):
        # if the plants commissioned year is less than the future tick, then passes from in pipeline to operational
        if self.commissionedYear <= futureyear:
            # also plants that are not having a
            if self.getExpectedEndOfLife() > futuretick:
                # Powerplant is not expected to be dismantled
                return True
        else:
            return False

    def isInPipeline(self, currentTick): # Todo, if this is not used, then erase
        finishedConstruction = self.constructionStartTime + self.actualPermittime + self.actualLeadtime
        if finishedConstruction <= currentTick:
            return False
        else:
            # finished construction
            if self.getDismantleTime() == 1000:
                # No dismantletime set, therefore must be not yet dismantled.
                return True
            elif self.getDismantleTime() > currentTick:
                # Dismantle time set, but not yet reached
                return True
            elif self.getDismantleTime() <= currentTick:
                # Dismantle time passed so not operational
                return False
        # Construction finished

    def getAvailableCapacity(self, currentTick):
        if self.isOperational(currentTick):
            return self.getActualNominalCapacity()
        else:
            return 0

    def calculateActualLeadtime(self):
        actual = None
        actual = self.actualLeadtime
        if actual <= 0:
            actual = self.technology.expected_leadtime
        return actual

    def calculateActualPermittime(self):
        actual = None
        actual = self.actualPermittime
        if actual <= 0:
            actual = self.technology.expected_permittime
        return actual

    def calculateActualLifetime(self):
        actual = None
        actual = self.actualLifetime
        if actual <= 0:
            actual = self.technology.expected_lifetime
        return actual

    def isWithinTechnicalLifetime(self, currentTick):
        endOfTechnicalLifetime = self.constructionStartTime + \
                                 self.actualPermittime + \
                                 self.actualLeadtime + \
                                 self.actualLifetime
        if endOfTechnicalLifetime <= currentTick:
            return False
        return True

    def calculateAndSetActualInvestedCapital(self, timeOfPermitorBuildingStart):
        self.setActualInvestedCapital(self.technology.getInvestmentCost(
            timeOfPermitorBuildingStart + self.getActualPermittime() + self.getActualLeadtime()) * self.get_actual_nominal_capacity())

    # the growth trend
    def calculateAndSetActualFixedOperatingCosts(self, timesinceBuildingStart):  # tick = timesinceBuildingStart
        self.setActualFixedOperatingCost(self.getTechnology().get_fixed_operating_cost_trend(timesinceBuildingStart \
                                                                                             + self.getActualLeadtime() + self.getActualPermittime()) \
                                         * self.getActualNominalCapacity())

    def calculateAndSetActualEfficiency(self, timeOfPermitorBuildingStart):
        self.setActualEfficiency(self.getTechnology().getEfficiency(
            timeOfPermitorBuildingStart + self.getActualLeadtime() + self.getActualPermittime()))

    def calculateEmissionIntensity(self):
        emission = 0
        for sub in self.getFuelMix():
            substance = sub.getSubstance()
            fuelAmount = sub.getShare()
            co2density = substance.getCo2Density() * (1 - self.getTechnology().getCo2CaptureEffciency())

            # determine the total cost per MWh production of this plant
            emissionForThisFuel = fuelAmount * co2density
            emission += emissionForThisFuel

        return emission

    def getActualNominalCapacity(self):
        return self.actualNominalCapacity

    def getActualFixedOperatingCost(self):
        return self.actualFixedOperatingCost

    def setActualFixedOperatingCost(self, actualFixedOperatingCost):
        self.actualFixedOperatingCost = actualFixedOperatingCost

    def getIntermittentTechnologyNodeLoadFactor(self):
        return self.reps.findIntermittentTechnologyNodeLoadFactorForNodeAndTechnology(self.getLocation(),
                                                                                      self.getTechnology())

    # general
    def setName(self, label):
        self.name = label
        self.label = label

    def getTechnology(self):
        return self.technology

    def setTechnology(self, technology):
        self.technology = technology

    def setLocation(self, location):
        self.location = location

    def getLocation(self):
        return self.location

    def setOwner(self, owner):
        self.owner = owner

    def getOwner(self):
        return self.owner

    def getCapacity(self):
        return self.capacity

    def setCapacity(self, capacity):
        self.capacity = capacity

    def setName(self, label):
        self.name = label
        self.label = label

    def getLabel(self):
        return self.label

    def setLabel(self, label):
        self.label = label

    # times
    def setConstructionStartTime(self):  # in terms of tick
        self.constructionStartTime = - (self.technology.expected_leadtime +
                                        self.technology.expected_permittime +
                                        self.age)

    def getConstructionStartTime(self):
        return self.constructionStartTime

    def setActualLeadtime(self, actualLeadtime):
        self.actualLeadtime = actualLeadtime

    def getActualLeadtime(self):
        return self.actualLeadtime

    def setExpectedEndOfLife(self, expectedEndOfLife):
        self.expectedEndOfLife = expectedEndOfLife

    def setActualPermittime(self, actualPermittime):
        self.actualPermittime = actualPermittime

    def getActualPermittime(self):
        return self.actualPermittime

    def getDismantleTime(self):
        return self.dismantleTime

    def setDismantleTime(self, dismantleTime):
        self.dismantleTime = dismantleTime

    def getActualEfficiency(self):
        return self.actualEfficiency

    def setActualEfficiency(self, actualEfficiency):
        self.actualEfficiency = actualEfficiency

    def getActualInvestedCapital(self):
        return self.actualInvestedCapital

    def setActualInvestedCapital(self, actualInvestedCapital):
        self.actualInvestedCapital = actualInvestedCapital

    def dismantlePowerPlant(self, time):
        self.setDismantleTime(time)

    def getExpectedEndOfLife(self):
        return self.expectedEndOfLife

    def setActualNominalCapacity(self, actualNominalCapacity):
        # self.setActualNominalCapacity(self.getCapacity() * location.getCapacityMultiplicationFactor())
        if actualNominalCapacity < 0:
            raise ValueError("ERROR: " + self.name + " power plant is being set with a negative capacity!")
        self.actualNominalCapacity = actualNominalCapacity

    def getActualFixedOperatingCost(self):
        return self.actualFixedOperatingCost

    def setActualFixedOperatingCost(self, actualFixedOperatingCost):
        self.actualFixedOperatingCost = actualFixedOperatingCost

    def getAwardedPowerinMWh(self):
        return self.AwardedPowerinMWh

    def getCostsinEUR(self):
        return self.CostsinEUR

    def getOfferedPowerinMWH(self):
        return self.OfferedPowerinMWH

    def getReceivedMoneyinEUR(self):
        return self.ReceivedMoneyinEUR

    def getProfit(self):
        return self.Profit

    def getFuelMix(self):
        return self.fuelMix

    def setFuelMix(self, fuelMix):
        self.fuelMix = fuelMix

    def updateFuelMix(self, fuelMix):
        self.setFuelMix(fuelMix)

    # loans

    def getLoan(self):
        return self.loan

    def setLoan(self, loan):
        self.loan = loan

    def getDownpayment(self):
        return self.downpayment

    def setDownpayment(self, downpayment):
        self.downpayment = downpayment

    def createOrUpdateLoan(self, loan):
        self.setLoan(loan)

    def createOrUpdateDownPayment(self, downpayment):
        self.setDownpayment(downpayment)

    def isHistoricalCvarDummyPlant(self):
        return self.historicalCvarDummyPlant

    # getter and setters
    def setHistoricalCvarDummyPlant(self, historicalCvarDummyPlant):
        self.historicalCvarDummyPlant = historicalCvarDummyPlant


class Decommissioned(ImportObject):
    def __init__(self, name):
        super().__init__(name)

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if parameter_value == None:
            self.Decommissioned = []
        else:
            setattr(self, parameter_name, parameter_value)
