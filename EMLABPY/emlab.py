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

from emlabpy.modules.payLoans import PayForLoansRole
from emlabpy.modules.short_invest import ShortInvestmentdecision
from modules.makefinancialreports import CreatingFinancialReports
from modules.marketstabilityreserve import DetermineMarketStabilityReserveFlow
from modules.payments import PayAndBankCO2Allowances, UseCO2Allowances
from modules.prepareMarketClearing import PrepareMarket
from util.spinedb_reader_writer import *
from modules.capacitymarket import *
from modules.co2market import *
from emlabpy.modules.Invest import *
from modules.prepareCandidatePowerPlants import *
from modules.dismantle import *

# Initialize Logging
if not os.path.isdir('logs'):
    os.makedirs('logs')
logging.basicConfig(filename='logs/' + str(round(time.time() * 1000)) + '-log.txt', level=logging.DEBUG)
# Log to console? Uncomment next line
# logging.getLogger().addHandler(logging.StreamHandler())
logging.info('Starting EM-Lab Run')
run_capacity_market = False
run_electricity_spot_market = False
run_future_power_plants = False
run_co2_market = False
run_investment_module = False
run_short_investment_module = False
run_decommission_module = False
run_next_year_market = False
run_financial_results = False
run_prepare_next_year_market_clearing = False
# Loop over provided arguments and select modules
# Depending on which booleans have been set to True, these modules will be run
# logging.info('Selected modules: ' + str(sys.argv[2:]))

for arg in sys.argv[3:]:
    if arg == 'run_capacity_market':
        run_capacity_market = True
    if arg == 'run_future_power_plants':
        run_future_power_plants = True
    if arg == 'run_co2_market':
        run_co2_market = True
    if arg == 'run_investment_module':
        run_investment_module = True
    if arg == 'run_short_investment_module':
        run_short_investment_module = True
    if arg == 'run_decommission_module':
        run_decommission_module = True
    if arg == 'run_prepare_next_year_market_clearing':
        run_prepare_next_year_market_clearing = True
    if arg == 'run_financial_results':
        run_financial_results = True


if run_investment_module or run_short_investment_module:
    emlab_url = sys.argv[1]
    logging.info('emlab database: ' + str(emlab_url))
    amiris_url = sys.argv[2]
    logging.info('amiris database: ' + str(amiris_url))
    spinedb_reader_writer = SpineDBReaderWriter("run_investment_module", emlab_url, amiris_url)
else:
    emlab_url = sys.argv[1]
    logging.info('emlab database: ' + str(emlab_url))
    spinedb_reader_writer = SpineDBReaderWriter("run_other_module", emlab_url)

try:  # Try statement to always close DB properly
    reps = spinedb_reader_writer.read_db_and_create_repository()     # Load repository
    print("repository complete")
    logging.info('Start Initialization Modules')
    capacity_market_submit_bids = CapacityMarketSubmitBids(reps)  # This function stages new dispatch power plant
    capacity_market_clear = CapacityMarketClearing(reps)  # This function adds rep to class capacity markets
    # This function adds rep to class capacity markets
    co2_market_determine_co2_price = CO2MarketDetermineCO2Price(reps)
    payment_and_bank_co2 = PayAndBankCO2Allowances(reps)
    use_co2_allowances = UseCO2Allowances(reps)
    market_stability_reserve = DetermineMarketStabilityReserveFlow(reps)
    # for the first year, specify the power plants and if the the simultaion is not stairting then add one year
    for p, power_plant in reps.power_plants.items():
        if reps.current_tick > 0:
            power_plant.addoneYeartoAge() # add one year to all power plants
        else:

            power_plant.specifyPowerPlantsInstalled(0, reps.energy_producers["Producer1"], "DE")  # TODO this shouldn't be hard coded

    spinedb_reader_writer.commit('Initialize all module import structures')
    logging.info('End Initialization Modules')

    # From here on modules will be run according to the previously set booleans
    logging.info('Start Run Modules')

    if run_decommission_module:
        logging.info('Start Run dismantle')
        dismantling = Dismantle(reps)
        dismantling.act_and_commit()
        payingLoans = PayForLoansRole(reps)
        payingLoans.act_and_commit()
        logging.info('End Run dismantle')

    if run_financial_results:
        logging.info('Start Saving Financial Results')
        financial_report = CreatingFinancialReports(reps)
        financial_report.act_and_commit() # TODO make faster
        logging.info('End saving Financial Results')

    if run_prepare_next_year_market_clearing:
        logging.info('Start Run preparing market for next year')
        preparing_market = PrepareMarket(reps)
        preparing_market.act_and_commit()
        logging.info('End Run market preparation for next year ')

    if run_future_power_plants:
        creating_power_plants = PrepareCandidatePowerPlants(reps)
        logging.info('Start creating future power plants')
        creating_power_plants.act_and_commit()
        logging.info('Start creating future power plants')

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
        investing.act_and_commit()
        logging.info('End Run Investment')

    if run_short_investment_module:
        short_investing = ShortInvestmentdecision(reps)
        logging.info('Start Run short term Investments')
        short_investing.act_and_commit()
        logging.info('End Run short term Investment')

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
