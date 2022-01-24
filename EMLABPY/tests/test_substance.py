

class TestSubstance:

    def test_get_price_for_tick(self, reps):
        subst = reps.substances['Oil']
        assert subst.get_price_for_tick(0) == 49.68000000000001
        prev_price = 49.68000000000001
        for i in range(1, 1000):
            new_price = subst.get_price_for_tick(i)
            assert prev_price * (1.01 + (0 * 1.01 - 0.96)) <= new_price <= prev_price * (1.01 + (1 * 1.04 - 1.01))
            prev_price = new_price

