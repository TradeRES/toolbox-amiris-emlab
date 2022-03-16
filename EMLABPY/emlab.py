"""
The main EM-Lab file for in SpineToolbox.
Commandline arguments provide which modules are run and which aren't.
Ingrid Sanchez 28-3-2022
Jim Hommes - 25-3-2021
"""
import sys
import logging
import os
import time
from modules.makefinancialreports import CreatingFinancialReports
from modules.marketstabilityreserve import DetermineMarketStabilityReserveFlow
from modules.payments import PayAndBankCO2Allowances, UseCO2Allowances
from util.spinedb_reader_writer import *
from modules.capacitymarket import *
from modules.co2market import *
from emlabpy.modules.Invest import *
from modules.futurePowerPlants import *
from modules.dismantle import *
# Initialize Logging
if not os.path.isdir('logs'):
    os.makedirs('logs')
logging.basicConfig(filename='logs/' + str(round(time.time() * 1000)) + '-log.txt', level=logging.DEBUG)
# Log to console? Uncomment next line
#logging.getLogger().addHandler(logging.StreamHandler())
logging.info('Starting EM-Lab Run')
run_capacity_market = False
run_electricity_spot_market = False
run_new_power_plants = False
run_co2_market = False
run_investment_module = False
run_decommission_module = False
# Loop over provided arguments and select modules
# Depending on which booleans have been set to True, these modules will be run
#logging.info('Selected modules: ' + str(sys.argv[2:]))
for arg in sys.argv[3:]:
    if arg == 'run_capacity_market':
        run_capacity_market = True
    if arg == 'run_new_power_plants':
        run_new_power_plants = True
    if arg == 'run_co2_market':
        run_co2_market = True
    if arg == 'run_investment_module':
        run_investment_module = True
    if arg == 'run_decommission_module':
        run_decommission_module = True

if run_investment_module:
    emlab_url = sys.argv[1]
    logging.info('emlab database: ' + str(emlab_url))
    amiris_url = sys.argv[2]
    logging.info('amiris database: ' + str(amiris_url))
    spinedb_reader_writer = SpineDBReaderWriter("run_investment_module", emlab_url, amiris_url)
else:
    emlab_url = sys.argv[1]
    logging.info('emlab database: ' + str(emlab_url))
    spinedb_reader_writer = SpineDBReaderWriter("run_other_module", emlab_url)


try:    # Try statement to always close DB properly
    # Load repository
    reps = spinedb_reader_writer.read_db_and_create_repository()
    print("repository complete")
    logging.info('Start Initialization Modules')
    capacity_market_submit_bids = CapacityMarketSubmitBids(reps) # This function stages new dispatch power plant
    capacity_market_clear = CapacityMarketClearing(reps) # This function adds rep to class capacity markets
     # This function adds rep to class capacity markets
    co2_market_determine_co2_price = CO2MarketDetermineCO2Price(reps)
    payment_and_bank_co2 = PayAndBankCO2Allowances(reps)
    use_co2_allowances = UseCO2Allowances(reps)
    market_stability_reserve = DetermineMarketStabilityReserveFlow(reps)
    for p, v in reps.power_plants.items():
        v.specifyPowerPlantsforFirstTick( 0 , "Producer1", "DE")
    financial_report = CreatingFinancialReports(reps)
    financial_report.act_and_commit()
    spinedb_reader_writer.commit('Initialize all module import structures')
    logging.info('End Initialization Modules')

    # From here on modules will be run according to the previously set booleans
    logging.info('Start Run Modules')

    if run_decommission_module:
        logging.info('Start Run dismantle')
        dismantling = Dismantle(reps)
        dismantling.act_and_commit()
        logging.info('End Run dismantle')

    if run_new_power_plants:
        creating_power_plants = FuturePowerPlants(reps)
        logging.info('Start definition of PP')
        creating_power_plants.act_and_commit()
        logging.info('End Run definition of PP')

    if run_capacity_market:
        logging.info('Start Run Capacity Market')
        capacity_market_submit_bids.act_and_commit()
        capacity_market_clear.act_and_commit()
        logging.info('End Run Capacity Market')

    if run_co2_market:
        logging.info('Start Run CO2 Market')
        market_stability_reserve.act_and_commit()
        co2_market_determine_co2_price.act_and_commit()
        # payment_and_bank_co2.act_and_commit(reps.current_tick)
        # use_co2_allowances.act_and_commit(reps.current_tick)
        logging.info('End Run CO2 Market')

    if run_investment_module:
        investing = Investmentdecision(reps)
        logging.info('Start Run Investment')
        #     investing.act_and_commit()
        logging.info('End Run Investment')
    logging.info('End Run Modules')

    spinedb_reader_writer.commit('Initialize all module import structures')
    logging.info('Commit Initialization Modules')

except Exception as e:
    logging.error('Exception occurred: ' + str(e))
    raise
finally:
    logging.info('Closing database connections...')
    print("finished emlab")
    spinedb_reader_writer.db.close_connection()
    if run_investment_module:
        spinedb_reader_writer.amirisdb.close_connection()

