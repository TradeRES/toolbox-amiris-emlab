# -*- coding:utf-8 -*-

__version__ = "0.2.0"
__authors__ = "Felix Nitsch"
__maintainer__ = "Felix Nitsch"
__email__ = "felix.nitsch@dlr.de"

import csv
import os
from datetime import datetime, timedelta
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yaml
from fameio.scripts.convert_results import run as convert_results
from fameio.scripts.make_config import DEFAULT_CONFIG
from fameio.scripts.make_config import run as make_config
from fameio.source.cli import Config
from fameio.source.loader import load_yaml
from fameio.source.time import DATE_FORMAT
from fameio.source.time import FameTime
from ioproc.logger import mainlogger
from ioproc.tools import action
from mpl_toolkits.axes_grid1 import make_axes_locatable

from iovrmr_tools import (
    ensure_path_exists,
    filter_for_columns,
    get_excel_sheet,
    get_filter_type_lists,
    get_from_dict_or_default,
    insert_agents_from_map,
    insert_contracts_from_map,
    get_header,
    get_field,
    write_yaml,
    to_list,
    round_to_full_hour,
    ensure_given_data_matches_dims,
    check_if_window_too_large,
    raise_and_log_critical_error,
    get_all_csv_files_in_folder,
    AmirisOutputs,
    OPERATOR_AGENTS,
    SUPPORTED_AGENTS,
    EXCHANGE,
    sum_per_agent,
    call_function_per_agent,
)

_FOUND_POWER = "Searched for `power` information in agent '{}' with id '{}. Found {} MW for technology `{}`."
_FOUND_NO_POWER = "Searched for `power` information in agent '{}' with id '{}'. Found none."


class Amiris:
    """Defines names of parameters in the `scenario.yaml`"""

    time_step = "TimeStep"
    awarded_power_name = "AwardedPowerInMWH"

    technology_name_for_storage = "Storage"
    identifier_for_storage = "Device"
    capacitiy_name_for_storage = "PowerInMW"

    capacitiy_name = "InstalledPowerInMW"
    energy_carrier_name = "EnergyCarrier"
    fuel_type_name = "FuelType"
    prototype_name = "Prototype"

    exchange_type_name = "EnergyExchange"
    storage_type_name = "StorageTrader"
    renewable_type_name = "VariableRenewableOperator"
    conventional_type_name = "PredefinedPlantBuilder"
    biogas_type_name = "Biogas"
    conventional_plant_operator = "ConventionalPlantOperator"
    max_efficiency = "Markup In EUR Per MWh"
    min_efficiency = "Markdown In EUR Per MWh"

    region_name = "Region"

    OPERATOR_AGENTS = [
        renewable_type_name,
        conventional_type_name,
        biogas_type_name,
    ]
    FLEX_AGENTS = [storage_type_name]
    SUPPORTED_AGENTS = ["RenewableTrader", "SystemOperatorTrader"]


@action("general")
def parse_excel(dmgr, config, params):
    """
    Parses given `excelFile` for specified `excelSheets` as dataframe object with the specified `write_to_dmgr` name.
    `excelHeader` can be set to `True` or `False`.

    The action may be specified in the user.yaml as follows:
        - action1:
            project: general
            call: parse_excel
            data:
              read_from_dmgr: null
              write_to_dmgr: powerPlants
            args:
              excelFile: Kraftwerksliste_komplett.xlsx
              excelSheet: Kraftwerke
              excelHeader: True
    """
    args = params["args"]
    file = get_field(args, "excelFile")
    excel_sheet = get_excel_sheet(args)
    header = get_header(get_field(args, "excelHeader"))
    parsed_excel = pd.read_excel(io=file, sheet_name=excel_sheet, header=header)

    with dmgr.overwrite:
        dmgr[params["data"]["write_to_dmgr"]] = parsed_excel


@action("general")
def parse_csv(dmgr, config, params):
    """
    Parses given `csvFile` as dataframe object with the specified `write_to_dmgr` name.
    The default delimiter is `,` if not configured otherwise in `csvSeparator`.
    The user may also specify a `csvHeader` (int or list of int) and a `csvIndex` (int or list of int).

    The action may be specified in the user.yaml as follows:
        - action1:
            project: general
            call: parse_csv
            data:
              read_from_dmgr: null
              write_to_dmgr: highreso_data
            args:
              csvFile: amiris-config/data/High_Res_O_output.csv
              csvSeparator: ";"
              csvHeader: [0, 1]
              csvIndex: [0, 1]
    """
    args = params["args"]
    file = get_field(args, "csvFile")

    separator = get_from_dict_or_default("csvSeparator", args, ",")

    header = get_from_dict_or_default("csvHeader", args, None)
    if header:
        header = to_list(header)

    index_col = get_from_dict_or_default("csvIndex", args, None)
    if index_col:
        index_col = to_list(index_col)

    parsed_data = pd.read_csv(file, sep=separator, header=header, index_col=index_col)

    with dmgr.overwrite:
        dmgr[params["data"]["write_to_dmgr"]] = parsed_data


@action("general")
def convert_time(dmgr, config, params):
    """
    Converts index in data specified in `read_from_dmgr` from given data to datetime string
    to date format as defined in `fameio`. Start year is derived from the original multiindex assuming that the first
    value is the year.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: convert_time
        data:
          read_from_dmgr: highreso_data
          write_to_dmgr: highreso_data_converted
    """
    data = dmgr[params["data"]["read_from_dmgr"]]
    start_year = data.index[0][0]

    # TODO: needs refactoring to account for missing time steps
    new_index = [d.strftime(DATE_FORMAT) for d in pd.date_range(str(start_year), periods=len(data.index), freq="60min")]
    data.index = new_index

    with dmgr.overwrite:
        dmgr[params["data"]["write_to_dmgr"]] = data


@action("general")
def filter_data(dmgr, config, params):
    """
    Action to filter specified input data with given filters.
    Filters are applied on the data set for the specified 'column'. Each entry of the resulting
    filtered data set is matching all filter 'value' entries specified in the dictionary of 'intersectingFilters'.
    Filters are applied consecutively narrowing down the set of matching values. If no explicit filter `type` is
    specified, `type` "EQUAL" is assumed. Otherwise, the following list of numeric filters may be specified
    "EQUAL", "GREATER", "GREATEREQUAL", "LESS" or "LESSEQUAL".

    The action may be specified in the user.yaml as follows:
        - action2:
            project: general
            call: filter_data
            data:
              read_from_dmgr: powerPlants
              write_to_dmgr: powerPlants_filtered
            args:
              intersectingFilters:
                - column: COUNTRY
                  values: ['GERMANY']
                - column: FUEL
                  values: 'UR'
    """
    args = params["args"]

    filters = args["intersectingFilters"]
    data = dmgr[params["data"]["read_from_dmgr"]]

    filter_columns = [x["column"] for x in filters]
    filter_value_lists = [x["values"] for x in filters]
    filter_type_lists = get_filter_type_lists(filters)

    matching_entries = filter_for_columns(data, filter_columns, filter_value_lists, filter_type_lists)

    with dmgr.overwrite:
        dmgr[params["data"]["write_to_dmgr"]] = matching_entries


@action("general")
def translate_data(dmgr, config, params):
    """
    Translates values in given data set based on definition in `translationDirective`. In specified `fields` which
    are the column names of the data set, the `origin` value is mapped to a `target` value. If `origin` is set to `'*'`,
    all entries are translated to `target`.

    The action may be specified in the user.yaml as follows:
        - action3:
            project: general
            call: translate_data
            data:
              read_from_dmgr: powerPlants_filtered
              write_to_dmgr: powerPlants_translated
            args:
              translationDirective: translationFieldMap
    """
    data = dmgr[params["data"]["read_from_dmgr"]]
    args = params["args"]

    translation_map = config["user"][args["translationDirective"]]

    for translation in translation_map["Translation"]:
        field = get_field(translation, "column")
        for item in translation["map"]:
            origin = get_field(item, "origin")
            target = get_field(item, "target")

            if origin == "*":
                data[field] = target
            else:
                data.loc[data[field] == origin, field] = target

    with dmgr.overwrite:
        dmgr[params["data"]["write_to_dmgr"]] = data


@action("general")
def write_AMIRIS_config(dmgr, config, params):
    """
    Writes AMIRIS specific configuration file in .yaml format by parsing `AMIRISConfigFieldMap` for maps of `Agents` and
    `Contracts`. The resulting full config file is written to the specified `outputFile` in the globally defined
    `output: filePath`.

    The action may be specified in the user.yaml as follows:
        - action4:
            project: general
            call: write_AMIRIS_config
            data:
              read_from_dmgr: powerPlants_translated_DE
              write_to_dmgr: null
            args:
              AMIRISConfigFieldMap: conventionalsFieldMap.yaml
              templateFile: scenario_template.yaml
              outputFile: scenario.yaml
    """
    data = dmgr[params["data"]["read_from_dmgr"]]
    args = params["args"]

    config_file = load_yaml(args["templateFile"])

    output_params = config["user"]["global"]["output"]
    output_path = output_params["filePath"] + "/"
    ensure_path_exists(output_path)
    output_file_path = output_path + args["outputFile"]

    amiris_maps = to_list(args["AMIRISConfigFieldMap"])
    for amiris_map in amiris_maps:
        translation_map = load_yaml(amiris_map)
        config_file, inserted_agents = insert_agents_from_map(data, translation_map["Agents"], config_file)
        config_file = insert_contracts_from_map(inserted_agents, translation_map["Contracts"], config_file)

    write_yaml(config_file, output_file_path)


@action("general")
def create_AMIRIS_protobuf(dmgr, config, params):
    """
    Calls the `fameio` package and converts given `input` config file to AMIRIS specific protobuf file.
    If no `output` path in the action definition is specified, the protobuf is saved as 'config.pb' to path as defined
    in `global->output->filePath`.

    The action may be specified in the user.yaml as follows:
        - action:
            project: general
            call: create_AMIRIS_protobuf
            data:
              read_from_dmgr: null
              write_to_dmgr: null
            args:
              input: output/scenario.yaml
              output: output/config.pb
    """
    args = params["args"]

    if "output" in args:
        output_path = args["output"]
        filename, file_extension = os.path.splitext(output_path)
        if file_extension != ".pb":
            raise_and_log_critical_error(
                "Provide a path to a config.pb file including the '.pb' extension. "
                "Got '{}' instead.".format(output_path)
            )
        input_path = args["input"]

    else:
        global_output_params = config["user"]["global"]["output"]
        output_path = global_output_params["filePath"] + "/"
        input_path = os.path.abspath(output_path + args["input"])
        output_path = os.path.abspath(output_path + DEFAULT_CONFIG[Config.OUTPUT])

    config = {
        Config.LOG_LEVEL: "info",
        Config.LOG_FILE: None,
        Config.OUTPUT: output_path,
    }

    make_config(input_path, config)


