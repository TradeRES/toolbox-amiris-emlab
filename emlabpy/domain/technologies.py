"""
This file contains all classes directly related to energy.
PowerGeneratingTechnology
Ingrid Sanchez added lans
Jim Hommes - 13-5-2021
"""
from domain.energyproducer import EnergyProducer
from domain.import_object import *
from domain.trends import *
import logging
import random
import sys


class PowerGeneratingTechnology(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.capacity = 0
        # self.annuity = 0
        self.investment_cost_eur_MW = None
        self.fixed_operating_costs = None
        self.variable_operating_costs = 0.0
        self.efficiency = 0
        self.depreciation_time = 0
        self.minimum_running_hours = 0
        self.fixed_operating_cost_modifier_after_lifetime = 0
        self.expected_lifetime = 0
        self.expected_leadtime = 0
        self.expected_permittime = 0
        self.maximum_installed_capacity_in_country = sys.float_info.max
        self.intermittent = False
        self.fuel = ''
        self.type = ''

        # here are missing info
        self.energyToPowerRatio = 0
        self.chargingEfficiency = 0
        self.dischargingEfficiency = 0

        self.selfDischargeRatePerHour = 0
        self.co2_capture_efficiency = 0
        self.techtype = ''
        self.efficiency_time_series = None
        self.investment_cost_time_series = None
        self.fixed_operating_cost_time_series = None
        self.minimum_fuel_quality = 0
        self.maximum_installed_capacity_fraction_per_agent = 0
        self.base_segment_dependent_availability = 0
        self.peak_segment_dependent_availability = 0
        self.applicable_for_long_term_contract = False

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'Intermittent':
            self.intermittent = bool(parameter_value)
        elif parameter_name == 'expectedPermittime':
            self.expected_permittime = int(parameter_value)
        elif parameter_name == 'expectedLeadtime':
            self.expected_leadtime = int(parameter_value)
        elif parameter_name == 'FixedOperatingCostModifierAfterLifetime':
            self.fixed_operating_cost_modifier_after_lifetime = float(parameter_value)
        elif parameter_name == 'PeakSegmentDependentAvailability':
            self.peak_segment_dependent_availability = float(parameter_value)
        elif parameter_name == 'ApplicableForLongTermContract':
            self.applicable_for_long_term_contract = bool(parameter_value)
        elif parameter_name == 'type':
            self.type = parameter_value
        # From here are the inputs from emlab electricity = traderes
        # elif parameter_name == 'annuity':
        #     self.annuity = float(parameter_value)
        elif parameter_name == 'lifetime_technical':
            self.expected_lifetime = int(parameter_value)
        elif parameter_name == 'lifetime_economic':
            self.depreciation_time = int(parameter_value)
        elif parameter_name == reps.country:  # TODO: Implement Investment limit per node
            self.maximum_installed_capacity_in_country = parameter_value * 1000  # capacities from GW to MW (emlab)
        elif parameter_name == 'interest_rate':
            self.interest_rate = float(parameter_value)
        elif parameter_name == 'fom_cost':
            self.fixed_operating_costs = float(parameter_value)
            # self.fixed_operating_cost_time_series = GeometricTrend("geometrictrend" + self.name)
            # self.fixed_operating_cost_time_series.growth_rate = 0.0
            self.fixed_operating_cost_time_series = reps.trends[self.name + "FixedOperatingCostTimeSeries"]
            self.fixed_operating_cost_time_series.start = self.fixed_operating_costs
        elif parameter_name == 'vom_cost':
            self.variable_operating_costs = float(parameter_value)
        elif parameter_name == 'investment_cost':  # these are already transmofred eur/kw Traderes *1000 -> eur /MW emlab
            self.investment_cost_eur_MW = float(parameter_value)
            self.initializeInvestmenttrend()
        elif parameter_name == 'EnergyToPowerRatio':
            self.energyToPowerRatio = float(parameter_value)
        elif parameter_name == 'co2CaptureEfficiency':
            self.co2_capture_efficiency = float(parameter_value)
        elif parameter_name == 'traderesfuels':
            self.fuel = reps.substances[parameter_value]
        elif parameter_name == 'efficiency_full_load':
            self.efficiency = float(parameter_value)
            self.initializeEfficiencytrend()
        elif parameter_name == 'EnergyToPowerRatio':
            self.energyToPowerRatio = float(parameter_value)
        elif parameter_name == 'SelfDischargeRatePerHour':
            self.selfDischargeRatePerHour = float(parameter_value)
        elif parameter_name == 'ChargingEfficiency':
            self.chargingEfficiency = float(parameter_value)
        elif parameter_name == 'DischargingEfficiency':
            self.dischargingEfficiency = float(parameter_value)

    def initializeEfficiencytrend(self):
        self.efficiency_time_series = GeometricTrend("geometrictrend" + self.name)
        self.efficiency_time_series.start = self.efficiency
        self.efficiency_time_series.growth_rate = 0.00

    def initializeInvestmenttrend(self):
        self.investment_cost_time_series = GeometricTrend("geometrictrend" + self.name)
        self.investment_cost_time_series.start = self.investment_cost_eur_MW
        self.investment_cost_time_series.growth_rate = 0.00


    def get_fixed_operating_cost_trend(self, time):
        return self.fixed_operating_cost_time_series.get_value(time)

    def get_fixed_operating_cost(self, time):
        return self.fixed_operating_cost_time_series.get_value(time)

    # --------------------------------------------------------------------------------------------------------------------------------------------------------

    def getDepreciationTime(self):
        return self.depreciation_time

    def setDepreciationTime(self, depreciation_time):
        self.depreciation_time = depreciation_time

    #     * assumption: the first is the main fuel
    def getMainFuel(self):
        if self.getFuels().size() > 0:
            return self.getFuels().iterator().next()
        else:
            return None

    def getCapacity(self):
        return self.capacity

    def getEfficiency(self, time):
        return self.efficiency_time_series.get_value(time)

    def getCo2CaptureEffciency(self):
        return self.co2CaptureEffciency

    def getFixedOperatingCostModifierAfterLifetime(self):
        return self.fixed_operating_cost_modifier_after_lifetime

    def getExpectedLifetime(self):
        return self.expected_lifetime

    def getExpectedLeadtime(self):
        return self.expected_leadtime

    def getExpectedPermittime(self):
        return self.expected_permittime

    def getFuels(self):
        return self.fuels

    def getInvestmentCost(self, time):
        #   print(help(self.investment_cost_time_series))
        return self.investment_cost_time_series.get_value(time)

    def getMaximumCapacityinCountry(self):
        return self.maximum_installed_capacity_in_country

