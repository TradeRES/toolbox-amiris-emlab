"""
The file responsible for all capacity market operations.

Jim Hommes - 25-3-2021
Sanchez 31-05-2022
"""
import json
import logging

from util import globalNames
from domain.cashflow import CashFlow
from modules.marketmodule import MarketModule
from util.repository import Repository
from domain.markets import SlopingDemandCurve


class CapacityMarketSubmitBids(MarketModule):
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
            for powerplant in self.reps.get_operational_and_to_be_decommissioned_power_plants_by_owner(
                    energy_producer.name):
                # Retrieve vars
                market = self.reps.get_capacity_market_for_plant(powerplant)
                fixed_on_m_cost = powerplant.calculate_fixed_operating_cost()
                capacity = powerplant.get_actual_nominal_capacity()  # TODO check if this has to be changed
                powerplant_load_factor = 1  # TODO: Power Plant Load Factor
                dispatch = self.reps.get_power_plant_electricity_dispatch(powerplant.id)
                price_to_bid = 0
                if dispatch is None:
                    print("no dispatch found for " + powerplant.name)
                else:
                    net_revenues = dispatch.revenues - dispatch.variable_costs - fixed_on_m_cost
                    if powerplant.get_actual_nominal_capacity() > 0 and net_revenues <= 0:
                        price_to_bid = -1 * net_revenues / (powerplant.get_actual_nominal_capacity() * powerplant.technology.peak_segment_dependent_availability)
                self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, energy_producer, market, \
                                                                           capacity * powerplant.technology.peak_segment_dependent_availability,\
                                                                           price_to_bid, self.reps.current_tick)


class CapacityMarketClearing(MarketModule):
    """
    The class that clears the Capacity Market based on the Sloping Demand curve
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Capacity Market: Clear Market', reps)
        self.isTheMarketCleared = False
        reps.dbrw.stage_init_capacitymechanisms_structure()

    def act(self):
        print("capacity market clearing")
        market = self.reps.get_capacity_market_in_country(self.reps.country)
        peak_load = max(
            self.reps.get_hourly_demand_by_power_grid_node_and_year(market.country)[
                1])  # todo later it should be also per year
        expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.simulated_prices,
                                                                                           self.reps.current_year)
        peakExpectedDemand = peak_load * (expectedDemandFactor)
        sdc = market.get_sloping_demand_curve(peakExpectedDemand)
        sorted_ppdp = self.reps.get_sorted_bids_by_market_and_time(market, self.reps.current_tick)

        clearing_price = 0
        total_supply = 0
        # Set the clearing price through the merit order
        for ppdp in sorted_ppdp:
            if self.isTheMarketCleared == False:
                if ppdp.price <= sdc.get_price_at_volume(total_supply + ppdp.amount):
                    # print(ppdp.name , " ACCEPTED ", ppdp.price, "", sdc.get_price_at_volume(total_supply + ppdp.amount))
                    total_supply += ppdp.amount
                    clearing_price = ppdp.price
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_accepted
                    ppdp.accepted_amount = ppdp.amount

                elif ppdp.price < sdc.get_price_at_volume(total_supply):
                    # print(ppdp.name , " partly ACCEPTED ")
                    clearing_price = ppdp.price
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_partly_accepted
                    ppdp.accepted_amount = sdc.get_volume_at_price(clearing_price) - total_supply
                    total_supply += sdc.get_volume_at_price(clearing_price)
                    self.isTheMarketCleared = True
            else:
                ppdp.status = globalNames.power_plant_dispatch_plan_status_failed
                ppdp.accepted_amount = 0

        # saving capacity market accepted amount and status
        self.reps.dbrw.set_power_plant_CapacityMarket_production(sorted_ppdp, self.reps.current_tick)
        self.stageCapacityMechanismRevenues(clearing_price)
        # save clearing point
        if self.isTheMarketCleared == True:
            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_supply,
                                                             self.reps.current_tick)
        else:
            print("Market is not cleared", market.name)
            # logging.WARN("market uncleared at price %s at volume %s ",  str(clearing_price), str(total_supply))

            # VERIFICATION #
            #
            # clearingPoint  = self.reps.get_market_clearing_point_price_for_market_and_time(market,self.reps.current_tick)
            # q1 = clearingPoint.volume
            # q2 = peakExpectedDemand * (1 - SlopingDemandCurve.lm) + (
            #             (SlopingDemandCurve.price_cap - clearingPoint.price ) * (
            #         SlopingDemandCurve.um + SlopingDemandCurve.lm) * peakExpectedDemand ) / SlopingDemandCurve.price_cap
            # q3 = ((clearingPoint.price - SlopingDemandCurve.price_cap) / - SlopingDemandCurve.m) + SlopingDemandCurve.lm_volume
            # if q1 == q2:
            #     logging.WARN("matches")
            # else:
            #     logging.WARN("does not match")

    # def createCashFlowforCM(self, market, clearing_price):
    #     accepted_ppdp = self.reps.get_accepted_CM_bids()
    #     for accepted in accepted_ppdp:
    #         # from_agent, to, amount, type, time, plant
    #         self.reps.createCashFlow(market , accepted.bidder, accepted.accepted_amount * clearing_price,
    #                                  "CAPMARKETPAYMENT", self.reps.current_tick,
    #                                   accepted.plant)

    def stageCapacityMechanismRevenues(self, clearing_price):
        print("staging capacity market")
        accepted_ppdp = self.reps.get_accepted_CM_bids()
        for accepted in accepted_ppdp:
            amount = accepted.accepted_amount * clearing_price
            self.reps.dbrw.stage_CM_revenues(accepted.plant, amount, self.reps.current_tick)
