import sys
import subprocess

# Create command arguments
args = ['java'] + sys.argv[1:]
       
print(f"Executing command '{' '.join(args)}'")
subprocess.run(args, check=True)   
