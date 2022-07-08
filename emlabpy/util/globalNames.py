import os

power_plant_dispatch_plan_status_accepted = 'Accepted'
power_plant_dispatch_plan_status_failed = 'Failed'
power_plant_dispatch_plan_status_partly_accepted = 'Partly Accepted'
power_plant_dispatch_plan_status_awaiting = 'Awaiting'

capacity_mechanism_contracted = "contracted"
capacity_mechanism_not_contracted = "not contracted"

power_plant_status_operational = 'Operational'
power_plant_status_inPipeline = 'InPipeline'
power_plant_status_decommissioned = 'Decommissioned'
power_plant_status_to_be_decommissioned = 'TobeDecommissioned'
power_plant_status_not_set = 'NOTSET'
power_plant_status_strategic_reserve = 'InStrategicReserve'
power_plant_status_capacity_mechanism = 'InCapacityMechanism'

future_prices = "futurePrice"
simulated_prices = "simulatedPrice"

modules_need_AMIRIS = ["run_short_investment_module" ,"run_capacity_market" , "run_strategic_reserve"]


# source directory is toolbox-amiris-emlab  for example C:\Users\isanchezjimene\Documents\TraderesCode\toolbox-amiris-emlab


years_path = "years.csv"
continue_path = 'continue.txt'
#continue_path = os.path.join(parentpath, 'continue.txt')
parentpath =  os.path.join(os.path.dirname(os.getcwd()) )
#amiris_data_path =  os.path.join(parentpath, 'amiris_data_structure.xlsx')
amiris_data_path =  os.path.join(  parentpath, 'amiris_workflow\\amiris_data_structure.xlsx' )
load_path = os.path.join(parentpath, 'amiris_workflow\\amiris-config\\data\\load.csv')
amiris_results_path =  os.path.join(parentpath,'amiris_workflow\\output\\amiris_results.csv')
