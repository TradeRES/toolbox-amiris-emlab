# -*- coding:utf-8 -*-

__version__ = '0.2.0'
__authors__ = 'Felix Nitsch'
__maintainer__ = 'Felix Nitsch'
__email__ = 'felix.nitsch@dlr.de'


import os
from enum import Enum
import re

import yaml
import numpy as np
import pandas as pd

from ioproc.logger import mainlogger
from typing import List

OUTPUT_FILE_ENDING = ".csv"


class FilterType(Enum):
    EQUAL = 0
    GREATER = 1
    GREATEREQUAL = 2
    LESS = 3
    LESSEQUAL = 4
    NOT = 5
    
    
def raise_and_log_critical_error(error_message):
    """ Raises a critical error and logs with given `error_message` """
    mainlogger.critical(error_message)
    raise Exception(error_message)


def to_list(data):
    """ Ensures that `data` is list """
    if isinstance(data, list):
        return data
    elif isinstance(data, tuple):
        return list(data)
    else:
        return [data]


class Header(Enum):
    TRUE = 0
    FALSE = None


def get_header(string):
    """" Returns converted operator from given bool """
    header_map = {True: Header.TRUE.value,
                  False: Header.FALSE.value,
                  }
    return header_map[string]


def get_field(dictionary, key):
    """ Returns value from given `dictionary` and raises `KeyError` if `key` is not specified """
    try:
        return dictionary[key]
    except KeyError:
        message = "Missing key '{}'. Given keys are '{}'.".format(key, [key for key in dictionary.keys()])
        raise_and_log_critical_error(message)


def get_excel_sheet(params):
    """ Returns a list of excel_sheets to parse from given dictionary or raises error when field is not specified """
    try:
        return get_field(params, 'excelSheet')
    except KeyError:
        message = "Please specify the Excel sheet(s) to parse in a list using under the field `excelSheets`."
        raise_and_log_critical_error(message)


def get_from_dict_or_default(key, dict, default):
    """Returns value for `key` in `dict` otherwise returns `default`"""
    if key in dict:
        return dict[key]
    else:
        return default


def filter_for_columns(data: pd.DataFrame, filter_columns: list, filter_value: list, filter_types: list):
    """
    Returns 'data' which is filtered for 'filter_values' in 'filter_columns'. The filters are applied consecutively,
    meaning that the results are narrowed down with each filter application.
    """
    data_to_filter = data.reset_index()
    for column_to_filter, filter_value, filter_type in zip(to_list(filter_columns), filter_value, filter_types):
        mainlogger.info("Filtering '{}' being '{}' to/than '{}'".format(column_to_filter, filter_type, filter_value))
        if filter_type is FilterType.EQUAL:
            mask = determine_intersection_mask(data_to_filter, to_list(column_to_filter), filter_value)
            data_to_filter = data_to_filter.loc[mask]
        elif filter_type is FilterType.NOT:
            mask = determine_intersection_mask(data_to_filter, to_list(column_to_filter), filter_value)
            data_to_filter = data_to_filter.loc[~mask]
        elif filter_type is FilterType.GREATER:
            data_to_filter = data_to_filter.loc[data_to_filter[column_to_filter] > filter_value]
        elif filter_type is FilterType.GREATEREQUAL:
            data_to_filter = data_to_filter.loc[data_to_filter[column_to_filter] >= filter_value]
        elif filter_type is FilterType.LESS:
            data_to_filter = data_to_filter.loc[data_to_filter[column_to_filter] < filter_value]
        elif filter_type is FilterType.LESSEQUAL:
            data_to_filter = data_to_filter.loc[data_to_filter[column_to_filter] <= filter_value]
        else:
            raise_and_log_critical_error("'{}' not implemented.".format(filter_type))
        data_to_filter.reset_index(drop=True, inplace=True)
    if any(data.index.names):
        data_to_filter.set_index(keys=data.index.names, inplace=True)
    return data_to_filter


