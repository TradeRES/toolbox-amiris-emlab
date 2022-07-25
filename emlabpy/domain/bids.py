from domain.import_object import *


class Bid(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.accepted_amount = 0
        self.tick = -1
        self.amount = 0
        self.price = 0
        self.status = 'Awaiting confirmation'
        self.bidder = ""
        self.market = ""
        self.plant = ""

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        setattr(self, parameter_name, parameter_value)