@action("general")
def write_timeseries(dmgr, config, params):
    """
    Writes data of tag `read_from_dmgr` to `.csv`file or multiple .csv files for each column when `multipleFileExport`
    is set to `True` (default is `False`).
    The user may limit the export to specific `columns_to_export`. If not specified, all columns are exported as is.
    Header is exported when `header` is `True` (default is `True`).
    Separator and output path are derived from the `global` `output`.

    The action may be specified in the user.yaml as follows:
      - action:
          project: general
          call: write_timeseries
          data:
            read_from_dmgr: timeSeries_corrected_load
            write_to_dmgr: Null
          args:
            multipleFileExport: True
            header: False
            columns_to_export: UNITID, PLANT
    """

    data = dmgr[params["data"]["read_from_dmgr"]]

    output_params = config["user"]["global"]["output"]
    output_path = output_params["filePath"] + "/export"
    ensure_path_exists(output_path)

    args = params["args"]

    if "columns_to_export" in args:
        columns_to_export = to_list(params["args"]["columns_to_export"])
        data = data[columns_to_export]

    header = get_from_dict_or_default("header", args, True)

    if "multipleFileExport" in args:
        if args["multipleFileExport"]:
            for column in data:
                file_name = "_".join(column).replace(" ", "_")
                data[column].to_csv(
                    output_path + "/{}.csv".format(file_name),
                    sep=output_params["csvSeparator"],
                    header=header,
                )
            return

    data.to_csv(
        path_or_buf=output_path + "/export_{}.csv".format(params["data"]["read_from_dmgr"]),
        sep=output_params["csvSeparator"],
        header=header,
    )


@action("general")
def convert_pb(dmgr, config, params):
    """
    Calls the `convertFameResults` routine provided by the `fameio` package to convert `pbFile` in `pbDir`
    (as defined in the `global` section of the `user.yaml`). The files are written to `pbOutputRaw`.
    You may specify certain `agentsToExtract` given in a list. This limits the conversion of results to the ones
    specified.

    The action may be specified in the user.yaml as follows:
    - action:
        project: general
        call: convert_pb
        args:
          agentsToExtract: ['MyAgent1', 'MyAgent2']
    """
    agents_to_extract = None

    if "args" in params:
        if "agentsToExtract" in params["args"]:
            agents_to_extract = to_list(params["args"]["agentsToExtract"])

    run_config = {
        Config.LOG_LEVEL: "info",
        Config.LOG_FILE: None,
        Config.AGENT_LIST: agents_to_extract,
        Config.OUTPUT: config["user"]["global"]["output"]["pbOutputRaw"],
        Config.SINGLE_AGENT_EXPORT: False,
    }

    ensure_path_exists(run_config[Config.OUTPUT])

    if config["user"]["global"]["pbDir"]:
        path_to_pb = config["user"]["global"]["pbDir"] + config["user"]["global"]["pbFile"]
    else:
        path_to_pb = config["user"]["global"]["pbFile"]

    convert_results(path_to_pb, run_config)


@action("general")
def run_AMIRIS(dmgr, config, params):
    """
    Invokes the AMIRIS model and executes simulation for `input` with specified parameters in `model`.
    `jar` is the compiled AMIRIS model which can be exchanged when an updated model is available.
    The arguments `vm` and `runner` can be used to specify the virtual machine and the runner configuration.
    Additionally, `fame_args` can be defined in the respective file.
    If no path to `fame_setup` file is provided, `fameSetup.yaml` is used instead.

    The action may be specified in the user.yaml as follows:
    - action:
          project: general
          call: run_AMIRIS
          args:
            input: output/config.pb
            model:
              jar: 'amiris/midgard/amiris-core_1.2-jar-with-dependencies.jar'
              vm: '-ea -Xmx2000M'
              fame_args: '-Dlog4j.configuration=file:amiris/log4j.properties'
              runner: 'de.dlr.gitlab.fame.setup.FameRunner'
              fame_setup: 'amiris/fameSetup.yaml'
    """
    args = params["args"]
    model = args["model"]

    fame_setup_path = model["fame_setup"] if "fame_setup" in model else "fameSetup.yaml"

    with open(fame_setup_path, "r") as stream:
        try:
            fame_setup = yaml.safe_load(stream)
        except yaml.YAMLError:
            raise_and_log_critical_error("Cannot open fame setup file in {}.".format(fame_setup_path))

    ensure_path_exists(fame_setup["outputPath"])

    call = "java {} -cp {} {} {} -f {} -s {}".format(
        model["vm"],
        model["jar"],
        model["fame_args"],
        model["runner"],
        args["input"],
        fame_setup_path,
    )

    os.system(call)


def get_region_of_all_exchanges(scenario: dict) -> dict:
    """Returns {ID: region_name, ...} map for `EnergyExchange` in given `scenario`. If no region is found, the string `Region` is applied"""
    try:
        exchanges = [
            {exchange["Id"]: exchange["Attributes"]["Region"]}
            for exchange in scenario["Agents"]
            if exchange["Type"] == "EnergyExchange"
        ]
    except KeyError:
        exchanges = [
            {exchange["Id"]: "Region"} for exchange in scenario["Agents"] if exchange["Type"] == "EnergyExchange"
        ]
    output = {}
    for exchange in exchanges:
        output.update(exchange)
    return output


