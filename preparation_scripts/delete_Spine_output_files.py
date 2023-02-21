import glob
import os
import shutil

from os import path
# Removing files where fails
pattern = r"C:\toolbox-amiris-emlab\.spinetoolbox\items\**\output\failed\*\*"
for item in glob.iglob(pattern, recursive=True):
    print("Deleting:", item)
    os.remove(item)


#Removing dirs where fails
pattern = r"C:\toolbox-amiris-emlab\.spinetoolbox\items\**\output\failed\*"
for item in glob.iglob(pattern, recursive=True):
    print("Deleting:", item)
    os.rmdir(item)

#Removing files where no failsfails
pattern = r"C:\toolbox-amiris-emlab\.spinetoolbox\items\**\output\*\*"
for item in glob.iglob(pattern, recursive=True):
    print("Deleting:", item)
    if path.isfile(item):
        os.remove(item)


def handler(func, path, exc_info):
    print("Inside handler")
    print(exc_info)
#Removing dirs where no fails
pattern = r"C:\toolbox-amiris-emlab\.spinetoolbox\items\**\output\*"

for item in glob.iglob(pattern, recursive=True):
    print("Deleting:", item)
    shutil.rmtree(item,  onerror = handler)

print("finished")