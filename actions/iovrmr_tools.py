__version__ = "0.2.0"
__authors__ = "Felix Nitsch"
__maintainer__ = "Felix Nitsch"
__email__ = "felix.nitsch@dlr.de"


import os
from enum import Enum, auto
from typing import List, Callable, Dict, NoReturn, Any, Union, Hashable

import pandas as pd
import yaml
from fameio.source.loader import load_yaml
from ioproc.logger import mainlogger

OUTPUT_FILE_ENDING = ".csv"
OPERATOR_AGENTS = [
    "VariableRenewableOperator",
    "Biogas",
    "StorageTrader",
    "ElectrolysisTrader",
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
SUPPORT_SCHEMES = {
    "NONE": "NoSupportTrader",
    "MPVAR": "RenewableTrader",
    "MPFIX": "RenewableTrader",
    "CFD": "RenewableTrader",
    "CP": "RenewableTrader",
    "FIT": "SystemOperatorTrader",
}
TRADER_SUFFIX = 10000


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
    CONSUMPTION_IN_MWH = auto()
    ENERGY_SHEDDED_IN_MWH = auto()


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
                            if append_operation["agent"] == 90 and "SupportPolicy" not in registered_agents_per_plant:
                                registered_agents_per_plant["SupportPolicy"] = 90
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
            if registered_agents_per_plant not in all_registered_agents:
                all_registered_agents.append(registered_agents_per_plant)

    agent_list = nest_flattened_items(agent_list)

    if len(agent_list) > 0 and agent_list[0]["Type"] in "VariableRenewableOperator":
        marketers = [agent for agent in agent_list if agent["Type"] in SUPPORT_SCHEMES]
        operators = [agent for agent in agent_list if agent not in marketers]
        for marketer in marketers:
            marketer["Type"] = SUPPORT_SCHEMES[marketer["Type"]]
            if marketer["Type"] in ["RenewableTrader", "NoSupportTrader"]:
                marketer["Attributes"] = {
                    "ShareOfRevenues": 0,
                }
            if marketer["Type"] == "RenewableTrader":
                marketer["Attributes"]["MarketValueForecastMethod"] = "PREVIOUS_MONTH"
        res_operators_and_marketers = []
        res_energy_carriers_and_operators = []
        for operator in operators:
            res_operators_and_marketers.append(add_trader_mapping(operator))
            res_energy_carriers_and_operators.append(add_energy_carrier_mapping(operator))

        template["Agents"].extend(agent_list)

        return (
            template,
            all_registered_agents,
            res_operators_and_marketers,
            res_energy_carriers_and_operators,
        )

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
        elif "list" in item:
            value = get_field(item, "list")
            value = get_elements_from_list(value, row)
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


def get_elements_from_list(value: List, row: pd.Series) -> List[Dict]:
    """Obtain list-like elements"""
    value = value.copy()
    length = value.pop(0)["length"]
    attr_dict = {col_count: {} for col_count in range(length)}
    for entry in value:
        for col_count in range(length):
            if "value" in entry:
                if isinstance(entry["value"], list):
                    value = get_field(entry, "value")[col_count]
                    attr_dict[col_count][entry["attribute"]] = value
                else:
                    value = entry["value"]
                    attr_dict[col_count][entry["attribute"]] = value
            elif "column" in entry:
                column = get_field(entry, "column")[col_count]
                value = get_field(row, column)
                attr_dict[col_count][entry["attribute"]] = value

    return list(attr_dict.values())


def add_trader_mapping(operator: Dict) -> Dict:
    """Add mapping between operator and trader and remove SupportInstrument attribute in case of no support"""
    try:
        support_instrument = operator["Attributes"]["SupportInstrument"]
        if support_instrument == "NONE":
            operator["Attributes"].pop("SupportInstrument")
    except KeyError:
        raise ValueError("Missing support instrument specification!")
    return {
        "Operator": operator["Id"],
        "Trader": int(str(operator["Id"]) + str(TRADER_SUFFIX)),
    }


def add_energy_carrier_mapping(operator: Dict) -> Dict:
    """Add mapping between operator and energy carrier for renewable energies"""
    try:
        energy_carrier = operator["Attributes"]["EnergyCarrier"]
    except KeyError:
        raise ValueError("Missing energy carrier specification!")
    return {"Operator": operator["Id"], "EnergyCarrier": energy_carrier}


def add_trader_by_support_instrument(agent: Dict, template: Dict):
    """Retrieve support instrument for VariableRenewableOperator and map Operator to Trader"""
    if agent["Type"] != "VariableRenewableOperator":
        raise ValueError(
            f"Malspecified AgentType: It should be 'VariableRenewableOperator'. You specified '{agent['Type']}'."
        )
    try:
        support_instrument = agent["Attributes"]["SupportInstrument"]
        if support_instrument in ["MPVAR", "MPFIX", "CFD", "CP"]:
            trader_id = retrieve_agent_id(template, "RenewableTrader")
        elif support_instrument == "FIT":
            trader_id = retrieve_agent_id(template, "SystemOperatorTrader")
        else:
            trader_id = retrieve_agent_id(template, "NoSupportTrader")
            agent["Attributes"].pop("SupportInstrument")
    except KeyError:
        trader_id = retrieve_agent_id(template, "NoSupportTrader")

    return {"Operator": agent["Id"], "Trader": trader_id}


def retrieve_agent_id(template: Dict, agent_type: str):
    """Retrieve Id for first item of given type of Agent from template"""
    for template_agent in template["Agents"]:
        if template_agent["Type"] == agent_type:
            return template_agent["Id"]


def get_storage_strategist_type(storage_traders: List[Dict], scenario: Dict) -> str:
    """Return type of storage strategist for given scenario"""
    strategist = None
    previous_strategist = None
    for storage_trader in storage_traders:
        trader_id = storage_trader["StorageTrader"]
        storage_attributes = retreive_agent_attributes_by_id(trader_id, scenario)
        if strategist:
            previous_strategist = strategist
        strategist = storage_attributes["Strategy"]["StrategistType"]
        if previous_strategist and previous_strategist != strategist:
            raise ValueError(
                "Working with different storage strategists is not implemented!\n"
                "Please use uniform strategist, either 'MULTI_AGENT_SIMPLE', "
                "'SINGLE_AGENT_MAX_PROFIT' or 'SINGLE_AGENT_MIN_SYSTEM_COST'."
            )

    return strategist


def retreive_agent_attributes_by_id(agent_id: int, scenario: Dict):
    """Return agent attributes for agent with given ID"""
    for agent in scenario["Agents"]:
        if agent["Id"] == agent_id:
            return agent["Attributes"]


def adjust_contracts_for_storages(
    strategist_type: str, inserted_agents: List[Dict], scenario: Dict, data: pd.DataFrame
):
    """Adjust contracts in scenario.yaml based on given storage type"""
    contracts_location = None
    if strategist_type == "MULTI_AGENT_SIMPLE":
        contracts_location = "./amiris-config/yaml/storage_contracts_multi/storage_contracts.yaml"
    elif strategist_type in ["SINGLE_AGENT_MAX_PROFIT", "SINGLE_AGENT_MIN_SYSTEM_COST"]:
        contracts_location = "./amiris-config/yaml/storage_contracts_single/storage_contracts.yaml"
        scenario = change_to_merit_order_forecaster(scenario)
        if agent_in_scenario("ElectrolysisTrader", scenario):
            raise ValueError(
                "'ElectrolysisTrader' requires a 'PriceForecaster', a 'StorageTrader' with strategy "
                "'SINGLE_AGENT_MAX_PROFIT' or 'SINGLE_AGENT_MIN_SYSTEM_COST' in turn requires a 'MeritOrderForecaster' "
                "instead. The two cannot be combined.\n"
                "Thus, you either can simulate an 'ElectrolysisTrader' in combination with a 'MULTI_AGENT_SIMPLE' "
                "storage strategy, or you have to remove the 'ElectrolysisTrader' from your scenario if you want "
                "to use the 'SINGLE_AGENT_MAX_PROFIT' or 'SINGLE_AGENT_MIN_SYSTEM_COST' strategy."
            )
    if not contracts_location:
        raise ValueError(
            "Invalid strategist type. Must be either 'MULTI_AGENT_SIMPLE', 'SINGLE_AGENT_MAX_PROFIT' "
            "or 'SINGLE_AGENT_MIN_SYSTEM_COST'."
        )

    translation_map = load_yaml(contracts_location)
    config_file = insert_contracts_from_map(
        inserted_agents,
        translation_map["Contracts"],
        scenario,
        res_operators_and_traders=None,
        raw_data=data,
    )

    return config_file


def agent_in_scenario(agent_type: str, scenario: Dict):
    """Check whether agent of certain type is in scenario"""
    for agent in scenario["Agents"]:
        if agent["Type"] == agent_type:
            return True

    return False


def change_to_merit_order_forecaster(scenario: Dict):
    """Change forecaster ID from price forecaster to merit order forecaster ID"""
    price_forecaster_id = retrieve_agent_id(scenario, "PriceForecaster")
    merit_order_forecaster_id = retrieve_agent_id(scenario, "MeritOrderForecaster")
    for contract in scenario["Contracts"]:
        if contract["ReceiverId"] == price_forecaster_id:
            contract["ReceiverId"] = merit_order_forecaster_id
        if contract["SenderId"] == price_forecaster_id:
            contract["SenderId"] = merit_order_forecaster_id

    return scenario


def insert_contracts_from_map(data, translation_map, template, res_operators_and_traders, raw_data):
    """
    Appends list of contracts to the given `template` as specified in `translation_map`.
    'SenderId' and 'ReceiverId' are derived either from `translation_map` if specified or from given 'data' which
    stores all inserted agents. Returns filled `template`.
    """
    if not res_operators_and_traders:
        if not list(data[0].keys())[0] == "SupportPolicy":
            contract_list = fill_contracts_list(data, translation_map)
        else:
            contract_list = fill_contracts_list_for_policy(data, translation_map, raw_data)
    else:
        contract_list = fill_contracts_list_for_res(data, translation_map, res_operators_and_traders)

    if not template["Contracts"]:
        template["Contracts"] = contract_list
    else:
        template["Contracts"].extend(contract_list)

    return template


def fill_contracts_list(data: list, translation_map: list):
    """Insert contracts and return contract list using standard approach"""
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
            if contract["SenderId"] and contract["ReceiverId"]:
                contract_list.append(contract)

    return contract_list


def fill_contracts_list_for_res(data: list, translation_map: list, res_operators_and_traders: list):
    """Insert contracts and return contract list using approach for RES (check for corresponding trader)"""
    contract_list = []
    for unit in data:
        # Only one dictionary entry
        unit_id = list(unit.values())[0]
        for translation in translation_map:
            contract = {}
            for field in translation:
                if "sender" in field.lower():
                    value = get_id_or_derive_from_type(translation, unit, "Sender")
                    # Replace placeholder marketer
                    if value != unit_id:
                        for entry in res_operators_and_traders:
                            if entry["Operator"] == unit_id:
                                value = entry["Trader"]
                                break
                    field = "SenderId"
                elif "receiver" in field.lower():
                    value = get_id_or_derive_from_type(translation, unit, "Receiver")
                    # Replace placeholder marketer
                    if value != unit_id:
                        for entry in res_operators_and_traders:
                            if entry["Operator"] == unit_id:
                                value = entry["Trader"]
                                break
                    field = "ReceiverId"
                else:
                    value = get_field(translation, field)
                contract.update({field: value})
            if contract["SenderId"] and contract["ReceiverId"]:
                contract_list.append(contract)

    return contract_list


def fill_contracts_list_for_policy(data: list, translation_map: list, raw_data: pd.DataFrame):
    """Insert contracts and return contract list using approach for policy (add traders)"""
    all_traders, supported_traders = obtain_traders_from_renewables_data(raw_data)
    contract_list = []
    support_contracts = [
        "SupportInfoRequest",
        "SupportInfo",
        "SupportPayoutRequest",
        "SupportPayout",
    ]
    for unit in data:
        for translation in translation_map:
            contract = {}
            for field in translation:
                if "sender" in field.lower():
                    value = get_id_or_derive_from_type(translation, unit, "Sender")
                    if not value:
                        if translation["ProductName"] in support_contracts:
                            value = supported_traders
                        else:
                            value = all_traders
                    field = "SenderId"
                elif "receiver" in field.lower():
                    value = get_id_or_derive_from_type(translation, unit, "Receiver")
                    if not value:
                        if translation["ProductName"] in support_contracts:
                            value = supported_traders
                        else:
                            value = all_traders
                    field = "ReceiverId"
                else:
                    value = get_field(translation, field)
                contract.update({field: value})
            if contract["SenderId"] and contract["ReceiverId"]:
                contract_list.append(contract)

    return contract_list


def obtain_traders_from_renewables_data(raw_data: pd.DataFrame):
    """Extract renewable traders for simulation based on support information from raw data for renewables"""
    all_traders = list((raw_data["identifier"].astype(str) + str(TRADER_SUFFIX)).values)
    supported_traders = list(
        (raw_data.loc[raw_data["SupportInstrument"] != "NONE", "identifier"].astype(str) + str(TRADER_SUFFIX)).values
    )
    all_traders = [int(trader_id) for trader_id in all_traders]
    supported_traders = [int(trader_id) for trader_id in supported_traders]

    return all_traders, supported_traders


def get_id_or_derive_from_type(contract, unit, param):
    """
    Returns Id derived from `param`+`id` in given `contract` dict or derived from `param`+`Type` in unit dictionary.
    Raises error if Id cannot be found either in `contract` or `unit`.
    """
    if param + "Id" in contract:
        return get_field(contract, param + "Id")
    else:
        return unit[get_field(contract, param + "Type")]


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
    residual_load_results: Dict[str, pd.DataFrame],
    operators_offset: int = 5,
    demand_offset: int = 1,
    offer_offset: int = 2,
) -> pd.DataFrame:
    """Calculate the residual load based on RES infeed and planned load (not considering storage / shedding etc.)"""
    residual_load = pd.DataFrame(
        columns=["residual_load_actual_infeed", "planned_demand", "res_potential", "residual_load_res_potential"]
    )
    to_aggregate = {"res_generation": [], "res_potential": [], "planned_demand": []}
    for key, val in residual_load_results.items():
        if key in OPERATOR_AGENTS:
            to_aggregate["res_generation"].append(extract_values(val, "AwardedPowerInMWH", -operators_offset))
            to_aggregate["res_potential"].append(extract_values(val, "OfferedPowerInMW", offer_offset))
        elif key in DEMAND:
            to_aggregate["planned_demand"].append(extract_values(val, "RequestedEnergyInMWH", demand_offset))
        else:
            raise ValueError("Received invalid key for residual_load_results!")

    overall_vres_generation = calculate_overall_value(to_aggregate["res_generation"])
    residual_load["res_potential"] = calculate_overall_value(to_aggregate["res_potential"])
    residual_load["planned_demand"] = calculate_overall_value(to_aggregate["planned_demand"])

    residual_load["residual_load_actual_infeed"] = residual_load["planned_demand"] - overall_vres_generation
    residual_load["residual_load_res_potential"] = residual_load["planned_demand"] - residual_load["res_potential"]
    residual_load = residual_load.round(4)
    residual_load.reset_index(drop=True, inplace=True)

    return residual_load


