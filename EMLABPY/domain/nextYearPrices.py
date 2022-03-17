
from emlabpy.modules.defaultmodule import DefaultModule

class NextYearPrices(DefaultModule):

    def __init__(self, reps):
        super().__init__("Next year prices", reps)
        self.nextTimePoint = 0

    def setTimeHorizon(self):
        self.nextTimePoint = self.reps.current_tick

    def setExpectations(self):
        for k, substance in self.reps.substances.items():
            substance.get_price_for_next_tick(self.nextTimePoint, substance)
            self.reps.dbrw.stage_next_fuel_prices(substance)
