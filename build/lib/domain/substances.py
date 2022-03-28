from emlabpy.domain.import_object import *
from emlabpy.domain.trends import GeometricTrendRegression
import numpy as np
import random

class Substance(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.co2_density = 0
        self.energy_density = 1
        self.quality = 0
        self.price = 0
        self.co2_price = 1
        self.trend = None
        self.initialprice2020 = 0
        self.initialprice2040 = 0
        self.futurePrice = []
        self.simulatedPrice = []
        self.resource_limit2020 = 0
        self.values = []
        self.geometricRegression = None

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'co2Density':
            self.co2_density = float(parameter_value)
        elif parameter_name == 'energyDensity':
            self.energy_density = float(parameter_value)
        elif parameter_name == 'quality':
            self.quality = float(parameter_value)
        elif parameter_name == 'price2020': # TODO take out the hardcoded price
            self.initialprice2020 = float(parameter_value)
        elif parameter_name == 'price2040':
            self.initialprice2040 = float(parameter_value)
        # elif parameter_name == 'co2_price':
        #     self.co2_price = float(parameter_value)
        elif parameter_name == 'annual_resource_limit' and alternative == "biopotential_2020":# TODO take out the hardcoded scenario
            self.resource_limit2020 = float(parameter_value)
        elif parameter_name == 'trend':
            self.trend = reps.trends[parameter_value]
        elif parameter_name == 'futurePrice':
            self.futurePrice = parameter_value
        elif parameter_name == 'simulatedPrice':
            self.simulatedPrice = parameter_value

    def get_price_for_next_tick(self, tick, substance):
        if tick == 0 :
            xp = [20, 40] # TODO avoid this to be hardcoded
            fp = [substance.initialprice2020, substance.initialprice2040]
            self.simulatedPrice.append(np.interp(tick, xp, fp))
            return
        else:
            while len(self.simulatedPrice) <= tick:
                last_value = self.simulatedPrice[-1]
                random_number = random.triangular(-1, 0, 1) # TODO this was (-1,  1, 0 ) for competes integration
                if random_number < 0:
                    self.simulatedPrice.append(last_value * (self.trend.top + (random_number * (self.trend.top - self.trend.min))))
                else:
                    self.simulatedPrice.append(last_value * (self.trend.top + (random_number * (self.trend.max - self.trend.top))))
        return

    def get_price_for_future_tick(self, currenttick, futuretick, substance):
        if currenttick >= 2:
            self.initializeGeometricTrendRegression()
            self.futurePrice = self.geometricRegression.predict(futuretick)
            return
        else:
            xp = [20, 40]
            fp = [substance.initialprice2020, substance.initialprice2040]
            self.futurePrice = np.interp(futuretick, xp, fp)
            return

    def initializeGeometricTrendRegression(self):
        self.geometricRegression = GeometricTrendRegression("geometrictrendRegression" + self.name)
        for index, simulatedPrices in enumerate(self.simulatedPrice):
            self.geometricRegression.addData(index, simulatedPrices)

class SubstanceInFuelMix(ImportObject):
    def __init__(self, name: str):
        super().__init__(name)
        self.substance = None
        self.substances = list()
        self.share = 1

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if parameter_name == 'FUELNEW':
            self.substances.append(reps.substances[parameter_value])
