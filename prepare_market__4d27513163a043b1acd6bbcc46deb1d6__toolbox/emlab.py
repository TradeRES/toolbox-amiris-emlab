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

from modules.payLoans import PayForLoansRole
from modules.short_invest import ShortInvestmentdecision
from modules.makefinancialreports import CreatingFinancialReports
from modules.marketstabilityreserve import DetermineMarketStabilityReserveFlow
from modules.payments import PayAndBankCO2Allowances, UseCO2Allowances
from modules.prepareMarketClearing import PrepareMarket
from util.spinedb_reader_writer import *
from modules.capacitymarket import *
from domain.StrategicReserveOperator import *
from modules.strategicreserve import *

from modules.co2market import *
from modules.Invest import *
from modules.prepareFutureMarketClearing import *
from modules.dismantle import *

# Initialize Logging
if not os.path.isdir('logs'):
    os.makedirs('logs')
logging.basicConfig(filename='logs/' + str(round(time.time() * 1000)) + '-log.txt', level=logging.DEBUG)
# Log to console? Uncomment next line
# logging.getLogger().addHandler(logging.StreamHandler())
logging.info('Starting EM-Lab Run')
run_capacity_market = False
run_strategic_reserve = False
run_electricity_spot_market = False
run_future_market = False
run_co2_market = False
run_investment_module = False
run_short_investment_module = False
run_decommission_module = False
run_next_year_market = False
run_financial_results = False
run_prepare_next_year_market_clearing = False
run_initialize_power_plants = False

# Loop over provided arguments and select modules
# Depending on which booleans have been set to True, these modules will be run
# logging.info('Selected modules: ' + str(sys.argv[2:]))

for arg in sys.argv[3:]:
    if arg == 'run_capacity_market':
        run_capacity_market = True
    if arg == 'run_strategic_reserve':
        run_strategic_reserve = True
    if arg == 'run_future_market':
        run_future_market = True
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
    if arg == 'run_initialize_power_plants':
        run_initialize_power_plants = True

if run_short_investment_module or run_capacity_market or run_strategic_reserve:
    emlab_url = sys.argv[1]
    logging.info('emlab database: ' + str(emlab_url))
    amiris_url = sys.argv[2]
    logging.info('amiris database: ' + str(amiris_url))
    spinedb_reader_writer = SpineDBReaderWriter(True, emlab_url, amiris_url)
else:
    emlab_url = sys.argv[1]
    logging.info('emlab database: ' + str(emlab_url))
    spinedb_reader_writer = SpineDBReaderWriter(False, emlab_url)

try:  # Try statement to always close DB properly
    reps = spinedb_reader_writer.read_db_and_create_repository()  # Load repository
    for p, power_plant in reps.power_plants.items():
        power_plant.specifyPowerPlantsInstalled(reps.current_tick, reps.energy_producers["Producer1"],
                                                "DE")
    print("repository complete")


    # for the first year, specify the power plants and if the the simultaion is not stairting then add one year

    if run_initialize_power_plants:
        pp_counter = 20  # start in 20, the first 20 are left to the candidate power plants.
        # adding id to power plants and candidate power plants
        for p, power_plant in reps.power_plants.items():
            power_plant.specifyPowerPlantsInstalled(reps.current_tick, reps.energy_producers["Producer1"],
                                                    "DE")  # TODO this shouldn't be hard coded
            pp_counter += 1
            power_plant.id = (int(str(power_plant.commissionedYear) +
                                  str("{:02d}".format(int(reps.dictionaryTechNumbers[power_plant.technology.name]))) +
                                  str("{:05d}".format(pp_counter))
                                  ))
            pp_counter = 0
        for p, power_plant in reps.candidatePowerPlants.items():
            pp_counter += 1
            power_plant.id = (int(str(9999) +  # TODO once installed, this will change to the commissioned year
                                  str("{:02d}".format(
                                      int(reps.dictionaryTechNumbers[power_plant.technology.name]))) +
                                  str("{:05d}".format(pp_counter))
                                  ))
            power_plant.capacity = 1  # See general description
        spinedb_reader_writer.stage_power_plant_id(reps.power_plants)
        spinedb_reader_writer.stage_candidate_power_plant_id(reps.candidatePowerPlants)


    spinedb_reader_writer.commit('Initialize all module import structures')
    print('Start Run Modules')
    # From here on modules will be run according to the previously set booleans
    if run_decommission_module:
        logging.info('Start Run dismantle')
        payingLoans = PayForLoansRole(reps)
        payingLoans.act_and_commit()
        dismantling = Dismantle(reps)
        dismantling.act_and_commit()
        logging.info('End Run dismantle')

    if run_financial_results:
        logging.info('Start Saving Financial Results')
        financial_report = CreatingFinancialReports(reps)
        financial_report.act_and_commit()  # TODO make faster
        logging.info('End saving Financial Results')

    if run_prepare_next_year_market_clearing:
        logging.info('Start Run preparing market for next year')
        preparing_market = PrepareMarket(reps)
        preparing_market.act_and_commit()
        logging.info('End Run market preparation for next year ')

    if run_future_market:
        future_market = PrepareFutureMarketClearing(reps)
        logging.info('Start creating future power plants')
        future_market.act_and_commit()
        logging.info('Start creating future power plants')

    if run_capacity_market:
        logging.info('Start Run Capacity Market')
        capacity_market_submit_bids = CapacityMarketSubmitBids(reps)  # This function stages new dispatch power plant
        capacity_market_clear = CapacityMarketClearing(reps)  # This function adds rep to class capacity markets
        capacity_market_submit_bids.act_and_commit()
        capacity_market_clear.act_and_commit()
        logging.info('End Run Capacity Market')

    if run_strategic_reserve:
        logging.info('Start strategic reserve')
        strategic_reserve_operator = StrategicReserveOperator(reps)
        strategic_reserve = StrategicReserve(strategic_reserve_operator)  # This function adds rep to class capacity markets
        strategic_reserve.act_and_commit()
        logging.info('End strategic reserve')

    if run_co2_market:
        logging.info('Start Run CO2 Market')
        market_stability_reserve = DetermineMarketStabilityReserveFlow(reps)
        market_stability_reserve.act_and_commit()
        co2_market_determine_co2_price = CO2MarketDetermineCO2Price(reps)
        co2_market_determine_co2_price.act_and_commit()
        payment_and_bank_co2 = PayAndBankCO2Allowances(reps)
        use_co2_allowances = UseCO2Allowances(reps)
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
    if run_short_investment_module or run_capacity_market or run_strategic_reserve:
        spinedb_reader_writer.amirisdb.close_connection()
