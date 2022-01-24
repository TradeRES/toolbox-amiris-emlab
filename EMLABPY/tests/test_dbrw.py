"""
This file tests the SpineDBReaderWriter class.
This means that the tests either check whether elements have been written or read correctly

Jim Hommes - 26-4-2021
"""
from conftest import *


class TestDBRW:

    def test_init(self, dbrw):
        assert isinstance(dbrw.db, SpineDB)
        assert dbrw.db_url == 'sqlite:///' + path_to_current_emlab_spinedb

    def test_read_db_and_create_repository(self, dbrw):
        reps = dbrw.read_db_and_create_repository()

        # PowerPlants
        pp = reps.power_plants['PLANT1']
        assert pp.technology == reps.power_generating_technologies['9']
        assert pp.location == reps.power_grid_nodes['NED']
        assert pp.owner == reps.energy_producers['FIRM1']
        assert pp.capacity == 18
        assert pp.efficiency == 0.35
        assert len(reps.power_plants.values()) == 18  # Check total number
        assert reps.power_plants['PLANT3'].age == 46  # Random check

        # TriangularTrends
        tt = reps.trends['biomassTrend']
        assert tt.top == 1.01
        assert tt.max == 1.05
        assert tt.min == 0.97
        assert tt.values == [28.8]
        assert len(reps.trends.values()) == 50  # Check total number (Triangular + Step + Geo)
        assert reps.trends['fuelOilTrend'].max == 1.04  # Random

        # Substances
        ss = reps.substances['Natural Gas']
        assert ss.co2_density == 0.20448
        assert ss.energy_density == 36
        assert ss.quality == 1
        assert ss.trend == reps.trends['naturalGasTrend']
        assert len(reps.substances.values()) == 17
        assert reps.substances['Derived Gas'].co2_density == 0.20448

        # PowerGridNodes
        pgn = reps.power_grid_nodes['NED']
        assert pgn.parameters['Country'] == 'NL'

        # ElectricitySpotMarkets
        esm = reps.electricity_spot_markets['DutchElectricitySpotMarket']
        assert esm.parameters['valueOfLostLoad'] == 2000
        assert esm.parameters['referencePrice'] == 40
        assert not bool(esm.parameters['isAuction'])
        assert esm.parameters['substance'] == 'electricity'
        assert esm.parameters['growthTrend'] == 'demandGrowthTrendNL'

        # CapacityMarkets
        cm = reps.capacity_markets['DutchCapacityMarket']
        assert cm.parameters['InstalledReserveMargin'] == 0.1
        assert cm.parameters['LowerMargin'] == 0.035
        assert cm.parameters['PriceCap'] == 75000
        assert cm.parameters['UpperMargin'] == 0.035
        assert cm.parameters['zone'] == 'NL'

        # CO2Auction
        co2auction = reps.co2_markets['CO2Auction']
        assert co2auction.parameters['referencePrice'] == 0

        # EnergyProducers
        ep = reps.energy_producers['FIRM1']
        assert ep.parameters['investorMarket'] == 'DutchElectricitySpotMarket'

        # StepTrends
        st = reps.trends['co2TaxTrend']
        assert st.duration == 1
        assert st.start == 0
        assert st.min_value == 0
        assert st.increment == 0

        # GeometricTrends
        gt = reps.trends['coalCHPFixedOperatingCostTimeSeries']
        assert gt.start == 24437.546793112055
        assert gt.growth_rate == 0.05

        # PowerGeneratingTechnologies
        pgt = reps.power_generating_technologies['9']
        assert pgt.peak_segment_dependent_availability == 1
        assert pgt.expected_permittime == 1
        assert pgt.expected_leadtime == 2
        assert pgt.expected_lifetime == 30
        assert pgt.fixed_operating_cost_time_series == reps.trends['gasGTFixedOperatingCostTimeSeries']

        # PowerGeneratingTechnologyFuel (SubstanceInFuelMix)
        sifm = reps.power_plants_fuel_mix['9']
        assert sifm.substances == [reps.substances['Natural Gas']]
        assert sifm.share == 1

    def test_db_relationships_to_arr(self, dbrw):
        output_arr = []
        add_relationship_to_repository_array(dbrw.db.export_data(), output_arr, 'TargetInvestorTargets')
        assert len(output_arr) == 2
        assert output_arr[0][0] == 'TargetInvestorNL'
        assert output_arr[0][1] == 'pvTarget'

    def test_stage_object_class(self, dbrw):
        importelement_testname = 'testclass'
        assert importelement_testname not in [i[0] for i in dbrw.db.export_data()['object_classes']]
        dbrw.stage_object_class(importelement_testname)
        assert importelement_testname in [i[0] for i in dbrw.db.export_data()['object_classes']]

    def test_stage_object_classes(self, dbrw):
        importelement_testname = 'testclass_array'
        assert importelement_testname not in [i[0] for i in dbrw.db.export_data()['object_classes']]
        dbrw.stage_object_classes([importelement_testname])
        assert importelement_testname in [i[0] for i in dbrw.db.export_data()['object_classes']]

    def test_stage_object_parameter(self, dbrw):
        importelement_testname = 'testobject_parameter'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['object_parameters']]
        dbrw.stage_object_parameter('testclass', importelement_testname)
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['object_parameters']]

    def test_stage_object_parameters(self, dbrw):
        importelement_testname = 'testobject_parameter_arr'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['object_parameters']]
        dbrw.stage_object_parameters('testclass', [importelement_testname])
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['object_parameters']]

    def test_stage_object(self, dbrw):
        importelement_testname = 'testobject'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['objects']]
        dbrw.stage_object('testclass', importelement_testname)
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['objects']]

    def test_stage_objects(self, dbrw):
        importelement_testname = 'testobject_arr'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['objects']]
        dbrw.stage_objects([('testclass', importelement_testname)])
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['objects']]

    def test_stage_object_parameter_values(self, dbrw):
        importelement_testname = 'testparametervalue'
        assert importelement_testname not in [i[3] for i in dbrw.db.export_data()['object_parameter_values']]
        dbrw.stage_object_parameter_values('testclass', 'testobject', [('testobject_parameter', importelement_testname)]
                                           , '0')
        assert importelement_testname in [i[3] for i in dbrw.db.export_data()['object_parameter_values']]

    def test_stage_init_market_clearing_point_structure(self, dbrw_fresh):
        assert dbrw_fresh.market_clearing_point_object_classname not in [i[0] for i in
                                                                         dbrw_fresh.db.export_data()['object_classes']]
        assert not all(x in [i[1] for i in dbrw_fresh.db.export_data()['object_parameters']] for x in
                       ['Market', 'Price', 'TotalCapacity'])
        dbrw_fresh.stage_init_market_clearing_point_structure()
        assert dbrw_fresh.market_clearing_point_object_classname in [i[0] for i in dbrw_fresh.db.export_data()['object_classes']]
        assert all(x in [i[1] for i in dbrw_fresh.db.export_data()['object_parameters']] for x in
                   ['Market', 'Price', 'TotalCapacity'])

    def test_stage_init_power_plant_dispatch_plan_structure(self, dbrw_fresh):
        assert dbrw_fresh.powerplant_dispatch_plan_classname not in [i[0] for i in dbrw_fresh.db.export_data()['object_classes']]
        assert not all(x in [i[1] for i in dbrw_fresh.db.export_data()['object_parameters']] for x in
                       ['Plant', 'Market', 'Price', 'Capacity', 'EnergyProducer', 'AcceptedAmount', 'Status'])
        dbrw_fresh.stage_init_power_plant_dispatch_plan_structure()
        assert dbrw_fresh.powerplant_dispatch_plan_classname in [i[0] for i in dbrw_fresh.db.export_data()['object_classes']]
        assert all(x in [i[1] for i in dbrw_fresh.db.export_data()['object_parameters']] for x in
                   ['Plant', 'Market', 'Price', 'Capacity', 'EnergyProducer', 'AcceptedAmount', 'Status'])

    def test_stage_power_plant_dispatch_plan(self, dbrw):
        importelement_testname = 'testppdp'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['object_parameter_values']
                                              if i[0] == dbrw.powerplant_dispatch_plan_classname]
        ppdp = PowerPlantDispatchPlan(importelement_testname)
        ppdp.plant = PowerPlant("testplant")
        ppdp.bidding_market = ElectricitySpotMarket("testmarket")
        ppdp.bidder = EnergyProducer("testbidder")
        dbrw.stage_power_plant_dispatch_plan(ppdp, '0')
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['object_parameter_values']
                                          if i[0] == dbrw.powerplant_dispatch_plan_classname]

    def test_stage_market_clearing_point(self, dbrw):
        importelement_testname = 'testmcp'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['object_parameter_values']
                                              if i[0] == dbrw.market_clearing_point_object_classname]
        mcp = MarketClearingPoint(importelement_testname)
        mcp.market = ElectricitySpotMarket('Testmarket')
        dbrw.stage_market_clearing_point(mcp, '0')
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['object_parameter_values']
                                              if i[0] == dbrw.market_clearing_point_object_classname]

    def test_stage_init_alternative(self, dbrw):
        importelement_testname = 'testalternative'
        assert importelement_testname not in [i[0] for i in dbrw.db.export_data()['alternatives']]
        dbrw.stage_init_alternative(importelement_testname)
        assert importelement_testname in [i[0] for i in dbrw.db.export_data()['alternatives']]
