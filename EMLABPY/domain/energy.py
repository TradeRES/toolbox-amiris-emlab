"""
This file contains all classes directly related to energy. PowerPlants, fuels, technologies, etc.
Ingrid Sanchez added lans
Jim Hommes - 13-5-2021
"""
from domain.actors import EnergyProducer
from domain.import_object import *
import logging
import random

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
        # this.setActualEfficiency(this.getTechnology().getEfficiency(
        #                 timeOfPermitorBuildingStart + getActualLeadtime() + getActualPermittime()));

        self.banked_allowances = [0 for i in range(100)]
        self.status = 'NOTSET'
        self.loan = None
        self.downpayment = None
        self.dismantleTime = 0
        self.constructionStartTime = 0
        self.actualLeadtime = 0
        self.actualPermittime = 0
        self.actualLifetime = 0
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

    def isExpectedToBeOperational(self, time):
        finishedConstruction = self.getConstructionStartTime() + self.calculateActualPermittime() + self.calculateActualLeadtime()
        if finishedConstruction <= time:
            # finished construction
            if self.getExpectedEndOfLife() > time:
                # Powerplant is not expected to be dismantled
                return True
        # Construction not yet finished.
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
        setActualInvestedCapital(self.technology.getInvestmentCost(timeOfPermitorBuildingStart + \
                                                                        self.actualPermittime + \
                                                                        self.actualLeadtime ) * self.actualNominalCapacity)



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

# def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
#     if parameter_name == 'TECHTYPENL':
#         self.techtypestr = parameter_value
#         if self.fuelstr != '':
#             self.technology = reps.get_power_generating_technology_by_techtype_and_fuel(self.techtypestr,
#                                                                                         self.fuelstr)
#             # self.constructionStartTime = - (self.technology.expected_leadtime +
#             #                                   self.technology.expected_permittime +
#             #                                   round(random.random() * self.technology.expected_lifetime)) + 2
#     elif parameter_name == 'FUELNL':
#         self.fuelstr = parameter_value
#         if self.techtypestr != '':
#             self.technology = reps.get_power_generating_technology_by_techtype_and_fuel(self.techtypestr,
#                                                                                         self.fuelstr)
#             # self.constructionStartTime = - (self.technology.expected_leadtime +
#             #                                   self.technology.expected_permittime +
#             #                                   round(random.random() * self.technology.expected_lifetime)) + 2
#     elif parameter_name == 'BUSNL':
#         self.location = reps.power_grid_nodes[parameter_value]
#     elif parameter_name == 'FirmNL':
#         try:
#             self.owner = reps.energy_producers[parameter_value]
#         except KeyError:
#             logging.warning('PowerPlant: EnergyProducer not found: ' + parameter_value)
#             reps.energy_producers[parameter_value] = EnergyProducer(parameter_value)
#             self.owner = reps.energy_producers[parameter_value]
#     elif parameter_name == 'MWNL':
#         self.capacity = int(parameter_value)
#     elif parameter_name == 'EfficiencyNL':
#         self.efficiency = float(parameter_value)
#     elif parameter_name == 'Allowances':    # TODO
#         self.banked_allowances[int(alternative)] = int(parameter_value)
#     elif parameter_name == 'STATUSNL':
#         self.status = parameter_value
#     elif parameter_name == 'ON-STREAMNL':
#         self.age = reps.current_tick - int(parameter_value) + reps.start_simulation_year

