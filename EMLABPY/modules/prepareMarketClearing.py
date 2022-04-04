
from emlabpy.modules.defaultmodule import DefaultModule

class PrepareMarket(DefaultModule):

    def __init__(self, reps):
        super().__init__("Next year prices", reps)
        self.tick = 0

    def act_and_commit(self):
        self.setTimeHorizon()
        self.setExpectations()

    def setTimeHorizon(self):
        self.tick = self.reps.current_tick

    def setExpectations(self):
        for k, substance in self.reps.substances.items():
            substance.get_price_for_next_tick(self.tick, substance)
            self.reps.dbrw.stage_simulated_fuel_prices(self.tick, substance)
