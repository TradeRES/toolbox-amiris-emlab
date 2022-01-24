from domain.trends import *


class TestTrend:

    def test_geometric_trend(self):
        gt = GeometricTrend("gt")
        gt.start = 1000
        gt.growth_rate = 0.05
        assert gt.get_value(0) == 1000
        assert gt.get_value(1) == 1.05 * 1000
        assert gt.get_value(10) == pow(1.05, 10) * 1000

    def test_triangular_trend(self):
        tt = TriangularTrend("tt")
        tt.top = 1
        tt.min = 0.5
        tt.max = 1.5
        tt.values = [100]   # It's definition of start, see add_parameter_value
        assert tt.get_value(0) == 100
        prev_price = 100
        for i in range(1, 1000):
            new_price = tt.get_value(i)
            assert prev_price * (1 + (0 * 1 - 0.5)) <= new_price <= prev_price * (1 + 1 * 1.5 - 1)
            prev_price = new_price

    def test_step_trend(self):
        st = StepTrend("st")
        st.duration = 1
        st.start = 50
        st.min_value = 25
        st.increment = -1
        assert st.get_value(0) == 50
        assert st.get_value(10) == 40
        assert st.get_value(1000) == 25

