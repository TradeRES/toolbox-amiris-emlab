"""
All operations for the Electricity Spot Market
Based on the role ClearIterativeCO2AndElectricitySpotMarketTwoCountryRole

Jim Hommes - 25-3-2021
"""
import json
from modules.marketmodule import MarketModule
from util.repository import Repository


class ElectricitySpotMarketSubmitBids(MarketModule):
    """
    The class that submits all bids to the Electricity Spot Market.
    """

    def __init__(self, reps: Repository):
        super().__init__('COMPETES Dummy: Electricity Spot Market: Submit Bids', reps)
        reps.dbrw.stage_init_power_plant_dispatch_plan_structure()

    def act(self):
        # For every energy producer we will submit bids to the Capacity Market
        for energy_producer in self.reps.energy_producers.values():

            # For every plant owned by energyProducer
            for powerplant in self.reps.get_operational_power_plants_by_owner(energy_producer):
                market = self.reps.get_electricity_spot_market_for_plant(powerplant)
                capacity = powerplant.get_actual_nominal_capacity()
                mc = powerplant.calculate_marginal_cost_excl_co2_market_cost(self.reps,
                                                                             self.reps.current_tick)
                self.reps.create_or_update_power_plant_dispatch_plan(powerplant, energy_producer, market, capacity, mc,
                                                                     self.reps.current_tick)


class ElectricitySpotMarketClearing(MarketModule):
    """
    The class that clears the Electricity Spot Market.
    """

    def __init__(self, reps: Repository):
        super().__init__('COMPETES Dummy: Electricity Spot Market: Clear Market', reps)
        reps.dbrw.stage_init_market_clearing_point_structure()

    def act(self):
        # Calculate and submit Market Clearing Price
        peak_load = max(json.loads(self.reps.load['NL'].parameters['ldc'].to_database())['data'].values())
        for market in self.reps.electricity_spot_markets.values():
            sorted_ppdp = self.reps.get_sorted_power_plant_dispatch_plans_by_market_and_time(market, self.reps.current_tick)
            clearing_price = 0
            total_load = 0
            for ppdp in sorted_ppdp:
                if total_load + ppdp.amount <= peak_load:
                    total_load += ppdp.amount
                    clearing_price = ppdp.price
                    self.reps.set_power_plant_dispatch_plan_production(
                        ppdp, self.reps.power_plant_dispatch_plan_status_accepted, ppdp.amount)
                elif total_load < peak_load:
                    clearing_price = ppdp.price
                    self.reps.set_power_plant_dispatch_plan_production(
                        ppdp, self.reps.power_plant_dispatch_plan_status_partly_accepted, peak_load - total_load)
                    total_load = peak_load
                else:
                    self.reps.set_power_plant_dispatch_plan_production(
                        ppdp, self.reps.power_plant_dispatch_plan_status_failed, 0)

            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_load, self.reps.current_tick)
