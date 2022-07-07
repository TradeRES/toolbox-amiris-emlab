"""
Dummy file to simulate a COMPETES output.
It executes a simple type of Electricity Spot Market.

Jim Hommes - 17-3-2021
"""

import sys
from util.spinedb_reader_writer import *
from modules.electricityspotmarket import *

# Input DB
db_url = sys.argv[1]
spinedbrw = SpineDBReaderWriter(db_url)
reps = spinedbrw.read_db_and_create_repository()

electricity_spot_market_submit_bids = ElectricitySpotMarketSubmitBids(reps)
electricity_spot_market_clear = ElectricitySpotMarketClearing(reps)

electricity_spot_market_submit_bids.act_and_commit(reps.current_tick)
electricity_spot_market_clear.act_and_commit(reps.current_tick)
