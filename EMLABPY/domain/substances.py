from emlabpy.domain.import_object import *
from emlabpy.domain.trends import GeometricTrendRegression
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
        if tick == 0:
            xp = [2020, 2040] # TODO avoid this to be hardcoded
            fp = [substance.initialprice2020, substance.initialprice2040]
            self.simulatedPrice = np.interp(year, xp, fp)
            return
        else:
            calculatedfuturePrices= reps.dbrw.get_calculated_simulated_fuel_prices(substance)
            df = pd.DataFrame(calculatedfuturePrices['data'])
            df.set_index(0, inplace=True)
            last_value = df.loc[str(year - 1)][1]
            random_number = random.triangular(-1, 0, 1) # TODO this was (-1,  1, 0 ) for competes integration
            if random_number < 0:
                newsimulatedPrice = last_value * (self.trend.top + (random_number * (self.trend.top - self.trend.min)))
            else:
                newsimulatedPrice = last_value * (self.trend.top + (random_number * (self.trend.max - self.trend.top)))
            #print(substance.name , 'lastvalue',last_value , "r " , random_number, "simulated", self.simulatedPrice  )
        return newsimulatedPrice

    def get_price_for_future_tick(self, reps, futureYear, substance):
        if reps.current_tick >= 2:
            self.initializeGeometricTrendRegression(reps, substance)
            self.futurePrice = self.geometricRegression.predict(futureYear)
            return
        else:
            xp = [2020, 2040] # todo: hard coded
            fp = [substance.initialprice2020, substance.initialprice2040]
            self.futurePrice = np.interp(futureYear, xp, fp)
            return

    def initializeGeometricTrendRegression(self, reps, substance):
        self.geometricRegression = GeometricTrendRegression("geometrictrendRegression" + self.name)
        calculatedfuturePrices =  reps.dbrw.get_calculated_future_fuel_prices(substance)
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
