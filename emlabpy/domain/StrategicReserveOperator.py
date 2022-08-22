
from domain.import_object import *

class StrategicReserveOperator(ImportObject):

    def __init__(self, name):
        super().__init__(name)
        self.reserveVolume = 0
        self.zone = None
        self.reservePriceSR = 0
        self.reserveVolumePercentSR = 0
        self.cash = 0
        self.list_of_plants = []

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        setattr(self, parameter_name, parameter_value)

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

    def setPlants(self, plant):
        self.list_of_plants.append(plant)

