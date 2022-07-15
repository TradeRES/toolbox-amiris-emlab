# AMIRIS EMLABpy softlinking using Spinetoolbox

The soft linking of AMIRIS and EMLabpy intends to investigate the investment incentives in a future flexible power
system. EMLabpy is based in EMLab and is rewritten in a modular way into python to easily couple with AMIRIS.

<p align="center">
  <a href="#page_with_curl-license">License</a> •
</p>

# Workflow

The integration is best illustrated with following diagram.
![](data/workflow.jpg)
# How to run it
To run EMLabpy from the spinetoolbox, it needs to be packed as a python module. 
To do so, run the following commands in the toolbox-amiris-emlab folder:

## Prepare environments
To run this project 3 anaconda environments (or any other virtual environment of your preference) should be created: 
spinetoolbox-dev, iovrmr and EMLabpy. To do so following commands can be executed

### install anaconda
(with miniconda there have been some errors)

### AMIRIS (iovrmr)

Make sure that java > 8 is installed
in toolbox-amiris-emlab folder
```
conda env create -f environment.yml
``` 



### EMLABpy
in toolbox-amiris-emlab folder
```
python setup.py install -> if changes are done to the code
conda create -n emlabpy python=3.8
python -m pip install .
conda activate emlabpy
pip install -r requirements.txt
pip install git+https://github.com/Spine-project/spinetoolbox-dev
```
### spinetoolbox-dev
download spinetoolbox and install all requirements
```
conda create -n spinetoolbox-dev python=3.8
conda activate spinetoolbox-dev
pip install git+https://github.com/Spine-project/spinetoolbox-dev
git clone https://github.com/Spine-project/Spine-Toolbox
cd Spine-toolbox\
pip install -r requirements.txt
cd bin 
upgrade_spine_reqs.bat
```
In the toolbox-amiris-emlab folder activate  the environment spinetoolbox-dev. type spinetoolbox to start the tool in this environment, and in this folder.

Once the project is open, make an emlabpy kernel as follows:
In spinetooolbox > file > settings> tools > jupyter console> kernel spec editor>
add
imterpreter: path to the python.exe in your conda environment emlabpy
name: emlabpy
make kernel specification > ok

Also change the path on the (Amiris future tool > basic console) to the iovrmr conda enviroment
And change the results path to

###  kernel
after making the enviroments emlabpy and iovrmr, the kernels can be created in the tool specification editor and double clicking any tool
Then click kernel spec editor and make a new kernel called emlabpy referencing to your miniconda environment


## Other steps to run AMIRIS
add data in amiris_workflow\amiris-config\data\
add folder in amiris_workflow\amiris with executable, setup.yaml and log
add the empty folder amiris_workflow\amiris\result
everytime there is a new change in the code (including git pull) , the emlabpy environment has to be updated. For that double click file install_emlabpy.bat
in the AMIRIS make sure the output files is adjusted to ...toolbox-amiris-emlab\amiris_workflow\output\amiris_results.csv

# Folder structure

## EMLABpy

### `emlabpy`

This code is based on the model EMLab. http://emlab.tudelft.nl/

### `scripts`

This folder stores the code triggered from Spinetoolbox to do the data exchange

### `data`

This folder could be used for storing the original data files. Please add metadata and licensing information as well.

### `logs`

The logging from all the workflow can be found in this folder

### `logs`

The result plots from the EMLabpy - AMIRIS soft coupling

## AMIRIS

### `amiris`

This is the code from the AMIRIS project https://gitlab.com/dlr-ve/esy/amiris/amiris/
Outdated -> the code is now packed in amiris_workflow

### `examples`

This folder contains the data to run Amiris https://gitlab.com/dlr-ve/esy/amiris/examples

## AMIRIS IoVRMR
### `actions`

These are the actions to run AMIRIS and which order is specified in the amiris_workflow
### `output`

The processed amiris_results.xls that will be used by EMLAB are saved here

### `amiris_workflow`

Here is the tool that imports all the needed data to run AMIRIS into yaml files. It also runs AMIRIS and exports the
data to files to be imported back to EMLAB.

#### `data`

The excel timeseries (fuel prices, renewable profiles, demand, availability) to run AMIRIS should be stored in this
folder.

#### `amiris`

The log4j.properties, fame setup YAML and the amiris jar should be stored here

#### `results`

The file traderes.pb contain the encrypted results. 


### Input Data

All parameters are to be added in the excel file : EMLAbparameters.xls WIP
The data specific per country shoud be added in the tabs: 
Capacity Market, Electricity Spot Market

The initial power plants are added in the excel file: 


## :page_with_curl: License and Terms of Use

The Spine Toolbox project example provided here can be used without any limitations. This does not apply to any data
files contained within or any parts of the models EMLab and AMIRIS.

The (Un)Licensing explicitly excludes:

    * Anything under "amiris", for which license of https://gitlab.com/dlr-ve/esy/amiris/amiris applies
    * Anything under "EMLABPY", for which MIT License applies
    * Any data contained in this repository.
