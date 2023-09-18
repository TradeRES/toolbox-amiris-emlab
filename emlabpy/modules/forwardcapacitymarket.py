"""
The file responsible for all forward capacity market operations.

Bart van Nobelen - 26-05-2022
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
        self.agent = reps.energy_producers[reps.agent]
        reps.dbrw.stage_init_market_clearing_point_structure()

    def act(self):
        # Retrieve every power plant in the active energy producer for the defined country
        # todo: if this is only for long term, should only in piepline power plants shold participate?
        # dont consider the to be decommmissinoed because 4 years agead they should be decommsiioned.
        for powerplant in self.reps.get_operational_and_in_pipeline_conventional_power_plants_by_owner(
                self.agent.name):
            # Retrieve variables: the active capacity market, fixed operating costs, power plant capacity and dispatch
            market = self.reps.get_capacity_market_for_plant(powerplant)
            fixed_on_m_cost = powerplant.actualFixedOperatingCost
            nominal_capacity = powerplant.get_actual_nominal_capacity()  # TODO check if this has to be changed
            dispatch = self.reps.get_power_plant_electricity_dispatch(powerplant.id)

            # Bid price is zero, unless net revenues are negative
            price_to_bid = 0

            # attention this is provisional > power plants should have the dispatch
            # if power plant is not dispatched, the net revenues are minus the fixed operating costs
            if dispatch is None:
                net_revenues = - fixed_on_m_cost
            # if power plant is dispatched, the net revenues are the revenues minus the total costs
            else:
                net_revenues = dispatch.revenues - dispatch.variable_costs - fixed_on_m_cost

            # if net revenues are negative, the bid price is the net revenues per mw of capacity
            if nominal_capacity > 0 and net_revenues <= 0:
                price_to_bid = -1 * net_revenues / (nominal_capacity *
                                                    powerplant.technology.peak_segment_dependent_availability)

            # all power plants place a bid pair of price and capacity on the market
            self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent, market, \
                                                                       capacity * powerplant.technology.peak_segment_dependent_availability,\
                                                                       price_to_bid, self.reps.current_tick)


class ForwardCapacityMarketClearing(MarketModule):
    """
    The class that clears the Capacity Market based on the Sloping Demand curve
    """

    def __init__(self, reps: Repository, operator: StrategicReserveOperator):
        super().__init__('EM-Lab Capacity Market: Clear Market', reps)
        reps.dbrw.stage_init_sr_results_structure()
        reps.dbrw.stage_init_capacitymechanisms_structure()
        self.operator = None
        self.isTheMarketCleared = False

    def act(self):
        print("capacity market clearing")

        # Retireve variables: active capacity market and active operator
        # The strategic reserve operator is used to save the power plants with a long term contract
        market = self.reps.get_capacity_market_in_country(self.reps.country)
        self.operator = self.reps.get_strategic_reserve_operator(self.reps.country)

        # Calculate the peak load for 4 years in the future
        future_year = self.reps.current_year + 4
        peak_load = self.reps.get_realized_peak_demand_by_year(self.reps.current_year)
        expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.simulated_prices,
                                                                                           future_year)
        # The expected peak load volume is defined as the base peak load with a demand factor for the defined year
        peakExpectedDemand = peak_load * (expectedDemandFactor)

        # Retrieve the sloping demand curve for the expected peak load volume
        sdc = market.get_sloping_demand_curve(peakExpectedDemand)

        # Retrieve the bids on the capacity market, sorted in ascending order on price
        sorted_ppdp = self.reps.get_sorted_bids_by_market_and_time(market, self.reps.current_tick)

        # Retrieve power plants with longterm contract
        list_of_plants_long_term_contracts = self.operator.list_of_plants_inSR_in_current_year

        clearing_price = 0
        total_supply = 0
        # Set the clearing price through the merit order
        for ppdp in sorted_ppdp:
            # As long as the market is not cleared
            if self.isTheMarketCleared == False:
                plant = self.reps.power_plants[ppdp.plant]
                # Firstly accept bids from plants with long term contracts
                if ppdp.plant in list_of_plants_long_term_contracts and plant.age < 15:
                    total_supply += ppdp.amount
                    clearing_price = ppdp.price
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_accepted
                    ppdp.accepted_amount = ppdp.amount

                elif ppdp.price <= sdc.get_price_at_volume(total_supply + ppdp.amount):
                    total_supply += ppdp.amount
                    clearing_price = ppdp.price
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_accepted
                    ppdp.accepted_amount = ppdp.amount

                    # short term are only for one year. no need to add them to the list, next year should be reset
                    if plant.status == globalNames.power_plant_status_inPipeline:
                        list_of_plants_long_term_contracts.append(ppdp.plant)

                elif ppdp.price < sdc.get_price_at_volume(total_supply):
                    clearing_price = ppdp.price
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_partly_accepted
                    ppdp.accepted_amount = sdc.get_volume_at_price(clearing_price) - total_supply
                    total_supply += sdc.get_volume_at_price(clearing_price)
                    self.isTheMarketCleared = True
                    if plant.status == globalNames.power_plant_status_inPipeline:
                        list_of_plants_long_term_contracts.append(ppdp.plant)

                elif ppdp.price > sdc.get_price_at_volume(total_supply):
                    self.isTheMarketCleared = True
            # When the market is cleared
            else:
                ppdp.status = globalNames.power_plant_dispatch_plan_status_failed
                ppdp.accepted_amount = 0

        # Save plants with longterm contracts
        self.operator.setPlants(list_of_plants_long_term_contracts)


        # saving yearly CM revenues to the power plants and update bids
        self.stageCapacityMechanismRevenues(market, clearing_price)

        # Update the operator with the current contracted plants
        self.reps.create_or_update_StrategicReserveOperator(self.operator.name,
                                                            self.operator.getZone(),
                                                            0,
                                                            0,
                                                            0,
                                                            self.operator.getPlants())

        # saving market clearing point
        if self.isTheMarketCleared == True:
            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_supply,
                                                             self.reps.current_tick)
            print("Cleared market", market.name)
        else:
            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_supply,
                                                             self.reps.current_tick)
            print("Market is not cleared", market.name)



    def stageCapacityMechanismRevenues(self, market, clearing_price):
        print("staging capacity market")
        # todo: test that bids are found
        accepted_ppdp = self.reps.get_accepted_CM_bids(self.reps.current_tick)
        for accepted in accepted_ppdp:
            amount = accepted.accepted_amount * clearing_price
            # saving yearly CM revenues to the power plants # todo: the bids could be erased later on if all the values can be read from clearing point
            self.reps.dbrw.stage_CM_revenues(accepted.plant, amount, self.reps.current_tick)
            # saving capacity market accepted bids amount and status
            self.reps.dbrw.stage_bids_status(accepted)

