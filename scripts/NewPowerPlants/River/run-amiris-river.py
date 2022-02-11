import sys
import subprocess
import os
# Create command arguments
print("arguments" ,  "*"*40)
print(sys.argv[1:])

args = ['java'] + sys.argv[1:]
os.chdir("C:\\Users\\isanchezjimene\\Documents\\TraderesCode\\toolbox-amiris-emlab\\scripts\\NewPowerPlants\\River")

print(f"Executing command '{' '.join(args)}'")
subprocess.run(args, check=True)   