@action("general")
def compile_price_exchange_file(dmgr, config, params):
    """
    Parses the `agent` csv file and converts the `fame_time_steps` into `datetime` strings.
    The `indexColumn` has to be specified.
    Further, a `mapping` of columns can be provided as dict with the origin values as `key` and the target values as
    `value`.
    The export is performed by a `groupby` specification which defines the columns for which a sum of all remaining
    column values is conducted.
    Replaces `Id` with `Region` name retrieved from specified `scenario` yaml where all `Exchanges` are parsed.
    If only one EnergyExchange is found, the value "Region" is applied.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: compile_price_exchange_file
        args:
          agent: EnergyExchange
          indexColumn: 'TimeStep'
          mapping:
            TimeStep: Time
            AgentId: Region
          groupby: ["Time", "Region"]
          scenario: "../couple_markets_AT-DE/data/scenario.yaml"
    """
    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    agent = args["agent"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    ensure_path_exists(output_folder_path)

    parsed_data = pd.read_csv(
        filepath_or_buffer=folder_name + "/" + agent + ".csv",
        sep=config["user"]["global"]["output"]["csvSeparator"],
    )

    index_label = args["indexColumn"]

    if "mapping" in args:
        parsed_data.rename(columns=args["mapping"], inplace=True)
        index_label = args["mapping"][index_label]

    parsed_data[index_label] = [
        time.replace("_", " ") for time in convert_fame_time_to_datetime(parsed_data[index_label])
    ]
    parsed_data = parsed_data.groupby(to_list(args["groupby"]), as_index=False).sum()
    parsed_data.set_index(index_label, inplace=True)
    parsed_data.rename(
        {"ElectricityPriceInEURperMWH": "Electricity Price In EUR Per MWh"},
        axis=1,
        inplace=True,
    )

    output = parsed_data.reset_index()[["Time", "Region", "Electricity Price In EUR Per MWh"]]

    scenario = load_yaml(args["scenario"])
    region_map = get_region_of_all_exchanges(scenario)

    output["Region"].replace(region_map, inplace=True)

    year = get_simulation_year_from(scenario)
    run_name = config["user"]["global"]["pbFile"].split(".")[0]
    run_id = get_runid_from(scenario)
    institution = "DLR"
    value = "Electricity-Prices-In-EUR-Per-MWh"
    file_name = "{}_{}_{}_{}_{}.csv".format(str(year), run_name, run_id, institution, value)

    output.to_csv(
        path_or_buf=output_folder_path + file_name,
        sep=config["user"]["global"]["output"]["csvSeparator"],
        index=None,
    )


def convert_fame_time_to_datetime(fame_times):
    """Returns converted `fame_times` (index format) as `date_times` (list of strings) rounded to minutes"""
    date_times = list()
    for timestep in fame_times.values:
        timestep = round_to_full_hour(timestep)
        date_times.append(FameTime.convert_fame_time_step_to_datetime(timestep))
    return date_times


def get_dict_with_installed_power_by_id(scenario):
    """Returns dict with `Id` and `InstalledPowerInMW` for all eligible agents in given `scenario`"""
    agents_with_installed_power = dict()

    for agent in scenario["Agents"]:
        if "Attributes" in agent:
            if "InstalledPowerInMW" in agent["Attributes"]:
                capacity = agent["Attributes"]["InstalledPowerInMW"]
                agents_with_installed_power[agent["Id"]] = capacity

    return agents_with_installed_power


def get_installed_power_by_technology(scenario: dict, single_file_mode=False) -> pd.DataFrame:
    """
    Parses given `scenario` looking for agents with attributes.
    If `InstalledPowerInMW` is found capacity is added for technology specified either by `EnergyCarrier` or `FuelType`.
    If `Device` is found in agent attributes, the `technology` `STORAGE` is used.

    Returns pd.DataFrame with aggregated `InstalledPowerInMW` by `Type` or (if `single_file_mode` is enabled)
    each `region_name` in `scenario` with `InstalledPowerInMW` per `Type`.
    """
    output_labels = ["Energy Carrier", "Region", "Installed Capacity In MW"]
    output_labels_no_region = ["Energy Carrier", "Installed Capacity In MW"]

    installed_power_by_type = get_installed_power_by_tech_from(scenario)

    if single_file_mode:
        all_plants = get_all_plants_from(scenario)
        agents_with_matched_regions = match_agent_to_technology(all_plants, installed_power_by_type)
        installed_power_by_type = aggregate_technologies(agents_with_matched_regions, output_labels)
    else:
        for technology in installed_power_by_type:
            installed_power_by_type[technology] = sum(
                [sum(list(entry.values())) for entry in installed_power_by_type[technology]]
            )
        installed_power_by_type = pd.DataFrame(
            installed_power_by_type.items(),
            index=None,
            columns=output_labels_no_region,
        )

    return installed_power_by_type


def aggregate_technologies(agents_with_matched_regions, output_labels) -> pd.DataFrame:
    """Returns pd.Dataframe of `EnergyCarrier`, `Region`, `Installed capacities` (names defined in output_labels)"""
    for region in agents_with_matched_regions:
        aggregated_techs = {}
        for item in agents_with_matched_regions[region]:
            for technology in item.keys():
                aggregated_techs[technology] = aggregated_techs.get(technology, 0) + item[technology]
        agents_with_matched_regions[region] = aggregated_techs
    installed_power_by_type = (
        pd.DataFrame(agents_with_matched_regions).stack().reset_index().set_axis(output_labels, axis=1)
    )
    return installed_power_by_type


def match_agent_to_technology(all_plants: list, installed_power_by_type: list) -> dict:
    """Returns `dict` where all agents {id: capacity} are matched to a technology"""
    output = {}
    for technology in installed_power_by_type:
        for plant in installed_power_by_type[technology]:
            for agent_id, capacity in plant.items():
                region = next(i[Amiris.region_name] for i in all_plants if i["Id"] == agent_id)
                output.setdefault(region, []).append({technology: capacity})
    return output


def get_installed_power_by_tech_from(scenario: dict) -> dict:
    """
    Returns `dict` of technologies each with list of {agent_id: installed capacity} from given `scenario`
    Allows that `Form` is specified in a agents' attributes to separate technologoes of same fuel_type_name further
    """
    installed_power_by_type = dict()

    for agent in scenario["Agents"]:
        if "Attributes" in agent:
            if Amiris.capacitiy_name in agent["Attributes"]:
                capacity = agent["Attributes"][Amiris.capacitiy_name]
                if Amiris.energy_carrier_name in agent["Attributes"]:
                    technology = agent["Attributes"][Amiris.energy_carrier_name]
                elif Amiris.fuel_type_name in agent["Attributes"][Amiris.prototype_name]:
                    if "Form" in agent["Attributes"]:
                        technology = agent["Attributes"]["Form"]
                    else:
                        technology = agent["Attributes"][Amiris.prototype_name][Amiris.fuel_type_name]
                else:
                    raise_and_log_critical_error(
                        "Found no eligible technology for agent '{}' with id '{}'".format(agent, agent["Id"])
                    )
                installed_power_by_type.setdefault(technology, []).append({agent["Id"]: capacity})
                mainlogger.info(_FOUND_POWER.format(agent["Type"], agent["Id"], capacity, technology))
            if Amiris.identifier_for_storage in agent["Attributes"]:
                capacity = agent["Attributes"][Amiris.identifier_for_storage][Amiris.capacitiy_name_for_storage]
                technology = Amiris.technology_name_for_storage
                installed_power_by_type.setdefault(technology, []).append({agent["Id"]: capacity})
                mainlogger.info(_FOUND_POWER.format(agent["Type"], agent["Id"], capacity, technology))
        else:
            mainlogger.info(_FOUND_NO_POWER.format(agent["Type"], agent["Id"]))

    return installed_power_by_type


def get_all_plants_from(scenario: dict) -> list:
    """Returns list of all plants with `Id`, `Type`, `Region` (default: "Region") from given `scenario` by searching relevant contracts"""
    contracts = scenario["Contracts"]

    exchanges = get_agent_with_id_and_type_and_region_from(scenario, Amiris.exchange_type_name)
    storages = get_agent_with_id_and_type_and_region_from(scenario, Amiris.storage_type_name)
    renewables = get_agent_with_id_and_type_and_region_from(scenario, Amiris.renewable_type_name)
    conventionals = get_agent_with_id_and_type_and_region_from(scenario, Amiris.conventional_type_name)
    # todo look for more elegant way to add biogas to res
    biogas = get_agent_with_id_and_type_and_region_from(scenario, Amiris.biogas_type_name)
    extended_res = renewables + biogas

    for storage in storages:
        contract_to_exchange = get_contract_from_sender_with_product(storage["Id"], "Bids", contracts)
        storage[Amiris.region_name] = get_region_of_connected_exchange(exchanges, contract_to_exchange)
    for plant in extended_res:
        trader_id = get_trader_id_for(plant["Id"], "SetRegistration", contracts)
        contract_to_exchange = get_contract_from_sender_with_product(trader_id, "Bids", contracts)
        plant[Amiris.region_name] = get_region_of_connected_exchange(exchanges, contract_to_exchange)
    for plant in conventionals:
        operator_id, plant_index_in_list = get_operator_id_for(plant, contracts)
        trader_id = get_trader_id_for(operator_id, "MarginalCostForecast", contracts, plant_index_in_list)
        contract_to_exchange = get_contract_from_sender_with_product(trader_id, "Bids", contracts)
        plant[Amiris.region_name] = get_region_of_connected_exchange(exchanges, contract_to_exchange)
    all_plants_with_regions = storages + renewables + conventionals + biogas

    return all_plants_with_regions


def get_trader_id_for(agent_id: int, product: str, contracts: list, plant_index_in_list=0) -> int:
    """Returns `trader_id` for agent_id looking for `product` in `contracts` considering position as stated in `plant_index_in_list`"""
    contract_to_trader = get_contract_from_sender_with_product(agent_id, product, contracts)
    trader_id = to_list(contract_to_trader["ReceiverId"])[plant_index_in_list]
    return trader_id


def get_agent_with_id_and_type_and_region_from(scenario: dict, agent_type_name: str) -> list:
    """Returns list of `{Id: agent_id, Type: agent_type_name, Region: (default: None)}` for all agents of type `agent_type_name` in given `scenario`"""
    try:
        return [
            {
                "Id": agent["Id"],
                "Type": agent_type_name,
                "Region": get_from_dict_or_default(Amiris.region_name, agent["Attributes"], None),
            }
            for agent in scenario["Agents"]
            if agent["Type"] == agent_type_name
        ]
    except KeyError:
        raise_and_log_critical_error("Failed looking for agent_type `{}` in given scenario.".format(agent_type_name))


def get_region_of_connected_exchange(exchanges: list, contract: dict) -> str:
    """Returns `region` of connected exchange from `ReceiverId` in `contract`, returns "Region" if not found"""
    _NOT_EXACTLY_ONE_EXCHANGE = "Your criteria match {} exchanges. Expected to find single exchange in " "Contract {}."
    exchange = [exchange for exchange in exchanges if exchange["Id"] == contract["ReceiverId"]]

    assert len(exchange) == 1, _NOT_EXACTLY_ONE_EXCHANGE.format(len(exchange, contract))

    if exchange[0]["Region"] is None:
        return "Region"
    else:
        return exchange[0]["Region"]


def get_contract_from_sender_with_product(sender_id: int, product_name: str, contracts: list) -> dict:
    """
    Returns single contract from `sender` with `product_name` found in `contracts`, raises AssertionError otherwise
    """
    _NOT_EXACTLY_ONE_CONTRACT = (
        "Your criteria match {} contracts. Expected to find single contract with "
        "`SenderId` '{}' and `ProductName` '{}'."
    )

    contract = [
        contract
        for contract in contracts
        if contract["ProductName"] == product_name
        if sender_id in to_list(contract["SenderId"])
    ]

    assert len(contract) == 1, _NOT_EXACTLY_ONE_CONTRACT.format(len(contract), sender_id, product_name)

    return contract[0]


@action("general")
def plot_lines(dmgr, config, params):
    """
    Generates `m` x `n` line plot for given `window` size for specified `agent`.
    You may specify a conversion to datetime format from `fame` `timesteps` by enabling `convertToDateTime`.
    The plot specifics are defined in `figure` and the plot data in list of `plotData`.
    You may specify a `ylim` as a reference to another subplot which limits to scale of the y-axis.`ylabel` sets the name of the y-axis.
    A renaming of values can be defined in `map` with keys as `origins` (old values) and values as `targets` (new values).
    `conversion` allows to convert to different units.
    A `watermark` is printed if stated `true`.

    Make sure that the number of items in `plotData` matches your `figure` dimensions specified as `ncols` and `nrows`.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: plot_lines
        args:
          agent: EnergyExchange
          time:
            convertToDateTime: true
            originName: TimeStep
            targetName: DateTime
          groupby: ["DateTime", "AgentId"]
          window: 168
          figure:
            width: 18
            height: 9
            dpi: 80
            ncols: 2
            nrows: 2
          map:
            AgentId:
              1: "Market A"
              6: "Market B"
              60: "Market C"
              600: "Market D"
          watermark: True
          plotData:
            - column: 'ElectricityPriceInEURperMWH'
              title: 'Electricity Price In EUR per MWh'
              position: [0, 0]
              ylabel: "EUR/MWh"
            - column: 'CoupledElectricityPriceInEURperMWH'
              title: 'Coupled Electricity Price In EUR per MWh'
              position: [0, 1]
              ylimFrom: [0, 0]
              ylabel: "EUR/MWh"
            - column: 'CoupledTotalAwardedPowerInMW'
              title: 'Coupled Total Awarded Power In GW'
              position: [1, 1]
              ylabel: "GW"
              conversion: 0.001
            - column: 'TotalAwardedPowerInMW'
              title: 'Total Awarded Power In GW'
              position: [1, 0]
              ylimFrom: [1, 1]
              ylabel: "GW"
              conversion: 0.001
    """
    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    agent_name = args["agent"]

    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    ensure_path_exists(output_folder_path)

    x_dim = args["figure"]["ncols"]
    y_dim = args["figure"]["nrows"]

    ensure_given_data_matches_dims(x_dim, y_dim, args["plotData"])

    parsed_data = pd.read_csv(
        filepath_or_buffer=folder_name + "/" + agent_name + ".csv",
        sep=config["user"]["global"]["output"]["csvSeparator"],
    )

    if args["time"]["convertToDateTime"]:
        parsed_data = convert_to_datetime(args, parsed_data)

    grouped_data = parsed_data.groupby(to_list(args["groupby"]), as_index=False).sum()

    if "map" in args:
        for element in args["map"]:
            grouped_data["AgentId"].replace(args["map"][element], inplace=True)

    sns.set_theme()

    window = args["window"]
    time_col_name = args["time"]["targetName"]
    begin = grouped_data[time_col_name].min()
    end = begin + timedelta(hours=window)
    check_if_window_too_large(end, grouped_data[time_col_name].max())

    output_path = output_folder_path + "/plots/"
    ensure_path_exists(output_path)

    while end < grouped_data[time_col_name].max():
        data = grouped_data[grouped_data[time_col_name].between(begin, end)]

        f, a = plt.subplots(
            nrows=y_dim,
            ncols=x_dim,
            figsize=(args["figure"]["width"], args["figure"]["height"]),
        )

        if x_dim == 1 and y_dim == 1:
            a = [a]

        for subplot in args["plotData"]:
            selection = (*args["groupby"], subplot["column"])
            plot_data = data.pivot(*selection)

            if "conversion" in subplot:
                plot_data = data.pivot(*selection) * subplot["conversion"]

            pos_x = subplot["position"][0]
            pos_y = subplot["position"][1]

            ylim = get_from_dict_or_default("ylimFrom", subplot, None)
            if ylim:
                if x_dim == 1 or y_dim == 1:
                    ylim = a[subplot["ylimFrom"][0]].get_ylim()
                else:
                    ylim = a[subplot["ylimFrom"][0], subplot["ylimFrom"][1]].get_ylim()

            if x_dim == 1:
                s = pos_x
            elif y_dim == 1:
                s = pos_y
            else:
                s = (pos_x, pos_y)

            plot_data.plot(
                ax=a[s],
                title=subplot["title"],
                ylim=ylim,
                label="Test",
                legend=0,
            )
            a[s].set_ylabel(subplot["ylabel"])
            a[s].set_xlabel("")
            a[s].grid(True, which="both")

        if x_dim == 1 or y_dim == 1:
            lines, labels = a[0].get_legend_handles_labels()
        else:
            lines, labels = a[0][0].get_legend_handles_labels()
        f.legend(lines, labels, loc="lower center", ncol=len(labels))

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)

        if get_from_dict_or_default("watermark", args, False):
            f.text(
                0.01,
                0.01,
                config["user"]["global"]["pbFile"],
                fontsize=8,
                c="grey",
            )
        time_string = datetime.strftime(begin, format="%Y-%m-%d_%H%M")
        plt.savefig(
            fname=output_path
            + agent_name
            + "_"
            + time_string[:-5]
            + "_"
            + str(window)
            + "_"
            + str(x_dim)
            + "X"
            + str(y_dim)
            + ".png",
            dpi=args["figure"]["dpi"],
        )
        begin += timedelta(hours=window)
        end += timedelta(hours=window)
        plt.close("all")
    sns.reset_orig()


