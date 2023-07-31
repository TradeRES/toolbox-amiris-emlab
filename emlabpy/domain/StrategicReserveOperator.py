
from domain.import_object import *
import pandas as pd
from domain.actors import EMLabAgent
class StrategicReserveOperator(EMLabAgent):

    def __init__(self, name):
        super().__init__(name)
        self.zone = None
        self.reservePriceSR = 0
        self.reserveVolumePercentSR = 0
        self.cash = 0
        self.reserveVolume = 0
        self.revenues_per_year = 0
        self.list_of_plants = []
        self.list_of_plants_all = dict()
        self.revenues_per_year_all = dict()
        self.reserveVolume_all = dict()

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative):
        # for list of plants and reserve volume, pass the tick as alternative
        if parameter_name == 'zone':
            self.zone = str(parameter_value)
        elif parameter_name == 'cash':
            self.cash = int(parameter_value)
        elif parameter_name == 'reserveVolumePercentSR':
            self.reserveVolumePercentSR = parameter_value
        elif parameter_name == 'reservePriceSR':
            self.reservePriceSR = parameter_value
        elif parameter_name == 'list_of_plants' and   reps.runningModule != "plotting" and alternative == reps.current_tick:
            self.list_of_plants = parameter_value
        elif reps.runningModule == "plotting" and  parameter_name == 'list_of_plants':
            self.list_of_plants_all[alternative] = parameter_value
        elif reps.runningModule == "plotting" and  parameter_name == "reserveVolume":
            self.reserveVolume_all[alternative] = parameter_value
        elif reps.runningModule == "plotting" and  parameter_name == "revenues_per_year":
            self.revenues_per_year_all[alternative] = parameter_value


    def getReserveVolume(self):
        return self.reserveVolume

    def setReserveVolume(self, reserveVolume):
        self.reserveVolume = reserveVolume

    def getZone(self):
        return self.zone

    def getReservePriceSR(self):
        return self.reservePriceSR

    def getReserveVolumePercentSR(self):
        return self.reserveVolumePercentSR

    def getCash(self):
        return self.cash

    def getPlants(self):
        return self.list_of_plants

    def setPlants(self, plants):
        self.list_of_plants = plants

