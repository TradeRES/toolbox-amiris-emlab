import sys
import os
from glob import glob
from pathlib import Path

from fameio.scripts.make_config import run as make_config
from fameio.source.cli import Config

CONFIG = {
    Config.LOG_LEVEL: 'info',
    Config.OUTPUT: 'fameConfigGas.pb',
    Config.LOG_FILE: None,
}

# Get scenario file from the command line
scenario_yaml = sys.argv[1] 

# Hack to overcome the issue that `make_config` has to be run
# from the scenario root dir (containing yaml and data folders
curdir = os.getcwd()
print("curdir ", curdir)
print("Path ", Path(scenario_yaml))
print("Config.OUTPUT", Config.OUTPUT)
print("CONFIG[Config.OUTPUT]", os.path.join(curdir, CONFIG[Config.OUTPUT]))

try:
    os.chdir(Path(scenario_yaml).parent)
    make_config(scenario_yaml, CONFIG)
    os.replace(CONFIG[Config.OUTPUT], os.path.join(curdir, CONFIG[Config.OUTPUT]))
except: 
    raise
finally:
    os.chdir(curdir)
