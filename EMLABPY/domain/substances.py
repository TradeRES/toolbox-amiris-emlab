from domain.import_object import *
from domain.trends import GeometricTrendRegression
import pandas as pd
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
        self.newSimulatedPrice = 0
        self.newFuturePrice = 0

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
        elif parameter_name == 'trend': # TODO this will change later
            self.trend = reps.trends[parameter_value]
        elif parameter_name == 'futurePrice':
            self.futurePrice = parameter_value
        elif parameter_name == 'simulatedPrice':
            self.simulatedPrice = parameter_value

    def get_price_for_next_tick(self, reps, tick, year, substance):
        if tick == 0 or substance.name == "CO2":
            if substance.name == "electricity":
                self.newSimulatedPrice = np.float64(1.0) # set electricity demand change as 1 for the first year. TODO
            else:
                xp = [2020, 2040] # TODO avoid this to be hardcoded
                fp = [substance.initialprice2020, substance.initialprice2040]
                self.newSimulatedPrice = np.interp(year, xp, fp)
            return self.newSimulatedPrice
        else:
            calculatedPrices = reps.dbrw.get_calculated_simulated_fuel_prices(substance, "simulatedPrice")
            df = pd.DataFrame(calculatedPrices['data'])
            df.set_index(0, inplace=True)
            last_value = df.loc[str(year - 1)][1]
            random_number = random.triangular(-1, 1, 0) # low, high, mode
            if random_number < 0:
                self.newSimulatedPrice = last_value * (self.trend.top + (random_number * (self.trend.top - self.trend.min)))
            else:
                self.newSimulatedPrice = last_value * (self.trend.top + (random_number * (self.trend.max - self.trend.top)))
        return self.newSimulatedPrice

    def get_price_for_future_tick(self, reps, futureYear, substance):
        if reps.current_tick >= 2 or substance.name != "CO2":
            self.initializeGeometricTrendRegression(reps, substance) # TODO should this
            self.newFuturePrice = self.geometricRegression.predict(futureYear)
            return self.newFuturePrice
        else:
            xp = [2020, 2040] # todo: hard coded
            fp = [substance.initialprice2020, substance.initialprice2040]
            self.newFuturePrice = np.interp(futureYear, xp, fp)
            return self.newFuturePrice

    def initializeGeometricTrendRegression(self, reps, substance):
        self.geometricRegression = GeometricTrendRegression("geometrictrendRegression" + self.name)
        calculatedfuturePrices =  reps.dbrw.get_calculated_simulated_fuel_prices(substance, "futurePrice")
        x = []
        y = []
        for i in calculatedfuturePrices['data']:
            x.append(int(i[0]))
            y.append(i[1])
        self.geometricRegression.addData(x,y)


class SubstanceInFuelMix(ImportObject):
    def __init__(self, name: str):
        super().__init__(name)
        self.substance = None
        self.substances = list()
        self.share = 1

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if parameter_name == 'FUELNEW':
            self.substances.append(reps.substances[parameter_value])
