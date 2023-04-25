"""
This file contains all classes directly related to
PowerPlant
"""
from domain.import_object import *
from random import random
import logging
import pandas as pd
from domain.actors import EMLabAgent
from domain.loans import Loan
from util import globalNames
import numpy as np


class PowerPlant(EMLabAgent):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.id = 0
        self.technology = None
        self.location = ""
        self.owner = None  # change if there are more energyproducers
        self.capacity = 0
        self.expectedTotalProfits = 0
        self.banked_allowances = [0 for i in range(100)]
        self.status = globalNames.power_plant_status_not_set  # 'Operational' , 'InPipeline', 'Decommissioned', 'TobeDecommissioned'
        self.fictional_status = globalNames.power_plant_status_not_set
        self.loan = Loan()
        self.loan_payments_in_year = 0
        self.downpayment_in_year = 0
        self.downpayment = Loan()
        self.decommissionInYear = None
        self.endOfLife = None  # in terms of tick
        # scenario from artificial emlab parameters
        self.constructionStartTick = 0
        self.actualLeadtime = 0
        self.actualPermittime = 0  # todo clear this functionalities
        self.age = 0
        self.commissionedYear = 0
        self.label = ""
        self.actualInvestedCapital = 0
        self.actualFixedOperatingCost = 'NOTSET'
        self.actualVariableCost = 'NOTSET'
        self.actualEfficiency = 'NOTSET'
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
        self.operationalProfit = 0
        self.initialEnergyLevelInMWH = 0
        self.DecommissionInYear = 0
        self.cash = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if reps.runningModule != "plotting" and self.name in (
                # do not import decommissioned power plants to the repository if it is not the plotting step
                reps.decommissioned["Decommissioned"]).Done:
            return
        elif parameter_name == 'Status':
            self.status = str(parameter_value)
        elif parameter_name == 'actualEfficiency':
            self.actualEfficiency = float(parameter_value)
        elif parameter_name == 'actualVariableCost':
            self.actualVariableCost = float(parameter_value)
        elif parameter_name == 'actualFixedOperatingCost':
            self.actualFixedOperatingCost = float(parameter_value)
        elif parameter_name == 'Location':
            self.location = parameter_value
            owner = "Producer" + parameter_value
            self.owner = reps.energy_producers[owner]
        elif parameter_name == 'Id':
            self.id = int(parameter_value)
        if parameter_name == 'Technology':
            self.technology = reps.power_generating_technologies[parameter_value]
        elif parameter_name == 'Capacity':
            self.capacity = parameter_value
        elif parameter_name == 'Age':
            if reps.current_tick == 0 and reps.runningModule == "run_decommission_module":
                # In the first decommission step,the year of the power plants list is added to the age of power plants
                self.age = int(parameter_value) + reps.add_initial_age_years
                self.commissionedYear = reps.current_year - int(parameter_value) - reps.add_initial_age_years
            else:
                self.age = int(parameter_value)  # for emlab data the commissioned year can be read from the age
                self.commissionedYear = reps.current_year - int(parameter_value)

            if self.is_new_installed() and reps.runningModule == "run_initialize_power_plants":
                if self.age > reps.current_tick:
                    raise Exception("age is higher than it should be " + str(self.id) + " Name " + str(self.name))
        elif parameter_name == 'DecommissionInYear':
            self.decommissionInYear = int(parameter_value)
            self.commissionedYear = int(parameter_value) - self.age
            self.age = reps.current_year - self.commissionedYear
            # the plant was added the age and immediately decommissioned.

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
        elif parameter_name == 'label':
            self.label = parameter_value
        elif parameter_name == 'LastEnergyLevels':
            # last energy levels will be next years initial Energy Level
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            all_storages = pd.Series(values, index=index)
            if (reps.current_year - 1) in all_storages.index:
                self.initialEnergyLevelInMWH = all_storages[reps.current_year - 1]
            else:
                self.initialEnergyLevelInMWH = 0
        elif parameter_name == 'expectedTotalProfits' and reps.runningModule == "run_future_market":
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            self.expectedTotalProfits = pd.Series(values, index=index)

    def add_values_from_df(self, results):
        self.AwardedPowerinMWh = results.PRODUCTION_IN_MWH
        self.CostsinEUR = results.VARIABLE_COSTS_IN_EURO
        self.ReceivedMoneyinEUR = results.REVENUES_IN_EURO
        self.operationalProfit = results.CONTRIBUTION_MARGIN_IN_EURO

    def specifyPowerPlantforInvest(self, reps, look_ahead_years):
        """"
        specify power plant invested by NPV or target invest
        """
        self.setCapacity(self.capacityTobeInstalled)
        self.setActualLeadtime(self.technology.getExpectedLeadtime())
        self.setActualPermittime(self.technology.getExpectedPermittime())
        if reps.install_at_look_ahead_year == True:
            self.age = - look_ahead_years
            self.commissionedYear = reps.current_year + look_ahead_years
            self.setEndOfLife(
                reps.current_year + reps.lookAhead + self.getTechnology().getExpectedLifetime())  # for dismantling decision
        else:
            self.age = - self.getExpectedLeadtime() - self.getExpectedPermittime()
            self.commissionedYear = reps.current_year + self.getExpectedLeadtime() + self.getExpectedPermittime()
            self.setEndOfLife(
                reps.current_year + self.getActualPermittime() + self.getActualLeadtime() + self.getTechnology().getExpectedLifetime())

        self.status = globalNames.power_plant_status_inPipeline
        self.setActualFixedOperatingCost(self.getTechnology().get_fixed_costs_by_commissioning_year(
            self.commissionedYear) * self.get_actual_nominal_capacity())
        self.calculateAndSetActualInvestedCapitalbyinterpolate(reps, self.technology, self.commissionedYear)  # INVEST

    def specifyPowerPlantsInstalled(self, reps, run_initialize_power_plants):
        """"
        specify power plant from initial database

        in the initialization, if not specified variable costs and efficiency are set according to age
        Each year, the variable costs are increased, and efficiency decreased in dismantle step

        Fixed operating costs are only changed after lifetime

        """
        self.setActualLeadtime(self.technology.getExpectedLeadtime())
        self.setActualPermittime(self.technology.getExpectedPermittime())
        self.setActualNominalCapacity(self.getCapacity())
        self.setConstructionStartTick()  # minus age, permit and lead time
        self.commissionedYear = reps.current_year - self.age

        if self.actualEfficiency == 'NOTSET':  # if there is not initial efficiency, then assign the efficiency by the technology
            self.calculateAndSetActualEfficiency(self.age)  # initialDB

        if self.actualVariableCost == 'NOTSET':
            self.calculateAndSetActualVariableOperatingCosts(self.age)

        if self.actualFixedOperatingCost == 'NOTSET':  # old power plants have set their fixed costs
            self.setActualFixedOperatingCost(self.getTechnology().get_fixed_costs_by_commissioning_year(
                self.commissionedYear) * self.get_actual_nominal_capacity())  # if plant passed its lifetime then it should have higher costs

        if reps.decommission_from_input == True and self.decommissionInYear is not None:
            self.setEndOfLife(self.decommissionInYear - reps.start_simulation_year)  # set in terms of tick

        # INITIAL investment cost by time series = 2020
        self.calculateAndSetActualInvestedCapital(reps, self.technology, self.age)

        if run_initialize_power_plants == True:  # only run this in the initialization step and while plotting
            self.setPowerPlantsStatusforInstalledPowerPlants()  # the status for each year is set in dismantle module
        return

    def set_loans_installed_pp(self, reps):
        amountPerPayment = reps.determineLoanAnnuities(
            self.getActualInvestedCapital() * self.owner.getDebtRatioOfInvestments(),
            self.getTechnology().getDepreciationTime(), self.owner.getLoanInterestRate())
        done_payments = self.age  # the loan  is paid since it was constructed.
        startpayments = - self.age
        reps.createLoan(self.owner.name, reps.bigBank.name, amountPerPayment,
                        self.getTechnology().getDepreciationTime(),
                        startpayments, done_payments, self)

    def setPowerPlantsStatusforInstalledPowerPlants(self):
        # the strategic reserve status is kept through the list of power plants
        if self.age is not None:
            if self.status == globalNames.power_plant_status_decommissioned:
                pass
            elif self.age >= self.technology.expected_lifetime:
                self.status = globalNames.power_plant_status_to_be_decommissioned
            elif self.age < 0:
                self.status = globalNames.power_plant_status_inPipeline
            else:
                self.status = globalNames.power_plant_status_operational
        else:
            print("power plant dont have an age ", self.name)

    def get_Profit(self):
        if not self.operationalProfit:
            self.operationalProfit = self.ReceivedMoneyinEUR - self.CostsinEUR
        return self.operationalProfit

    def get_actual_nominal_capacity(self):
        return self.capacity

    def is_new_installed(self):
        # power plants that have a name/number higher than 100000 can be considered as newly installed.
        if int(self.name) > 100000:
            return True
        else:
            return False

    def is_invested_by_target_investor(self):
        if len(str(self.id)) == 12:
            return True
        else:
            return False

    def is_not_candidate_power_plant(self):
        if str(self.id)[0: 4] != "9999":
            return True
        else:
            return False

    def calculateAndSetActualInvestedCapital(self, reps, technology, age):
        investment_year = - age + reps.current_year
        if investment_year <= technology.investment_cost_eur_MW.index.min():
            # Finds investment cost by time series if there are no prices available
            self.setActualInvestedCapital(self.technology.getInvestmentCostbyTimeSeries(
                - age) * self.get_actual_nominal_capacity())
        else:  # by year
            self.setActualInvestedCapital(
                technology.get_investment_costs_perMW_by_year(investment_year) * self.get_actual_nominal_capacity())

    def calculateAndSetActualInvestedCapitalbyinterpolate(self, reps, technology, commissionedYear):
        self.setActualInvestedCapital(
            technology.get_investment_costs_perMW_by_year(commissionedYear) * self.get_actual_nominal_capacity())

    def calculateAndSetActualVariableOperatingCosts(self, tick):
        # get fixed costs by GeometricTrend by tick. Active in tick = 0 in initialization
        self.actualVariableCost = (self.getTechnology().get_variable_operating_by_time_series(tick))

    def calculateAndSetActualEfficiency(self, age):  # for initializatio
        self.setActualEfficiency(self.getTechnology().get_efficiency_by_time_series(age))

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

    def getCapacity(self):
        return self.capacity

    def setCapacity(self, capacity):
        self.capacity = capacity

    def setConstructionStartTick(self):  # in terms of tick
        # construction start time doesnt change
        self.constructionStartTick = - (self.technology.expected_leadtime +
                                        self.technology.expected_permittime +
                                        self.age)

    def getConstructionStartTick(self):
        return self.constructionStartTick

    def setActualLeadtime(self, actualLeadtime):
        self.actualLeadtime = actualLeadtime

    def getActualLeadtime(self):
        return self.actualLeadtime

    def setActualPermittime(self, actualPermittime):
        self.actualPermittime = actualPermittime

    def getActualPermittime(self):
        return self.actualPermittime

    def setActualEfficiency(self, actualEfficiency):
        self.actualEfficiency = actualEfficiency

    def setActualVariableCosts(self, actualVariableCost):
        self.actualVariableCost = actualVariableCost

    def getActualInvestedCapital(self):
        return self.actualInvestedCapital

    def setActualInvestedCapital(self, actualInvestedCapital):
        self.actualInvestedCapital = actualInvestedCapital

    def setdismantleYear(self, dismantleTime):
        self.decommissionInYear = dismantleTime

    def setEndOfLife(self, endOfLife):
        self.endOfLife = endOfLife

    def setActualNominalCapacity(self, actualNominalCapacity):
        # self.setActualNominalCapacity(self.getCapacity() * location.getCapacityMultiplicationFactor())
        if actualNominalCapacity < 0:
            raise ValueError("ERROR: " + self.name + " power plant is being set with a negative capacity!")
        self.actualNominalCapacity = actualNominalCapacity

    def getFuelMix(self):
        return self.fuelMix

    def getLoan(self):
        return self.loan

    def setLoan(self, loan):
        self.loan = loan

    def setDownpayment(self, downpayment):
        self.downpayment = downpayment

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

    # def calculate_marginal_cost_excl_co2_market_cost(self, reps, time):
    #     mc = 0
    #     if self.technology.fuel != '':
    #         xp = [2020, 2050]
    #         fp = [self.technology.fuel.initialprice2020, self.technology.fuel.initialprice2050]
    #         newSimulatedPrice = np.interp(reps.current_year, xp, fp)
    #         fc = newSimulatedPrice / self.technology.efficiency
    #     else:
    #         fc = 0
    #     mc += fc
    #     mc += self.calculate_co2_tax_marginal_cost(reps)
    #     return mc

    # def calculate_co2_tax_marginal_cost(self, reps):
    #     co2_intensity = self.calculate_emission_intensity(reps)
    #     co2_tax = 0  # TODO: Retrieve CO2 Market Price
    #     return co2_intensity * co2_tax

    # def get_load_factor_for_production(self, production):
    #     if self.capacity != 0:
    #         return production / self.capacity
    #     else:
    #         return 0


class Decommissioned(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.Done = []
        self.Expectation = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if parameter_name == 'Done':
            self.Done = parameter_value
        elif len(parameter_name) == 4:
            self.Expectation[int(parameter_name)] = parameter_value
