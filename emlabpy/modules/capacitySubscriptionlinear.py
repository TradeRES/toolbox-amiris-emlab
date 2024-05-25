
from modules.marketmodule import MarketModule
from util.repository import Repository
from util import globalNames
import numpy as np

class DemandCurve:
    """
    The SlopingDemandCurve as required in the CapacityMarket.
    """

    def __init__(self, consumers_prices,consumers_volume):
        self.consumers_prices = consumers_prices
        self.consumers_volume = consumers_volume

    def get_demand_price(self, x) :
        # print("-----------------------------------" + str(cummulative_supply))
        left_index = np.searchsorted(self.consumers_volume, x, side='right') - 1
        # If x is smaller than the smallest consumer volume, return the corresponding y value

        if left_index == -1:
            return self.consumers_prices[0], False
        # If x is larger than the largest consumer volume, return the corresponding y value
        if left_index == len(self.consumers_volume) - 1:
            return self.consumers_prices[-1], True
        #  return y_values[-1]
        # Interpolate between the nearest x values
        x_left, x_right = self.consumers_volume[left_index], self.consumers_volume[left_index + 1]
        y_left, y_right = self.consumers_prices[left_index], self.consumers_prices[left_index + 1]
        slope = (y_right - y_left) / (x_right - x_left)
        return y_left + slope * (x - x_left), False


class CapacitySubscriptionClearingLinear(MarketModule):
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
        clearing_price, total_supply_volume = self.capacity_subscription_clearing(sorted_ppdp,
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

    def capacity_subscription_clearing(self, sorted_supply, capacity_market_year):
        expectedDemandFactor = self.reps.substances["electricity"].get_price_for_tick(self.reps, capacity_market_year,
                                                                                      True)
        peak_load = self.reps.get_peak_future_demand_by_year(capacity_market_year) * expectedDemandFactor
        sorted_consumers = self.reps.get_CS_subscribed_consumers_descending_bid()
        total_subscribed_volume = 0

        print("consumer;cummulative_bids;bid")
        consumers_prices = []
        consumers_volume = []
        for i, consumer in enumerate(sorted_consumers):
            total_subscribed_volume += consumer.subscribed_yearly[self.reps.current_tick] * peak_load
            consumer.cummulative_quantity = total_subscribed_volume
            print(consumer.name +";"+ str(total_subscribed_volume) + ";" + str(consumer.bid))
            consumers_prices.append(consumer.bid)
            consumers_volume.append(total_subscribed_volume)
        dc = DemandCurve( consumers_prices, consumers_volume  ) # price cap is set as the WTP of the most expensive consumer

        clearing_price = 0
        total_supply_volume = 0
        cummulative_supply = 0
        supply_volumes = []
        supply_prices = []
        # equilibriumprices = [] # todelete

        for num, supply_bid in enumerate(sorted_supply):
            # As long as the market is not cleared
            cummulative_supply = supply_bid.amount + cummulative_supply
            supply_volumes.append(cummulative_supply)
            supply_prices.append(supply_bid.price)
            demand_price , isnotlast = dc.get_demand_price(cummulative_supply)
            last_demand_price , is_last_demand = dc.get_demand_price( supply_volumes[num-1])

            if supply_bid.price <= demand_price: # not crossed line, price set by demand
                total_supply_volume += supply_bid.amount
                clearing_price =  demand_price
                supply_bid.accepted_amount = supply_bid.amount
                supply_bid.status = globalNames.power_plant_dispatch_plan_status_accepted

                if is_last_demand == True: # last demand, price set by supply
                    clearing_price = supply_bid.price
                    print("last demand and not crossed line, clearing price is last supply price")
                    break
                # equilibriumprices.append(clearing_price) # todelete

            elif supply_bid.price < last_demand_price: # crossed line, price set by supply
                clearing_price = supply_bid.price
                total_supply_volume += supply_bid.amount
                supply_bid.accepted_amount = supply_bid.amount
                supply_bid.status = globalNames.power_plant_dispatch_plan_status_accepted
                # equilibriumprices.append(clearing_price) # todelete
                break
            else: # crossed line from the beginning, clearing price is zero
                supply_bid.status = globalNames.power_plant_dispatch_plan_status_failed
                supply_bid.accepted_amount = 0
                break
        print("clearing_price", clearing_price)
        print("total_supply_volume", total_supply_volume)
        # from plots.test_linear_market import plot_CS_linear
        # plot_CS_linear( supply_volumes, supply_prices, consumers_volume, consumers_prices, clearing_price, total_supply_volume, equilibriumprices )
        return clearing_price, total_supply_volume
