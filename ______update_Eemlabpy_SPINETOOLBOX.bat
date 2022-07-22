call activate emlabpy
python setup.py install
python -m pip install .
call conda deactivate
call activate spinetoolbox
spinetoolbox
@pause