def convert_to_datetime(args, parsed_data):
    """Converts `fame` time to `datetime`"""
    origin_name = args["time"]["originName"]
    target_name = args["time"]["targetName"]
    parsed_data[target_name] = [round_to_full_hour(x) for x in parsed_data[origin_name]]
    parsed_data[target_name] = [
        datetime.strptime(FameTime.convert_fame_time_step_to_datetime(x), DATE_FORMAT) for x in parsed_data[target_name]
    ]
    parsed_data = parsed_data.drop(labels=origin_name, axis=1)
    return parsed_data


@action("general")
def analyse_time_series(dmgr, config, params):
    """
    Reads `.csv` of given `agent` and performs `time` conversion from `fame timesteps` to `datetime` (if enabled).
    Writes standard statistical parameters (min, max, mean, etc.) for each `column` specified in `analysis` to disk.
    When `consoleOutput is set to `True`, the output gets also printed to the console.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: analyse_time_series
        args:
          agent: ElectricityExchange
          time:
            convertToDateTime: true
            originName: TimeStep
            targetName: DateTime
          analysis:
            - column: 'ElectricityPriceInEURperMWH'
              countNumberOfValue: 3000
          consoleOutput: True
    """
    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    agent_name = args["agent"]

    parsed_data = pd.read_csv(
        filepath_or_buffer=folder_name + "/" + agent_name + ".csv",
        sep=config["user"]["global"]["output"]["csvSeparator"],
    )

    if args["time"]["convertToDateTime"]:
        parsed_data = convert_to_datetime(args, parsed_data)

    grouped_data = parsed_data.groupby(to_list(args["groupby"]), as_index=False).sum()
    grouped_data_by_agentid = {key: value for (key, value) in grouped_data.groupby("AgentId")}

    ensure_path_exists(output_folder_path)

    for evaluation in args["analysis"]:
        column = evaluation["column"]
        file_name = output_folder_path + "analysis_" + column + ".txt"

        file = open(file_name, "w")
        for agent_id, data in grouped_data_by_agentid.items():
            selected_data = data[column]
            write_to_file(
                file,
                "`{}` for Agent with Id `{}`".format(column, str(agent_id)),
                args["consoleOutput"],
            )
            write_to_file(
                file,
                "{}".format(selected_data.describe().reset_index().to_string(header=None, index=None)),
                args["consoleOutput"],
            )
            write_to_file(
                file,
                "`{}` occurances: {}".format(
                    evaluation["countNumberOfValue"],
                    len(selected_data[selected_data == evaluation["countNumberOfValue"]]),
                ),
                args["consoleOutput"],
            )
            write_to_file(file, "-" * 40, args["consoleOutput"])


def write_to_file(file, text, print_to_console=False):
    """Writes `text` to `file` and additionally to console if `print_to_console` is `True`"""
    file.write(text + "\n")
    if print_to_console:
        print(text)


@action("general")
def plot_price_duration_curve(dmgr, config, params):
    """
    Generates a price duration plot for a specified exchange `agent`. For this, values in `column` are sorted in ascending
    order and plotted against time. If you provide a `csv` file to `backtestAgainst`, you will receive an additional
    dashed curve to validate against a provided timeseries.
    You may specify a conversion to datetime format from `fame` `timesteps` by enabling `convertToDateTime`.
    The plot specifics are defined in `figure`.
    A renaming of names can be defined in `map` with keys as `origins` (old values) and values as `targets` (new values).
    `ylabel`  defines the labelling of the y-axis, whereas the x-axis is always called `hours`.
    A `watermark` is printed if stated `true`.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: plot_price_duration_curve
        args:
          agent: EnergyExchange
          column: 'ElectricityPriceInEURperMWH'
          time:
            convertToDateTime: true
            originName: TimeStep
            targetName: DateTime
          groupby: [ "DateTime", "AgentId" ]
          figure:
            width: 16
            height: 7
            dpi: 80
          map:
            AgentId:
              1: "Market A"
              6: "Market B"
              60: "Market C"
              600: "Market D"
          backtestAgainst: file.csv
          ylabel: 'EUR/MWh'
          watermark: True
    """
    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    agent_name = args["agent"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]

    parsed_data = pd.read_csv(
        filepath_or_buffer=folder_name + "/" + agent_name + ".csv",
        sep=config["user"]["global"]["output"]["csvSeparator"],
    )

    if args["time"]["convertToDateTime"]:
        parsed_data = convert_to_datetime(args, parsed_data)

    grouped_data = parsed_data.groupby(to_list(args["groupby"]), as_index=False).sum()

    if "map" in args:
        for element in args["map"]:
            grouped_data["AgentId"].replace(args["map"][element], inplace=True)

    sns.set_theme()

    output_path = output_folder_path + "/plots/"
    ensure_path_exists(output_path)

    f, a = plt.subplots(
        nrows=1,
        ncols=1,
        figsize=(args["figure"]["width"], args["figure"]["height"]),
    )
    selection = (*args["groupby"], args["column"])
    plot_data = grouped_data.pivot(*selection)

    for i, col in enumerate(plot_data.columns):
        sorted_data = plot_data[col].copy().sort_values(axis=0)
        sorted_data.plot(ax=a, legend=0, use_index=False)

    if "backtestAgainst" in args:
        backtest_data = pd.read_csv(
            filepath_or_buffer=args["backtestAgainst"],
            sep=config["user"]["global"]["output"]["csvSeparator"],
            names=[args["time"]["originName"], "Backtest"],
        )
        backtest_data = convert_to_datetime(args, backtest_data)
        backtest_data.set_index(args["time"]["targetName"], inplace=True)
        backtest_data = backtest_data.copy().sort_values(axis=0, by="Backtest")
        backtest_data.plot(ax=a, legend=0, use_index=False, linestyle="--", c="black")

    a.set_ylabel(args["ylabel"])
    a.set_xlabel("Hours")
    plt.suptitle("")
    plt.title(str(grouped_data[args["time"]["targetName"]].min().year), size=20)
    a.grid(True, which="both")

    lines, labels = a.get_legend_handles_labels()
    f.legend(
        lines,
        labels,
        loc="lower center",
        ncol=len(labels),
        bbox_to_anchor=(0.5, 0.06),
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.26)

    if get_from_dict_or_default("watermark", args, False):
        f.text(
            0.01,
            0.01,
            config["user"]["global"]["pbFile"],
            fontsize=8,
            c="grey",
        )
    plt.savefig(
        fname=output_path + agent_name + "_" + args["column"] + "_price_duration.png",
        dpi=args["figure"]["dpi"],
    )
    plt.close("all")
    sns.reset_orig()