def extract_values(val: pd.DataFrame, col_name: str, offset: int):
    """Extract time series values for one type of agents"""
    value = val.loc[val[col_name].notna()]
    value["new_time_step"] = value["TimeStep"] + offset
    return value.groupby("new_time_step").sum()[col_name]


def calculate_overall_value(to_aggregate: List[pd.DataFrame]):
    """Calculate overall time series value for one type of agents"""
    overall_value = pd.Series(index=to_aggregate[0].index, data=0)
    for entry in to_aggregate:
        overall_value += entry

    return overall_value


def calculate_overall_res_infeed(
    residual_load_results: Dict[str, pd.DataFrame],
    biogas_results: pd.DataFrame,
    operators_offset: int = 5,
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
    operator_results: Dict,
    conventional_results: pd.DataFrame,
    demand_results: pd.DataFrame,
    renewables_energy_carriers: pd.DataFrame = None,
    operators_offset: int = 5,
    trader_offset: int = 4,
    demand_offset: int = 1,
) -> (pd.DataFrame, pd.DataFrame):
    """Evaluate the dispatch per group (res, conventionals, storages) as well as final storage states"""
    final_storage_levels = pd.DataFrame()
    dispatch = pd.DataFrame()
    for key, val in operator_results.items():
        if key in ["Biogas", "VariableRenewableOperator"]:
            operator_results = val.loc[val["AwardedPowerInMWH"].notna()]
            operator_results["new_time_step"] = operator_results["TimeStep"] - operators_offset
            operator_results = operator_results.set_index("new_time_step")
            if dispatch.empty:
                dispatch = initialize_dispatch(operator_results)
            for group in operator_results.groupby("AgentId"):
                dispatch["res"] += group[1]["AwardedPowerInMWH"]
            if key == "VariableRenewableOperator":
                dispatch = extract_generation_by_energy_carrier(operator_results, renewables_energy_carriers, dispatch)
        elif key == "StorageTrader":
            storage_results = val[
                [
                    "TimeStep",
                    "AgentId",
                    "AwardedDischargePowerInMWH",
                    "AwardedChargePowerInMWH",
                    "StoredEnergyInMWH",
                ]
            ].dropna()
            storage_results["new_time_step"] = storage_results["TimeStep"] - trader_offset
            storage_results = storage_results.set_index("new_time_step")
            if dispatch.empty:
                dispatch = initialize_dispatch(storage_results)

            final_storage_levels = pd.DataFrame(
                index=[group[0] for group in storage_results.groupby("AgentId")],
                columns=["value"],
            )
            for group in storage_results.groupby("AgentId"):
                dispatch["storages_discharging"] += group[1]["AwardedDischargePowerInMWH"]
                dispatch["storages_charging"] += group[1]["AwardedChargePowerInMWH"]
                dispatch["storages_aggregated_level"] += group[1]["StoredEnergyInMWH"]
                final_storage_levels.at[group[0], "value"] = group[1]["StoredEnergyInMWH"].iloc[-1]
        elif key == "ElectrolysisTrader":
            electrolysis_results = val[
                [
                    "TimeStep",
                    "AgentId",
                    "AwardedEnergyInMWH",
                    "ProducedHydrogenInMWH",
                ]
            ].dropna()
            electrolysis_results["new_time_step"] = electrolysis_results["TimeStep"] - trader_offset
            electrolysis_results = electrolysis_results.set_index("new_time_step")
            if dispatch.empty:
                dispatch = initialize_dispatch(electrolysis_results)

            for group in electrolysis_results.groupby("AgentId"):
                dispatch["electrolysis_power_consumption"] += group[1]["AwardedEnergyInMWH"]
                dispatch["electrolysis_hydrogen_generation"] += group[1]["ProducedHydrogenInMWH"]

    conventional_generation = conventional_results[["TimeStep", "AgentId", "AwardedPowerInMWH"]].dropna()
    conventional_generation["new_time_step"] = conventional_generation["TimeStep"] - operators_offset
    conventional_generation = conventional_generation.set_index("new_time_step")

    for group in conventional_generation.groupby("AgentId"):
        dispatch["conventionals"] += group[1]["AwardedPowerInMWH"]

    # Ensure data set is sorted by agent ids in increasing order
    demand_results = demand_results.sort_values(by=["AgentId", "TimeStep"])
    demand_results["AwardedEnergyInMWH"].fillna(method="bfill", inplace=True)
    demand_dispatch = demand_results.dropna()
    demand_dispatch["Shedding"] = demand_dispatch["RequestedEnergyInMWH"] - demand_dispatch["AwardedEnergyInMWH"]
    demand_dispatch["new_time_step"] = demand_dispatch["TimeStep"] + demand_offset
    demand_dispatch = demand_dispatch.set_index("new_time_step")

    for group in demand_dispatch.groupby("AgentId"):
        dispatch["load_shedding"] += group[1]["Shedding"]
        dispatch[f"unit_{group[0]}"] = group[1]["Shedding"]

    dispatch.reset_index(drop=True, inplace=True)

    return dispatch, final_storage_levels


