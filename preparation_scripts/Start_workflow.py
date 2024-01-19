import pathlib
import subprocess
import sys
from spinedb_api import create_new_spine_database

db_file = pathlib.Path("C:\\toolbox-amiris-emlab\\.spinetoolbox\\items\\emlabdb\\EmlabDB.sqlite")
db_file.unlink()
url = "sqlite:///" + str(db_file.resolve())
create_new_spine_database(url)



db_file_amiris = pathlib.Path("C:\\toolbox-amiris-emlab\\.spinetoolbox\\items\\amiris_db\\AMIRIS DB.sqlite")
db_file_amiris.unlink()
url_amiris = "sqlite:///" + str(db_file_amiris.resolve())
create_new_spine_database(url_amiris)


project_dir = pathlib.Path(".")
completed_process = subprocess.run([sys.executable, "-m", "spinetoolbox", "--execute-only", str(project_dir)])
if completed_process.returncode != 0:
    print("Run failed.")