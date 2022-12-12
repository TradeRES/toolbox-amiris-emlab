__version__ = "0.2.0"
__authors__ = "Felix Nitsch"
__maintainer__ = "Felix Nitsch"
__email__ = "felix.nitsch@dlr.de"


import os
from enum import Enum, auto
from typing import List, Callable, Dict, NoReturn, Any, Union, Hashable

import pandas as pd
import yaml
from ioproc.logger import mainlogger

OUTPUT_FILE_ENDING = ".csv"
OPERATOR_AGENTS = [
    "VariableRenewableOperator",
    "Biogas",
    "StorageTrader",
]
SUPPORTED_AGENTS = ["RenewableTrader", "SystemOperatorTrader"]
EXCHANGE = ["EnergyExchangeMulti"]
DEMAND = ["DemandTrader"]
CONVENTIONAL_AGENT_RESULTS = {
    "ConventionalPlantOperator_VariableCostsInEURperPlant": "VariableCostsInEURperPlant",
    "ConventionalPlantOperator_ReceivedMoneyInEURperPlant": "ReceivedMoneyInEURperPlant",
    "ConventionalPlantOperator_DispatchedPowerInMWHperPlant": "DispatchedPowerInMWHperPlant",
}
CONVENTIONAL_RESULTS_GROUPED = ["ConventionalPlantOperator"]


class FilterType(Enum):
    EQUAL = 0
    GREATER = 1
    GREATEREQUAL = 2
    LESS = 3
    LESSEQUAL = 4
    NOT = 5


class AmirisOutputs(Enum):
    ID = auto()
    REVENUES_IN_EURO = auto()
    VARIABLE_COSTS_IN_EURO = auto()
    CONTRIBUTION_MARGIN_IN_EURO = auto()
    PRODUCTION_IN_MWH = auto()


def raise_and_log_critical_error(error_message: str) -> NoReturn:
    """Raises a critical error and logs with given `error_message`"""
    mainlogger.critical(error_message)
    raise Exception(error_message)


def to_list(data: Any) -> List:
    """Ensures that given data is list"""
    if isinstance(data, list):
        return data
    elif isinstance(data, tuple):
        return list(data)
    else:
        return [data]


def get_header(bool_expression: str) -> Union[int, None]:
    """
    Parses given expression to a pandas read header
    Args:
        bool_expression: string that resembles a boolean
    Returns:
        0 if given expression is an equivalent of True
        None if given expression is an equivalent of False
    """
    value = None
    if isinstance(bool_expression, bool):
        value = bool_expression
    elif isinstance(bool_expression, str):
        if bool_expression.lower() in ["true", "t", "yes", "y", "j", "1"]:
            value = True
        elif bool_expression.lower() in ["false", "f", "no", "n", "0"]:
            value = False
    if value is None:
        raise ValueError(f"Cannot convert '{bool_expression}' to bool.")
    return 0 if value else None


def get_field(dictionary: Dict, key: Hashable) -> Any:
    """
    Get key from dictionary or raise
    Args:
        dictionary: to get the data from
        key: to get from dictionary
    Returns: dictionary[key]
    Raises: Critical error if key is not found in dictionary
    """
    try:
        return dictionary[key]
    except KeyError:
        message = "Missing key '{}'. Given keys are '{}'.".format(key, [key for key in dictionary.keys()])
        raise_and_log_critical_error(message)


def write_yaml(configuration: dict, output_file_path: str) -> None:
    """Writes given `configuration` to `output_file_path` in YAML format"""
    with open(output_file_path, "w") as stream:
        try:
            yaml.safe_dump(configuration, stream)
        except yaml.YAMLError:
            raise_and_log_critical_error("Failed writing yaml to {}".format(output_file_path))


def ensure_path_exists(path) -> None:
    """Creates a specified path if not already existent"""
    if not os.path.exists(path):
        os.makedirs(path)


def nest_flattened_items(list_of_dicts: List[Dict]) -> List[Dict]:
    """For each dictionary of given List, keys containing "/" will be split and interpreted as nested address, i.e.
    {'a/b/c': x} will be converted to {'a':{'b':{'c': x}}}. A new List of dicts is returned."""
    result = []
    for single_dict in list_of_dicts:
        result_dict = {}
        for key, value in single_dict.items():
            key_parts = key.split("/")
            temp_dict = result_dict
            for part in key_parts[:-1]:
                if part not in temp_dict:
                    temp_dict[part] = {}
                temp_dict = temp_dict[part]
            temp_dict[key_parts[-1]] = value
        result.append(result_dict)
    return result


