#-*- coding:utf-8 -*-

__version__ = '0.2.0'
__authors__ = 'Felix Nitsch'
__maintainer__ = 'Felix Nitsch'
__email__ = 'felix.nitsch@dlr.de'

import sys
import os
print("current", os.getcwd())
import ioproc.runners as run

sys.path.append("../../")
run.start()
