__version__ = "0.2.0"
__authors__ = "Felix Nitsch"
__maintainer__ = "Felix Nitsch"
__email__ = "felix.nitsch@dlr.de"

import os
import subprocess

import pandas as pd
import yaml
from fameio.scripts.convert_results import run as convert_results
from fameio.scripts.make_config import DEFAULT_CONFIG
from fameio.scripts.make_config import run as make_config
from fameio.source.cli import Options, ResolveOptions
from fameio.source.loader import load_yaml
from ioproc.tools import action

from iovrmr_tools import (
    ensure_path_exists,
    insert_agents_from_map,
    insert_contracts_from_map,
    get_header,
    get_field,
    write_yaml,
    to_list,
    raise_and_log_critical_error,
    get_all_csv_files_in_folder,
    OPERATOR_AGENTS,
    AmirisOutputs,
    sum_per_agent,
    CONVENTIONAL_AGENT_RESULTS,
    sum_per_plant,
    clear_folder,
    EXCHANGE,
    calculate_residual_load,
)


@action("general")
def parse_excel(data_manager, config, params):
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
              excelFile: power_plant_list.xlsx
              excelSheet: power_plants
              excelHeader: True
    """
    args = params["args"]
    file = get_field(args, "excelFile")
    excel_sheets = get_field(args, "excelSheet")
    header = get_header(get_field(args, "excelHeader"))
    parsed_excel = pd.read_excel(io=file, sheet_name=excel_sheets, header=header)

    with data_manager.overwrite:
        data_manager[params["data"]["write_to_dmgr"]] = parsed_excel


@action("general")
def write_amiris_config(data_manager, config, params):
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
              AMIRISConfigFieldMap: AMIRISConfigFieldMap_DE.yaml
              templateFile: scenario_template.yaml
              outputFile: scenario.yaml
    """
    data = data_manager[params["data"]["read_from_dmgr"]]
    args = params["args"]

    config_file = load_yaml(args["templateFile"])

    output_params = config["user"]["global"]["output"]
    output_path = output_params["filePath"] + "/"
    ensure_path_exists(output_path)
    output_file_path = output_path + args["outputFile"]

    amiris_maps = to_list(args["AMIRISConfigFieldMap"])
    for amiris_map in amiris_maps:
        translation_map = load_yaml(amiris_map)
        if "Agents" not in translation_map:
            raise_and_log_critical_error("Found no Agents to create/append in {}.".format(amiris_maps))
        config_file, inserted_agents = insert_agents_from_map(data, translation_map["Agents"], config_file)
        if "Contracts" in translation_map:
            config_file = insert_contracts_from_map(inserted_agents, translation_map["Contracts"], config_file)

    write_yaml(config_file, output_file_path)


@action("general")
def create_amiris_protobuf(data_manager, config, params):
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
        output_path = os.path.abspath(output_path + DEFAULT_CONFIG[Options.OUTPUT])

    config = {
        Options.LOG_LEVEL: "info",
        Options.LOG_FILE: None,
        Options.OUTPUT: output_path,
    }

    make_config(input_path, config)


@action("general")
def convert_pb(data_manager, config, params):
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
        Options.LOG_LEVEL: "info",
        Options.LOG_FILE: None,
        Options.AGENT_LIST: agents_to_extract,
        Options.OUTPUT: config["user"]["global"]["output"]["pbOutputRaw"],
        Options.SINGLE_AGENT_EXPORT: False,
        Options.MEMORY_SAVING: False,
        Options.RESOLVE_COMPLEX_FIELD: ResolveOptions.SPLIT,
    }

    ensure_path_exists(run_config[Options.OUTPUT])
    clear_folder(run_config[Options.OUTPUT])

    if config["user"]["global"]["pbDir"]:
        path_to_pb = config["user"]["global"]["pbDir"] + config["user"]["global"]["pbFile"]
    else:
        path_to_pb = config["user"]["global"]["pbFile"]

    convert_results(path_to_pb, run_config)


@action("general")
def run_amiris(data_manager, config, params):
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
        model["vm"], model["jar"], model["fame_args"], model["runner"], args["input"], fame_setup_path
    )

    subprocess.run(call, check=True)


@action("general")
def aggregate_results(data_manager, config, params):
    """Calculate refinancing-related results for AMIRIS agents"""
    folder_name = config["user"]["global"]["output"]["pbOutputRaw"]
    files = get_all_csv_files_in_folder(folder=folder_name)
    to_concat = []
    conventional_series = []
    residual_load_results = {}
    for file in files:
        file_name = file.rsplit("/", 1)[1].rsplit(".", 1)[0]
        if file_name in OPERATOR_AGENTS:
            type_df = pd.read_csv(file, sep=";")
            column_names = {
                "VariableCostsInEUR": AmirisOutputs.VARIABLE_COSTS_IN_EURO.name,
                "ReceivedMoneyInEUR": AmirisOutputs.REVENUES_IN_EURO.name,
                "AwardedPowerInMWH": AmirisOutputs.PRODUCTION_IN_MWH.name,
            }
            outputs_per_agent = sum_per_agent(type_df, list(column_names.keys()))
            outputs_per_agent.rename(columns=column_names, inplace=True)
            to_concat.append(outputs_per_agent)

            if file_name != "StorageTrader":
                residual_load_results[file_name] = type_df

        elif file_name in CONVENTIONAL_AGENT_RESULTS:
            conventional_df = pd.read_csv(file, sep=";")
            column_names = {
                "VariableCostsInEURperPlant": AmirisOutputs.VARIABLE_COSTS_IN_EURO.name,
                "ReceivedMoneyInEURperPlant": AmirisOutputs.REVENUES_IN_EURO.name,
                "DispatchedPowerInMWHperPlant": AmirisOutputs.PRODUCTION_IN_MWH.name,
            }
            column = CONVENTIONAL_AGENT_RESULTS[file_name]
            column_per_plant = sum_per_plant(conventional_df, column, column_names[column])
            conventional_series.append(column_per_plant)

        elif file_name in EXCHANGE:
            type_df = pd.read_csv(file, sep=";")
            residual_load_results[file_name] = type_df

    residual_load = calculate_residual_load(residual_load_results)

    if conventional_series:
        to_concat.append(pd.concat(conventional_series, axis=1))

    all_outputs_per_agent = pd.concat(to_concat)
    all_outputs_per_agent[AmirisOutputs.CONTRIBUTION_MARGIN_IN_EURO.name] = (
        all_outputs_per_agent[AmirisOutputs.REVENUES_IN_EURO.name]
        - all_outputs_per_agent[AmirisOutputs.VARIABLE_COSTS_IN_EURO.name]
    )

    all_outputs_per_agent.index.name = "identifier"

    if params["args"]["write"]:
        all_outputs_per_agent.to_csv(
            config["user"]["global"]["output"]["pbOutputProcessed"] + params["args"]["file_name_aggregated_results"]
        )
        residual_load.to_csv(
            config["user"]["global"]["output"]["pbOutputProcessed"] + params["args"]["file_name_residual_load"]
        )

    with data_manager.overwrite:
        data_manager[params["data"]["write_to_dmgr"]] = all_outputs_per_agent