def insert_agents_from_map(data: pd.DataFrame, translation_map: list, template: dict) -> (dict, list):
    """
    Appends list of agents to given `template` as specified in `translation_map`. For each row in given `data`, it
    iterates over `translations` in `translation_map` and creates agent. The agent creation can also be for an
    specified agent type as defined with `column` and `target`.
    Values for the agent attributes can be derived directly from the `translation_map` when specified as `value` or be
    derived from `column` in `data`. Raises error when none is defined. Additionally a `suffix` can be added to a field
    when so specified.
    Returns filled `template` and a list of `all_registered_agents` with the key `agent_type` and value `agent_id`.
    """
    agent_list = []
    all_registered_agents = []
    for _, row in data.iterrows():
        registered_agents_per_plant = {}
        for translation in translation_map:
            if isinstance(translation, dict):
                column = get_field(translation, "column")
                target = get_field(translation, "target")
                if row[column] == target:
                    if "create" in translation:
                        agent = create_agent(row, translation["create"])
                        agent_list.append(agent)
                        registered_agents_per_plant[agent["Type"]] = agent["Id"]
                    elif "append" in translation:
                        items_to_append = []
                        for append_operation in translation["append"]:
                            elements = create_agent(row, append_operation["elements"])
                            if "Id" in elements:
                                elements["Id"] = str(elements["Id"])
                            items_to_append.append(elements)
                            template = append_elements_to(
                                template,
                                append_operation["agent"],
                                append_operation["below"],
                                nest_flattened_items(items_to_append),
                            )
                    else:
                        raise_and_log_critical_error(
                            "Missing either `create` or `append` key for {}".format(translation)
                        )
            elif isinstance(translation, list):
                agent = create_agent(row, translation)
                agent_list.append(agent)
                registered_agents_per_plant[agent["Type"]] = agent["Id"]
            else:
                raise_and_log_critical_error("Failed creating agent specified as {}".format(translation))
        if registered_agents_per_plant:
            all_registered_agents.append(registered_agents_per_plant)

    agent_list = nest_flattened_items(agent_list)

    if not template["Agents"]:
        template["Agents"] = agent_list
    else:
        template["Agents"].extend(agent_list)

    return template, all_registered_agents


def append_elements_to(template: dict, agent_id: int, append_below: str, items_to_append: list) -> dict:
    """Returns `template` with `items_to_append` placed below `append_below` for agent with `agent_id`"""
    agent_to_append_to = [agent for agent in template["Agents"] if agent["Id"] == agent_id]
    if len(agent_to_append_to) != 1:
        raise_and_log_critical_error(
            "Cannot append elements to agent with Id `{}`. "
            "Check if missing or duplicates in template.".format(agent_id)
        )
    agent_to_append_to = agent_to_append_to[0]

    if len(items_to_append) != 1:
        raise_and_log_critical_error("Cannot append nested elements to agent with Id `{}`.".format(agent_id))
    items_to_append = items_to_append[0]

    key_parts = append_below.split("/")
    for part in key_parts:
        if part not in agent_to_append_to:
            agent_to_append_to[part] = []
        agent_to_append_to = agent_to_append_to[part]

    agent_to_append_to.append(items_to_append)
    return template


def create_agent(row, translation: List[Dict]) -> Dict:
    """Returns created agent from data in `row` according to specifications in `translation`."""
    agent = {}
    for item in translation:
        field = get_field(item, "attribute")
        if "value" in item:
            value = get_field(item, "value")
        elif "column" in item:
            column = get_field(item, "column")
            value = get_field(row, column)
            if "suffix" in item:
                value = str(value) + str(get_field(item, "suffix"))
                value = int(value)
        else:
            raise_and_log_critical_error("No 'value' or `column` found for attribute '{}'".format(item))
        # noinspection PyUnboundLocalVariable
        agent.update({field: value})
    return agent


def get_id_or_derive_from_type(contract, unit, param):
    """
    Returns Id derived from `param`+`id` in given `contract` dict or derived from `param`+`Type` in unit dictionary.
    Raises error if Id cannot be found either in `contract` or `unit`.
    """
    if param + "Id" in contract:
        return get_field(contract, param + "Id")
    else:
        return unit[get_field(contract, param + "Type")]


