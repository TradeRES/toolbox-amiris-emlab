"""
The file responsible for all capacity market operations.

Jim Hommes - 25-3-2021
"""
import json
from modules.marketmodule import MarketModule
from util.repository import Repository


class CapacityMarketSubmitBids(MarketModule):
    """
    The class that submits all bids to the Capacity Market
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Capacity Market: Submit Bids', reps)
        reps.dbrw.stage_init_power_plant_dispatch_plan_structure()

    def act(self):
        # For every EnergyProducer
        for energy_producer in self.reps.energy_producers.values():

            # For every PowerPlant owned by energyProducer
            for powerplant in self.reps.get_operational_power_plants_by_owner(energy_producer):
                # Retrieve vars
                market = self.reps.get_capacity_market_for_plant(powerplant)
                emarket = self.reps.get_electricity_spot_market_for_plant(powerplant)
                capacity = powerplant.get_actual_nominal_capacity()
                powerplant_load_factor = 1  # TODO: Power Plant Load Factor

                # Get Marginal Cost and Fixed Operating Costs
                mc = powerplant.calculate_marginal_cost_excl_co2_market_cost(self.reps, self.reps.current_tick)
                fixed_on_m_cost = powerplant.get_actual_fixed_operating_cost()

                # Determine revenues from ElectricitySpotMarket
                clearing_point_price = self.reps.get_power_plant_dispatch_plan_price_by_plant_and_time_and_market(
                    powerplant, self.reps.current_tick, emarket)
                planned_dispatch = self.reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(powerplant,
                                                                                                           self.reps.current_tick,
                                                                                                           emarket)
                expected_electricity_revenues = planned_dispatch * (clearing_point_price - mc)

                net_revenues = expected_electricity_revenues - fixed_on_m_cost
                price_to_bid = 0
                if powerplant.get_actual_nominal_capacity() > 0 and net_revenues <= 0:
                    price_to_bid = -1 * net_revenues / (powerplant.get_actual_nominal_capacity() *
                                                        powerplant.technology.peak_segment_dependent_availability)

                self.reps.create_or_update_power_plant_dispatch_plan(powerplant, energy_producer, market, capacity * powerplant.technology.peak_segment_dependent_availability,
                                                                         price_to_bid, self.reps.current_tick)


class CapacityMarketClearing(MarketModule):
    """
    The class that clears the Capacity Market based on the Sloping Demand curve
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Capacity Market: Clear Market', reps)

    def act(self):
        for market in self.reps.capacity_markets.values():
            node = self.reps.get_power_grid_node_by_zone(market.parameters['zone'])
            peak_load = max(
                self.reps.get_hourly_demand_by_power_grid_node_and_year(node, self.reps.current_tick +
                                                                        self.reps.start_simulation_year))

            # Retrieve vars
            sdc = market.get_sloping_demand_curve(peak_load)
            sorted_ppdp = self.reps.get_sorted_power_plant_dispatch_plans_by_market_and_time(market,
                                                                                             self.reps.current_tick)

            clearing_price = 0
            total_supply = 0

            # Set the clearing price through the merit order
            for ppdp in sorted_ppdp:
                if ppdp.price <= sdc.get_price_at_volume(total_supply + ppdp.amount):
                    total_supply += ppdp.amount
                    clearing_price = ppdp.price
                    self.reps.set_power_plant_dispatch_plan_production(
                        ppdp, self.reps.power_plant_dispatch_plan_status_accepted, ppdp.amount)
                elif ppdp.price < sdc.get_price_at_volume(total_supply):
                    clearing_price = ppdp.price
                    self.reps.set_power_plant_dispatch_plan_production(
                        ppdp, self.reps.power_plant_dispatch_plan_status_partly_accepted,
                        sdc.get_volume_at_price(clearing_price) - total_supply)
                    total_supply += sdc.get_volume_at_price(clearing_price)
                else:
                    self.reps.set_power_plant_dispatch_plan_production(
                        ppdp, self.reps.power_plant_dispatch_plan_status_failed, 0)

            print(clearing_price)
            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_supply,
                                                             self.reps.current_tick)
