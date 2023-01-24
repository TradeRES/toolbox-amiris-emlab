from domain.import_object import *
from domain.trends import GeometricTrendRegression
import pandas as pd
import numpy as np
import random

class Substance(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.co2_density = 0
     #   self.energy_density = 1
        self.quality = 0
        self.price = 0
        self.trend = None
        self.all_years_CO2_price = pd.Series(dtype='float64')
        self.initialPrice = pd.Series(dtype='float64')
        self.futurePrice = []
        self.futurePrice_inYear = 0
        self.simulatedPrice = []
        self.simulatedPrice_inYear = 0
        self.resource_limit2020 = 0
        self.values = []
        self.geometricRegression = None
        self.newPrice = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'AmirisFuelSpecificCo2EmissionsInTperMWH': # todo: AMIRIS add this as an input parameter 'co2Density'
            self.co2_density = float(parameter_value)
        # elif parameter_name == 'energyDensity': # this was from EMLab, not used here
        #     self.energy_density = float(parameter_value)
        elif parameter_name == 'quality':
            self.quality = float(parameter_value)
        elif parameter_name == 'annual_resource_limit' and alternative == "biopotential_2020":# TODO take out the hardcoded scenario
            self.resource_limit2020 = float(parameter_value)
        elif parameter_name == 'trend':
            self.trend = reps.trends[parameter_value]
        elif parameter_name == 'futurePrice':
            self.futurePrice = parameter_value
        elif parameter_name == 'simulatedPrice':
            self.simulatedPrice = parameter_value
        elif parameter_name == reps.country:
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index = index)
            self.all_years_CO2_price = pd_series
        elif parameter_name == "price":
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index = index)
            self.initialPrice = pd_series.sort_values(ascending=True)

    def get_price_for_tick(self, reps, year, simulating_future_market):
        # first consider prices if these are supposed to be fix
        if reps.fix_fuel_prices_to_year == True: # attention this shouldnt be neede once all data is there
            # fixing prices to year
            if  self.name == "CO2" and reps.yearly_CO2_prices == True:
                # yearly prices
                self.get_CO2_yearly_price(reps.fix_price_year)
            else:
                self.newPrice = self.interpolate_year(reps.fix_price_year)
                return self.newPrice

        elif self.name == "CO2":
            if reps.yearly_CO2_prices == True:
                # dont fix prices
                self.newPrice = self.get_CO2_yearly_price(year)
            else:
                print("should not extrapolate with CO2 prices")
                self.newPrice = self.get_CO2_yearly_price(year)
            return self.newPrice

        elif reps.current_tick >= reps.start_tick_fuel_trends:
            if simulating_future_market == True:
                self.initializeGeometricTrendRegression(reps)
                self.newPrice = self.geometricRegression.predict(year)
                return self.newPrice
            else:
                # simulating next year prices from past results and random
                calculatedPrices = reps.dbrw.get_calculated_simulated_fuel_prices(self.name, "simulatedPrice")
                df = pd.DataFrame(calculatedPrices['data'])
                df.set_index(0, inplace=True)
                last_value = df.loc[str(year - 1)][1]
                random_number = random.triangular(self.trend.min, self.trend.max,  self.trend.top) # low, high, mode
                self.newPrice = last_value * random_number
        else:
            self.newPrice = self.interpolate_year(year)
            return self.newPrice

    def get_CO2_yearly_price(self, year):
        if year in self.all_years_CO2_price.index:
            self.newPrice = self.all_years_CO2_price[year]
        else:
            xp = [2020, 2050]
            fp = [self.all_years_CO2_price[2020], self.all_years_CO2_price[2050]]
            self.newPrice = np.interp(year, xp, fp)
        return self.newPrice

    def interpolate_year(self, year):
        c = np.polyfit(self.initialPrice.index, self.initialPrice.values, 2)
        f = np.poly1d(c)
        return f(year)

    def initializeGeometricTrendRegression(self, reps):
        self.geometricRegression = GeometricTrendRegression("geometrictrendRegression" + self.name)
        calculatedfuturePrices =  reps.dbrw.get_calculated_simulated_fuel_prices(self.name, "futurePrice")
        x = []
        y = []
        for i in calculatedfuturePrices['data']:
            # todo improve
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
