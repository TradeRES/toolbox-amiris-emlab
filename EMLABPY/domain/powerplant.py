"""
This file contains all classes directly related to
PowerPlant
"""
from emlabpy.domain.energyproducer import EnergyProducer
from emlabpy.domain.import_object import *
from random import random
import logging

class PowerPlant(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.technology = None
        self.location = None
        self.age = 0
        self.owner = None
        self.capacity = 0
        self.efficiency = 0
        # TODO: Implement GetActualEfficiency
        self.banked_allowances = [0 for i in range(100)]
        self.status = 'NOTSET'
        self.loan = None
        self.downpayment = None
        self.dismantleTime = 0
        self.constructionStartTime = 0
        self.actualLeadtime = 0
        self.actualPermittime = 0
        self.actualLifetime = 0
        self.commissionedYear = 0
        self.name = ""
        self.label = ""
        self.actualInvestedCapital = 0
        self.actualFixedOperatingCost = 0
        self.actualEfficiency = 0
        self.expectedEndOfLife = 0
        self.actualNominalCapacity = 0
        self.historicalCvarDummyPlant = 0
        self.electricityOutput = 0
        self.flagOutputChanged = True

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'Id':
            self.name = parameter_value
        if parameter_name == 'Technology':
            self.technology = reps.power_generating_technologies[parameter_value]
        elif parameter_name == 'InstalledPowerInMW':
            self.capacity = parameter_value
        elif parameter_name == 'Owner':
            self.owner = parameter_value
        elif parameter_name == 'ComissionedYear':
            self.age = reps.current_tick + reps.start_simulation_year - int(parameter_value)
            self.commissionedYear = int(parameter_value)
        elif parameter_name == 'Maximal':
            self.efficiency = float(parameter_value)

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

    def isExpectedToBeOperational(self, futuretick):
        if self.commissionedYear <= futuretick:
            if self.getExpectedEndOfLife() > futuretick:
                # Powerplant is not expected to be dismantled
                return True
        else:
            return False

    def isInPipeline(self, currentTick):
        finishedConstruction = self.constructionStartTime() + self.actualPermittime() + self.actualLeadtime()
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

    def getAvailableCapacity(self, currentTick, segment, numberOfSegments):
        if isOperational(currentTick):
            if self.getTechnology().isIntermittent():
                intermittentTechnologyNodeLoadFactor = getIntermittentTechnologyNodeLoadFactor()
                factor = intermittentTechnologyNodeLoadFactor.getLoadFactorForSegment(segment)
                return getActualNominalCapacity() * factor
            else:
                factor = 1
                if segment is not None:
                    # capacity
                    segmentID = segment.getSegmentID()
                    if int(segmentID) > 1:

                        min = getTechnology().getPeakSegmentDependentAvailability()
                        max = getTechnology().getBaseSegmentDependentAvailability()
                        segmentPortion = (numberOfSegments - segmentID) / (numberOfSegments - 1)
                        Logger.getGlobal().finer("Segment portion for segment " + segmentID + " is "+ segmentPortion)
                        range = max - min
                        factor = max - segmentPortion * range
                    else:
                        factor = getTechnology().getPeakSegmentDependentAvailability()
                cap = getActualNominalCapacity() * factor
                if factor < 1:
                    Logger.getGlobal().finer("Capacity factor for " + getTechnology() + " is " + cap + " for segment " + segment + " because load factor is " + factor)
                return cap
        else:
            return 0

    # def getExpectedAvailableCapacity(self, futureTick, segment, numberOfSegments):
    #     if isExpectedToBeOperational(futureTick):
    #         if self.getTechnology().isIntermittent():
    #             factor = getIntermittentTechnologyNodeLoadFactor().getLoadFactorForSegment(segment)
    #             return getActualNominalCapacity() * factor
    #         else:
    #             factor = 1
    #             if segment is not None:
    #                 # capacity
    #                 segmentID = segment.getSegmentID()
    #                 min = getTechnology().getPeakSegmentDependentAvailability()
    #                 max = getTechnology().getBaseSegmentDependentAvailability()
    #                 segmentPortion = (numberOfSegments - segmentID) / (numberOfSegments - 1) # start
    #                 # counting
    #                 # at
    #                 # 1.
    #
    #                 range = max - min
    #
    #                 factor = max - segmentPortion * range
    #             return getActualNominalCapacity() * factor
    #     else:
    #         return 0

    def getAvailableCapacity(self, currentTick):
        if isOperational(currentTick):
            return getActualNominalCapacity()
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
        self.setActualInvestedCapital(self.technology.getInvestmentCost(timeOfPermitorBuildingStart + \
                                                                   self.actualPermittime + \
                                                                   self.actualLeadtime ) * self.actualNominalCapacity)
# the growth trend
    def calculateAndSetActualFixedOperatingCosts(self, timesinceBuildingStart):
        self.setActualFixedOperatingCost(self.getTechnology().get_fixed_operating_cost_trend(timesinceBuildingStart \
                                         + self.getActualLeadtime() + self.getActualPermittime())\
                                         * self.getActualNominalCapacity())

    def calculateAndSetActualEfficiency(self):
        #self.setActualEfficiency(self.getTechnology().getEfficiency(timeOfPermitorBuildingStart + getActualLeadtime() + getActualPermittime()))
        self.efficiency

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

    #TODO expensive method!!
    def calculateElectricityOutputAtTime(self, time, forecast):

        if (not forecast) and not flagOutputChanged:
            return electricityOutput
        else:
            electricityOutput = reps.calculateElecitricityOutputForPlantForTime(self, time, forecast)
            return electricityOutput
        # TODO This is in MWh (so hours of segment included!!)
        #         double amount = 0d

        #        Logger.getGlobal().warning("Finding electricity output for " + this + "  reps " + reps)

        #        return reps.findAllPowerPlantDispatchPlansForPowerPlantForTime(this, time, forecast).stream().mapToDouble(p -> calculateElectricityOutputForPlan(p)).sum()
        #        for (PowerPlantDispatchPlan plan : reps.findAllPowerPlantDispatchPlansForPowerPlantForTime(this, time, forecast)) {
        #//            Logger.getGlobal().warning("plant; " + plan)
        #
        #            amount +=
        #        }
        #        return amount

    def calculateCO2EmissionsAtTime(self, time, forecast):
        return self.calculateEmissionIntensity() * self.calculateElectricityOutputAtTime(time, forecast)

    def dismantlePowerPlant(self, time):
        self.setDismantleTime(time)

    def createOrUpdateLoan(self, loan):
        self.setLoan(loan)

    def createOrUpdateDownPayment(self, downpayment):
        self.setDownpayment(downpayment)

    def updateFuelMix(self, fuelMix):
        self.setFuelMix(fuelMix)

    def getActualNominalCapacity(self):
        return self.actualNominalCapacity

    def setActualNominalCapacity(self, actualNominalCapacity):
        if actualNominalCapacity < 0:
            raise RuntimeException("ERROR: " + self.name + " power plant is being set with a negative capacity!")
        self.actualNominalCapacity = actualNominalCapacity

    def getActualFixedOperatingCost(self):
        return self.actualFixedOperatingCost

    def setActualFixedOperatingCost(self, actualFixedOperatingCost):
        self.actualFixedOperatingCost = actualFixedOperatingCost

    def getIntermittentTechnologyNodeLoadFactor(self):
        return reps.findIntermittentTechnologyNodeLoadFactorForNodeAndTechnology(self.getLocation(), self.getTechnology())

    def isHistoricalCvarDummyPlant(self):
        return self.historicalCvarDummyPlant
#getter and setters
    def setHistoricalCvarDummyPlant(self, historicalCvarDummyPlant):
        self.historicalCvarDummyPlant = historicalCvarDummyPlant

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

    def setConstructionStartTime(self):
        self.constructionStartTime = - (self.technology.expected_leadtime +
                                        self.technology.expected_permittime +
                                        round(random() * self.technology.expected_lifetime)) + 2

    def getCapacity(self):
        return self.capacity

    def getConstructionStartTime(self):
        return self.constructionStartTime

    def setActualLeadtime(self, actualLeadtime):
        self.actualLeadtime = actualLeadtime

    def getActualLeadtime(self):
        return self.actualLeadtime

    def getExpectedEndOfLife(self):
        return self.expectedEndOfLife

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

    def setName(self, label):
        self.name = label
        self.label = label

    def getLabel(self):
        return self.label

    def setLabel(self, label):
        self.label = label

    def getActualInvestedCapital(self):
        return self.actualInvestedCapital

    def setActualInvestedCapital(self, actualInvestedCapital):
        self.actualInvestedCapital = actualInvestedCapital

    def getFuelMix(self):
        return self.fuelMix

    def setFuelMix(self, fuelMix):
        self.fuelMix = fuelMix

    def getLoan(self):
        return self.loan

    def setLoan(self, loan):
        self.loan = loan

    def getDownpayment(self):
        return self.downpayment

    def setDownpayment(self, downpayment):
        self.downpayment = downpayment

    def getActualEfficiency(self):
        self.efficiency
        #return self.actualEfficiency

    def setActualEfficiency(self, actualEfficiency):
        self.actualEfficiency = actualEfficiency

    def dismantlePowerPlant(self, time):
        self.setDismantleTime(time)

    def createOrUpdateLoan(self, loan):
        self.setLoan(loan)

    def createOrUpdateDownPayment(self, downpayment):
        self.setDownpayment(downpayment)

    def getExpectedEndOfLife(self):
        return self.expectedEndOfLife

    def setExpectedEndOfLife(self, expectedEndOfLife):
        self.expectedEndOfLife = expectedEndOfLife

    def updateFuelMix(self, fuelMix):
        self.setFuelMix(fuelMix)

    def getActualNominalCapacity(self):
        return self.actualNominalCapacity

    def setActualNominalCapacity(self, actualNominalCapacity):
        # self.setActualNominalCapacity(self.getCapacity() * location.getCapacityMultiplicationFactor())
        if actualNominalCapacity < 0:
            raise ValueError("ERROR: " + self.name + " power plant is being set with a negative capacity!")
        self.actualNominalCapacity = actualNominalCapacity

    def getActualFixedOperatingCost(self):
        return self.actualFixedOperatingCost

    def setActualFixedOperatingCost(self, actualFixedOperatingCost):
        self.actualFixedOperatingCost = actualFixedOperatingCost

    def getIntermittentTechnologyNodeLoadFactor(self):
        return reps.findIntermittentTechnologyNodeLoadFactorForNodeAndTechnology(self.getLocation(), self.getTechnology())

    '''
     # FROM HERE EQUATIONS ARE OLD   
    
    '''
    def calculate_emission_intensity(self, reps):
        emission = 0
        substance_in_fuel_mix_object = reps.get_substances_in_fuel_mix_by_plant(self)
        for substance_in_fuel_mix in substance_in_fuel_mix_object.substances:
            # CO2 Density is a ton CO2 / MWh
            co2_density = substance_in_fuel_mix.co2_density * (1 - float(
                self.technology.co2_capture_efficiency))

            # Returned value is ton CO2 / MWh
            emission_for_this_fuel = substance_in_fuel_mix_object.share * co2_density / self.efficiency
            emission += emission_for_this_fuel
        return emission

    def get_actual_fixed_operating_cost(self):
        per_mw = self.technology.get_fixed_operating_cost(self.constructionStartTime +
                                                          int(self.technology.expected_leadtime) +
                                                          int(self.technology.expected_permittime))
        capacity = self.get_actual_nominal_capacity()

        return per_mw * capacity

    def get_actual_nominal_capacity(self):
        return self.capacity
        # if self.capacity == 0:
        #     return self.technology.capacity * float(self.location.parameters['CapacityMultiplicationFactor'])
        # else:
        #     return self.capacity

    def calculate_marginal_fuel_cost_per_mw_by_tick(self, reps, time):
        fc = 0
        substance_in_fuel_mix_object = reps.get_substances_in_fuel_mix_by_plant(self)
        for substance_in_fuel_mix in substance_in_fuel_mix_object.substances:
            # Fuel price is Euro / MWh
            fc += substance_in_fuel_mix_object.share * substance_in_fuel_mix.get_price_for_tick(time) / self.efficiency
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

