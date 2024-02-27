@echo off

set RELATIVE_FOLDER= %CD%
echo Relative folder: %RELATIVE_FOLDER%
set SUBFOLDER=preparation_scripts
cd %RELATIVE_FOLDER%\%SUBFOLDER%
echo Current folder: %CD%
python delete_Spine_output_files.py
@pause
