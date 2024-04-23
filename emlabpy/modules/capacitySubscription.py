
from modules.marketmodule import MarketModule
from util.repository import Repository
from util import globalNames


class DemandCurve:
    """
    The SlopingDemandCurve as required in the CapacityMarket.
    """

    def __init__(self, price_cap, sorted_demand):
        self.price_cap = price_cap
        self.sorted_demand = sorted_demand

    def get_demand_price_at_volume(self, cummulative_supply, supply):
        price = self.price_cap
        # print("-----------------------------------" + str(cummulative_supply))
        for demand in self.sorted_demand:
            last_capacity = cummulative_supply - supply.amount
            if demand.cummulative_quantity >= cummulative_supply:
                price = demand.bid
                break
            else:
                # demand quantity is still less than supply quantity but the price is
                if demand.bid < supply.price and demand.cummulative_quantity >= last_capacity:
                    price = demand.bid
                    break
                # if there is no demand, take the last price
                price = demand.bid
        return price


class CapacitySubscriptionClearing(MarketModule):
    """
    After a capacity market has been cleared, the accepted bids are cleared and the revenues are staged.
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Capacity Subscription: Clear Market', reps)
        reps.dbrw.stage_init_capacitymechanisms_structure()
        self.agent = reps.energy_producers[reps.agent]

    def act(self):
        print("capacity subscription clearing")
        capacity_market = self.reps.get_capacity_market_in_country(self.reps.country, False)
        capacity_market_year = self.reps.current_year + capacity_market.forward_years_CM
        sorted_ppdp = self.reps.get_sorted_bids_by_market_and_time(capacity_market, self.reps.current_tick)
        clearing_price, total_supply_volume,total_subscribed_volume = self.capacity_subscription_clearing(sorted_ppdp, capacity_market,
                                                                                   capacity_market_year)
        accepted_supply_bid = self.reps.get_accepted_CM_bids(self.reps.current_tick)
        print("--------------------accepted_supply_bid-------------------")
        for accepted in accepted_supply_bid:
            amount = accepted.accepted_amount * clearing_price
            self.reps.dbrw.stage_CM_revenues(accepted.plant, amount,
                                             [self.reps.current_tick + capacity_market.forward_years_CM])

        self.reps.create_or_update_market_clearing_point(capacity_market, clearing_price, total_supply_volume,
                                                         self.reps.current_tick + capacity_market.forward_years_CM)

        print("Cleared market", capacity_market.name, "at ", str(clearing_price))

    def capacity_subscription_clearing(self, sorted_supply, capacity_market, capacity_market_year):
        expectedDemandFactor = self.reps.substances["electricity"].get_price_for_tick(self.reps, capacity_market_year,
                                                                                      True)
        peak_load = self.reps.get_peak_future_demand_by_year(capacity_market_year)
        expensive_load_peak =  peak_load * expectedDemandFactor *( self.reps.get_percentage_load_LS("1") + self.reps.get_percentage_load_LS("2"))
        sorted_consumers = self.reps.get_CS_subscribed_consumers_descending_bid()

        total_subscribed_volume = 0
        print("consumer;cummulative_bids;bid")
        for i, consumer in enumerate(sorted_consumers):
            total_subscribed_volume += consumer.subscribed_yearly[self.reps.current_tick] * expensive_load_peak
            consumer.cummulative_quantity = total_subscribed_volume
            print(consumer.name +";"+ str(total_subscribed_volume) + ";" + str(consumer.bid))

        clearing_price = 0
        total_supply_volume = 0

        demandCurve = DemandCurve(sorted_consumers[0].WTP, sorted_consumers) # price cap is set as the WTP of the most expensive consumer
        cummulative_supply = 0
        for supply_bid in sorted_supply:
            # As long as the market is not cleared
            cummulative_supply = supply_bid.amount + cummulative_supply
            demand_price = demandCurve.get_demand_price_at_volume(cummulative_supply, supply_bid)

            if supply_bid.price < demand_price and total_supply_volume < total_subscribed_volume:
                total_supply_volume += supply_bid.amount
                supply_bid.accepted_amount = supply_bid.amount
                supply_bid.status = globalNames.power_plant_dispatch_plan_status_accepted
                clearing_price = demand_price
            else:
                #  total_supply_volume += supply_bid.amount
                clearing_price = demand_price  # price set by demand
                supply_bid.status = globalNames.power_plant_dispatch_plan_status_failed
                supply_bid.accepted_amount = 0
                print("clearing_price", clearing_price)
                print("total_supply_volume", total_supply_volume)
                break

        # from plots.testclearmarket import plot_CS_market
        # plot_CS_market(sorted_supply, sorted_demand, clearing_price, total_supply_volume)
        return clearing_price, total_supply_volume, total_subscribed_volume