def initialize_dispatch(dispatch_df) -> pd.DataFrame:
    """Initialize a DataFrame for storing dispatch results"""
    return pd.DataFrame(
        index=dispatch_df.loc[dispatch_df["AgentId"] == dispatch_df["AgentId"].unique()[0]].index,
        columns=[
            "res",
            "conventionals",
            "storages_discharging",
            "storages_charging",
            "storages_aggregated_level",
            "load_shedding",
            "electrolysis_power_consumption",
            "electrolysis_hydrogen_generation",
        ],
        data=0,
    )


def extract_generation_by_energy_carrier(
    operator_results: pd.DataFrame, renewables_energy_carriers: pd.DataFrame, dispatch: pd.DataFrame
) -> pd.DataFrame:
    """Extract generation from variable renewables per energy carrier"""
    combined_df = pd.merge(
        operator_results.reset_index(), renewables_energy_carriers, how="left", left_on="AgentId", right_on="Operator"
    )
    combined_df = combined_df.set_index("new_time_step")
    for energy_carrier, values in combined_df.groupby("EnergyCarrier"):
        if energy_carrier not in dispatch.columns:
            dispatch[energy_carrier] = 0
        for group in values.groupby("AgentId"):
            dispatch[energy_carrier] += group[1]["AwardedPowerInMWH"]

    return dispatch
