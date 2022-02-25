"""
This file contains all classes directly related to energy.
PowerPlant

PowerGeneratingTechnology
Substance
SubstanceInFuelMix
YearlyEmissions
Ingrid Sanchez added lans
Jim Hommes - 13-5-2021
"""
from emlabpy.domain.energyproducer import EnergyProducer
from emlabpy.domain.import_object import *
import logging
import random

class PowerGeneratingTechnology(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.capacity = 0
        self.annuity = 0

        self.variable_operating_costs = None
        self.investment_cost = None
        self.fixed_operating_costs = None
        self.depreciation_time = 0
        self.minimum_running_hours = 0
        self.fixed_operating_cost_modifier_after_lifetime = 0
        self.expected_lifetime = 0
        self.expected_leadtime = 0
        self.expected_permittime = 0
        self.maximum_installed_capacity_fraction_in_country = 0
        self.intermittent = False
        self.fuel = ''
        # here are missing info
        self.efficiency_time_series = None
        self.applicable_for_long_term_contract = False
        self.co2_capture_efficiency = 0
        self.techtype = ''
        self.investment_cost_time_series = None
        self.fixed_operating_cost_time_series = None
        self.minimum_fuel_quality = 0
        self.maximum_installed_capacity_fraction_per_agent = 0
        self.base_segment_dependent_availability = 0
        self.peak_segment_dependent_availability = 0
        self.applicableForLongTermContract = False

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        # according to the scenario.yaml, if is has energy carrier then it is intermittent

        if parameter_name == 'intermittent':
            self.intermittent = parameter_value
        #From here are the inputs from emlab unit
        elif parameter_name == 'annuity':
            self.annuity = float(parameter_value)
        elif parameter_name == 'lifetime_technical':
            self.expected_lifetime = int(parameter_value)
        elif parameter_name == 'lifetime_economic':
            self.depreciation_time = int(parameter_value)
        elif parameter_name == 'investment_limit':
            self.maximum_installed_capacity_fraction_in_country = int(parameter_value)
        elif parameter_name == 'interest_rate':
            self.interest_rate = int(parameter_value)
        #From here are the inputs from emlab electricity = traderes
        elif parameter_name == 'fom_cost':
            self.fixed_operating_costs = float(parameter_value)
        elif parameter_name == 'vom_cost':
            self.variable_operating_costs = float(parameter_value)
        elif parameter_name == 'investment_cost': # these are in eur/kw -> *1000 eur /MW
            self.investment_cost = float(parameter_value)
#From here are the inputs from emlab TechnologyEmlab
        elif parameter_name == 'expectedPermittime':
            self.expected_permittime = int(parameter_value)
        elif parameter_name == 'expectedLeadtime':
            self.expected_leadtime = int(parameter_value)


        # elif parameter_name == 'maximumInstalledCapacityFractionPerAgent':
        #     self.maximum_installed_capacity_fraction_per_agent = float(parameter_value)
        # elif parameter_name == 'minimumFuelQuality':
        #     self.minimum_fuel_quality = float(parameter_value)

        # elif parameter_name == 'minimumRunningHours':
        #     self.minimum_running_hours = int(parameter_value)
        # elif parameter_name == 'efficiencyTimeSeries':
        #     self.efficiency_time_series = reps.trends[parameter_value]
        # FOR THE FIXED OPERATING COSTS TIME SERIES IT COULD BE ENOUGH TO PUT AS A START THE INITIAL VALUES AND THEN GROWTH TREND 0.05
        # elif parameter_name == 'fixedOperatingCostTimeSeries':
        #     self.fixed_operating_cost_time_series = reps.trends[parameter_value]
        # elif parameter_name == 'fixedOperatingCostModifierAfterLifetime':
        #     self.fixed_operating_cost_modifier_after_lifetime = float(parameter_value)
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


