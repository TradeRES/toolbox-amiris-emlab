import sys
import os
from pathlib import Path
from glob import glob

import pandas as pd
from fameio.scripts.convert_results import run as convert_results
from fameio.source.cli import Config
from fameio.source.time import FameTime

csv_files = glob(f'{CONFIG[Config.OUTPUT]}/*.csv')