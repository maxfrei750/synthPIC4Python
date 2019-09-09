@echo off
cls

set blender_version=2.80
set blender_platform=windows64

set blender_string=blender-%blender_version%-%blender_platform%
set blender_python_directory=%blender_string%\%blender_version%\python

cd external

echo [32mDeleting external\%blender_string% if it exists...[0m
rmdir /S /Q %blender_string% 2> nul
ver > nul

echo. 
echo [32mDownloading blender to external\%blender_string%.zip (may take a few minutes)...[0m 
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://ftp.halifax.rwth-aachen.de/blender/release/Blender%blender_version%/%blender_string%.zip', '%blender_string%.zip')"

echo. 
echo [32mUnzipping blender...[0m 
powershell -Command "Expand-Archive %blender_string%.zip ./"

echo. 
echo [32mDeleting blender archive, as it is no longer needed...[0m 
del %blender_string%.zip

if ERRORLEVEL 1 (
    echo [33mWarning: There was an error deleting the blender archive. Please delete it manually at external\%blender_string%.zip.[0m
    ver > nul
)

cd "%blender_python_directory%\bin\" 2> nul

if ERRORLEVEL 1 (
	echo. 
    echo [31mCouldn't find python.exe in external\%blender_python_directory%\bin\. Please check if blender was downloaded correctly and check the paths within this script.[0m
    echo. 
    pause
    exit /b 1
)

echo. 
echo [32mInstalling and updating pip...[0m 
python -m ensurepip

echo. 
python -m pip install -U pip

echo.
echo [32mUninstalling the numpy version that comes with blender (because it is buggy)...[0m 
python -m pip uninstall --yes numpy

echo.
echo [32mDeleting numpy remains...[0m 
rmdir /S /Q %blender_python_directory%\lib\site-packages\numpy 2> nul

if ERRORLEVEL 1 (
    echo [31mThere was an error deleting the numpy remains.[0m
    echo. 
    pause
    exit /b 1
)

echo.
echo [32mInstalling python dependencies...[0m 
cd "%blender_python_directory%\bin\" 2> nul

echo. 
python -m pip install numpy

echo. 
python -m pip install trimesh

if ERRORLEVEL 0 (
    echo.
	echo [32mSetup complete![0m
)

echo. 
pause