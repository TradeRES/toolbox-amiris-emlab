import sys
import os
from pathlib import Path
from glob import glob
# from datetime import timedelta
import datetime as dt
import pandas as pd
from fameio.scripts.convert_results import run as convert_results
from fameio.source.cli import Config
from fameio.source.time import FameTime, Constants
import math

CONFIG = {
    Config.LOG_LEVEL: "info",
    Config.LOG_FILE: None,
    Config.AGENT_LIST: None,
    Config.OUTPUT: 'FameResults_converted_gas',
    Config.SINGLE_AGENT_EXPORT: False
}


def process_file(filepath: str) -> pd.DataFrame:
    """Process single AMIRIS csv file"""
    df = pd.read_csv(filepath, sep=';')
    object_class = Path(filepath).stem
    assert df.columns[1] == 'TimeStep'
    assert df.columns[0] == 'AgentId'
    # Convert times steps
    df['TimeStamp'] = df['TimeStep'].apply(roundup)
    df['TimeStamp'] = df['TimeStamp'].apply(convert_fame_time_step_to_datetime)
    df['ObjectClass'] = object_class
    return df.drop('TimeStep', axis=1).melt(['ObjectClass', 'AgentId', 'TimeStamp']).dropna()


def roundup(x):
    return round(x / 1000.0) * 1000


def convert_fame_time_step_to_datetime(fame_time_steps: int) -> str:
    """Converts given `fame_time_steps` to corresponding real-world datetime string"""
    years_since_start_time = math.floor(fame_time_steps / Constants.STEPS_PER_YEAR)
    current_year = years_since_start_time + Constants.FIRST_YEAR
    beginning_of_year = dt.datetime(year=current_year, month=1, day=1, hour=0, minute=0, second=0)
    steps_in_current_year = (fame_time_steps - years_since_start_time * Constants.STEPS_PER_YEAR)
    seconds_in_current_year = steps_in_current_year / Constants.STEPS_PER_SECOND
    simulatedtime = beginning_of_year + dt.timedelta(seconds=seconds_in_current_year)
    timerounded = simulatedtime.replace(second=0, microsecond=0, minute=0, hour=simulatedtime.hour) + dt.timedelta(
        hours=simulatedtime.minute // 30)
    return timerounded.strftime('%Y-%m-%dT%H:%M:%S')


# Get input file from cmd line arguments
print("GAS ----------------------------------------------")
print("PATH")
print(os.getcwd())
print("PB")
print(sys.argv[1])
input_pb_file = sys.argv[1]

#parent = os.path.basename(os.getcwd())
#complete = os.path.join(Path(os.getcwd()).parent, "data", input_pb_file)

# Convert Proto Buffer file to csv's
convert_results(input_pb_file, CONFIG)
# Combine csv files into one data frame
csv_files = glob(f'{CONFIG[Config.OUTPUT]}/*.csv')
data = pd.concat(map(process_file, csv_files))
grouped = data.groupby(["ObjectClass", "variable", "AgentId"]).sum()
# Write results
#data.to_csv('AMIRIS_combined.csv2', index=False)
grouped.to_csv('AMIRIS_combinedGas.csv', index=True)
