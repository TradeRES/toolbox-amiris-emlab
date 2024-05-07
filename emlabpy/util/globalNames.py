import os
# in the initialization if there is missing too much capacity, too much of one caapacity would be installed
maximum_installed_share_initialization = 0.15

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
power_plant_status_decommissioned_from_SR = 'DecommissionedSR'

capacity_subscription = 'capacity_subscription'
capacity_market = "capacity_market"

power_plant_dispatch_plan_status_accepted = 'Accepted'
power_plant_dispatch_plan_status_failed = 'Failed'
power_plant_dispatch_plan_status_partly_accepted = 'Partly Accepted'
power_plant_dispatch_plan_status_awaiting = 'Awaiting'

capacity_mechanism_contracted = "contracted"
capacity_mechanism_not_contracted = "not contracted"

future_prices = "futurePrice"
simulated_prices = "simulatedPrice"

modules_need_AMIRIS = ["run_short_investment_module" , "run_financial_results", "plotting"]
modules_need_bids = [ "run_financial_results", "run_create_results", "plotting", "run_CRM"]

fuels_in_AMIRIS = ["NUCLEAR", "LIGNITE", "HARD_COAL", "NATURAL_GAS", "OIL", "OTHER", "HYDROGEN", "BIOMASS", "WASTE"]
# source directory is toolbox-amiris-emlab  for example C:\Users\isanchezjimene\Documents\TraderesCode\toolbox-amiris-emlab
technologies_not_in_SR =[ "Nuclear","Lithium ion battery", "Lithium ion battery 4"]

# yearspath = os.path.join(grandparentpath, globalNames.years_path)

years_file = "years.txt"
continue_path = 'continue.txt'
#continue_path = os.path.join(parentpath, 'continue.txt')
parentpath =  os.path.join(os.path.dirname(os.getcwd()) )

#amiris_data_path =  os.path.join(parentpath, 'amiris_data_structure.xlsx')
amiris_data_path =  os.path.join(  os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris_data_structure.xlsx' )
load_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\load.csv')
future_load_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\future_load.csv' )


windon_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\windon.csv' )
windoff_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\windoff.csv' )
pv_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\pv.csv' )

windon_firstyear_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\first_year_windon.csv' )
windoff_firstyear_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\first_year_windoff.csv' )
pv_firstyear_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\first_year_pv.csv' )


future_windon_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\future_windon.csv' )
future_windoff_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\future_windoff.csv' )
future_pv_file_for_amiris = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\future_pv.csv' )

input_data = os.path.join(os.path.dirname(os.getcwd()), 'data')
#input_data = os.path.join(parentpath, 'data\\VREprofilesandload2019-2050.xlsx')
input_load_de = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data\\load_DE.csv')
amiris_results_path =  os.path.join(os.path.dirname(os.getcwd()),'amiris_workflow\\output\\amiris_results.csv')
amiris_RAWresults_path = os.path.join(os.path.dirname(os.getcwd()),'amiris_workflow\\output\\raw\\EnergyExchange.csv')
hourly_generation_per_group_path = os.path.join(os.path.dirname(os.getcwd()),'amiris_workflow\\output\\hourly_generation_per_group.csv')
power_plants_path = os.path.join(os.path.dirname(os.getcwd()),'data\\Power_plants.xlsx')
scenarios_path = os.path.join(os.path.dirname(os.getcwd()),'emlabpy\\plots\\Scenarios\\')
amiris_config_data = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow\\amiris-config\\data' )
amiris_worklow = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow' )