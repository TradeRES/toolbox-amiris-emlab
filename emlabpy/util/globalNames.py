import os

power_plant_dispatch_plan_status_accepted = 'Accepted'
power_plant_dispatch_plan_status_failed = 'Failed'
power_plant_dispatch_plan_status_partly_accepted = 'Partly Accepted'
power_plant_dispatch_plan_status_awaiting = 'Awaiting'

capacity_mechanism_contracted = "contracted"
capacity_mechanism_not_contracted = "not contracted"

CF_UNCLASSIFIED = "UNCLASSIFIED"
CF_ELECTRICITY_SPOT = "ELECTRICITY_SPOT"
CF_ELECTRICITY_LONGTERM = "ELECTRICITY_LONGTERM"
CF_FIXEDOMCOST = "FIXEDOMCOST"
CF_COMMODITY = "COMMODITY"
CF_CO2TAX = "CO2TAX"
CF_CO2AUCTION = "CO2AUCTION"
CF_LOAN = "LOAN"
CF_DOWNPAYMENT = "DOWNPAYMENT"
CF_NATIONALMINCO2 = "NATIONALMINCO2"
CF_STRRESPAYMENT = "STRRESPAYMENT"
CF_CAPMARKETPAYMENT = "CAPMARKETPAYMENT"
CF_CO2HEDGING = "CO2HEDGING"

power_plant_status_operational = 'Operational'
power_plant_status_inPipeline = 'InPipeline'
power_plant_status_decommissioned = 'Decommissioned'
power_plant_status_to_be_decommissioned = 'TobeDecommissioned'
power_plant_status_not_set = 'NOTSET'
power_plant_status_strategic_reserve = 'InStrategicReserve'
#power_plant_status_capacity_mechanism = 'InCapacityMechanism'

future_prices = "futurePrice"
simulated_prices = "simulatedPrice"

modules_need_AMIRIS = ["run_short_investment_module" ,"run_capacity_market" , "run_strategic_reserve" ,
                       "run_strategic_reserve_swe" , "run_strategic_reserve_ger" , "run_forward_market",
                       "run_financial_results", "plotting"]
modules_need_bids = [ "run_financial_results", "run_capacity_market" , "run_strategic_reserve" , "run_strategic_reserve_swe" ,
                     "run_strategic_reserve_ger" , "run_forward_market" , "run_create_results", "plotting"]

# source directory is toolbox-amiris-emlab  for example C:\Users\isanchezjimene\Documents\TraderesCode\toolbox-amiris-emlab
# grandparentpath =  os.path.join(os.path.dirname(os.path.dirname(os.getcwd())))
# yearspath = os.path.join(grandparentpath, globalNames.years_path)

years_file = "years.txt"
continue_path = 'continue.txt'
#continue_path = os.path.join(parentpath, 'continue.txt')
parentpath =  os.path.join(os.path.dirname(os.getcwd()) )
#amiris_data_path =  os.path.join(parentpath, 'amiris_data_structure.xlsx')
amiris_data_path =  os.path.join(  parentpath, 'amiris_workflow\\amiris_data_structure.xlsx' )
load_path_DE = os.path.join(parentpath, 'amiris_workflow\\amiris-config\\data\\load.csv')
load_path_NL = os.path.join(parentpath, 'amiris_workflow\\amiris-config\\data\\load_NL.csv')
amiris_results_path =  os.path.join(parentpath,'amiris_workflow\\output\\amiris_results.csv')
amiris_RAWresults_path = os.path.join(parentpath,'amiris_workflow\\output\\raw\\EnergyExchangeMulti.csv')
power_plants_path = os.path.join(parentpath,'data\\Power_plants.xlsx')