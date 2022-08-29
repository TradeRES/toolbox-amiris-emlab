"""
The file responsible for writing results into an excel to analyse the data

Bart van Nobelen - 05-07-2022
"""

import pandas as pd

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
        self.country = 0
        self.marketclearingvolume = 0      # MW
        self.marketclearingprice = 0       # EUR
        self.nr_of_powerplants = 0
        self.nr_of_powerplants_in_sr = 0
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
        self.powerplant_results = 0
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
        self.pp_market_price = 0

        # capacity parameters
        self.total_installed_capacity = 0
        self.biomass_capacity = 0
        self.biomass_generation = 0
        self.biomass_costs = 0
        self.coal_capacity = 0
        self.coal_generation = 0
        self.coal_costs = 0
        self.ccgt_capacity = 0
        self.ccgt_generation = 0
        self.ccgt_costs = 0
        self.ocgt_capacity = 0
        self.ocgt_generation = 0
        self.ocgt_costs = 0
        self.hydro_storage_capacity = 0
        self.hydro_storage_generation = 0
        self.hydro_storage_costs = 0
        self.nuclear_capacity = 0
        self.nuclear_generation = 0
        self.nuclear_costs = 0
        self.windonshore_capacity = 0
        self.windonshore_generation = 0
        self.windonshore_costs = 0
        self.windoffshore_capacity = 0
        self.windoffshore_generation = 0
        self.windoffshore_costs = 0
        self.pv_capacity = 0
        self.pv_generation = 0
        self.pv_costs = 0
        self.lignite_capacity = 0
        self.lignite_generation = 0
        self.lignite_costs = 0
        self.oil_capacity = 0
        self.oil_generation = 0
        self.oil_costs = 0
        self.hydro_ror_capacity = 0
        self.hydro_ror_generation = 0
        self.hydro_ror_costs = 0
        self.lithium_capacity = 0
        self.lithium_generation = 0
        self.lithium_costs = 0
        self.biomass_price_per_mwh = 0
        self.coal_price_per_mwh = 0
        self.ccgt_price_per_mwh = 0
        self.ocgt_price_per_mwh = 0
        self.hydro_storage_price_per_mwh = 0
        self.nuclear_price_per_mwh = 0
        self.windonshore_price_per_mwh = 0
        self.windoffshore_price_per_mwh = 0
        self.pv_price_per_mwh = 0
        self.lignite_price_per_mwh = 0
        self.oil_price_per_mwh = 0
        self.hydro_ror_price_per_mwh = 0
        self.lithium_price_per_mwh = 0

    def act(self):
        self.tick = self.reps.current_tick
        self.year = self.reps.current_year
        self.country = self.reps.country

        # Reading AMIRIS results
        self.powerplant_results = pd.read_csv(globalNames.amiris_results_path)

        # Creating a new powerplant dataframe
        powerplant_data = pd.DataFrame()

        # Retrieving all the values per powerplant
        for powerplant in self.reps.power_plants.values():
            self.get_powerplant_values(powerplant)
            self.get_capacity_values(powerplant)

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
                                              'Profit (€)':self.pp_profit,
                                              'Market price (€)':self.pp_market_price}, index=[0])

            # Appending all powerplants into the dataframe for the year
            powerplant_data = pd.concat([powerplant_data, powerplant_values], ignore_index=True)

        self.get_shortage_hours(self.year, self.total_installed_capacity)
        self.nr_of_powerplants = len(self.reps.power_plants)

        self.get_accepted_bids_CM()
        self.get_strategic_reserve_values()
        try:
            self.average_price_per_mwh = self.total_costs / self.total_production
        except:
            self.average_price_per_mwh = 0
        self.get_price_per_technology()

        # Reading previous overview data
        overview_data = pd.read_excel('Yearly_results.xlsx', sheet_name='Overview', index_col=0)
        capacity_data = pd.read_excel('Yearly_results.xlsx', sheet_name='Capacity', index_col=0)
        # overview_data = pd.DataFrame()
        # capacity_data = pd.DataFrame()

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

        capacity_values = pd.DataFrame({'Year':self.year,
                                        'Biomass capacity (MW)':self.biomass_capacity,
                                        'Biomass production (MWh)':self.biomass_generation,
                                        'Biomass costs (€)':self.biomass_costs,
                                        'Biomass price per MWh (€/MWh)':self.biomass_price_per_mwh,
                                        'Coal capacity (MW)':self.coal_capacity,
                                        'Coal production (MWh)':self.coal_generation,
                                        'Coal costs (€)':self.coal_costs,
                                        'Coal price per MWh (€/MWh)':self.coal_price_per_mwh,
                                        'CCGT capacity (MW)':self.ccgt_capacity,
                                        'CCGT production (MWh)':self.ccgt_generation,
                                        'CCGT costs (€)':self.ccgt_costs,
                                        'CCGT price per MWh (€/MWh)':self.ccgt_price_per_mwh,
                                        'OCGT capacity (MW)':self.ocgt_capacity,
                                        'OCGT production (MWh)':self.ocgt_generation,
                                        'OCGT costs (€)':self.ocgt_costs,
                                        'OCGT price per MWh (€/MWh)':self.ocgt_price_per_mwh,
                                        'Hydro storage capacity (MW)':self.hydro_storage_capacity,
                                        'Hydro storage production (MWh)':self.hydro_storage_generation,
                                        'Hydro storage costs (€)':self.hydro_storage_costs,
                                        'Hydro storage price per MWh (€/MWh)':self.hydro_storage_price_per_mwh,
                                        'Nuclear capacity (MW)':self.nuclear_capacity,
                                        'Nuclear production (MWh)':self.nuclear_generation,
                                        'Nuclear costs (€)':self.nuclear_costs,
                                        'Nuclear price per MWh (€/MWh)':self.nuclear_price_per_mwh,
                                        'Wind onshore capacity (MW)':self.windonshore_capacity,
                                        'Wind onshore production (MWh)':self.windonshore_generation,
                                        'Wind onshore costs (€)':self.windonshore_costs,
                                        'Wind onshore price per MWh (€/MWh)':self.windonshore_price_per_mwh,
                                        'Wind offshore capacity (MW)':self.windoffshore_capacity,
                                        'Wind offshore production (MWh)':self.windoffshore_generation,
                                        'Wind offshore costs (€)':self.windoffshore_costs,
                                        'Wind offshore price per MWh (€/MWh)':self.windoffshore_price_per_mwh,
                                        'PV capacity (MW)':self.pv_capacity,
                                        'PV production (MWh)':self.pv_generation,
                                        'PV costs (€)':self.pv_costs,
                                        'PV price per MWh (€/MWh)':self.pv_price_per_mwh,
                                        'Lignite capacity (MW)':self.lignite_capacity,
                                        'Lignite production (MWh)':self.lignite_generation,
                                        'Lignite costs (€)':self.lignite_costs,
                                        'Lignite price per MWh (€/MWh)':self.lignite_price_per_mwh,
                                        'Fuel oil capacity (MW)':self.oil_capacity,
                                        'Fuel oil production (MWh)':self.oil_generation,
                                        'Fuel oil costs (€)':self.oil_costs,
                                        'Fuel oil price per MWh (€/MWh)':self.oil_price_per_mwh,
                                        'Hydro ROR capacity (MW)':self.hydro_ror_capacity,
                                        'Hydro ROR production (MWh)':self.hydro_ror_generation,
                                        'Hydro ROR costs (€)':self.hydro_ror_costs,
                                        'Hydro ROR price per MWh (€/MWh)':self.hydro_ror_price_per_mwh,
                                        'Lithium capacity (MW)':self.lithium_capacity,
                                        'Lithium production (MWh)':self.lithium_generation,
                                        'Lithium costs (€)':self.lithium_costs,
                                        'Lithium price per MWh (€/MWh)':self.lithium_price_per_mwh}, index=[0])

        # Appending new data to existing
        overview_data = pd.concat([overview_data, overview_values], ignore_index=True)
        capacity_data = pd.concat([capacity_data, capacity_values], ignore_index=True)

        # Writing all the data into the excel
        writer = pd.ExcelWriter('Yearly_results.xlsx')
        overview_data.to_excel(writer, sheet_name='Overview')
        capacity_data.to_excel(writer, sheet_name='Capacity')
        pp_year = 'Powerplants' + str(self.year)
        powerplant_data.to_excel(writer, sheet_name=pp_year)
        writer.save()


    # Section with functions for retrieving data

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
                self.SR_volume = i.reserveVolume
                self.nr_of_powerplants_in_sr = len(i.list_of_plants)
                if i.cash == 0 or i.reserveVolume == 0:
                    price_per_mw = 0
                else:
                    price_per_mw = -i.cash/i.reserveVolume
                self.SR_cost_per_MW = price_per_mw

    def get_shortage_hours(self, year, capacity):
        demand_list = []
        if self.country == 'DE':
            market_zone = 'GermanElectricitySpotMarket'
        else:
            market_zone = 'DutchElectricitySpotMarket'
        peak_load = max(self.reps.get_hourly_demand_by_country(market.country)[1])
        expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.simulated_prices,
                                                                                           self.reps.current_year)
        peakExpectedDemand = peak_load * (expectedDemandFactor)
        count = 0
        for i in self.reps.electricity_spot_markets.values():
            if i.name == market_zone:
                demand_list = i.hourlyDemand[1].values
        for i in demand_list:
            x = i * expectedDemandFactor
            if x > capacity:
                count += 1
        self.shortage_hours = count
        self.supply_ratio = capacity/peakExpectedDemand

    def get_powerplant_values(self, powerplant):
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
        self.pp_status = powerplant.status
        self.pp_fixedoperatingcosts = powerplant.actualFixedOperatingCost
        self.pp_variablecosts_perMWh = powerplant.technology.variable_operating_costs
        if powerplant.id in self.powerplant_results['identifier'].values:
            self.pp_total_variable_costs = float(self.powerplant_results.loc[self.powerplant_results['identifier']
                                                                        == powerplant.id,
                                                                        'VARIABLE_COSTS_IN_EURO'].iloc[0])
            self.pp_revenues = float(self.powerplant_results.loc[self.powerplant_results['identifier']
                                                            == powerplant.id,
                                                            'REVENUES_IN_EURO'].iloc[0])
            self.pp_production_in_MWh = float(self.powerplant_results.loc[self.powerplant_results['identifier']
                                                                     == powerplant.id,
                                                                     'PRODUCTION_IN_MWH'].iloc[0])
        else:
            self.pp_total_variable_costs = 0
            self.pp_revenues = 0
            self.pp_production_in_MWh = 0

        self.pp_profit = self.pp_revenues - self.pp_total_variable_costs - self.pp_fixedoperatingcosts
        self.total_production += self.pp_production_in_MWh
        self.total_costs += self.pp_revenues
        if self.pp_production_in_MWh != 0:
            self.pp_market_price = self.pp_revenues / self.pp_production_in_MWh
        else:
            self.pp_market_price = 0

    def get_capacity_values(self, powerplant):
        if powerplant.status == globalNames.power_plant_status_operational \
                or powerplant.status == globalNames.power_plant_status_to_be_decommissioned \
                or powerplant.status == globalNames.power_plant_status_strategic_reserve:
            self.total_installed_capacity += powerplant.actualNominalCapacity
            if powerplant.technology.name == 'Biomass_CHP_wood_pellets_DH':
                self.biomass_capacity += powerplant.actualNominalCapacity
                self.biomass_generation += self.pp_production_in_MWh
                self.biomass_costs += self.pp_revenues
            elif powerplant.technology.name == 'Coal PSC':
                self.coal_capacity += powerplant.actualNominalCapacity
                self.coal_generation += self.pp_production_in_MWh
                self.coal_costs += self.pp_revenues
            elif powerplant.technology.name == 'CCGT':
                self.ccgt_capacity += powerplant.actualNominalCapacity
                self.ccgt_generation += self.pp_production_in_MWh
                self.ccgt_costs += self.pp_revenues
            elif powerplant.technology.name == 'OCGT':
                self.ocgt_capacity += powerplant.actualNominalCapacity
                self.ocgt_generation += self.pp_production_in_MWh
                self.ocgt_costs += self.pp_revenues
            elif powerplant.technology.name == 'Hydropower_reservoir_medium':
                self.hydro_storage_capacity += powerplant.actualNominalCapacity
                self.hydro_storage_generation += self.pp_production_in_MWh
                self.hydro_storage_costs += self.pp_revenues
            elif powerplant.technology.name == 'Nuclear':
                self.nuclear_capacity += powerplant.actualNominalCapacity
                self.nuclear_generation += self.pp_production_in_MWh
                self.nuclear_costs += self.pp_revenues
            elif powerplant.technology.name == 'WTG_onshore':
                self.windonshore_capacity += powerplant.actualNominalCapacity
                self.windonshore_generation += self.pp_production_in_MWh
                self.windonshore_costs += self.pp_revenues
            elif powerplant.technology.name == 'WTG_offshore':
                self.windoffshore_capacity += powerplant.actualNominalCapacity
                self.windoffshore_generation += self.pp_production_in_MWh
                self.windoffshore_costs += self.pp_revenues
            elif powerplant.technology.name == 'PV_utility_systems':
                self.pv_capacity += powerplant.actualNominalCapacity
                self.pv_generation += self.pp_production_in_MWh
                self.pv_costs += self.pp_revenues
            elif powerplant.technology.name == 'Lignite PSC':
                self.lignite_capacity += powerplant.actualNominalCapacity
                self.lignite_generation += self.pp_production_in_MWh
                self.lignite_costs += self.pp_revenues
            elif powerplant.technology.name == 'Fuel oil PGT':
                self.oil_capacity += powerplant.actualNominalCapacity
                self.oil_generation += self.pp_production_in_MWh
                self.oil_costs += self.pp_revenues
            elif powerplant.technology.name == 'Hydropower_ROR':
                self.hydro_ror_capacity += powerplant.actualNominalCapacity
                self.hydro_ror_generation += self.pp_production_in_MWh
                self.hydro_ror_costs += self.pp_revenues
            elif powerplant.technology.name == 'Lithium_ion_battery':
                self.lithium_capacity += powerplant.actualNominalCapacity
                self.lithium_generation += self.pp_production_in_MWh
                self.lithium_costs += self.pp_revenues

    def get_price_per_technology(self):
        try:
            self.biomass_price_per_mwh = self.biomass_costs / self.biomass_generation
        except:
            self.biomass_price_per_mwh = 0
        try:
            self.coal_price_per_mwh = self.coal_costs / self.coal_generation
        except:
            self.coal_price_per_mwh = 0
        try:
            self.ccgt_price_per_mwh = self.ccgt_costs / self.ccgt_generation
        except:
            self.ccgt_price_per_mwh = 0
        try:
            self.ocgt_price_per_mwh = self.ocgt_costs / self.ocgt_generation
        except:
            self.ocgt_price_per_mwh = 0
        try:
            self.hydro_storage_price_per_mwh = self.hydro_storage_costs / self.hydro_storage_generation
        except:
            self.hydro_storage_price_per_mwh = 0
        try:
            self.nuclear_price_per_mwh = self.nuclear_costs / self.nuclear_generation
        except:
            self.nuclear_price_per_mwh = 0
        try:
            self.windonshore_price_per_mwh = self.windonshore_costs / self.windonshore_generation
        except:
            self.windonshore_price_per_mwh = 0
        try:
            self.windoffshore_price_per_mwh = self.windoffshore_costs / self.windoffshore_generation
        except:
            self.windoffshore_price_per_mwh = 0
        try:
            self.pv_price_per_mwh = self.pv_costs / self.pv_generation
        except:
            self.pv_price_per_mwh = 0
        try:
            self.lignite_price_per_mwh = self.lignite_costs / self.lignite_generation
        except:
            self.lignite_price_per_mwh = 0
        try:
            self.oil_price_per_mwh = self.oil_costs / self.oil_generation
        except:
            self.oil_price_per_mwh = 0
        try:
            self.hydro_ror_price_per_mwh = self.hydro_ror_costs / self.hydro_ror_generation
        except:
            self.hydro_ror_price_per_mwh = 0
        try:
            self.lithium_price_per_mwh = self.lithium_costs / self.lithium_generation
        except:
            self.lithium_price_per_mwh = 0