def insert_contracts_from_map(data, translation_map, template):
    """
    Appends list of contracts to the given `template` as specified in `translation_map`.
    'SenderId' and 'ReceiverId' are derived either from `translation_map` if specified or from given 'data' which
    stores all inserted agents. Returns filled `template`.
    """
    contract_list = []
    for unit in data:
        for translation in translation_map:
            contract = {}
            for field in translation:
                if "sender" in field.lower():
                    value = get_id_or_derive_from_type(translation, unit, "Sender")
                    field = "SenderId"
                elif "receiver" in field.lower():
                    value = get_id_or_derive_from_type(translation, unit, "Receiver")
                    field = "ReceiverId"
                else:
                    value = get_field(translation, field)
                contract.update({field: value})
            contract_list.append(contract)

    if not template["Contracts"]:
        template["Contracts"] = contract_list
    else:
        template["Contracts"].extend(contract_list)

    return template


def get_all_csv_files_in_folder(folder: str) -> List[str]:
    """Returns list of strings including path to folder for CSV files"""
    return get_all_files_in_folder_ending_with(folder=folder, ending=OUTPUT_FILE_ENDING)


def get_all_files_in_folder_ending_with(folder: str, ending: str) -> List[str]:
    """Returns a list of strings including path to folder for files with given ending"""
    return [folder + "/" + file for file in os.listdir(folder) if file.endswith(ending)]