@action("general")
def plot_multiple_lines(dmgr, config, params):
    """
    Generates `m` x `n` line plot for given `window` size for specified `agent`.
    If you provide a `csv` file to `backtestAgainst`, you will receive an additional
    dashed curve to validate against a provided timeseries.
    You may specify a conversion to datetime format from `fame` `timesteps` by enabling `convertToDateTime`.
    The plot specifics are defined in `figure` and the plot data in list of `plotData`.
    `ymin` and `ymax` define global lower and upper limits for the y-axis.
    `ylabel` sets the name of the y-axis.
    A renaming of values can be defined in `map` with keys as `origins` (old values) and values as `targets` (new values).
    `conversion` allows to convert to different units.
    A `watermark` is printed if stated `true`.

    Make sure that the number of items in `plotData` matches your `figure` dimensions specified as `ncols` and `nrows`.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: plot_multiple_lines
        args:
          agent: EnergyExchange
          time:
            convertToDateTime: true
            originName: TimeStep
            targetName: DateTime
          groupby: ["DateTime", "AgentId"]
          window: 168
          figure:
            width: 18
            height: 9
            dpi: 80
            ncols: 2
            nrows: 2
            ymin: -10
            ymax: 100
          map:
            AgentId:
              1: "Market A"
              6: "Market B"
              60: "Market C"
              600: "Market D"
          watermark: True
          backtestAgainst: file.csv
          plotData:
            - column: 'ElectricityPriceInEURperMWH'
              title: 'Electricity Price In EUR per MWh'
              position: [0, 0]
              ylabel: "EUR/MWh"
            - column: 'CoupledElectricityPriceInEURperMWH'
              title: 'Coupled Electricity Price In EUR per MWh'
              position: [0, 1]
              ylabel: "EUR/MWh"
            - column: 'CoupledTotalAwardedPowerInMW'
              title: 'Coupled Total Awarded Power In GW'
              position: [1, 1]
              ylabel: "GW"
              conversion: 0.001
            - column: 'TotalAwardedPowerInMW'
              title: 'Total Awarded Power In GW'
              position: [1, 0]
              ylabel: "GW"
              conversion: 0.001
    """
    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    agent_name = args["agent"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]

    x_dim = args["figure"]["ncols"]
    y_dim = args["figure"]["nrows"]

    y_min = args["figure"]["ymin"]
    y_max = args["figure"]["ymax"]

    ensure_given_data_matches_dims(x_dim, y_dim, args["plotData"])

    parsed_data = pd.read_csv(
        filepath_or_buffer=folder_name + "/" + agent_name + ".csv",
        sep=config["user"]["global"]["output"]["csvSeparator"],
    )

    if args["time"]["convertToDateTime"]:
        parsed_data = convert_to_datetime(args, parsed_data)

    grouped_data = parsed_data.groupby(to_list(args["groupby"]), as_index=False).sum()

    if "backtestAgainst" in args:
        backtest_data = pd.read_csv(
            filepath_or_buffer=args["backtestAgainst"],
            sep=config["user"]["global"]["output"]["csvSeparator"],
            names=[args["time"]["originName"], "Historical prices"],
        )
        backtest_data = convert_to_datetime(args, backtest_data)

    if "map" in args:
        for element in args["map"]:
            grouped_data["AgentId"].replace(args["map"][element], inplace=True)

    sns.set_theme()

    window = args["window"]
    time_col_name = args["time"]["targetName"]
    begin = grouped_data[time_col_name].min()
    end = begin + timedelta(hours=window)
    check_if_window_too_large(end, grouped_data[time_col_name].max())

    output_path = output_folder_path + "/plots/"
    ensure_path_exists(output_path)

    while end < grouped_data[time_col_name].max():
        data = grouped_data[grouped_data[time_col_name].between(begin, end)]

        f, a = plt.subplots(
            nrows=y_dim,
            ncols=x_dim,
            figsize=(args["figure"]["width"], args["figure"]["height"]),
        )

        if x_dim == 1 and y_dim == 1:
            a = [a]

        for subplot in args["plotData"]:
            selection = (*args["groupby"], subplot["column"])
            plot_data = data.pivot(*selection)

            if "conversion" in subplot:
                plot_data = data.pivot(*selection) * subplot["conversion"]

            pos_x = subplot["position"][0]
            pos_y = subplot["position"][1]

            if x_dim == 1:
                s = pos_x
            elif y_dim == 1:
                s = pos_y
            else:
                s = (pos_x, pos_y)

            plot_data.plot(
                ax=a[s],
                title=subplot["title"],
                ylim=(y_min, y_max),
                label="Test",
                legend=0,
            )

            a[s].set_ylabel(subplot["ylabel"])

        if "backtestAgainst" in args:
            backtest_data_to_plot = backtest_data[backtest_data[time_col_name].between(begin, end)]
            backtest_data_to_plot.set_index(args["time"]["targetName"], inplace=True)
            backtest_data_to_plot.plot(ax=a[s], legend=0, linestyle="--", c="black")

        a[s].set_xlabel("")
        a[s].grid(True, which="both")

        if x_dim == 1 or y_dim == 1:
            lines, labels = a[0].get_legend_handles_labels()
        else:
            lines, labels = a[0][0].get_legend_handles_labels()
        f.legend(lines, labels, loc="lower center", ncol=len(labels))

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.20)

        if get_from_dict_or_default("watermark", args, False):
            f.text(
                0.01,
                0.01,
                config["user"]["global"]["pbFile"],
                fontsize=8,
                c="grey",
            )
        time_string = datetime.strftime(begin, format="%Y-%m-%d_%H%M")
        plt.savefig(
            fname=output_path
            + agent_name
            + "_"
            + time_string[:-5]
            + "_"
            + str(window)
            + "_"
            + str(x_dim)
            + "X"
            + str(y_dim)
            + ".png",
            dpi=args["figure"]["dpi"],
        )
        begin += timedelta(hours=window)
        end += timedelta(hours=window)
        plt.close("all")

    sns.reset_orig()


@action("general")
def plot_heat_map(dmgr, config, params):
    """
    Generates a heat map plot for a specified `agent`. For this, values in `column` are plotted in a 2D plot with
    `days` on x-axis and `hours` on y-axis.
    You may specify a conversion to datetime format from `fame` `timesteps` by enabling `convertToDateTime`.
    The plot specifics are defined in `figure`.
    The `cbarlabel` defines the labelling of the color bar, whereas `cmap` defines the color scheme (see available list
    for colormaps in matplotlib).
    `vmin` defines the minimum value for the color bar. If not given, a symmetrical color bar is used with the max value.
    If specified with as `MINIMUM`, the minimum value in data is used as minimum instead. You may also use your custom
    float or integer value.

    The action may be specified in the user.yaml as follows:

    - action:
      project: general
      call: plot_heat_map
      args:
        agent: StorageTrader
        column: 'AwardedPower'
        time:
          convertToDateTime: true
          originName: TimeStep
          targetName: DateTime
        groupby: [ "DateTime", "AwardedPower" ]
        figure:
          width: 13
          height: 5
          dpi: 200
        cbarlabel: 'Awareded Power in MWh'
        cmap: "RdBu"
        vmin: MINIMUM
    """
    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    agent_name = args["agent"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]

    parsed_data = pd.read_csv(
        filepath_or_buffer=folder_name + "/" + agent_name + ".csv",
        sep=config["user"]["global"]["output"]["csvSeparator"],
    )

    if args["time"]["convertToDateTime"]:
        parsed_data = convert_to_datetime(args, parsed_data)

    plot_data = parsed_data[to_list(args["groupby"])].groupby(["DateTime"]).sum().values.reshape(-1, 24).T

    f, a = plt.subplots(
        nrows=1,
        ncols=1,
        figsize=(args["figure"]["width"], args["figure"]["height"]),
    )

    if "vmin" in args:
        if args["vmin"] == "MINIMUM":
            vmin = np.min(plot_data)
        elif isinstance(args["vmin"], float) or isinstance(args["vmin"], int):
            vmin = args["vmin"]
        else:
            raise_and_log_critical_error("Provide either `MINIMUM` or `float` value for `vmin`.")
    else:
        vmin = -np.max(np.abs(plot_data))
    vmax = np.max(np.abs(plot_data))

    plt.imshow(
        plot_data,
        aspect="auto",
        origin="lower",
        cmap=args["cmap"],
        interpolation="nearest",
        vmin=vmin,
        vmax=vmax,
    )
    cbar = plt.colorbar(pad=0.02)

    plt.grid(False)

    # setting ticks positions
    t = np.arange(-0.5, 364.6, 30)
    a.xaxis.set_ticks(t)
    a.set_xticklabels(((t + 0.5)).astype(int))

    t = np.arange(-0.5, 23.6, 6)
    a.yaxis.set_ticks(t)
    a.set_yticklabels(list(map(lambda x: x + ":00", (t + 0.5).astype(int).astype(str))))

    cbar.set_label(args["cbarlabel"], labelpad=10)
    a.set_ylabel("Hour")
    a.set_xlabel("Day")

    output_path = output_folder_path + "/plots/"
    ensure_path_exists(output_path)

    plt.savefig(
        fname=output_path + agent_name + "_" + args["column"] + "_heat_map.png",
        dpi=args["figure"]["dpi"],
    )
    plt.close("all")


def get_simulation_year_from(scenario: dict) -> int:
    """Returns simulation year from given `scenario` assuming simulation starts in `StartTime` year + `1` year"""
    try:
        start_time = scenario["GeneralProperties"]["Simulation"]["StartTime"]
    except KeyError:
        raise_and_log_critical_error("Could not find `StartTime` in given scenario.")
    return int(start_time.split("-")[0]) + 1


def get_runid_from(scenario: dict) -> str:
    """Returns run_id from given `scenario` in format `xxx`"""
    try:
        return str(scenario["GeneralProperties"]["RunId"]).zfill(3)
    except KeyError:
        raise_and_log_critical_error("Could not find `RunId` in given scenario.")


