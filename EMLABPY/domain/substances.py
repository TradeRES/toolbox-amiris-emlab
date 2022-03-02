from emlabpy.domain.import_object import *

class Substance(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        print(name)
        self.co2_density = 0
        self.energy_density = 1
        self.quality = 0
        self.trend = None

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'co2Density':
            self.co2_density = float(parameter_value)
        elif parameter_name == 'energyDensity':
            self.energy_density = float(parameter_value)
        elif parameter_name == 'quality':
            self.quality = float(parameter_value)
        elif parameter_name == 'trend':
            self.trend = reps.trends[parameter_value]

    def get_price_for_tick(self, tick):
        return self.trend.get_value(tick)

class SubstanceInFuelMix(ImportObject):
    def __init__(self, name: str):
        super().__init__(name)
        self.substance = None
        self.substances = list()
        self.share = 1

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if parameter_name == 'FUELNEW':
            self.substances.append(reps.substances[parameter_value])
