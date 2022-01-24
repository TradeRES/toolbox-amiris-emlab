from conftest import *
from domain.actors import *


class TestRepository:

    def test_get_power_plants_by_owner(self, reps):
        assert reps.get_operational_power_plants_by_owner(reps.energy_producers['FIRM1']) == \
               [reps.power_plants['PLANT1'], reps.power_plants['PLANT3']]

    def test_create_power_plant_dispatch_plan(self, reps, mocker):
        spy = mocker.spy(reps.dbrw, 'stage_power_plant_dispatch_plan')

        previous_size = len(reps.power_plant_dispatch_plans.keys())
        reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp"),
                                                        EnergyProducer("newbidder"),
                                                        ElectricitySpotMarket("newesm"),
                                                        10, 20, 0)
        assert len(reps.power_plant_dispatch_plans.keys()) == previous_size + 1
        assert reps.power_plant_dispatch_plans[sorted(reps.power_plant_dispatch_plans.keys())[0]].plant.name == 'newpp'
        assert spy.call_count == 1

    def test_get_sorted_dispatch_plans_by_market(self, reps: Repository):
        esm = reps.electricity_spot_markets['DutchElectricitySpotMarket']
        ppdp1 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp1"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 10, 0)
        ppdp2 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp2"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 20, 0)
        ppdp3 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp3"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 30, 0)
        ppdp4 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp4"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 5, 0)
        ppdp5 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp5"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 60, 0)
        assert reps.get_sorted_power_plant_dispatch_plans_by_market_and_time(esm, 0) == [ppdp4, ppdp1, ppdp2, ppdp3, ppdp5]

    def test_create_market_clearing_point(self, reps: Repository, mocker):
        spy = mocker.spy(reps.dbrw, 'stage_market_clearing_point')
        previous_size = len(reps.market_clearing_points)
        reps.create_or_update_market_clearing_point(ElectricitySpotMarket("newmarket"),
                                                    10, 20, 0)
        assert len(reps.market_clearing_points) == previous_size + 1
        assert reps.market_clearing_points[sorted(reps.market_clearing_points.keys())[0]].market.name == 'newmarket'
        assert spy.call_count == 1

    def test_get_available_power_plant_capacity_at_tick(self, reps: Repository):
        plant = reps.power_plants['PLANT1']
        market = reps.electricity_spot_markets['DutchElectricitySpotMarket']
        reps.create_or_update_power_plant_dispatch_plan(plant, plant.owner, market, 100, 1, 0)
        reps.create_or_update_power_plant_dispatch_plan(plant, plant.owner, market, 20, 1, 0)
        reps.create_or_update_power_plant_dispatch_plan(plant, plant.owner, market, 300, 1, 1)

        # Accept all plans
        for ppdp in reps.power_plant_dispatch_plans.values():
            ppdp.status = reps.power_plant_dispatch_plan_status_accepted
            ppdp.accepted_amount = ppdp.amount

        assert reps.get_available_power_plant_capacity_at_tick(plant, 0) == plant.capacity - 20
        assert reps.get_available_power_plant_capacity_at_tick(plant, 1) == plant.capacity - 300

    def test_get_power_plant_dispatch_plans_by_plant(self, reps: Repository):
        plant = PowerPlant("new plant test 1")
        ppdp1 = PowerPlantDispatchPlan('ppdp1')
        ppdp2 = PowerPlantDispatchPlan('ppdp2')
        ppdp1.plant = plant
        ppdp2.plant = plant
        reps.power_plant_dispatch_plans[ppdp1.name] = ppdp1
        reps.power_plant_dispatch_plans[ppdp2.name] = ppdp2
        assert reps.get_power_plant_dispatch_plans_by_plant(plant) == [ppdp1, ppdp2]

    def test_get_power_plant_dispatch_plans_by_plant_and_tick(self, reps: Repository):
        plant = PowerPlant("new plant test 1")
        ppdp1 = PowerPlantDispatchPlan('ppdp1')
        ppdp2 = PowerPlantDispatchPlan('ppdp2')
        ppdp1.plant = plant
        ppdp2.plant = plant
        reps.power_plant_dispatch_plans[ppdp1.name] = ppdp1
        reps.power_plant_dispatch_plans[ppdp2.name] = ppdp2
        ppdp1.tick = 20
        ppdp2.tick = 21
        assert reps.get_power_plant_dispatch_plans_by_plant_and_tick(plant, 20) == [ppdp1]
        assert reps.get_power_plant_dispatch_plans_by_plant_and_tick(plant, 21) == [ppdp2]

    def test_set_power_plant_dispatch_plan_production(self, reps: Repository, mocker):
        spy = mocker.spy(reps.dbrw, 'stage_power_plant_dispatch_plan')
        ppdp = PowerPlantDispatchPlan("newppdp")
        ppdp.plant = PowerPlant("newplant")
        ppdp.bidding_market = ElectricitySpotMarket("newmarket")
        ppdp.price = 10
        ppdp.amount = 100
        ppdp.bidder = EnergyProducer("newproducer")
        reps.set_power_plant_dispatch_plan_production(ppdp, reps.power_plant_dispatch_plan_status_accepted, 100)

        assert ppdp.status == reps.power_plant_dispatch_plan_status_accepted
        assert ppdp.accepted_amount == 100
        assert spy.call_count == 1

    def test_get_electricity_spot_market_for_plant(self, reps: Repository):
        assert reps.get_electricity_spot_market_for_plant(reps.power_plants['PLANT1']) == \
               reps.electricity_spot_markets['DutchElectricitySpotMarket']

    def test_get_capacity_market_for_plant(self, reps: Repository):
        assert reps.get_capacity_market_for_plant(reps.power_plants['PLANT1']) == \
               reps.capacity_markets['DutchCapacityMarket']

    def test_get_substances_in_fuel_mix_by_plant(self, reps: Repository):
        assert reps.get_substances_in_fuel_mix_by_plant(reps.power_plants['PLANT1']) == \
               reps.power_plants_fuel_mix['9']

    def test_get_market_clearing_point_for_market_and_time(self, reps: Repository):
        market = ElectricitySpotMarket("testmarketforget")
        tick = 2019
        mcp1 = MarketClearingPoint("new")
        mcp1.market = market
        mcp1.tick = tick
        mcp1.price = 1234
        mcp3 = MarketClearingPoint("new3")
        reps.market_clearing_points[mcp1.name] = mcp1
        reps.market_clearing_points[mcp3.name] = mcp3
        assert reps.get_market_clearing_point_for_market_and_time(market, tick) == mcp1

    def test_get_market_clearing_point_price_for_market_and_time(self, reps: Repository):
        market = ElectricitySpotMarket("testmarketforget")
        tick = 2019
        mcp1 = MarketClearingPoint("new")
        mcp1.market = market
        mcp1.tick = tick
        mcp1.price = 1234
        mcp3 = MarketClearingPoint("new3")
        reps.market_clearing_points[mcp1.name] = mcp1
        reps.market_clearing_points[mcp3.name] = mcp3
        assert reps.get_market_clearing_point_price_for_market_and_time(market, tick) == 1234

    def test_get_national_government_by_zone(self, reps: Repository):
        assert reps.get_national_government_by_zone(reps.zones['NL']) == reps.national_governments['DutchGov']

    def test_get_government(self, reps: Repository):
        assert reps.get_government() == next(i for i in reps.governments.values())

    def test_get_power_plant_revenues_by_tick(self, reps: Repository):
        plant = PowerPlant("newplant")
        ppdp1 = PowerPlantDispatchPlan("ppdp1_for_revenues")
        ppdp2 = PowerPlantDispatchPlan("ppdp2_for_revenues")
        ppdp1.accepted_amount = 100
        ppdp1.price = 10
        ppdp1.plant = plant
        ppdp1.tick = 123
        ppdp2.accepted_amount = 200
        ppdp2.price = 5
        ppdp2.plant = plant
        ppdp2.tick = 123
        reps.power_plant_dispatch_plans[ppdp1.name] = ppdp1
        reps.power_plant_dispatch_plans[ppdp2.name] = ppdp2
        assert reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant, 123) == 100 * 10 + 200 * 5

    def test_get_total_accepted_amounts_by_power_plant_and_tick(self, reps: Repository):
        plant = PowerPlant("newplant")
        ppdp1 = PowerPlantDispatchPlan("ppdp1_for_revenues")
        ppdp2 = PowerPlantDispatchPlan("ppdp2_for_revenues")
        market1 = reps.electricity_spot_markets['DutchElectricitySpotMarket']
        ppdp1.accepted_amount = 100
        ppdp1.price = 10
        ppdp1.plant = plant
        ppdp1.bidding_market = market1
        ppdp1.tick = 123
        ppdp2.accepted_amount = 200
        ppdp2.price = 5
        ppdp2.plant = plant
        ppdp2.tick = 123
        ppdp2.bidding_market = market1
        reps.power_plant_dispatch_plans[ppdp1.name] = ppdp1
        reps.power_plant_dispatch_plans[ppdp2.name] = ppdp2
        assert reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(plant, 123, market1) == 100 + 200

    def test_get_power_plant_costs_by_tick(self, reps: Repository):
        market1 = reps.electricity_spot_markets['DutchElectricitySpotMarket']
        mc = 1 * 12.78 / 0.35
        fixed_operating_cost = pow(1.05, 0 + 1 + 2) * 3850.4628350434846 * 18
        accepted_capacity = reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(
            reps.power_plants['PLANT1'], 0, market1)
        assert round(reps.get_power_plant_costs_by_tick_and_market(reps.power_plants['PLANT1'], 0, market1), 3) == \
               round(fixed_operating_cost + mc * accepted_capacity, 3)

    def test_get_power_plant_operationlal_profits_by_tick(self, reps: Repository):
        plant1 = reps.power_plants['PLANT1']
        plant2 = reps.power_plants['PLANT2']
        plant3 = reps.power_plants['PLANT3']

        market1 = reps.electricity_spot_markets['DutchElectricitySpotMarket']

        profit_plant1 = reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant1, 0) - \
                        plant1.calculate_marginal_cost_excl_co2_market_cost(reps, 0) * \
                        reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(plant1, 0, market1)
        profit_plant2 = reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant2, 0) - \
                        plant2.calculate_marginal_cost_excl_co2_market_cost(reps, 0) * \
                        reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(plant2, 0, market1)
        profit_plant3 = reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant3, 0) - \
                        plant3.calculate_marginal_cost_excl_co2_market_cost(reps, 0) * \
                        reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(plant3, 0, market1)

        assert {k: v for (k, v) in reps.get_power_plant_operational_profits_by_tick_and_market(0, market1).items()
                if k == plant1.name or k == plant2.name or k == plant3.name} == \
               {plant1.name: profit_plant1,
                plant2.name: profit_plant2,
                plant3.name: profit_plant3}

    def test_get_power_plant_emissions_by_tick(self, reps: Repository):
        plant1 = reps.power_plants['PLANT1']
        plant2 = reps.power_plants['PLANT2']
        plant3 = reps.power_plants['PLANT3']

        market1 = reps.electricity_spot_markets['DutchElectricitySpotMarket']

        emission1 = reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(plant1, 0, market1) * \
                    plant1.calculate_emission_intensity(reps)
        emission2 = reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(plant2, 0, market1) * \
                    plant2.calculate_emission_intensity(reps)
        emission3 = reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(plant3, 0, market1) * \
                    plant3.calculate_emission_intensity(reps)

        assert {k: v for (k, v) in reps.get_power_plant_emissions_by_tick(0).items()
                if k == plant1.name or k == plant2.name or k == plant3.name} == {
            plant1.name: emission1,
            plant2.name: emission2,
            plant3.name: emission3
        }

    def test_get_power_plant_dispatch_plan_price_by_plant_and_time_and_market(self, reps: Repository):
        ppdp1 = PowerPlantDispatchPlan('newppdp1_for_plant1')
        ppdp1.plant = reps.power_plants['PLANT1']
        ppdp1.price = 100
        ppdp1.bidding_market = reps.electricity_spot_markets['DutchElectricitySpotMarket']
        ppdp1.tick = 10
        reps.power_plant_dispatch_plans['newppdp1_for_plant1'] = ppdp1
        assert reps.get_power_plant_dispatch_plan_price_by_plant_and_time_and_market(
            reps.power_plants['PLANT1'], 10, reps.electricity_spot_markets['DutchElectricitySpotMarket']) == 100

    def test_get_power_plant_dispatch_plan_price_by_plant_and_time_and_market_none(self, reps: Repository):
        assert reps.get_power_plant_dispatch_plan_price_by_plant_and_time_and_market(
            PowerPlant('nonexistent'), 0, Market('NonExistent')) == 0

    def test_get_electricity_spot_market_for_plant_none(self, reps: Repository):
        pp = PowerPlant('nonexistent')
        pp.location = Zone('nonexistent')
        pp.location.parameters['Country'] = 'nonexistent'
        assert reps.get_electricity_spot_market_for_plant(pp) is None

    def test_get_capacity_market_for_plant_none(self, reps: Repository):
        pp = PowerPlant('nonexistent')
        pp.location = Zone('nonexistent')
        pp.location.parameters['Country'] = 'nonexistent'
        assert reps.get_capacity_market_for_plant(pp) is None

    def test_get_allowances_in_circulation(self, reps: Repository):
        assert reps.get_allowances_in_circulation(reps.zones['NL'], 10) == 0
        reps.power_plants['PLANT1'].banked_allowances[10] = 100
        reps.power_plants['PLANT2'].banked_allowances[10] = 550
        assert reps.get_allowances_in_circulation(reps.zones['NL'], 10) == 650

    def test_get_co2_market_for_zone(self, reps: Repository):
        assert reps.get_co2_market_for_zone(reps.zones['NL']) == reps.co2_markets['CO2Auction']

    def test_get_co2_market_for_zone_none(self, reps: Repository):
        assert reps.get_co2_market_for_zone(Zone('nonexistent')) is None

    def test_get_co2_market_for_plant(self, reps: Repository):
        assert reps.get_co2_market_for_plant(reps.power_plants['PLANT1']) == reps.co2_markets['CO2Auction']

    def test_get_market_stability_reserve_for_market(self, reps: Repository):
        assert reps.get_market_stability_reserve_for_market(
            reps.electricity_spot_markets['DutchElectricitySpotMarket']) == \
               reps.market_stability_reserves['MarketStabilityReserve']

    def test_get_market_stability_reserve_for_market_none(self, reps: Repository):
        market1 = Market('nonexistent')
        market1.parameters['zone'] = 'nonexistent'
        assert reps.get_market_stability_reserve_for_market(market1) is None

    def test_get_substances_in_fuel_mix_by_plant_none(self, reps: Repository):
        plant = PowerPlant('nonexistent')
        plant.technology = PowerGeneratingTechnology('nonexistent')
        assert reps.get_substances_in_fuel_mix_by_plant(plant) is None

    def test_get_market_clearing_point_for_market_and_time_none(self, reps: Repository):
        assert reps.get_market_clearing_point_for_market_and_time(Market('nonexistnet'), 10) is None

    def test_get_market_clearing_point_price_for_market_and_time_none(self, reps: Repository):
        assert reps.get_market_clearing_point_price_for_market_and_time(Market('nonexistent'), -1) == 0

    def test_get_power_generating_technology_by_techtype_and_fuel_none(self, reps: Repository):
        assert reps.get_power_generating_technology_by_techtype_and_fuel('nonexistent', 'nonexistent') is None

    def test_get_power_grid_node_by_zone(self, reps: Repository):
        assert reps.get_power_grid_node_by_zone('NL') == reps.power_grid_nodes['NED']

    def test_get_power_grid_node_by_zone_none(self, reps: Repository):
        assert reps.get_power_grid_node_by_zone('nonexistent') is None

    def test_get_hourly_demand_by_power_grid_node_and_year(self, reps: Repository):
        assert list(reps.get_hourly_demand_by_power_grid_node_and_year(reps.power_grid_nodes['NED'], 2020)) == \
               list(reps.load['NED'].get_hourly_demand_by_year(2020).values())

    def test_to_string(self, reps: Repository):
        assert reps.__str__().strip() == str(vars(reps)).strip()

    def test_to_repr(self, reps: Repository):
        assert reps.__repr__().strip() == str(vars(reps)).strip()