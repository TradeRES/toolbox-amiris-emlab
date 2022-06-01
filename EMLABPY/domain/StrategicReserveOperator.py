
from domain.import_object import *

class StrategicReserveOperator(ImportObject):

    def __init__(self, name):
        super().__init__(name)

        self.reserveVolume = 0
        self.zone = None
        self.reservePriceSR = 0
        self.reserveVolumePercentSR = 0.06 # todo add this to

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
