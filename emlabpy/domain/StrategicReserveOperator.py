
from domain.import_object import *
import pandas as pd

class StrategicReserveOperator(ImportObject):

    def __init__(self, name):
        super().__init__(name)
        self.zone = None
        self.reservePriceSR = 0
        self.reserveVolumePercentSR = 0
        self.cash = 0
        self.reserveVolume = 0
        self.list_of_plants = []

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        if parameter_name == 'zone':
            self.zone = str(parameter_value)
        elif parameter_name == 'cash':
            self.cash = int(parameter_value)
        elif parameter_name == 'reserveVolumePercentSR':
            self.reserveVolumePercentSR = parameter_value
        elif parameter_name == 'reservePriceSR':
            self.reservePriceSR = parameter_value
        elif reps.runningModule == "plotting" and  parameter_name == 'list_of_plants':
            array = parameter_value.to_dict()
            self.list_of_plants = pd.Series(i[1] for i in array["data"])
        elif reps.runningModule == "plotting" and  parameter_name == "reserveVolume":
            array = parameter_value.to_dict()
            self.reserveVolume = pd.Series(i[1] for i in array["data"])

    def getReserveVolume(self):
        return self.reserveVolume

    def setReserveVolume(self, reserveVolume):
        self.reserveVolume = reserveVolume

    def getZone(self):
        return self.zone

    def setZone(self, zone):
        self.zone = zone

    def getReservePriceSR(self):
        return self.reservePriceSR

    def setReservePriceSR(self, reservePriceSR):
        self.reservePriceSR = reservePriceSR

    def getReserveVolumePercentSR(self):
        return self.reserveVolumePercentSR

    def setReserveVolumePercentSR(self, reserveVolumePercentSR):
        self.reserveVolumePercentSR = reserveVolumePercentSR

    def getCash(self):
        return self.cash

    def setCash(self, cash):
        self.cash = cash

    def getPlants(self):
        return self.list_of_plants

    def setPlants(self, plants):
        self.list_of_plants = plants

