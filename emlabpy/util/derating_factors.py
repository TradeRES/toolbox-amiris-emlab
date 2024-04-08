import os
from plots.plots import prepare_pp_status
from util.spinedb_reader_writer import *
import matplotlib.pyplot as plt
type = "sqlite:///"
folder = "C:\\toolbox-amiris-emlab\\emlabpy\\plots\\Scenarios\\"
first = type + folder
emlab_sql = "\\EmlabDB.sqlite"
amiris_sql = "\\AMIRIS db.sqlite"
energy_exchange_url_sql = "\\energy exchange.sqlite"
scenario_name = "NL-EOM"
emlab_url = first + scenario_name + emlab_sql
amiris_url = first + scenario_name + emlab_sql
spinedb_reader_writer = SpineDBReaderWriter("Amiris", emlab_url, amiris_url)
reps = spinedb_reader_writer.read_db_and_create_repository("plotting")
global years_to_generate
years_to_generate = list(range(reps.start_simulation_year, reps.current_year + 1))  # control the current year

global unique_technologies
unique_technologies = reps.get_unique_candidate_technologies_names()
annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_commissioned, \
    all_techs_capacity, last_year_in_pipeline, last_year_decommissioned, \
    last_year_operational_capacity, last_year_to_be_decommissioned_capacity, \
    last_year_strategic_reserve_capacity, capacity_per_status, number_per_status_last_year = \
    prepare_pp_status(years_to_generate, unique_technologies, reps)

yearly_electricity_prices = pd.DataFrame()
TotalAwardedPowerInMW = pd.DataFrame()
residual_load = pd.DataFrame()
DispatchSystemCostInEUR = pd.DataFrame()
hourly_load_shedded = pd.DataFrame()
hourly_load_shedders_per_year = pd.DataFrame()
hourly_industrial_heat = pd.DataFrame()
hourly_generation_res = pd.DataFrame()
derating_factor = pd.DataFrame()
for year in years_to_generate:
    year_excel = folder + scenario_name + "\\" + str(year) + ".xlsx"
    df = pd.read_excel(year_excel, sheet_name=["energy_exchange", "residual_load", "hourly_generation"])
    hourly_load_shedders = pd.DataFrame()
    for unit in df['hourly_generation'].columns.values:
        if unit[0:4] == "unit"  and unit[5:] != "8888888" :
            hourly_load_shedders[unit[5:]] = df['hourly_generation'][unit]
        elif unit =="PV":
            hourly_generation_res["Solar PV large"] = df['hourly_generation'][unit]
        elif unit =="WindOff":
            hourly_generation_res["Wind Offshore"] = df['hourly_generation'][unit]
        elif unit =="WindOn":
            hourly_generation_res["Wind Onshore"] = df['hourly_generation'][unit]
        elif unit =="storages_discharging":
            hourly_generation_res["Lithium ion battery"] = df['hourly_generation'][unit]
        elif unit =="conventionals":
            hourly_generation_res["hydrogen OCGT"] = df['hourly_generation'][unit]
        else:
            pass

    total_hourly_load_shedders = hourly_load_shedders.sum(axis=1)
    yearly_near_scarcity_hours =  total_hourly_load_shedders[total_hourly_load_shedders >0].index

    for tech in all_techs_capacity:
        if tech in all_techs_capacity.loc[year] and tech in hourly_generation_res.columns:
            installed_capacity = all_techs_capacity.loc[year, tech]
            average_generation = hourly_generation_res.loc[yearly_near_scarcity_hours, tech].mean()
            derating_factor.at[tech,year] = average_generation / installed_capacity
        else:
            pass


derating_factor.to_excel("derating_factors.xlsx")
axs21 = derating_factor.T.plot() #color=colors_unique_techs
axs21.set_axisbelow(True)
plt.xlabel('Years', fontsize='medium')
plt.ylabel('Derating factors (€/MWh)', fontsize='medium')
plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
plt.grid()
axs21.set_title(scenario_name + ' \n Derating factors')
plt.show()


