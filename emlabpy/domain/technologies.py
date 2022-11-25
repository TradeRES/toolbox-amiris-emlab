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
import pandas as pd
import sys


class PowerGeneratingTechnology(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.capacity = 0
        # self.annuity = 0
        self.investment_cost_eur_MW = pd.Series(dtype='float64')
        self.fixed_operating_costs = None
        self.variable_operating_costs = 0.0
        self.efficiency = 0
        self.depreciation_time = 0
        self.minimum_running_hours = 0
        self.fixed_operating_cost_modifier_after_lifetime = 0
        self.expected_lifetime = 0
        self.expected_leadtime = 0
        self.expected_permittime = 0
        self.maximum_installed_capacity_in_country = pd.Series(dtype='float64')
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
            pass
        elif parameter_name == 'lifetime_economic':
            self.depreciation_time = int(parameter_value)
            self.expected_lifetime = int(parameter_value)
        elif parameter_name == 'interest_rate':
            self.interest_rate = float(parameter_value)
        elif parameter_name == 'fom_cost':
            self.fixed_operating_costs = float(parameter_value)
            self.fixed_operating_cost_time_series = reps.trends[self.name + "FixedOperatingCostTimeSeries"]
            self.fixed_operating_cost_time_series.start = self.fixed_operating_costs
        elif parameter_name == 'vom_cost':
            self.variable_operating_costs = float(parameter_value)
        elif parameter_name == 'investment_cost':  # these are already transmofred eur/kw Traderes *1000 -> eur /MW emlab
           # self.investment_cost_eur_MW = float(parameter_value)
            self.investment_cost_eur_MW.at[int(alternative)] = parameter_value
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

    def add_potentials(self, reps, db_line):
        object_name = db_line[1]
        parameter_name = db_line[2]
        parameter_value = db_line[3]
        if object_name not in reps.power_generating_technologies.keys():
            reps.power_generating_technologies[object_name] = self(object_name)
        if parameter_name[0:2] == reps.country:
            year = parameter_name[2:6]
            if isinstance(year, str): # if there is no yearly value, add it at year 0
                reps.power_generating_technologies[object_name].maximum_installed_capacity_in_country.at[0] = parameter_value * 1000
            else:
                reps.power_generating_technologies[object_name].maximum_installed_capacity_in_country.at[int(year)] = parameter_value * 1000 # capacities from GW to MW (emlab)

    def getMaximumCapacityinCountry(self, futureInvestmentyear):
        if self.maximum_installed_capacity_in_country.size==0:
            return np.nan
        elif futureInvestmentyear in self.maximum_installed_capacity_in_country.index.values:  # value is present
            return self.maximum_installed_capacity_in_country[futureInvestmentyear]
        elif 0 in self.maximum_installed_capacity_in_country.index.values: # unique value for all years
            return self.maximum_installed_capacity_in_country[0]
        else: # interpolate years
            self.maximum_installed_capacity_in_country.at[futureInvestmentyear] = np.nan
            self.maximum_installed_capacity_in_country.sort_index(ascending=True, inplace=True)
            self.maximum_installed_capacity_in_country.interpolate(method='linear',  inplace=True)
            print(self.name + "MAX capacity " + self.maximum_installed_capacity_in_country[futureInvestmentyear])
            return self.maximum_installed_capacity_in_country[futureInvestmentyear]

    def initializeEfficiencytrend(self):
        self.efficiency_time_series = GeometricTrend("geometrictrend" + self.name)
        self.efficiency_time_series.start = self.efficiency
        self.efficiency_time_series.growth_rate = 0.00

    def get_investment_costs_by_year(self, year):
        if year in self.investment_cost_eur_MW.index.values:  # value is present
            return self.investment_cost_eur_MW[year]
        else: # interpolate years
            self.investment_cost_eur_MW.at[year] = np.nan
            self.investment_cost_eur_MW.sort_index(ascending=True, inplace=True)
            self.investment_cost_eur_MW.interpolate(method='linear',  inplace=True)
            return self.investment_cost_eur_MW[year]

    def initializeInvestmenttrend(self):
        self.investment_cost_time_series = GeometricTrend("geometrictrend" + self.name)
        if 2020 in self.investment_cost_eur_MW.index.values: # Attention! there should be for all
            self.investment_cost_time_series.start = self.investment_cost_eur_MW[2020]
        else:
            print("missing investemnt cost for " + self.name )
        self.investment_cost_time_series.growth_rate = 0.00 # todo, this can be changed to actual data and interpolation

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


