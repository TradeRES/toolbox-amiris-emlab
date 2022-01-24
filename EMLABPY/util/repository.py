"""
The Repository: home of all objects that play a part in the model.
All objects are read through the SpineDBReader and stored in the Repository.

Jim Hommes - 25-3-2021
"""
from datetime import datetime
from typing import Optional, Dict, List

from domain.actors import *
from domain.energy import *
from domain.markets import *
from domain.trends import *
from domain.zones import *


class Repository:
    """
    The Repository class reads DB data at initialization and loads all objects and relationships
    Also provides all functions that require e.g. sorting
    """

    def __init__(self):
        """
        Initialize all Repository variables
        """
        self.dbrw = None

        self.current_tick = 0
        self.time_step = 0
        self.start_simulation_year = 0

        self.energy_producers = dict()
        self.power_plants = dict()
        self.substances = dict()
        self.power_plants_fuel_mix = dict()
        self.electricity_spot_markets = dict()
        self.capacity_markets = dict()
        self.co2_markets = dict()
        self.power_plant_dispatch_plans = dict()
        self.power_generating_technologies = dict()
        self.market_clearing_points = dict()
        self.power_grid_nodes = dict()
        self.trends = dict()
        self.zones = dict()
        self.national_governments = dict()
        self.governments = dict()
        self.market_stability_reserves = dict()

        self.load = dict()
        self.emissions = dict()

        self.exports = dict()

        self.power_plant_dispatch_plan_status_accepted = 'Accepted'
        self.power_plant_dispatch_plan_status_failed = 'Failed'
        self.power_plant_dispatch_plan_status_partly_accepted = 'Partly Accepted'
        self.power_plant_dispatch_plan_status_awaiting = 'Awaiting'

        self.power_plant_status_operational = 'OPR'

    """
    Repository functions:
    All functions to get/create/set/update elements and values, possibly under criteria. Sorted on elements.
    """

    # PowerPlants
    def get_operational_power_plants_by_owner(self, owner: EnergyProducer) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.owner == owner and i.status == self.power_plant_status_operational]

    def get_available_power_plant_capacity_at_tick(self, plant: PowerPlant, current_tick: int) -> float:
        ppdps_sum_accepted_amount = sum([float(i.accepted_amount) for i in
                                         self.get_power_plant_dispatch_plans_by_plant(plant)
                                         if i.tick == current_tick])
        return plant.capacity - ppdps_sum_accepted_amount

    def get_power_plant_electricity_spot_market_revenues_by_tick(self, power_plant: PowerPlant, time: int) -> float:
        # Accepted Amount is in MW
        # MCP Price is in Euro / MWh
        return sum([float(i.accepted_amount * i.price)
                    for i in self.get_power_plant_dispatch_plans_by_plant_and_tick(power_plant, time)])

    def get_total_accepted_amounts_by_power_plant_and_tick_and_market(self, power_plant: PowerPlant, time: int, market: Market) -> float:
        return sum([i.accepted_amount for i in self.power_plant_dispatch_plans.values() if i.tick == time and
                    i.plant == power_plant and i.bidding_market == market])

    def get_power_plant_costs_by_tick_and_market(self, power_plant: PowerPlant, time: int, market: Market) -> float:
        # MC is Euro / MW
        mc = power_plant.calculate_marginal_cost_excl_co2_market_cost(self, time)
        # FOC is Euro
        foc = power_plant.get_actual_fixed_operating_cost()
        # total capacity is in MWh
        total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant, time, market)
        return foc + mc * total_capacity

    def get_power_plant_operational_profits_by_tick_and_market(self, time: int, market: Market) -> Dict[str, float]:
        res = {}
        for power_plant in [i for i in self.power_plants.values() if i.status == self.power_plant_status_operational]:
            revenues = self.get_power_plant_electricity_spot_market_revenues_by_tick(power_plant, time)
            mc = power_plant.calculate_marginal_cost_excl_co2_market_cost(self, time)
            total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant, time, market)
            res[power_plant.name] = revenues - mc * total_capacity
        return res

    def get_power_plant_emissions_by_tick(self, time: int) -> Dict[str, float]:
        if 'YearlyEmissions' in self.emissions.keys():
            res = self.emissions['YearlyEmissions'].emissions[time]
        else:
            res = {}
        for power_plant in [i for i in self.power_plants.values() if i.status == self.power_plant_status_operational and i.name not in res.keys()]:
            # Total Capacity is in MWh
            total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant, time,
                                                                                                self.electricity_spot_markets['DutchElectricitySpotMarket'])
            # Emission intensity is in ton CO2 / MWh
            emission_intensity = power_plant.calculate_emission_intensity(self)
            res[power_plant.name] = total_capacity * emission_intensity
        return res

    # PowerPlantDispatchPlans
    def get_power_plant_dispatch_plan_price_by_plant_and_time_and_market(self, plant: PowerPlant, time: int,
                                                                         market: Market) -> float:
        try:
            return next(i.price for i in self.power_plant_dispatch_plans.values() if i.plant == plant and i.tick == time
                        and i.bidding_market == market)
        except StopIteration:
            logging.warning('No PPDP Price found for plant ' + plant.name + ' and at time ' + str(time))
            return 0

    def get_sorted_power_plant_dispatch_plans_by_market_and_time(self, market: Market, time: int) -> \
            List[PowerPlantDispatchPlan]:
        return sorted([i for i in self.power_plant_dispatch_plans.values()
                       if i.bidding_market == market and i.tick == time], key=lambda i: i.price)

    def get_power_plant_dispatch_plans_by_plant(self, plant: PowerPlant) -> List[PowerPlantDispatchPlan]:
        return [i for i in self.power_plant_dispatch_plans.values() if i.plant == plant]

    def get_power_plant_dispatch_plans_by_plant_and_tick(self, plant: PowerPlant, time: int) -> \
            List[PowerPlantDispatchPlan]:
        return [i for i in self.power_plant_dispatch_plans.values() if i.plant == plant and i.tick == time]

    def set_power_plant_dispatch_plan_production(self,
                                                 ppdp: PowerPlantDispatchPlan,
                                                 status: str, accepted_amount: float):
        ppdp.status = status
        ppdp.accepted_amount = accepted_amount
        self.dbrw.stage_power_plant_dispatch_plan(ppdp, self.current_tick)

    def create_or_update_power_plant_dispatch_plan(self, plant: PowerPlant,
                                                   bidder: EnergyProducer,
                                                   bidding_market: Market,
                                                   amount: float,
                                                   price: float,
                                                   time: int) -> PowerPlantDispatchPlan:
        ppdp = next((ppdp for ppdp in self.power_plant_dispatch_plans.values() if ppdp.plant == plant and
                     ppdp.bidding_market == bidding_market and
                     ppdp.tick == time), None)
        if ppdp is None:
            # PowerPlantDispatchPlan not found, so create a new one
            name = 'PowerPlantDispatchPlan ' + str(datetime.now())
            ppdp = PowerPlantDispatchPlan(name)

        ppdp.plant = plant
        ppdp.bidder = bidder
        ppdp.bidding_market = bidding_market
        ppdp.amount = amount
        ppdp.price = price
        ppdp.status = self.power_plant_dispatch_plan_status_awaiting
        ppdp.accepted_amount = 0
        ppdp.tick = time

        self.power_plant_dispatch_plans[ppdp.name] = ppdp
        self.dbrw.stage_power_plant_dispatch_plan(ppdp, time)
        return ppdp

    # Markets
    def get_electricity_spot_market_for_plant(self, plant: PowerPlant) -> Optional[ElectricitySpotMarket]:
        try:
            return next(i for i in self.electricity_spot_markets.values() if
                        i.parameters['zone'] == plant.location.parameters['Country'])
        except StopIteration:
            return None

    def get_capacity_market_for_plant(self, plant: PowerPlant) -> Optional[CapacityMarket]:
        try:
            return next(i for i in self.capacity_markets.values() if
                        i.parameters['zone'] == plant.location.parameters['Country'])
        except StopIteration:
            return None

    def get_allowances_in_circulation(self, zone: Zone, time: int) -> int:
        return sum([i.banked_allowances[time] for i in self.power_plants.values()
                    if i.location.parameters['Country'] == zone.name])

    def get_co2_market_for_zone(self, zone: Zone) -> Optional[CO2Market]:
        try:
            return next(i for i in self.co2_markets.values()
                        if i.parameters['zone'] == zone.name)
        except StopIteration:
            return None

    def get_co2_market_for_plant(self, power_plant: PowerPlant) -> Optional[CO2Market]:
        return self.get_co2_market_for_zone(self.zones[power_plant.location.parameters['Country']])

    def get_market_stability_reserve_for_market(self, market: Market) -> Optional[MarketStabilityReserve]:
        try:
            return next(i for i in self.market_stability_reserves.values()
                        if i.zone.name == market.parameters['zone'])
        except StopIteration:
            return None

    # SubstanceInFuelMix
    def get_substances_in_fuel_mix_by_plant(self, plant: PowerPlant) -> Optional[SubstanceInFuelMix]:
        if plant.technology.name in self.power_plants_fuel_mix.keys():
            return self.power_plants_fuel_mix[plant.technology.name]
        else:
            return None

    # MarketClearingPoints
    def get_market_clearing_point_for_market_and_time(self, market: Market, time: int) -> Optional[MarketClearingPoint]:
        try:
            return next(i for i in self.market_clearing_points.values() if i.market == market and i.tick == time)
        except StopIteration:
            return None

    def get_market_clearing_point_price_for_market_and_time(self, market: Market, time: int) -> float:
        if time >= 0:
            mcp = self.get_market_clearing_point_for_market_and_time(market, time)
            return mcp.price
        else:
            return 0

    def create_or_update_market_clearing_point(self,
                                               market: Market,
                                               price: float,
                                               capacity: float,
                                               time: int) -> MarketClearingPoint:
        mcp = next((mcp for mcp in self.market_clearing_points.values() if mcp.market == market and mcp.tick == time),
                   None)
        if mcp is None:
            # MarketClearingPoint not found, so create a new one
            name = 'MarketClearingPoint ' + str(datetime.now())
            mcp = MarketClearingPoint(name)

        mcp.market = market
        mcp.price = price
        mcp.capacity = capacity
        mcp.tick = time
        self.market_clearing_points[mcp.name] = mcp
        self.dbrw.stage_market_clearing_point(mcp, time)
        return mcp

    # Governments
    def get_national_government_by_zone(self, zone: Zone) -> NationalGovernment:
        return next(i for i in self.national_governments.values() if i.governed_zone == zone)

    def get_government(self) -> Government:
        return next(i for i in self.governments.values())

    # PowerGeneratingTechnologies
    def get_power_generating_technology_by_techtype_and_fuel(self, techtype: str, fuel: str):
        try:
            return next(i for i in self.power_generating_technologies.values()
                        if i.techtype == techtype and i.fuel == fuel)
        except StopIteration:
            logging.warning('PowerGeneratingTechnology not found for ' + techtype + ' and ' + fuel)
            return None

    # PowerGridNode
    def get_power_grid_node_by_zone(self, zone: str):
        try:
            return next(i for i in self.power_grid_nodes.values() if i.parameters['Country'] == zone)
        except StopIteration:
            return None

    # Hourly Demand
    def get_hourly_demand_by_power_grid_node_and_year(self, node: PowerGridNode, year: int):
        year_to_lookup = 5 * round(float(year / 5))
        return self.load[node.name].get_hourly_demand_by_year(year_to_lookup).values()

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))