def determine_intersection_mask(data: pd.DataFrame, column_names: list, values_to_filter: list) -> pd.Series:
    """
    Returns a boolean mask as Series. For each 'column_name' in 'data' True is returned if row value matches at
    least one in 'values_to_filter'. This also supports the wildcard '*' which are replaced by '.*' and applied as
    regex.
    """
    mask = pd.DataFrame(index=data.index)
    ensure_all_str(values_to_filter)
    values_to_filter = get_at_least_2d_array(to_list(values_to_filter))
    for column_index, column_name in enumerate(column_names):
        relevant_values = np.squeeze(values_to_filter[:, column_index:column_index + 1])
        if str(relevant_values) == "*":
            mask[column_index] = np.full(len(data[column_name]), True)
        else:
            relevant_values = np.atleast_1d(relevant_values)
            for value in list(relevant_values):
                check_if_in_list(value, list(set(data[column_name].values.flat)))
            if "*" not in str(relevant_values):
                mask[column_index] = data[column_name].isin(relevant_values)
            else:
                relevant_values = [str(entry).replace("*", ".*") for entry in relevant_values]
                reg_ex_mask = "(" + '|'.join(relevant_values) + ")"
                mask[column_index] = apply_re_fullmatch(reg_ex_mask, data[column_name])
    return mask.all(axis='columns')


def check_if_in_list(value: str, data: list):
    """ Raises error if given 'value' is not part in 'data' while accounting for regex wildcard '*' """
    if not data:
        raise_and_log_critical_error("Cannot validate if `{}` is in list because of empty list.".format(value))

    if len(value) == 0:
        raise_and_log_critical_error("Cannot validate if item of len()=0 is in list `{}`.".format(data))

    reg_ex_mask = value.replace("*", ".*")
    mask = apply_re_fullmatch(reg_ex_mask, data)
    if not any(mask):
        raise_and_log_critical_error("Selection `{}` is not in available values `{}`.".format(value, data))


def get_at_least_2d_array(data):
    """ Returns at least 2 dimensional np array of given data """
    data = np.array(data)
    if data.ndim < 2:
        data = np.expand_dims(data, axis=1)
    return data


def ensure_all_str(items):
    """ Raises exception if any item in 'items' (flat or nested) is not of type string """
    items = to_list(items)
    for item in items:
        if isinstance(item, list):
            ensure_all_str(item)
        elif not isinstance(item, str):
            raise_and_log_critical_error("Item `{}` in given list `{}` must be of type str().".format(item, items))


def apply_re_fullmatch(mask, data):
    """ Returns bool list of re.fullmatch when applying 'mask' on 'data' """
    return [bool(re.fullmatch(mask, str(s))) for s in data]


def write_yaml(config_file, output_file_path):
    """ Writes given `config_file` in yaml format to `output_file_path` """
    with open(output_file_path, 'w') as stream:
        try:
            yaml.safe_dump(config_file, stream)
        except yaml.YAMLError:
            raise_and_log_critical_error("Failed writing yaml to {}".format(output_file_path))


def ensure_path_exists(path):
    """ Creates a specified path if not already existent """
    if not os.path.exists(path):
        os.makedirs(path)


def unflatten_list_of_dicts(list_of_dicts):
    """ Returns list of `input` dicts as unflattened dictionaries for keys with the special character `/` """
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


