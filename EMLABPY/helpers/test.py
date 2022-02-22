
import sys
import logging
import os
import time

from util.spinedb_reader_writer import *
from modules.capacitymarket import *

from emlabpy.util.spinedb_reader_writer import SpineDBReaderWriter

run_capacity_market = True

db_url ="sqlite:///C:\\Users\\isanchezjimene\\Documents\\TraderesCode\toolbox-amiris-emlab\\.spinetoolbox\\items\\emlabdb\\EmlabDB.sqlite"
logging.info('Selected database: ' + str(db_url))


# Initialize SpineDB Reader Writer (also initializes DB connection)
spinedb_reader_writer = SpineDBReaderWriter(db_url)

try:    # Try statement to always close DB properly
    # Load repository
    reps = spinedb_reader_writer.read_db_and_create_repository()

    # Initialize all the modules
    # This initialization often includes the commit of the first structure to SpineDB
    logging.info('Start Initialization Modules')
    capacity_market_submit_bids = CapacityMarketSubmitBids(reps)
    capacity_market_clear = CapacityMarketClearing(reps)
    co2_market_determine_co2_price = CO2MarketDetermineCO2Price(reps)
    payment_and_bank_co2 = PayAndBankCO2Allowances(reps)
    use_co2_allowances = UseCO2Allowances(reps)
    market_stability_reserve = DetermineMarketStabilityReserveFlow(reps)
    logging.info('End Initialization Modules')

    # Commit Initialization changes to SpineDB
    logging.info('Commit Initialization Modules')
    spinedb_reader_writer.commit('Initialize all module import structures')

    # From here on modules will be run according to the previously set booleans
    logging.info('Start Run Modules')
    if run_capacity_market:
        logging.info('Start Run Capacity Market')
        capacity_market_submit_bids.act_and_commit(reps.current_tick)
        capacity_market_clear.act_and_commit(reps.current_tick)
        logging.info('End Run Capacity Market')

    if run_co2_market:
        logging.info('Start Run CO2 Market')
        market_stability_reserve.act_and_commit(reps.current_tick)
        co2_market_determine_co2_price.act_and_commit(reps.current_tick)
        # payment_and_bank_co2.act_and_commit(reps.current_tick)
        # use_co2_allowances.act_and_commit(reps.current_tick)
        logging.info('End Run CO2 Market')
    logging.info('End Run Modules')
except Exception as e:
    logging.error('Exception occurred: ' + str(e))
    raise
finally:
    logging.info('Closing database connections...')
    spinedb_reader_writer.db.close_connection()
    spinedb_reader_writer.config_db.close_connection()
