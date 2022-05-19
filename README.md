# AMIRIS EMLABpy softlinking using Spinetoolbox

The soft linking of AMIRIS and EMLabpy intends to investigate the investment
incentives in a future flexible power system. 
EMLabpy is based in EMLab and is rewritten in a modular way into python to easily couple with AMIRIS. 

## Workflow
The integration is best illustrated with following diagram. 
![](data/workflow.jpg)

## Folder structure

### `emlabpy`
This code is based on the model EMLab. http://emlab.tudelft.nl/

### `scripts`

This folder stores the code triggered from Spinetoolbox to do the data exchange

### `amiris`

This is the code from the amiris project https://gitlab.com/dlr-ve/esy/amiris/amiris/

### `amiris_workflow`

This workflow define the steps to feed data , run and export data from AMIRIS

### `actions`

These are the actions to run AMIRIS and which order is specified in the amiris_workflow

### `amiris_workflow`

Here is the tool that imports all the needed data to run AMIRIS into yaml files.
It also runs AMIRIS and exports the data to files to be imported back to EMLAB.

### `examples`

This folder contains the data to run Amiris https://gitlab.com/dlr-ve/esy/amiris/examples

### `data`

This folder could be used for storing the original data files.
Please add metadata and licensing information as well.

## License and Terms of Use

The Spine Toolbox project example provided here can be used without any 
limitations. This does not apply to any data files contained within or any parts of the models EMLab and AMIRIS.

The (Un)Licensing explicitly excludes:

    * Anything under "amiris", for which license of https://gitlab.com/dlr-ve/esy/amiris/amiris applies
    * Anything under "EMLABPY", for which MIT License applies
    * Any data contained in this repository.
