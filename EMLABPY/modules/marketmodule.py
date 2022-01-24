"""
This is the parent class of all market modules.
The advantage of this parent class is that some calculations can be static as they are done for all market modules.

Jim Hommes - 7-4-2021
"""
from modules.defaultmodule import DefaultModule


class MarketModule(DefaultModule):
    pass