def sum_per_agent(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Calculates summed values per agent for each given column individually"""
    all_values_per_agent = pd.DataFrame(columns=columns)
    for column in columns:
        function = calc_sum(column)
        value_per_agent = call_function_per_agent(df, function)
        for agent_id, value in value_per_agent.items():
            all_values_per_agent.at[agent_id, column] = value

    return all_values_per_agent


def calc_sum(column: str) -> Callable[[pd.DataFrame], float]:
    """Returns function on dataframe to calculate `sum of column`"""
    return lambda df: df[column].sum()


def call_function_per_agent(type_df: pd.DataFrame, function: Callable[[pd.DataFrame], float]) -> Dict:
    """Splits given dataframe by AgentId and applies `function`; Returns dict of {AgentId: `function` return value}"""
    groups = type_df.groupby(by="AgentId", sort=False)
    return {agent_id: function(agent_df) for agent_id, agent_df in groups}


def sum_per_plant(df: pd.DataFrame, column: str, target_name: str) -> pd.Series:
    """Calculates summed values per plant ID and given column returning renamed Series"""
    df["ID"] = df["ID"].astype(str)
    to_drop = df.loc[df["ID"].str.contains("Auto_")]
    df.drop(index=to_drop.index, inplace=True)
    groups = df.groupby(by="ID", sort=False)
    function = calc_sum(column)
    result = {plant_id: function(plant_df) for plant_id, plant_df in groups}
    return pd.Series(data=result, name=target_name)


def clear_folder(path: str) -> None:
    for file in get_all_csv_files_in_folder_except(path):
        try:
            os.remove(file)
        except FileNotFoundError:
            print(f"Info: File for deletion not found: {file}")


def get_all_csv_files_in_folder_except(folder: str, exceptions: List[str] = None) -> List[str]:
    """Returns list of strings including path to folder for CSV files"""
    if exceptions is None:
        exceptions = list()
    return [
        folder + "/" + file
        for file in os.listdir(folder)
        if file.endswith(OUTPUT_FILE_ENDING) and file not in exceptions
    ]


def calculate_residual_load(
    residual_load_results: Dict[str, pd.DataFrame], operators_offset: int = 5, demand_offset: int = 1
) -> pd.Series:
    """Calculate the residual load based on RES infeed and planned load (not considering storage / shedding etc.)"""
    res_generation_to_aggregate = []
    overall_demand = None
    for key, val in residual_load_results.items():
        if key in OPERATOR_AGENTS:
            value = val.loc[val["AwardedPowerInMWH"].notna()]
            value["new_time_step"] = value["TimeStep"] - operators_offset
            res_generation_to_aggregate.append(value.groupby("new_time_step").sum()["AwardedPowerInMWH"])
        elif key in DEMAND:
            value = val.copy()
            value["new_time_step"] = value["TimeStep"] + demand_offset
            overall_demand = value.set_index("new_time_step")["RequestedEnergyInMWH"]
            overall_demand = overall_demand.loc[overall_demand.notna()]
        else:
            raise ValueError("Received invalid key for residual_load_results!")

    overall_res_generation = pd.Series(index=res_generation_to_aggregate[0].index, data=0)
    for res_generation in res_generation_to_aggregate:
        overall_res_generation += res_generation

    residual_load = overall_demand - overall_res_generation
    residual_load.name = "residual_load"
    residual_load = residual_load.round(4)
    residual_load = residual_load.reset_index().drop(columns="new_time_step")["residual_load"]

    return residual_load


def calculate_overall_res_infeed(
    residual_load_results: Dict[str, pd.DataFrame], biogas_results: pd.DataFrame, operators_offset: int = 5
) -> pd.Series:
    """Calculate the overall RES infeed"""
    res_generation = []
    for key, val in residual_load_results.items():
        if key in OPERATOR_AGENTS:
            value = val.loc[val["AwardedPowerInMWH"].notna()]
            value["new_time_step"] = value["TimeStep"] - operators_offset
            res_generation.append(value.groupby("new_time_step").sum()["AwardedPowerInMWH"])

    if not biogas_results.empty:
        biogas_results = biogas_results.loc[biogas_results["AwardedPowerInMWH"].notna()]
        biogas_results["new_time_step"] = biogas_results["TimeStep"] - operators_offset
        res_generation.append(biogas_results.groupby("new_time_step").sum()["AwardedPowerInMWH"])

    overall_res_generation = pd.DataFrame(index=res_generation[0].index, columns=["values"], data=0)
    for generation in res_generation:
        overall_res_generation["values"] += generation

    overall_res_generation = overall_res_generation["values"].reset_index(drop=True)

    return overall_res_generation


def evaluate_dispatch_per_group(
    operator_results: Dict, conventional_results: pd.DataFrame, operators_offset: int = 5, trader_offset: int = 4
) -> (pd.DataFrame, pd.DataFrame):
    """Evaluate the dispatch per group (res, conventionals, storages) as well as final storage states"""
    final_storage_levels = pd.DataFrame()
    generation = pd.DataFrame()
    for key, val in operator_results.items():
        if key in ["Biogas", "VariableRenewableOperator"]:
            value = val.loc[val["AwardedPowerInMWH"].notna()]
            value["new_time_step"] = value["TimeStep"] - operators_offset
            value = value.set_index("new_time_step")
            if generation.empty:
                # Properly define index if run for the first time
                generation = pd.DataFrame(
                    index=value.loc[value["AgentId"] == value["AgentId"].unique()[0]].index,
                    columns=[
                        "res",
                        "conventionals",
                        "storages_discharging",
                        "storages_charging",
                        "storages_aggregated_level",
                    ],
                    data=0,
                )
            for group in value.groupby("AgentId"):
                generation["res"] += group[1]["AwardedPowerInMWH"]
        elif key == "StorageTrader":
            storage_results = val[
                ["TimeStep", "AgentId", "AwardedDischargePowerInMWH", "AwardedChargePowerInMWH", "StoredEnergyInMWH"]
            ].dropna()
            storage_results["new_time_step"] = storage_results["TimeStep"] - trader_offset
            storage_results = storage_results.set_index("new_time_step")

            final_storage_levels = pd.DataFrame(
                index=[group[0] for group in storage_results.groupby("AgentId")], columns=["value"]
            )
            for group in storage_results.groupby("AgentId"):
                generation["storages_discharging"] += group[1]["AwardedDischargePowerInMWH"]
                generation["storages_charging"] += group[1]["AwardedChargePowerInMWH"]
                generation["storages_aggregated_level"] += group[1]["StoredEnergyInMWH"]
                final_storage_levels.at[group[0], "value"] = group[1]["StoredEnergyInMWH"].iloc[-1]

    conventional_generation = conventional_results[["TimeStep", "AgentId", "AwardedPowerInMWH"]].dropna()
    conventional_generation["new_time_step"] = conventional_generation["TimeStep"] - operators_offset
    conventional_generation = conventional_generation.set_index("new_time_step")

    for group in conventional_generation.groupby("AgentId"):
        generation["conventionals"] += group[1]["AwardedPowerInMWH"]

    generation.reset_index(drop=True, inplace=True)

    return generation, final_storage_levels
