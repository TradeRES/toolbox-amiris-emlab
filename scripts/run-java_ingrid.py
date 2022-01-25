import sys
import subprocess
import os
# Create command arguments
args = ['java'] + sys.argv[1:]
#os.chdir("C:\\Users\\isanchezjimene\\Documents\\TraderesCode\\toolbox-amiris-emlab\\amiris")
print(f"Executing command '{' '.join(args)}'")
subprocess.run(args, check=True)   
