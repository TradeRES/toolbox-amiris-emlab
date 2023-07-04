from domain.import_object import *
from domain.trends import GeometricTrendRegression
from domain.trends import TriangularTrend
import pandas as pd
import numpy as np
import random

class Substance(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.co2_density = 0
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
        if parameter_name == 'AmirisFuelSpecificCo2EmissionsInTperMWH': # todo: AMIRIS: add this as an input parameter 'co2Density'
            self.co2_density = float(parameter_value)
        elif parameter_name == 'quality':
            self.quality = float(parameter_value)
        elif parameter_name == 'annual_resource_limit' and alternative == "biopotential_2020":# TODO take out the hardcoded scenario
            self.resource_limit2020 = float(parameter_value)
        elif parameter_name == 'trend':
            self.trend = reps.trends[parameter_value]
        elif parameter_name == 'futurePrice':
            self.futurePrice = parameter_value
        elif parameter_name == 'simulatedPrice'and reps.runningModule in ["plotting", "run_future_market", "run_prepare_next_year_market_clearing"]:
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index = index)
            self.simulatedPrice = pd_series
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
        """
        electricity price  = demand can be increased even if othe fuel prices remain fix
        for future estimation fuel prices interpolate bewteen available data
        """
        if self.name == "electricity" and reps.increase_demand ==True:
            if simulating_future_market == True:
                if reps.initialization_investment == True:
                    self.newPrice = self.trend.top ** (reps.investment_initialization_years)  # assuming that demand incrases according to mode on the last years
                else:
                    self.initializeGeometricTrendRegression(reps, self.simulatedPrice)
                    self.newPrice = self.geometricRegression.predict(reps.lookAhead)
            else: # realized market
                last_value = self.simulatedPrice.loc[year - 1]
                random_number = random.triangular(self.trend.min, self.trend.max,  self.trend.top) # low, high, mode
                self.newPrice = random_number * last_value

        elif reps.fix_fuel_prices_to_year == True:  # fixing prices to year
            if  self.name == "CO2" and reps.yearly_CO2_prices == True:
                # but dont fix yearly prices
                self.newPrice = self.get_CO2_yearly_price(year)
            else:
                self.newPrice = self.interpolate_year(reps.fix_price_year)
        else:
            # dont fix prices to first year
            if self.name == "CO2" and reps.yearly_CO2_prices == True:
                self.newPrice = self.get_CO2_yearly_price(year)
            elif reps.current_tick >= reps.start_tick_fuel_trends:
                if simulating_future_market == True:
                    # simulating next year prices from past results and random
                    calculatedPrices = reps.dbrw.get_calculated_simulated_fuel_prices(self.name, "simulatedPrice")
                    df = pd.DataFrame(calculatedPrices['data'])
                    df.set_index(0, inplace=True)
                    last_value = df.loc[str(year - 1)][1]
                    random_number = random.triangular(self.trend.min, self.trend.max,  self.trend.top) # low, high, mode
                    self.newPrice = last_value * random_number
                elif simulating_future_market == False:  #realized prices
                    self.newPrice = self.interpolate_year(year)
            else:
                self.newPrice = self.interpolate_year(year)

        if self.newPrice < 0:
            raise Exception("negative price")

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
        if year < self.initialPrice.index.min() and self.name == "CO2":
            interpolated_price = self.initialPrice.values.min()
        else:
            c = np.polyfit(self.initialPrice.index, self.initialPrice.values, 2)
            f = np.poly1d(c)
            interpolated_price = f(year)
        return interpolated_price

    def initializeGeometricTrendRegression(self, reps, calculatedPrices):
        self.geometricRegression = GeometricTrendRegression("geometrictrendRegression" + self.name)
        if reps.current_tick >= reps.pastTimeHorizon:
            values = range(reps.current_year - reps.pastTimeHorizon, reps.current_year + 1)
            years = [*values]
            y = calculatedPrices.loc[years]
        else:
            y = calculatedPrices.values
        x = [range( -len(y) + 1 , 1)]
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
