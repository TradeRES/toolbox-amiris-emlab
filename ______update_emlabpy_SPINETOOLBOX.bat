call activate emlabpy
python setup.py install
python -m pip install --editable .
set RELATIVE_FOLDER= %CD%
echo Relative folder: %RELATIVE_FOLDER%
set SUBFOLDER=preparation_scripts
cd %RELATIVE_FOLDER%\%SUBFOLDER%
echo Current folder: %CD%
python CleanDBs.py
echo !!!!!!!!!!!!!!!!!!!!!!!!
cd ..
echo Current folder: %CD%
call conda deactivate
call activate spinetoolbox
spinetoolbox
@pause