def insert_agents_from_map(data, translation_map, template):
    """
    Appends list of agents to given `template` as specified in `translation_map`. For each row in given `data`, it
    iterates over `translations` in `translation_map` and creates agent. The agent creation can also be for an
    specified agent type as defined with `column` and `target`.
    Values for the agent attributes can be derived directely from the `translation_map` when specified as `value` or be
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
                column = get_field(translation, 'column')
                target = get_field(translation, 'target')
                if row[column] == target:
                    agent = create_agent(row, translation['map'])
                    agent_list.append(agent)
                else:
                    continue
            elif isinstance(translation, list):
                agent = create_agent(row, translation)
                agent_list.append(agent)
            else:
                raise_and_log_critical_error("Failed creating agent specified as {}".format(translation))
            registered_agents_per_plant[agent['Type']] = agent['Id']
        all_registered_agents.append(registered_agents_per_plant)

    agent_list = unflatten_list_of_dicts(agent_list)

    if not template['Agents']:
        template['Agents'] = agent_list
    else:
        template['Agents'].extend(agent_list)

    return template, all_registered_agents


def create_agent(row, translation):
    """ Returns created agent from data in `row` according to specifications in `translation`. """
    agent = {}
    for item in translation:
        field = get_field(item, 'attribute')
        if 'value' in item:
            value = get_field(item, 'value')
        elif 'column' in item:
            column = get_field(item, 'column')
            value = get_field(row, column)
            if 'suffix' in item:
                value = str(value) + str(get_field(item, 'suffix'))
                value = int(value)
        else:
            raise_and_log_critical_error("No 'value' or `column` found for attribute '{}'".format(item))
        agent.update({field: value})
    return agent


def get_filter_type_lists(filters):
    """
    Returns list of `type` values from list of `filters` with key `type`.
    If 'type' is not specified for any filter, FilterType 'EQUAL' is used.
    """
    filter_type_lists = []
    for filter_item in filters:
        if 'type' in filter_item.keys():
            filter_type = get_filter_type(filter_item['type'])
        else:
            filter_type = FilterType.EQUAL
        filter_type_lists.append(filter_type)
    return filter_type_lists


def get_filter_type(filter_name):
    """ Returns FilterType enum of given `filter_name` """
    try:
        return FilterType[filter_name.upper()]
    except KeyError:
        message = "Unknown filter type '{}'. Please provide one of the following: {}".\
            format(filter_name, [f.name for f in FilterType])
        raise_and_log_critical_error(message)


def get_id_or_derive_from_type(contract, unit, param):
    """
    Returns Id derived from `param`+`id` in given `contract` dict or derived from `param`+`Type` in unit dictionary.
    Raises error if Id cannot be found either in `contract` or `unit`.
    """
    if param + 'Id' in contract:
        return get_field(contract, param + 'Id')
    else:
        return unit[get_field(contract, param + 'Type')]
    raise_and_log_critical_error("Cannot derive Id for the contract '{}'.".format(contract))


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
                if 'sender' in field.lower():
                    value = get_id_or_derive_from_type(translation, unit, 'Sender')
                    field = 'SenderId'
                elif 'receiver' in field.lower():
                    value = get_id_or_derive_from_type(translation, unit, 'Receiver')
                    field = 'ReceiverId'
                else:
                    value = get_field(translation, field)
                contract.update({field: value})
            contract_list.append(contract)

    if not template['Contracts']:
        template['Contracts'] = contract_list
    else:
        template['Contracts'].extend(contract_list)

    return template


def round_to_full_hour(time_step: int, base=3600) -> int:
    """Returns given `time_step` and rounds it to nearest full hour"""
    return base * round(time_step / base)


def ensure_given_data_matches_dims(x_dim: int, y_dim: int, data: list):
    """Raises error when dimensions `x_dim` x `y_dim` don't match length of specified data"""
    if x_dim * y_dim != len(data):
        raise_and_log_critical_error("Defined dimensions {}X{} don't match length of specified data {}".
                                     format(x_dim, y_dim, len(data)))


def check_if_window_too_large(win_size, simulation_length):
    """Raises warning when `win_size` is greater than `simulation_length`"""
    if win_size > simulation_length:
        difference = win_size - simulation_length
        difference = round(divmod(difference.total_seconds(), 3600)[0])
        msg = "Given window size is `{}` hours greater than simulation length. \
            Please choose a shorter window size.".format(difference)
        mainlogger.warning(msg)


def get_all_files_in_folder_ending_with(folder: str, ending: str) -> List[str]:
    """Returns a list of strings including path to folder for files with given ending"""
    return [folder + "/" + file for file in os.listdir(folder) if file.endswith(ending)]


def get_all_csv_files_in_folder(folder: str) -> List[str]:
    """Returns list of strings including path to folder for CSV files"""
    return get_all_files_in_folder_ending_with(folder=folder, ending=OUTPUT_FILE_ENDING)