@action("general")
def compile_installed_capacities_exchange_file(dmgr, config, params):
    """
    Reads given `scenario` and calculates aggregated `InstalledPowerInMW` by `Type`.
    If `one_file_per_exchange` is enabled, a nested dict for each `Region` in `scenario` with a dict of
    `InstalledPowerInMW` per `Type` is calculated.
    In `map` you may specify a dict where the key represents the column name and the value ({old_value: new_value}, ...)
    the respective mapping of old and new values.

    Saves output as "year_runname_runid_DLR_Installed-Capacities-In-MW.csv" to `global` output folder with columns "EnergyCarrier, (Region), and
    Installed_capacity_in_MW". `Year`, `RunId` are retrieved from the `scenario.yaml`, whereas `runname` is defined in
    as `pbFile` in the `global` setting of the `user.yaml` (this should match the name specified in `fameSetup.yaml`).

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call:
        args:
          scenario: "../couple_markets_AT-DE/data/scenario.yaml"
          one_file_per_exchange: true
          map:
            Energy Carrier:
                Storage: Pumped Hydro Storage
                NUCLEAR: Nuclear Power
                LIGNITE: Lignite
                HARD_COAL: Hard coal
                NATURAL_GAS: Gas (Turbine + CCGT)
                OIL: Other conventional
                PV: Photovoltaic
                WindOn: Wind Onshore
                RunOfRiver: Run of river
                Biogas: Bioenergy
                WindOff: Wind Offshore
    """

    args = params["args"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    ensure_path_exists(output_folder_path)

    scenario = load_yaml(args["scenario"])

    single_file = get_from_dict_or_default("one_file_per_exchange", args, False)

    installed_capacities = get_installed_power_by_technology(scenario, single_file)

    if "map" in args:
        for column in args["map"]:
            installed_capacities[column].replace(args["map"][column], inplace=True)

    installed_capacities.rename(
        {"InstalledCapacitiesInMW": "Installed Capacities In MW"},
        axis=1,
        inplace=True,
    )

    year = get_simulation_year_from(scenario)
    run_name = config["user"]["global"]["pbFile"].split(".")[0]
    run_id = get_runid_from(scenario)
    institution = "DLR"
    value = "Installed-Capacities-In-MW"
    file_name = "{}_{}_{}_{}_{}.csv".format(str(year), run_name, run_id, institution, value)

    installed_capacities.to_csv(
        path_or_buf=output_folder_path + file_name,
        sep=config["user"]["global"]["output"]["csvSeparator"],
        index=None,
    )


def get_energycarrier_name_for(agent_id: int, installed_power_by_energycarrier: dict) -> str:
    """Returns `energy_carrier_name` for `agent_id` in `dict` of installed capacities"""
    for (
        energy_carrier_name,
        energy_carrier_group,
    ) in installed_power_by_energycarrier.items():
        for plant in energy_carrier_group:
            for plant_id, _ in plant.items():
                if agent_id == plant_id:
                    return energy_carrier_name

    raise_and_log_critical_error(
        "Did not find agent with `Id` {} in list of installed powers by energycarrier.".format(agent_id)
    )


@action("general")
def compile_awarded_power_exchange_file(dmgr, config, params):
    """
    Reads given `scenario`, parses raw results from agents and calculates aggregated `Awarded Power In MWh` by `Type`
    and `Region`. If `aggregated_yearly_sum` is enabled, a sum for the simulation year is calculated as Awarded Power
    In TWh`. This is currently only support for simulations spanning one year.
    `one_file_per_exchange` is currently not implemented.
    In `map` you may specify a dict where the key represents the column name and the value ({old_value: new_value}, ...)
    the respective mapping of old and new values.

    Saves output as "year_runname_runid_DLR_Installed-Capacities-In-MW.csv" to `global` output folder with columns
    "EnergyCarrier, (Region), and Awarded-Power-In-MWh". `Year`, `RunId` are retrieved from the `scenario.yaml`,
    whereas `runname` is defined in as `pbFile` in the `global` setting of the `user.yaml`
    (this should match the name specified in `fameSetup.yaml`).

    The action has currently the following limitations:
    - there is currently no feature which allows to aggregate values accross all regions
    - aggregation of yearly sums is only available for a single simulation year, not multiple year runs.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: compile_awarded_power_exchange_file
        args:
          scenario: "../couple_markets_AT-DE/data/scenario.yaml"
          aggregated_yearly_sum: false
          map:
            Energy Carrier:
              Storage: Pumped Hydro Storage
              NUCLEAR: Nuclear Power
              LIGNITE: Lignite
              HARD_COAL: Hard Coal
              NATURAL_GAS: Gas (Turbine + CCGT)
              OIL: Other Conventional
              PV: Photovoltaic
              WindOn: Wind Onshore
              RunOfRiver: Hydro Energy
              Biogas: Bioenergy
              WindOff: Wind Offshore
    """
    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    ensure_path_exists(output_folder_path)

    scenario = load_yaml(args["scenario"])
    contracts = scenario["Contracts"]
    agents = get_all_plants_from(scenario)
    installed_power_by_energycarrier = get_installed_power_by_tech_from(scenario)

    parsed_agents = parse_agents_in(folder_name)

    for agent in agents:
        agent[Amiris.energy_carrier_name] = get_energycarrier_name_for(agent["Id"], installed_power_by_energycarrier)

        if agent["Type"] == Amiris.conventional_type_name:
            data_of_all_agents_of_type = parsed_agents[Amiris.conventional_plant_operator]
            operator_id, _ = get_operator_id_for(agent, contracts)
            agent_data = data_of_all_agents_of_type.loc[data_of_all_agents_of_type["AgentId"] == operator_id].copy()
        else:
            data_of_all_agents_of_type = parsed_agents[agent["Type"]]
            agent_data = data_of_all_agents_of_type.loc[data_of_all_agents_of_type["AgentId"] == agent["Id"]].copy()

        agent_data[Amiris.time_step] = [
            time.replace("_", " ") for time in convert_fame_time_to_datetime(agent_data[Amiris.time_step])
        ]
        agent_data = agent_data.groupby([Amiris.time_step, "AgentId"], as_index=False).sum()
        agent_data.set_index(Amiris.time_step, inplace=True)
        if agent["Type"] == Amiris.storage_type_name:
            agent[Amiris.awarded_power_name] = agent_data["AwardedChargePower"]
        else:
            agent[Amiris.awarded_power_name] = agent_data[Amiris.awarded_power_name]

    regions = dict()
    for agent in agents:
        regions.setdefault(agent["Region"], []).append(agent)

    main_output = pd.DataFrame()
    for region, agents in regions.items():
        energy_carriers = dict()
        for agent in agents:
            energy_carriers.setdefault(agent["EnergyCarrier"], []).append(agent["AwardedPowerInMWH"])

        temp = dict()
        for energy_carrier, awarded_powers in energy_carriers.items():
            temp[energy_carrier] = sum(awarded_powers)

        output = (
            pd.DataFrame(*[temp])
            .stack()
            .reset_index()
            .set_axis(["Time", "Energy Carrier", "Awarded Power In MWh"], axis=1)
        )
        output["Region"] = region
        main_output = pd.concat(
            [
                main_output,
                output.reindex(
                    [
                        "Time",
                        "Region",
                        "Energy Carrier",
                        "Awarded Power In MWh",
                    ],
                    axis=1,
                ),
            ]
        )

    if "map" in args:
        for column in args["map"]:
            main_output[column].replace(args["map"][column], inplace=True)

    year = get_simulation_year_from(scenario)
    run_name = config["user"]["global"]["pbFile"].split(".")[0]
    run_id = get_runid_from(scenario)
    institution = "DLR"
    value = "Awarded-Power-In-MWh"

    if args["aggregated_yearly_sum"]:
        # todo: allow to aggregate multi-year simulation runs
        main_output.index = pd.to_datetime(main_output["Time"])
        main_output = main_output.loc[str(year)]
        main_output = main_output.groupby(["Energy Carrier", "Region"]).resample("Y").sum()
        main_output.reset_index(inplace=True)
        main_output["Awarded Power In TWh"] = main_output["Awarded Power In MWh"] * 10**-6
        main_output.drop(["Time", "Awarded Power In MWh"], axis=1, inplace=True)
        value = "Yearly-Awarded-Power-In-TWh"

    file_name = "{}_{}_{}_{}_{}.csv".format(str(year), run_name, run_id, institution, value)

    main_output.to_csv(
        path_or_buf=output_folder_path + file_name,
        sep=config["user"]["global"]["output"]["csvSeparator"],
        index=None,
    )


def get_operator_id_for(agent: dict, contracts: list) -> int:
    """Returns `operator_id` and `plant_index_in_list` for `PredefinedPlantBuilder` agent in `contracts`"""
    assert (
        agent["Type"] == Amiris.conventional_type_name
    ), "Can only find operator_id for `PredefinedPlantBuilder`, but not provided `{}`.".format(agent["Type"])
    contract_to_operator = get_contract_from_sender_with_product(agent["Id"], "PowerPlantPortfolio", contracts)
    plant_index_in_list = next(i for i, x in enumerate(to_list(contract_to_operator["SenderId"])) if x == agent["Id"])
    operator_id = to_list(contract_to_operator["ReceiverId"])[plant_index_in_list]
    return operator_id, plant_index_in_list


def parse_agents_in(folder: str) -> Dict[str, pd.DataFrame]:
    """Returns `dict` with `pd.DataFrame` of parsed `agents` found in `folder`"""
    files = get_all_csv_files_in_folder(folder=folder)
    results = dict()
    for file in files:
        agent_df = pd.read_csv(file, sep=";")
        agent_name = file.rsplit("/", 1)[1].rsplit(".", 1)[0]
        results.update({agent_name: agent_df})
    return results


@action("general")
def compile_transfer_capacity_exchange_file(dmgr, config, params):
    """
    Parses the `agent` csv file and converts the `fame_time_steps` into `datetime` strings.
    The `indexColumn` has to be specified.
    Further, a `mapping` of columns can be provided as dict with the origin values as `key` and the target values as
    `value`.
    Replaces `OriginAgentId` and `TargetAgentId` with `Region` name retrieved from specified `scenario` yaml where all `Exchanges` are parsed.

    Saves output as "year_runname_runid_DLR_Used-Transfer-Capacity-In-MWh.csv" to `global` output folder with columns
    "Time, from_zone, to_zone, Used Transfer Capacity In MWh". `Year`, `RunId` are retrieved from the `scenario.yaml`,
    whereas `runname` is defined in as `pbFile` in the `global` setting of the `user.yaml`
    (this should match the name specified in `fameSetup.yaml`).

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: compile_transfer_capacity_exchange_file
        args:
          agent: MarketCoupling
          indexColumn: 'TimeStep'
          mapping:
            TimeStep: Time
            OriginAgentId: From
            TargetAgentId: To
            AvailableTransferCapacityInMWH: Available Transfer Capacity In MWh
            UsedTransferCapacityInMWH: Used Transfer Capacity In MWh
          groupby: ["Time"]
          scenario: "../couple_markets_AT-DE/data/scenario.yaml"
    """
    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    agent = args["agent"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    ensure_path_exists(output_folder_path)

    parsed_data = pd.read_csv(
        filepath_or_buffer=folder_name + "/" + agent + ".csv",
        sep=config["user"]["global"]["output"]["csvSeparator"],
    )

    scenario = load_yaml(args["scenario"])
    region_map = get_region_of_all_exchanges(scenario)
    parsed_data["OriginAgentId"].replace(region_map, inplace=True)
    parsed_data["TargetAgentId"].replace(region_map, inplace=True)
    parsed_data.drop(["AgentId"], axis=1, inplace=True)

    # todo: remove once marketcoupling output file from AMIRIS is fixed
    parsed_data["UsedTransferCapacityInMWH"] = (
        parsed_data["AvailableTransferCapacityInMWH"] - parsed_data["UsedTransferCapacityInMWH"]
    )
    parsed_data[["OriginAgentId", "TargetAgentId"]] = parsed_data[["TargetAgentId", "OriginAgentId"]]

    index_label = args["indexColumn"]

    if "mapping" in args:
        parsed_data.rename(columns=args["mapping"], inplace=True)
        index_label = args["mapping"][index_label]

    parsed_data[index_label] = [
        time.replace("_", " ") for time in convert_fame_time_to_datetime(parsed_data[index_label])
    ]

    year = get_simulation_year_from(scenario)
    run_name = config["user"]["global"]["pbFile"].split(".")[0]
    run_id = get_runid_from(scenario)
    institution = "DLR"
    value = "Used-Transfer-Capacity-In-MWh"
    file_name = "{}_{}_{}_{}_{}.csv".format(str(year), run_name, run_id, institution, value)

    parsed_data.to_csv(
        path_or_buf=output_folder_path + file_name,
        sep=config["user"]["global"]["output"]["csvSeparator"],
        index=None,
    )


@action("general")
def compile_powerplant_generation_exchange_file(dmgr, config, params):
    """
    Parses the `agent` csv file and converts the `fame_time_steps` into `datetime` strings.
    The `indexColumn` has to be specified.
    Further, a `mapping` of columns can be provided as dict with the origin values as `key` and the target values as
    `value`.
    The export is performed by a `groupby` specification which defines the columns for which a sum of all remaining
    column values is conducted.

    Adds `Ramping Up Potential in MWh` & `Ramping Down Potential in MWh` to given output file.
    For this, the capacity for each agent in `fileName` is derived from `scenario` and simple routine is calcualted for
    `Ramping Down Potential in MWh = current_power_level` and `Ramping Up Potential in MWh = capacity_installed - current_power_level`.

    This action assumes that the power plants follow a specific pattern in their Ids.
    Specifically, builders must share the same Id with their operator except with the suffix `0`.
    Traders do not have to follow any specific pattern.
    For example:
        - operator [500]
        - builder [5000]
        - trader [1000]

    Saves output as "year_runname_runid_DLR_Powerplant-Generation-In-MWh.csv" to `global` output folder with columns
    "Time, Id, Powerplant Generation In MWh, Ramping Up Potential in MWh, Ramping Down Potential in MWh".
    `Year`, `RunId` are retrieved from the `scenario.yaml`, whereas `runname` is defined in as `pbFile` in the `global`
    setting of the `user.yaml` (this should match the name specified in `fameSetup.yaml`).

    If `save_as_hdf5` is given, the output is saved in `hdf5` format.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: compile_powerplant_generation_exchange_file
        args:
          agent: EnergyExchange
          indexColumn: 'TimeStep'
          mapping:
            TimeStep: Time
            AgentId: Region
          groupby: ["Time", "Region"]
          scenario: "../couple_markets_AT-DE/data/scenario.yaml"
          save_as_hdf5: True
    """
    ramp_up_name = "Ramping Up Potential in MWh"
    ramp_down_name = "Ramping Down Potential in MWh"
    power_name = "Powerplant Generation In MWh"

    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    agent = args["agent"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    ensure_path_exists(output_folder_path)

    parsed_data = pd.read_csv(
        filepath_or_buffer=folder_name + "/" + agent + ".csv",
        sep=config["user"]["global"]["output"]["csvSeparator"],
    )

    index_label = args["indexColumn"]

    if "mapping" in args:
        parsed_data.rename(columns=args["mapping"], inplace=True)
        index_label = args["mapping"][index_label]

    parsed_data[index_label] = [
        time.replace("_", " ") for time in convert_fame_time_to_datetime(parsed_data[index_label])
    ]
    parsed_data = parsed_data.groupby(to_list(args["groupby"]), as_index=False).sum()
    parsed_data.rename({"Power": power_name}, axis=1, inplace=True)

    parsed_data = parsed_data[["Time", "Id", power_name]]

    scenario = load_yaml(args["scenario"])

    agents_with_installed_power = get_dict_with_installed_power_by_id(scenario)

    suffix = str(0)
    output_data = pd.DataFrame(columns=parsed_data.columns)

    for unique_id in parsed_data["Id"].unique():
        tmp_data = parsed_data.loc[parsed_data["Id"] == unique_id].copy()
        powerplant_id = int(unique_id)
        powerplant_id = str(powerplant_id) + suffix

        tmp_data[ramp_down_name] = tmp_data.apply(lambda row: row[power_name], axis=1)
        tmp_data[ramp_up_name] = tmp_data.apply(
            lambda row: (agents_with_installed_power[int(powerplant_id)] - row[power_name]),
            axis=1,
        )

        output_data = pd.concat([output_data, tmp_data])

    year = get_simulation_year_from(scenario)
    run_name = config["user"]["global"]["pbFile"].split(".")[0]
    run_id = get_runid_from(scenario)
    institution = "DLR"
    value = "Powerplant-Generation-In-MWh"
    file_name = "{}_{}_{}_{}_{}.csv".format(str(year), run_name, run_id, institution, value)

    if get_from_dict_or_default("save_as_hdf5", args, False):
        output_data.to_hdf(
            output_folder_path + file_name.split(".")[0] + ".hdf5",
            key=value,
            mode="w",
            complevel=9,
        )
    else:
        output_data.to_csv(
            path_or_buf=output_folder_path + file_name,
            sep=config["user"]["global"]["output"]["csvSeparator"],
            index=None,
        )


@action("general")
def compare_price_duration_curves(dmgr, config, params):
    """
    Generates a price duration plot for a list of `data` inputs.
    For this, `file_path`, `origin` and `column_name` have to be specified.
    The plot can be limited to certain regions as stated in the `limit_to_regions` list.
    `ylabel`  defines the labelling of the y-axis, whereas the x-axis is always called `hours`.
    A `watermark` of the file origins is printed if stated `true`.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: compare_price_duration_curves
        args:
          data:
            - file_path: "output/2019_couplingtest_001_DLR_Electricity-Prices-In-EUR-Per-MWh.csv"
              origin: DLR
              column_name: "Electricity Price In EUR Per MWh"
            - file_path: "external/2019_couplingtest_001_KIT_DayAheadPrices.csv"
              origin: KIT
              column_name: "ElectricityPriceInEURperMWh"
          limit_to_regions: ['DE', 'AT']
          groupby: [ "Time", "Region" ]
          figure:
            width: 8.1
            height: 5.8
            dpi: 200
          ylabel: 'EUR/MWh'
          watermark: True
    """
    args = params["args"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]

    sns.set_theme()

    output_path = output_folder_path + "/plots/"
    ensure_path_exists(output_path)

    f, a = plt.subplots(
        nrows=1,
        ncols=1,
        figsize=(args["figure"]["width"], args["figure"]["height"]),
    )

    linestyles = {"DLR": "dotted", "KIT": "solid"}

    regions_to_plot = get_from_dict_or_default("limit_to_regions", args, None)

    for item in args["data"]:
        parsed_data = pd.read_csv(
            filepath_or_buffer=item["file_path"],
            sep=config["user"]["global"]["output"]["csvSeparator"],
        )
        parsed_data.rename({item["column_name"]: "EUR/MWh"}, axis=1, inplace=True)

        if regions_to_plot:
            parsed_data = parsed_data[parsed_data["Region"].isin(regions_to_plot)]

        selection = (*args["groupby"], "EUR/MWh")
        plot_data = parsed_data.pivot(*selection)

        plt.gca().set_prop_cycle(None)  # reset color cycle for better comparability
        for i, col in enumerate(plot_data.columns):
            sorted_data = plot_data[col].copy().sort_values(axis=0)
            color = next(a._get_lines.prop_cycler)["color"]
            sorted_data.plot(
                ax=a,
                legend=0,
                use_index=False,
                color=color,
                linestyle=linestyles[item["origin"]],
            )

    a.set_ylabel(args["ylabel"])
    a.set_xlabel("Hours")
    plt.suptitle("")
    a.grid(True, which="both")

    lines, labels = a.get_legend_handles_labels()
    f.legend(
        lines,
        labels,
        loc="lower center",
        ncol=len(labels),
        bbox_to_anchor=(0.5, 0.06),
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.26)

    # todo: print better legend enhancement
    f.text(0.8, 0.01, str(linestyles), fontsize=8, c="grey")

    if "watermark" in args:
        y = 0.01
        for item in args["data"]:
            f.text(0.01, y, item["file_path"].split("/")[1], fontsize=8, c="grey")
            y += 0.02

    # todo: make more robust
    filename = args["data"][0]["file_path"].split("/")[1]
    filename = filename.split("_")[0:3]
    filename = "_".join(filename)

    plt.savefig(
        fname=output_path + str(filename) + "_Price_Duration.png",
        dpi=args["figure"]["dpi"],
    )
    plt.close("all")
    sns.reset_orig()


@action("general")
def compare_heat_maps(dmgr, config, params):
    """
    Generates a 2x1 heat map plot.
    for a list of `data` inputs.
    For this, `file_path`, `origin` and `column_name` have to be specified.
    The plot can be limited to certain regions as stated in the `limit_to_region` list.

    The `cbarlabel` defines the labelling of the color bar, whereas `cmap` defines the color scheme (see available list
    for colormaps in matplotlib).
    `vmin` defines the minimum value for the color bar. If not given, a symmetrical color bar is used with the max value.
    If specified with as `MINIMUM`, the minimum value in data is used as minimum instead. You may also use your custom
    float or integer value.
    A `watermark` of the file origins is printed if stated `true`.

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: compare_heat_maps
        args:
          data:
            - file_path: "output/2019_couplingtest_001_DLR_Electricity-Prices-In-EUR-Per-MWh.csv"
              origin: DLR
              column_name: "Electricity Price In EUR Per MWh"
            - file_path: "external/2019_couplingtest_001_KIT_DayAheadPrices.csv"
              origin: KIT
              column_name: "ElectricityPriceInEURperMWh"
          limit_to_region: 'DE'
          groupby: [ "Time", "Region" ]
          figure:
            width: 13
            height: 5
            dpi: 200
          cbarlabel: 'EUR/MWh'
          cmap: "RdBu"
          vmin: MINIMUM
          watermark: True
          normalize: False
    """
    args = params["args"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    x_dim = 2
    y_dim = 1

    output_path = output_folder_path + "/plots/"
    ensure_path_exists(output_path)

    normalize = get_from_dict_or_default("normalize", args, False)

    f, a = plt.subplots(
        nrows=x_dim,
        ncols=y_dim,
        figsize=(args["figure"]["width"], args["figure"]["height"]),
    )

    s = 0

    for idx, item in enumerate(args["data"]):
        parsed_data = pd.read_csv(
            filepath_or_buffer=item["file_path"],
            sep=config["user"]["global"]["output"]["csvSeparator"],
        )
        parsed_data.rename({item["column_name"]: "EUR/MWh"}, axis=1, inplace=True)
        parsed_data = parsed_data[parsed_data["Region"].isin(to_list(args["limit_to_region"]))]
        plot_data = parsed_data[["Time", "EUR/MWh"]].groupby(["Time"]).sum().values.reshape(-1, 24).T

        if normalize:
            plot_data = (plot_data - plot_data.mean()) / plot_data.std()
            vmin = -1
            vmax = 1
        else:
            if "vmin" in args:
                if args["vmin"] == "MINIMUM":
                    vmin = np.min(plot_data)
                elif isinstance(args["vmin"], float) or isinstance(args["vmin"], int):
                    vmin = args["vmin"]
                else:
                    raise_and_log_critical_error("Provide either `MINIMUM` or `float` value for `vmin`.")
            else:
                vmin = -np.max(np.abs(plot_data))

            if "vmax" in args:
                if args["vmax"] == "MAXIMUM":
                    vmax = np.min(plot_data)
                elif isinstance(args["vmax"], float) or isinstance(args["vmax"], int):
                    vmax = args["vmax"]
                else:
                    raise_and_log_critical_error("Provide either `MAXIMUM` or `float` value for `vmax`.")
            else:
                vmax = np.max(np.abs(plot_data))

        a[s].set_title(item["origin"])
        im = a[s].imshow(
            plot_data,
            aspect="auto",
            origin="lower",
            cmap=args["cmap"],
            interpolation="nearest",
            vmin=vmin,
            vmax=vmax,
        )
        divider = make_axes_locatable(a[s])
        cax = divider.append_axes("right", size="1%", pad=0.05)
        cbar = plt.colorbar(im, cax=cax, pad=0.02)

        plt.grid(False)

        if s != 0 and x_dim > 1:
            # setting ticks positions
            t = np.arange(-0.5, 364.6, 30)
            a[s].xaxis.set_ticks(t)
            a[s].set_xticklabels(((t + 0.5)).astype(int))
            a[s].set_xlabel("Day")
        else:
            a[s].xaxis.set_visible(False)

        t = np.arange(-0.5, 23.6, 6)
        a[s].yaxis.set_ticks(t)
        a[s].set_yticklabels(list(map(lambda x: x + ":00", (t + 0.5).astype(int).astype(str))))

        cbar.set_label(args["cbarlabel"], labelpad=10)
        a[s].set_ylabel("Hour")

        s += 1

    if "watermark" in args:
        y = 0.01
        for item in args["data"]:
            f.text(0.01, y, item["file_path"].split("/")[1], fontsize=8, c="grey")
            y += 0.02

    # todo: make more robust
    filename = args["data"][0]["file_path"].split("/")[1]
    filename = filename.split("_")[0:3]
    filename.append(args["limit_to_region"])
    if "vmin" in args:
        filename.append(str(args["vmin"]))
    if "vmax" in args:
        filename.append(str(args["vmax"]))
    filename = "_".join(filename)

    if normalize:
        plt.savefig(
            fname=output_path + str(filename) + "_Heat_Map_normalized.png",
            dpi=args["figure"]["dpi"],
        )
    else:
        plt.savefig(
            fname=output_path + str(filename) + "_Heat_Map.png",
            dpi=args["figure"]["dpi"],
        )
    plt.close("all")


@action("general")
def compile_demand_exchange_file(dmgr, config, params):
    """
    Parses the `agent` csv file and converts the `fame_time_steps` into `datetime` strings.
    The `indexColumn` has to be specified.
    Further, a `mapping` of columns can be provided as dict with the origin values as `key` and the target values as
    `value`.
    The export is performed by a `groupby` specification which defines the columns for which a sum of all remaining
    column values is conducted.
    Replaces `Id` with `Region` name retrieved from specified `scenario` yaml where all `Exchanges` are parsed.
    If only one EnergyExchange is found, the value "Region" is applied.

    Saves output as "year_runname_runid_DLR_Demand-In-MWh.csv" to `global` output folder with columns
    "Time, Id, Region, Demand In MWh".
    `Year`, `RunId` are retrieved from the `scenario.yaml`, whereas `runname` is defined in as `pbFile` in the `global`
    setting of the `user.yaml` (this should match the name specified in `fameSetup.yaml`).

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: compile_demand_exchange_file
        args:
          agent: EnergyExchange
          indexColumn: 'TimeStep'
          mapping:
            TimeStep: Time
            AgentId: Region
          groupby: ["Time", "Region"]
          scenario: "../couple_markets_AT-DE/data/scenario.yaml"
    """
    args = params["args"]
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    agent = args["agent"]
    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    ensure_path_exists(output_folder_path)

    parsed_data = pd.read_csv(
        filepath_or_buffer=folder_name + "/" + agent + ".csv",
        sep=config["user"]["global"]["output"]["csvSeparator"],
    )

    index_label = args["indexColumn"]

    if "mapping" in args:
        parsed_data.rename(columns=args["mapping"], inplace=True)
        index_label = args["mapping"][index_label]

    parsed_data[index_label] = [
        time.replace("_", " ") for time in convert_fame_time_to_datetime(parsed_data[index_label])
    ]
    parsed_data = parsed_data.groupby(to_list(args["groupby"]), as_index=False).sum()
    parsed_data.set_index(index_label, inplace=True)
    parsed_data.rename({"TotalAwardedPowerInMW": "Demand In MWh"}, axis=1, inplace=True)

    output = parsed_data.reset_index()[["Time", "Region", "Demand In MWh"]]

    scenario = load_yaml(args["scenario"])
    region_map = get_region_of_all_exchanges(scenario)

    output["Region"].replace(region_map, inplace=True)

    year = get_simulation_year_from(scenario)
    run_name = config["user"]["global"]["pbFile"].split(".")[0]
    run_id = get_runid_from(scenario)
    institution = "DLR"
    value = "Demand-In-MWh"
    file_name = "{}_{}_{}_{}_{}.csv".format(str(year), run_name, run_id, institution, value)

    output.to_csv(
        path_or_buf=output_folder_path + file_name,
        sep=config["user"]["global"]["output"]["csvSeparator"],
        index=None,
    )


def get_markup_for(id: int, scenario: dict, type: str) -> float:
    """Returns `markup` of `type` for trader of `id`"""
    trader_agent = [agent for agent in scenario["Agents"] if agent["Id"] == id]
    if len(trader_agent) != 1:
        raise_and_log_critical_error(
            "Found {} occurences for trader with id `{}`. Expected 1 instead.".format(len(trader_agent), id)
        )
    return trader_agent[0]["Attributes"][type]


@action("general")
def compile_markup_exchange_file(dmgr, config, params):
    """
    Collects `markup` information from `ConventionalTrader`s in `scenario` and compiles the information in tabular form.

    Saves output as "year_runname_runid_DLR_Markups-In-EUR-Per-MWh.csv" to `global` output folder with columns
    "Year, Id, Markup In EUR Per MWh, Markdown In EUR Per MWh".
    `Year`, `RunId` are retrieved from the `scenario.yaml`, whereas `runname` is defined in as `pbFile` in the `global`
    setting of the `user.yaml` (this should match the name specified in `fameSetup.yaml`).

    The action may be specified in the user.yaml as follows:

    - action:
        project: general
        call: compile_markup_exchange_file
        args:
          scenario: "../couple_markets_AT-DE/data/scenario.yaml"
    """
    args = params["args"]

    output_folder_path = config["user"]["global"]["output"]["pbOutputProcessed"]
    ensure_path_exists(output_folder_path)

    scenario = load_yaml(args["scenario"])
    contracts = scenario["Contracts"]
    conventionals = get_agent_with_id_and_type_and_region_from(scenario, Amiris.conventional_type_name)

    year = get_simulation_year_from(scenario)

    export_columns = [
        "Year",
        "Id",
        "Markup In EUR Per MWh",
        "Markdown In EUR Per MWh",
    ]

    conventional_powerplant_agents = []
    for plant in conventionals:
        operator_id, plant_index_in_list = get_operator_id_for(plant, contracts)
        plant_id = get_trader_id_for(operator_id, "MarginalCostForecast", contracts, plant_index_in_list)
        plant[Amiris.max_efficiency] = get_markup_for(plant_id, scenario, "maxMarkup")
        plant[Amiris.min_efficiency] = get_markup_for(plant_id, scenario, "minMarkup")
        plant["Year"] = year

        sorted_plant = {}
        for key in export_columns:
            sorted_plant[key] = plant[key]

        conventional_powerplant_agents.append(sorted_plant)

    run_name = config["user"]["global"]["pbFile"].split(".")[0]
    run_id = get_runid_from(scenario)
    institution = "DLR"
    value = "Markups-In-EUR-Per-MWh"
    file_name = "{}_{}_{}_{}_{}.csv".format(str(year), run_name, run_id, institution, value)

    output = conventional_powerplant_agents

    with open(output_folder_path + file_name, "w", encoding="utf8", newline="") as output_file:
        fc = csv.DictWriter(
            output_file,
            fieldnames=output[0].keys(),
            delimiter=config["user"]["global"]["output"]["csvSeparator"],
        )
        fc.writeheader()
        fc.writerows(output)


@action("general")
def aggregate_results(dmgr, config, params):
    """Calculate refinancing-related results for AMIRIS agents"""
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    files = get_all_csv_files_in_folder(folder=folder_name)
    to_concat = []
    for file in files:
        type_df = pd.read_csv(file, sep=";")
        agent_name = file.rsplit("/", 1)[1].rsplit(".", 1)[0]
        if agent_name in OPERATOR_AGENTS:
            column_names = {
                "CostsInEUR": AmirisOutputs.VARIABLE_COSTS_IN_EURO.name,
                "ReceivedMoneyInEUR": AmirisOutputs.REVENUES_IN_EURO.name,
                "AwardedPowerInMWH": AmirisOutputs.PRODUCTION_IN_MWH.name,
            }
            outputs_per_agent = sum_per_agent(type_df, column_names.keys())
            outputs_per_agent.rename(columns=column_names, inplace=True)
            outputs_per_agent[AmirisOutputs.CONTRIBUTION_MARGIN_IN_EURO.name] = (
                outputs_per_agent[AmirisOutputs.REVENUES_IN_EURO.name]
                - outputs_per_agent[AmirisOutputs.VARIABLE_COSTS_IN_EURO.name]
            )
            to_concat.append(outputs_per_agent)
    all_outputs_per_agent = pd.concat(to_concat)
    all_outputs_per_agent.index.name = "identifier"

    if params["args"]["write"]:
        all_outputs_per_agent.to_csv(
            config["user"]["global"]["output"]["pbOutputProcessed"] + params["args"]["file_name"]
        )

    with dmgr.overwrite:
        dmgr[params["data"]["write_to_dmgr"]] = all_outputs_per_agent
