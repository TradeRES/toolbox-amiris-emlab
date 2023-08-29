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
        self.agent = reps.energy_producers[reps.agent]
        reps.dbrw.stage_init_market_clearing_point_structure()

    def act(self):
        # in the future : do for every EnergyProducer
        # Retrieve every power plant in the active energy producer for the defined country
        for powerplant in self.reps.get_operational_and_to_be_decommissioned():
            # Retrieve variables: the active capacity market, fixed operating costs, power plant capacity and dispatch
            market = self.reps.get_capacity_market_for_plant(powerplant)
            fixed_on_m_cost = powerplant.actualFixedOperatingCost

            capacity = powerplant.get_actual_nominal_capacity()  # TODO check if this has to be changed
            powerplant_load_factor = 1  # TODO: Power Plant Load Factor
            dispatch = self.reps.get_power_plant_electricity_dispatch(powerplant.id)

            # Bid price is zero, unless net revenues are negative
            price_to_bid = 0
            loan = powerplant.getLoan()
            if loan is not None:
                if loan.getNumberOfPaymentsDone() < loan.getTotalNumberOfPayments():
                    pending_loan = loan.getAmountPerPayment()
                else:
                    pending_loan = 0
            # if power plant is not dispatched, the net revenues are minus the fixed operating costs
            if dispatch is None:
                #print("no dispatch found for " + str(powerplant.id)+  " with name "+str(powerplant.name))
                net_revenues = - fixed_on_m_cost - pending_loan
            # if power plant is dispatched, the net revenues are the revenues minus the total costs
            else:
                # todo: should add loans to fixed costs?
                net_revenues = dispatch.revenues - dispatch.variable_costs - fixed_on_m_cost - pending_loan

            # if net revenues are negative, the bid price is the net revenues per mw of capacity
            if powerplant.get_actual_nominal_capacity() > 0 and net_revenues <= 0:
                price_to_bid = -1 * net_revenues /\
                               (powerplant.get_actual_nominal_capacity() * powerplant.technology.peak_segment_dependent_availability)
                #print(str(powerplant.name) + "   "+str(price_to_bid))
            # all power plants place a bid pair of price and capacity on the market
            self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent, market, \
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

        # Retireve variables: active capacity market, peak load volume and expected demand factor in defined year
        market = self.reps.get_capacity_market_in_country(self.reps.country)
        spot_market = self.reps.get_spot_market_in_country(self.reps.country)
        expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.future_prices,
                                                                                           self.reps.current_year)
        #peak_load = self.reps.get_realized_peak_demand_by_year(self.reps.current_year) - >
        # changed to fix number because peak load can change per weather year.
        # changing peak load according to higher than median year.
        peak_load = spot_market.get_peak_load_per_year(self.reps.current_year)
        # The expected peak load volume is defined as the base peak load with a demand factor for the defined year
        peakExpectedDemand = peak_load * (expectedDemandFactor)

        print("peak load " + str(peakExpectedDemand))
        # Retrieve the sloping demand curve for the expected peak load volume
        sdc = market.get_sloping_demand_curve(peakExpectedDemand)

        # Retrieve the bids on the capacity market, sorted in ascending order on price
        sorted_ppdp = self.reps.get_sorted_bids_by_market_and_time(market, self.reps.current_tick)

        clearing_price = 0
        total_supply = 0
        # Set the clearing price through the merit order
        for ppdp in sorted_ppdp:
            # As long as the market is not cleared
            if self.isTheMarketCleared == False:
                total_supply += ppdp.amount

                if total_supply < sdc.um_volume:
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_accepted
                    clearing_price = sdc.get_price_at_volume(total_supply) # this should result in price cap
                    ppdp.accepted_amount = ppdp.amount
                    #print(ppdp.name , " ACCEPTED ", total_supply, "", clearing_price)

                elif total_supply > sdc.lm_volume:
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_partly_accepted
                    clearing_price = ppdp.price
                    ppdp.accepted_amount = sdc.get_volume_at_price(clearing_price) - total_supply
                    total_supply = sdc.get_volume_at_price(clearing_price)
                    self.isTheMarketCleared = True
                    #print(ppdp.name , " partly ACCEPTED ", total_supply, "", clearing_price)
                    break

            # When the market is cleared
            else:
                ppdp.status = globalNames.power_plant_dispatch_plan_status_failed
                ppdp.accepted_amount = 0

        # saving yearly CM revenues to the power plants and update bids
        self.stageCapacityMechanismRevenues(market, clearing_price)

        # saving market clearing point
        if self.isTheMarketCleared == True:
            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_supply,
                                                             self.reps.current_tick)
            print("Cleared market", market.name, "at " , str(clearing_price))
        else:
            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_supply,
                                                             self.reps.current_tick)
            print("Market is not cleared", market.name, "at " , str(clearing_price))

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