class PowerGeneratingTechnology(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.capacity = 0
        self.investment_cost_time_series = None
        self.fixed_operating_cost_time_series = None
        self.efficiency_time_series = None
        self.applicable_for_long_term_contract = False
        self.co2_capture_efficiency = 0
        self.depreciation_time = 0
        self.minimum_running_hours = 0
        self.fixed_operating_cost_modifier_after_lifetime = 0
        self.expected_lifetime = 0
        self.expected_leadtime = 0
        self.expected_permittime = 0
        self.minimum_fuel_quality = 0
        self.maximum_installed_capacity_fraction_in_country = 0
        self.maximum_installed_capacity_fraction_per_agent = 0
        self.base_segment_dependent_availability = 0
        self.peak_segment_dependent_availability = 0
        self.applicableForLongTermContract = False
        self.intermittent = False
        self.fuel = ''
        self.techtype = ''

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        # elif parameter_name == 'capacity': # TODO
        #     self.capacity = int(parameter_value)
        # elif parameter_name == 'intermittent':
        #     self.intermittent = 'TRUE' == parameter_value
        # elif parameter_name == 'applicableForLongTermContract':
        #     self.applicable_for_long_term_contract = bool(parameter_value)
        elif parameter_name == 'peakSegmentDependentAvailability':
            self.peak_segment_dependent_availability = float(parameter_value)
        # elif parameter_name == 'baseSegmentDependentAvailability':
        #     self.base_segment_dependent_availability = float(parameter_value)
        # elif parameter_name == 'maximumInstalledCapacityFractionPerAgent':
        #     self.maximum_installed_capacity_fraction_per_agent = float(parameter_value)
        # elif parameter_name == 'maximumInstalledCapacityFractionInCountry':
        #     self.maximum_installed_capacity_fraction_in_country = float(parameter_value)
        # elif parameter_name == 'minimumFuelQuality':
        #     self.minimum_fuel_quality = float(parameter_value)
        elif parameter_name == 'expectedPermittime':
            self.expected_permittime = int(parameter_value)
        elif parameter_name == 'expectedLeadtime':
            self.expected_leadtime = int(parameter_value)
        elif parameter_name == 'LifeTime(Years)':
            self.expected_lifetime = int(parameter_value)
        # elif parameter_name == 'fixedOperatingCostModifierAfterLifetime':
        #     self.fixed_operating_cost_modifier_after_lifetime = float(parameter_value)
        # elif parameter_name == 'minimumRunningHours':
        #     self.minimum_running_hours = int(parameter_value)
        # elif parameter_name == 'depreciationTime':
        #     self.depreciation_time = int(parameter_value)
        # elif parameter_name == 'efficiencyTimeSeries':
        #     self.efficiency_time_series = reps.trends[parameter_value]
        elif parameter_name == 'fixedOperatingCostTimeSeries':
            self.fixed_operating_cost_time_series = reps.trends[parameter_value]
        # elif parameter_name == 'investmentCostTimeSeries':
        #     self.investment_cost_time_series = reps.trends[parameter_value]
        elif parameter_name == 'co2CaptureEfficiency':
            self.co2_capture_efficiency = float(parameter_value)

    def get_fixed_operating_cost(self, time):
        return self.fixed_operating_cost_time_series.get_value(time)


class Substance(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.co2_density = 0
        self.energy_density = 1
        self.quality = 0
        self.trend = None

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'co2Density':
            self.co2_density = float(parameter_value)
        elif parameter_name == 'energyDensity':
            self.energy_density = float(parameter_value)
        elif parameter_name == 'quality':
            self.quality = float(parameter_value)
        elif parameter_name == 'trend':
            self.trend = reps.trends[parameter_value]

    def get_price_for_tick(self, tick):
        return self.trend.get_value(tick)


class SubstanceInFuelMix(ImportObject):
    def __init__(self, name: str):
        super().__init__(name)
        self.substance = None
        self.substances = list()
        self.share = 1

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if parameter_name == 'FUELNEW':
            self.substances.append(reps.substances[parameter_value])


class PowerPlantDispatchPlan(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.plant = None
        self.bidder = None
        self.bidding_market = None
        self.amount = None
        self.price = None
        self.status = 'Awaiting confirmation'
        self.accepted_amount = 0
        self.tick = -1

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        self.tick = int(alternative)
        if parameter_name == 'Plant':
            self.plant = reps.power_plants[parameter_value]
        elif parameter_name == 'EnergyProducer':
            try:
                self.bidder = reps.energy_producers[parameter_value]
            except KeyError:
                logging.warning('New Energy Producer created for: ' + self.name + ', ' + str(parameter_name))
                reps.energy_producers[parameter_value] = EnergyProducer(parameter_value)
                self.bidder = reps.energy_producers[parameter_value]
        if parameter_name == 'Market':
            self.bidding_market = reps.capacity_markets[parameter_value] if \
                parameter_value in reps.capacity_markets.keys() \
                else reps.electricity_spot_markets[parameter_value]
        if parameter_name == 'Capacity':
            self.amount = parameter_value
        if parameter_name == 'AcceptedAmount':
            self.accepted_amount = float(parameter_value)
        if parameter_name == 'Price':
            self.price = float(parameter_value)
        if parameter_name == 'Status':
            self.status = parameter_value


class YearlyEmissions(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.emissions = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if int(alternative) not in self.emissions.keys():
            self.emissions[int(alternative)] = dict()
        self.emissions[int(alternative)][parameter_name] = parameter_value


