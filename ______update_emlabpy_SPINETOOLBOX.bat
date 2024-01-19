call activate emlabpy
python setup.py install
python -m pip install --editable .
call conda deactivate
call activate spinetoolbox
python "C:\toolbox-amiris-emlab\preparation_scripts\CleanDBs.py"
spinetoolbox
@pause