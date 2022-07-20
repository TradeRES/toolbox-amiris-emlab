"""
The file responsible for writing results into an excel to analyse the data
Bart van Nobelen - 05-07-2022
"""

import pandas as pd
from openpyxl import load_workbook

from domain.import_object import *
from modules.defaultmodule import DefaultModule
from util.repository import Repository
from domain.StrategicReserveOperator import StrategicReserveOperator
from util import globalNames

import logging
class CreatingResultsExcel(DefaultModule):

    def __init__(self, reps: Repository, operator: StrategicReserveOperator):
        super().__init__("Creating Results Excel", reps)
        reps.dbrw.stage_init_financial_results_structure()
        self.operator = operator

        # Parameters for the overview
        self.tick = 0
        self.year = 0
        self.marketclearingvolume = 0      # MW
        self.marketclearingprice = 0       # EUR
        self.total_installed_capacity = 0
        self.nr_of_powerplants = 0
        self.nr_of_powerplants_in_sr = 0
        # self.cost_of_sr =0]       # EUR
        # self.volume_of_sr =0]      # MW
        self.average_electricity_price = 0         # EUR/MWh
        self.shortage_hours = 0        # hours/year
        self.supply_ratio = 0      # MW/MW
        self.cost_to_consumer = 0       # EUR/MWh
        self.CM_volume = 0     # MW
        self.CM_price = 0      # EUR
        self.CM_cost_per_MW = 0       # EUR/MWh
        self.SR_operator_cash = 0      # EUR
        self.SR_volume = 0     # MW
        self.SR_price = 0      # EUR
        self.SR_cost_per_MW = 0       # EUR/MWh

        # Parameters for the power plants
        self.pp_name = 0
        self.pp_owner = 0
        self.pp_location = 0
        self.pp_technology = 0
        self.pp_fuel = 0
        self.pp_age = 0
        self.pp_efficiency = 0
        self.pp_capacity = 0
        self.pp_acceptedcapacity = 0
        self.pp_status = 0
        self.pp_profit = 0
        self.pp_fixedoperatingcosts = 0
        self.pp_variablecosts_perMWh = 0
        self.pp_total_variable_costs = 0
        self.pp_revenues = 0
        self.pp_production_in_MWh = 0
        self.total_production = 0
        self.total_costs = 0
        self.average_price_per_mwh = 0
        self.market_price = 0

    def act(self):
        self.tick = self.reps.current_tick
        self.year = self.reps.current_year
        self.country = self.reps.country

        installed_capacity = 0
        for i in self.reps.power_plants.values():
            installed_capacity += i.capacity
        self.total_installed_capacity = installed_capacity

        self.get_shortage_hours(self.year, installed_capacity)

        self.nr_of_powerplants = len(self.reps.power_plants)

        # self.get_marketclearingpoint(self.tick)
        # self.get_power_plant_dispatch_plans(self.tick)
        self.get_accepted_bids_CM()
        self.get_strategic_reserve_values()

        # self.SR_price.append(self.operator.getCash())
        # self.SR_cost_per_MW =0]       # EUR/MWh
        # self.cost_to_consumer_CM.append(0)
        # self.cost_to_consumer.append(0)

        # Reading AMIRIS results
        powerplant_results = pd.read_csv(globalNames.amiris_results_path)

        # Creating a new powerplant dataframe
        powerplant_data = pd.DataFrame()

        # Retrieving all the values per powerplant
        for powerplant in self.reps.power_plants.values():
            self.pp_name = powerplant.name
            self.pp_owner = powerplant.owner.name
            self.pp_location = powerplant.location
            self.pp_technology = powerplant.technology.name
            if powerplant.technology.fuel != '':
                self.pp_fuel = powerplant.technology.fuel.name
            else:
                self.pp_fuel = ''
            self.pp_age = powerplant.age
            self.pp_efficiency = powerplant.actualEfficiency
            self.pp_capacity = powerplant.actualNominalCapacity
            # self.pp_acceptedcapacity = powerplant.AwardedPowerinMWh
            self.pp_status = powerplant.status
            # self.pp_profit = powerplant.operationalProfit
            self.pp_fixedoperatingcosts = powerplant.actualFixedOperatingCost
            self.pp_variablecosts_perMWh = powerplant.technology.variable_operating_costs
            # self.pp_revenues = self.reps.dbrw.findFinancialPowerPlantProfitsForPlant(powerplant)
            # self.pp_revenues = self.reps.get_power_plant_electricity_spot_market_revenues_by_tick(powerplant.id, self.reps.current_tick)

            # testding = powerplant_results.loc[powerplant_results['identifier'] == powerplant.id]
            # self.pp_total_variable_costs = testding.loc[testding['VARIABLE_COSTS_IN_EURO']]
            # self.pp_revenues = testding.iloc[2]
            # self.pp_production_in_MWh = testding.iloc[3]
            if powerplant.id in powerplant_results['identifier'].values:
                self.pp_total_variable_costs = float(powerplant_results.loc[powerplant_results['identifier']
                                                                            == powerplant.id,
                                                                            'VARIABLE_COSTS_IN_EURO'].iloc[0])
                self.pp_revenues = float(powerplant_results.loc[powerplant_results['identifier']
                                                                == powerplant.id,
                                                                'REVENUES_IN_EURO'].iloc[0])
                self.pp_production_in_MWh = float(powerplant_results.loc[powerplant_results['identifier']
                                                                         == powerplant.id,
                                                                         'PRODUCTION_IN_MWH'].iloc[0])
            else:
                self.pp_total_variable_costs = 0
                self.pp_revenues = 0
                self.pp_production_in_MWh = 0

            self.pp_profit = self.pp_revenues - self.pp_total_variable_costs - self.pp_fixedoperatingcosts
            # if powerplant.technology.variable_operating_costs != None:
            #     self.pp_variablecostcheck = self.pp_variablecosts_perMWh * self.pp_production_in_MWh
            # else:
            #     self.pp_variablecostcheck = 0

            self.total_production += self.pp_production_in_MWh
            self.total_costs += self.pp_revenues
            if self.pp_production_in_MWh != 0:
                self.market_price = self.pp_revenues /  self.pp_production_in_MWh
            else:
                self.market_price = 0


            # Combining the data into a dataframe
            powerplant_values = pd.DataFrame({'Name':self.pp_name,
                                              'Owner':self.pp_owner,
                                              'Technology':self.pp_technology,
                                              'Fuel':self.pp_fuel,
                                              'Location':self.pp_location,
                                              'Age':self.pp_age,
                                              'Status':self.pp_status,
                                              'Efficiency':self.pp_efficiency,
                                              'Capacity (MW)':self.pp_capacity,
                                              # 'Accepted capacity':self.pp_acceptedcapacity,
                                              'Fixed Operating Costs (€)':self.pp_fixedoperatingcosts,
                                              'Variable Costs per MWh (€/MWh)':self.pp_variablecosts_perMWh,
                                              'Total variable costs (€)':self.pp_total_variable_costs,
                                              'Production (MWh)':self.pp_production_in_MWh,
                                              'Revenues (€)':self.pp_revenues,
                                              'operationalProfit (€)':self.pp_profit,
                                              'Market price (€)':self.market_price}, index=[0])

            # Appending all powerplants into the dataframe for the year
            powerplant_data = pd.concat([powerplant_data, powerplant_values], ignore_index=True)

        self.average_price_per_mwh = self.total_costs / self.total_production

        # Reading previous overview data
        overview_data = pd.read_excel('Yearly_results.xlsx', sheet_name='Overview', index_col=0)
        # overview_data = pd.DataFrame()
        # Creating the dataframe with the new values of current year
        overview_values = pd.DataFrame({'Year':self.year,
                                        'Market clearing volume (MWh)':self.total_production,
                                        'Market clearing price (€)':self.total_costs,
                                        'Average price of electricity (€/MWh)':self.average_price_per_mwh,
                                        'Number of power plants':self.nr_of_powerplants,
                                        'Total installed capacity (MW)':self.total_installed_capacity,
                                        'Shortage hours':self.shortage_hours,
                                        'Supply ratio':self.supply_ratio,
                                        'CM volume (MW)':self.CM_volume,
                                        'CM price (€)':self.CM_price,
                                        'CM price per MW (€/MWh)':self.CM_cost_per_MW,
                                        'Number of power plants in SR':self.nr_of_powerplants_in_sr,
                                        'SR volume (MW)':self.SR_volume,
                                        'SR operator cash (€)':self.SR_operator_cash,
                                        'SR price per MW (€/MWh)':self.SR_cost_per_MW}, index=[0])

        # Appending new data to existing
        overview_data = pd.concat([overview_data, overview_values], ignore_index=True)

        # Writing all the data into the excel
        writer = pd.ExcelWriter('Yearly_results.xlsx')
        # writer.book = load_workbook('Yearly_results.xlsx')
        overview_data.to_excel(writer, sheet_name='Overview')
        pp_year = 'Powerplants' + str(self.year)
        powerplant_data.to_excel(writer, sheet_name=pp_year)
        writer.save()


    # Section with functions for retrieving data

    # def get_marketclearingpoint(self, tick):
    #     total_volume = 0
    #     total_price = 0
    #     for i in self.reps.market_clearing_points.values():
    #         if i.time == tick and i.market.name == 'DutchCapacityMarket':
    #             total_volume += i.volume
    #             total_price += i.price
    #     self.marketclearingvolume = total_volume
    #     self.marketclearingprice = total_price

    def get_accepted_bids_CM(self):
        accepted_amount = 0
        total_price = 0
        if self.country == 'DE':
            market_zone = 'GermanCapacityMarket'
        else:
            market_zone = 'DutchCapacityMarket'
        for i in self.reps.bids.values():
            if i.market == market_zone and \
                    (i.status == globalNames.power_plant_dispatch_plan_status_partly_accepted or
                     i.status == globalNames.power_plant_dispatch_plan_status_accepted):
                accepted_amount += i.accepted_amount
                total_price += i.price
        self.CM_volume = accepted_amount
        self.CM_price = total_price
        if total_price == 0 or accepted_amount == 0:
            price_per_mw = 0
        else:
            price_per_mw = total_price/accepted_amount
        self.CM_cost_per_MW = price_per_mw

    def get_strategic_reserve_values(self):
        for i in self.reps.sr_operator.values():
            if len(i.list_of_plants) != 0 and i.zone == self.country:
                self.SR_operator_cash = i.cash
                self.SR_volume = i.strategic_reserve_volume
                self.nr_of_powerplants_in_sr = len(i.list_of_plants)
                if i.cash == 0 or i.strategic_reserve_volume == 0:
                    price_per_mw = 0
                else:
                    price_per_mw = -i.cash/i.strategic_reserve_volume
                self.SR_cost_per_MW = price_per_mw


        # if self.reps.country == 'DE':
        #     SR_operator = self.reps.sr_operator['SRO_DE']
        # else:
        #     SR_operator = self.reps.sr_operator['SRO_NL']
        # self.SR_operator_cash = SR_operator.cash
        # self.SR_volume = SR_operator.strategic_reserve_volume
        # self.nr_of_powerplants_in_sr = len(SR_operator.list_of_plants)
        # if SR_operator.cash == 0 or SR_operator.strategic_reserve_volume == 0:
        #     price_per_mw = 0
        # else:
        #     price_per_mw = -SR_operator.cash/SR_operator.strategic_reserve_volume
        # self.SR_cost_per_MW = price_per_mw

    def get_shortage_hours(self, year, capacity):
        demand_list = []
        if self.country == 'DE':
            market_zone = 'GermanElectricitySpotMarket'
        else:
            market_zone = 'DutchElectricitySpotMarket'
        trend = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity", globalNames.simulated_prices, year)
        peak_load_without_trend = max(self.reps.get_hourly_demand_by_power_grid_node_and_year(self.country)[1])
        peak_load_volume = peak_load_without_trend * trend
        count = 0
        for i in self.reps.electricity_spot_markets.values():
            if i.name == market_zone:
                demand_list = i.hourlyDemand[1].values
        for i in demand_list:
            x = i * trend
            if x > capacity:
                count += 1
        self.shortage_hours = count
        self.supply_ratio = capacity/peak_load_volume

    # def get_power_plant_dispatch_plans(self, tick):
    #     count = 0
    #     sum = 0
    #     for i in self.reps.power_plant_dispatch_plans.values():
    #         if i.tick == tick:
    #             count += 1
    #             sum += i.price
    #     if count == 0 or sum == 0:
    #         average_price = 0
    #     else:
    #         average_price = sum/count
    #     self.average_electricity_price = average_price