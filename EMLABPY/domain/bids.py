
from domain.import_object import *

class Bid(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.accepted_amount = 0
        self.tick = -1
        self.amount = None
        self.price = None
        self.status = 'Awaiting confirmation'
        self.bidder = None
        self.market = None
        self.plant = None

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        setattr(self, parameter_name, parameter_value)
