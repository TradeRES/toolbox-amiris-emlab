from modules.capacitymarket import CapacityMarketClearing
from modules.marketmodule import MarketModule
from util.repository import Repository
from util import globalNames
import pandas as pd
class DemandCurve:
    """
    The SlopingDemandCurve as required in the CapacityMarket.
    """
    def __init__(self,  price_cap, sorted_demand):
        self.price_cap = price_cap
        self.sorted_demand = sorted_demand

    def get_price_at_volume(self, cummulative_supply):
        price = self.price_cap
        for demand in self.sorted_demand:
            price = demand.price
            if demand.cummulative_quantity > cummulative_supply:
                break
        return price



class CapacitySubscriptionClearing(MarketModule):
    """
    The class that clears the Capacity Market based on the Sloping Demand curve
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Capacity Subscription: Clear Market', reps)
        reps.dbrw.stage_init_capacitymechanisms_structure()
        self.agent = reps.energy_producers[reps.agent]

    def act(self):
        print("capacity subscription ")
        capacity_market = self.reps.get_capacity_market_in_country(self.reps.country)
        capacity_market_year = self.reps.current_year + capacity_market.forward_years_CM
        sorted_ppdp = self.reps.get_sorted_bids_by_market_and_time(capacity_market, self.reps.current_tick)
        clearing_price, total_supply_volume, = self.capacity_subscription_clearing(sorted_ppdp, capacity_market, capacity_market_year)
        accepted_ppdp = self.reps.get_accepted_CM_bids(self.reps.current_tick)

        for accepted in accepted_ppdp:
            amount = accepted.accepted_amount * clearing_price
            self.reps.dbrw.stage_CM_revenues(accepted.plant, amount, self.reps.current_tick + capacity_market.forward_years_CM)
            self.reps.dbrw.stage_bids_status(accepted)

        self.reps.create_or_update_market_clearing_point(capacity_market, clearing_price, total_supply_volume,
                                                         self.reps.current_tick)

        print("Cleared market", capacity_market.name, "at ", str(clearing_price))

    def capacity_subscription_clearing(self, sorted_supply, capacity_market, capacity_market_year):
        expectedDemandFactor = self.reps.substances["electricity"].get_price_for_tick(self.reps, capacity_market_year, True)
        peak_load = self.reps.get_peak_future_demand_by_year(capacity_market_year)
        peakExpectedDemand = peak_load * (expectedDemandFactor)
        load_shedders = self.reps.get_load_shedders_by_time( self.reps.current_tick)
        for ls in load_shedders:
            ls.price = ls.VOLL*ls.reliability_standard
        sorted_demand = sorted(load_shedders, key=lambda x: x.price, reverse=True)

        total = 0
        for i , demand in enumerate(sorted_demand):
            total += demand.percentageLoad * peakExpectedDemand
            print(str(demand.price)+ ";"+ str(  demand.percentageLoad * peakExpectedDemand))
            demand.cummulative_quantity = total

        print("peak load " + str(peakExpectedDemand))
        clearing_price = 0
        total_supply_volume = 0

        demandCurve = DemandCurve(capacity_market.PriceCap, sorted_demand)
        cummulative_supply = 0
        for ppdp in sorted_supply:
                # As long as the market is not cleared
                cummulative_supply = ppdp.amount + cummulative_supply
                price_at_volume = demandCurve.get_price_at_volume(cummulative_supply)
                if ppdp.price <= price_at_volume:
                    total_supply_volume += ppdp.amount
                    clearing_price = price_at_volume
                    ppdp.status = globalNames.power_plant_dispatch_plan_status_accepted
                else:
                    print("clearing price ", clearing_price)
                    print("total_supply", total_supply_volume)
                    break
        return  clearing_price, total_supply_volume

