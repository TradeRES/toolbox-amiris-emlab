call activate emlabpy
python setup.py install
python -m pip install --editable .
call conda deactivate
call activate spinetoolbox
python "C:\toolbox-amiris-emlab\scripts\Util\CleanDBs.py"
spinetoolbox
@pause