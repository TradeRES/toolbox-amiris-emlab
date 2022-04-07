
from emlabpy.modules.defaultmodule import DefaultModule

class PrepareMarket(DefaultModule):

    def __init__(self, reps):
        super().__init__("Next year prices", reps)
        self.tick = 0
        self.year = 0
        self.fuel_price = 0
        reps.dbrw.stage_init_next_prices_structure()

    def act(self):
        self.setTimeHorizon()
        self.setExpectations()

    def setTimeHorizon(self):
        self.tick = self.reps.current_tick
        self.year = self.reps.current_year

    def setExpectations(self):
        for k, substance in self.reps.substances.items():
            self.fuel_price  = substance.get_price_for_next_tick( self.reps,  self.tick, self.year, substance)
            self.reps.dbrw.stage_simulated_fuel_prices(self.year, self.fuel_price, substance)
