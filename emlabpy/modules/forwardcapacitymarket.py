"""
The file responsible for all capacity market operations.

Jim Hommes - 25-3-2021
Sanchez 31-05-2022
"""
import json
import logging
import numpy as np
from scipy import interpolate

from util import globalNames
from domain.cashflow import CashFlow
from modules.marketmodule import MarketModule
from util.repository import Repository
from domain.markets import SlopingDemandCurve
from domain.StrategicReserveOperator import StrategicReserveOperator


class ForwardCapacityMarketSubmitBids(MarketModule):
    """
    The class that submits all bids to the Capacity Market
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Capacity Market: Submit Bids', reps)
        reps.dbrw.stage_init_bids_structure()

    def act(self):
        # For every EnergyProducer
        for energy_producer in self.reps.energy_producers.values():

            # For every PowerPlant owned by energyProducer
            for powerplant in self.reps.get_operational_and_in_pipeline_conventional_power_plants_by_owner(energy_producer.name):
                # Retrieve vars

                market = self.reps.get_capacity_market_for_plant(powerplant)
                fixed_on_m_cost = powerplant.get_actual_fixed_operating_cost()
                nominal_capacity = powerplant.get_actual_nominal_capacity()  # TODO check if this has to be changed
                dispatch = self.reps.get_power_plant_electricity_dispatch(powerplant.id)
                # attention this is provisional > power plants should have the dispatch
                if dispatch is None:
                    net_revenues = - fixed_on_m_cost
                else:
                    net_revenues = dispatch.revenues - dispatch.variable_costs - fixed_on_m_cost
                price_to_bid = 0

                if nominal_capacity > 0 and net_revenues <= 0:
                    price_to_bid = -1 * net_revenues / (nominal_capacity *
                                                        powerplant.technology.peak_segment_dependent_availability)

                self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, energy_producer, market,
                                                                           nominal_capacity * powerplant.technology.peak_segment_dependent_availability,
                                                                           price_to_bid, self.reps.current_tick)


class ForwardCapacityMarketClearing(MarketModule):
    """
    The class that clears the Capacity Market based on the Sloping Demand curve
    """

    def __init__(self, reps: Repository, operator: StrategicReserveOperator):
        super().__init__('EM-Lab Capacity Market: Clear Market', reps)
        reps.dbrw.stage_init_sr_operator_structure()
        reps.dbrw.stage_init_capacitymechanisms_structure()
        self.operator = operator
        self.isTheMarketCleared = False

    def act(self):
        print("capacity market clearing")
        market = self.reps.get_capacity_market_in_country(self.reps.country)
        # Calculate the peak load for 4 years in the future
        future_year = self.reps.current_year + 4
        peak_load = max(
            self.reps.get_hourly_demand_by_power_grid_node_and_year(market.country)[
                1])  # todo later it should be also per year
        try:
            expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.simulated_prices,
                                                                                           future_year)
        except:
            expectedDemandFactor = self.get_extrapolated_demand_factor(self.reps.current_year, future_year)

        peakExpectedDemand = peak_load * (expectedDemandFactor)

        sdc = market.get_sloping_demand_curve(peakExpectedDemand)
        sorted_ppdp = self.reps.get_sorted_bids_by_market_and_time(market, self.reps.current_tick)

        self.operator.setZone(market.country)
        CMO_name = "CMO_" + market.country
        try:
            CM_operator = self.reps.sr_operator[CMO_name]
        except:
            CM_operator = self.operator

        clearing_price = 0
        total_supply = 0
        # Set the clearing price through the merit order
        for ppdp in sorted_ppdp:
            if self.isTheMarketCleared == False:
                plant = self.reps.power_plants[ppdp.plant]
                if ppdp.plant in CM_operator.list_of_plants and plant.age < 15:
                    total_supply += ppdp.amount
                    clearing_price = ppdp.price
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_accepted
                    ppdp.accepted_amount = ppdp.amount
                    self.operator.setPlants(ppdp.plant)

                elif ppdp.price <= sdc.get_price_at_volume(total_supply + ppdp.amount):
                    total_supply += ppdp.amount
                    clearing_price = ppdp.price
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_accepted
                    ppdp.accepted_amount = ppdp.amount
                    if plant.status == globalNames.power_plant_status_inPipeline:
                        self.operator.setPlants(ppdp.plant)

                elif ppdp.price < sdc.get_price_at_volume(total_supply):
                    clearing_price = ppdp.price
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_partly_accepted
                    ppdp.accepted_amount = sdc.get_volume_at_price(clearing_price) - total_supply
                    total_supply += sdc.get_volume_at_price(clearing_price)
                    self.isTheMarketCleared = True
                    if plant.status == globalNames.power_plant_status_inPipeline:
                        self.operator.setPlants(ppdp.plant)

                elif ppdp.price > sdc.get_price_at_volume(total_supply):
                    self.isTheMarketCleared = True

            else:
                ppdp.status = globalNames.power_plant_dispatch_plan_status_failed
                ppdp.accepted_amount = 0

        self.reps.dbrw.set_power_plant_CapacityMarket_production(sorted_ppdp, self.reps.current_tick)
        # save clearing point
        if self.isTheMarketCleared == True:
            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_supply,
                                                             self.reps.current_tick)
            # self.createCashFlowforCM(market, clearing_price)
            self.stageCapacityMechanismRevenues(clearing_price)
            self.reps.create_or_update_StrategicReserveOperator(CMO_name, self.operator.getZone(),
                                                                0, 0, 0, 0,
                                                                self.operator.getPlants())
        else:
            print("Market is not cleared")


    # def createCashFlowforCM(self, market, clearing_price):
    #     accepted_ppdp = self.reps.get_accepted_CM_bids()
    #     for accepted in accepted_ppdp:
    #         # from_agent, to, amount, type, time, plant
    #         self.reps.createCashFlow(market, self.reps.energy_producers[accepted.bidder], accepted.accepted_amount * clearing_price,
    #                                  "CAPMARKETPAYMENT", self.reps.current_tick,
    #                                  self.reps.power_plants[accepted.plant])

    def get_extrapolated_demand_factor(self, current_year, future_year):
        demand_factor = []
        x = []
        i = -4
        while i <= 0:
            year = current_year + i
            x.append(year)
            demand_factor.append(self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                             globalNames.simulated_prices,
                                                                                             year))
            i += 1

        extrapolated_demand_factor = interpolate.interp1d(x, demand_factor, fill_value='extrapolate')
        return extrapolated_demand_factor(future_year)

    def stageCapacityMechanismRevenues(self, clearing_price):
        print("staging capacity market")
        accepted_ppdp = self.reps.get_accepted_CM_bids()
        for accepted in accepted_ppdp:
            amount = accepted.accepted_amount * clearing_price
            self.reps.dbrw.stage_CM_revenues(accepted.plant, amount, self.reps.current_tick)

