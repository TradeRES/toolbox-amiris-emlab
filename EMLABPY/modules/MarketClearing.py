from emlabpy.domain.trends import TriangularTrend
from emlabpy.modules.defaultmodule import DefaultModule
from emlabpy.domain.powerplant import PowerPlant
import logging
class MarketClearing(DefaultModule):

    def __init__(self, reps):
        super().__init__("Clearing the market", reps)
        self.triangular


    def export_fuelpriceyears(cursor, simulation_year):
        """
        :param simulation_year:
        :return:
        """
        for substance in substances:
            fuelprices = TriangularTrend.get_values(simulation_year)

