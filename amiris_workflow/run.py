import sys
import os

print("current", os.getcwd())
import ioproc.runners as run  # noqa

sys.path.append("../../")
run.start()
