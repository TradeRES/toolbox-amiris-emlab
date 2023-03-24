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

        self.efficiency_modifier_after_lifetime = 0
        self.expected_lifetime = 0
        self.expected_leadtime = 0
        self.expected_permittime = 0
        self.yearlyPotential = pd.Series(dtype='float64')
        self.totalPotential = None # in MW
        self.intermittent = False # in MW
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
        elif parameter_name == 'MaximumLifeExtension':
            self.maximumLifeExtension = int(parameter_value)
        elif parameter_name == 'EfficiencyModifierAfterLifetime':
            self.efficiency_modifier_after_lifetime = float(parameter_value)
        elif parameter_name == 'PeakSegmentDependentAvailability':
            self.peak_segment_dependent_availability = float(parameter_value)
        elif parameter_name == 'ApplicableForLongTermContract':
            self.applicable_for_long_term_contract = bool(parameter_value)
        elif parameter_name == 'type':
            self.type = parameter_value
        # From here are the inputs from emlab electricity = traderes
        elif parameter_name == 'lifetime_technical':
            self.expected_lifetime = int(parameter_value)
        elif parameter_name == 'lifetime_economic':
            self.depreciation_time = int(parameter_value) # depreciation time is used to calculate the loans
        elif parameter_name == 'interest_rate':
            self.interest_rate = float(parameter_value)
        elif parameter_name == 'fom_cost':
            self.fixed_operating_costs = float(parameter_value)
            self.fixed_operating_cost_time_series = reps.trends[self.name + "FixedOperatingCostTimeSeries"] # geometric Trends
            self.fixed_operating_cost_time_series.start = self.fixed_operating_costs
        elif parameter_name == 'vom_cost':
            self.variable_operating_costs = float(parameter_value)
        elif parameter_name == 'investment_cost':  # these are already transmofred eur/kw Traderes *1000 -> eur /MW emlab
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            self.investment_cost_eur_MW = pd.Series(values, index=index)
            self.investment_cost_eur_MW.sort_index(ascending=True, inplace=True)
            self.investment_cost_time_series = reps.trends[self.name + "InvestmentCostTimeSeries"] # geometric Trends
            self.investment_cost_time_series.start = self.investment_cost_eur_MW.iloc[0]
        elif parameter_name == 'EnergyToPowerRatio':
            self.energyToPowerRatio = float(parameter_value)
        elif parameter_name == 'co2CaptureEfficiency':
            self.co2_capture_efficiency = float(parameter_value)
        elif parameter_name == 'traderesfuels':
            self.fuel = reps.substances[parameter_value]
        elif parameter_name == 'totalPotential' and alternative == reps.country:
            self.totalPotential = float(parameter_value)
        elif parameter_name == 'yearlyPotential' and alternative == reps.country:
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            self.yearlyPotential = pd.Series(values, index=index)
        elif parameter_name == 'efficiency_full_load':
            self.efficiency = float(parameter_value)
        elif parameter_name == 'EnergyToPowerRatio':
            self.energyToPowerRatio = float(parameter_value)
        elif parameter_name == 'SelfDischargeRatePerHour':
            self.selfDischargeRatePerHour = float(parameter_value)
        elif parameter_name == 'ChargingEfficiency':
            self.chargingEfficiency = float(parameter_value)
        elif parameter_name == 'DischargingEfficiency':
            self.dischargingEfficiency = float(parameter_value)

    def getMaximumCapacityinCountry(self, futureInvestmentyear):
        if self.totalPotential != None:
            return self.totalPotential
        elif self.yearlyPotential.size > 0:
            if futureInvestmentyear in self.yearlyPotential.index.values:  # value is present
                return self.yearlyPotential[futureInvestmentyear]
            else: # interpolate years
                self.yearlyPotential.at[futureInvestmentyear] = np.nan
                self.yearlyPotential.sort_index(ascending=True, inplace=True)
                self.yearlyPotential.interpolate(method='linear',  inplace=True)
                return self.yearlyPotential[futureInvestmentyear]
        else: #self.totalPotential == None and self.yearlyPotential.size == 0:
            return 100000000000 # if there is no declared limit, use a very high number


    def get_investment_costs_perMW_by_year(self, year):
        if year in self.investment_cost_eur_MW.index.values:  # value is present
            return self.investment_cost_eur_MW[year]
        elif self.investment_cost_eur_MW.index.min() > year: # take first year
            self.investment_cost_eur_MW.sort_index(ascending=True, inplace=True)
            return self.investment_cost_eur_MW.iloc[0]
        else: # interpolate years
            self.investment_cost_eur_MW.at[year] = np.nan
            self.investment_cost_eur_MW.sort_index(ascending=True, inplace=True)
            self.investment_cost_eur_MW.interpolate(method='linear',  inplace=True)
            return self.investment_cost_eur_MW[year]


    def getInvestmentCostbyTimeSeries(self, time):
        return self.investment_cost_time_series.get_value(time)

    def get_fixed_operating_cost_trend(self, commissionedTick):
        return self.fixed_operating_cost_time_series.get_value(commissionedTick) # geometric trend

    # --------------------------------------------------------------------------------------------------------

    def getDepreciationTime(self):
        return self.depreciation_time


    def getEfficiency(self, time):
        return self.efficiency_time_series.get_value(time)

    def getCo2CaptureEffciency(self):
        return self.co2CaptureEffciency

    # def getFixedOperatingCostModifierAfterLifetime(self):
    #     return self.fixed_operating_cost_modifier_after_lifetime

    def getExpectedLifetime(self):
        return self.expected_lifetime

    def getExpectedLeadtime(self):
        return self.expected_leadtime

    def getExpectedPermittime(self):
        return self.expected_permittime




