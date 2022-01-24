from domain.energy import PowerPlant
from domain.energy import ImportObject
from util.repository import Repository


class TestPowerPlant:

    def test_get_load_factor_for_production(self, reps: Repository):
        pp1 = reps.power_plants['PLANT1']
        assert pp1.get_load_factor_for_production(pp1.capacity * 3.75) == 3.75

    def test_get_load_factor_for_production_zero(self):
        pp1 = PowerPlant('new')
        pp1.capacity = 0
        assert pp1.get_load_factor_for_production(100) == 0

    def test_calculate_emission_intensity(self, reps: Repository):
        pp1 = reps.power_plants['PLANT1']
        assert pp1.calculate_emission_intensity(reps) == 1 * 0.20448 / 0.35

    def test_get_actual_fixed_operating_cost(self, reps: Repository):
        pp1 = reps.power_plants['PLANT1']
        assert pp1.get_actual_fixed_operating_cost() == reps.power_generating_technologies['9']\
            .get_fixed_operating_cost(pp1.construction_start_time +
                                      int(pp1.technology.expected_leadtime) +
                                      int(pp1.technology.expected_permittime)) * pp1.capacity

    def test_get_actual_nominal_capacity(self, reps: Repository):
        pp1 = reps.power_plants['PLANT1']
        assert pp1.get_actual_nominal_capacity() == 18
        pp_test = PowerPlant("newpp")
        pp_test.capacity = 0
        pp_test.location = reps.power_grid_nodes['NED']
        pp_test.technology = reps.power_generating_technologies['1']
        assert pp_test.get_actual_nominal_capacity() == 0

    def test_calculate_marginal_fuel_cost(self, reps):
        pp1 = reps.power_plants['PLANT1']
        print(pp1.calculate_marginal_fuel_cost_per_mw_by_tick(reps, 0))
        assert pp1.calculate_marginal_fuel_cost_per_mw_by_tick(reps, 0) == 1 * 12.78 / 0.35

    def test_calculate_co2_tax_marginal_cost(self, reps):
        # 0 because tax has been set to 0
        assert reps.power_plants['PLANT1'].calculate_co2_tax_marginal_cost(reps) == 0

    def test_calculate_marginal_cost_excl_co2_market_cost(self, reps):
        pp1 = reps.power_plants['PLANT1']
        print(pp1.calculate_marginal_cost_excl_co2_market_cost(reps, 0))
        assert pp1.calculate_marginal_cost_excl_co2_market_cost(reps, 0) == \
               pp1.calculate_marginal_fuel_cost_per_mw_by_tick(reps, 0)

    def test_import_object_to_string(self):
        testobj = ImportObject('testobj')
        testobj.parameters['test'] = 'test'
        assert testobj.__str__().strip() == str(vars(testobj)).strip()

    def test_import_object_to_repr(self):
        testobj = ImportObject('testobj')
        testobj.parameters['test'] = 'test'
        assert testobj.__repr__().strip() == str(vars(testobj)).strip()
