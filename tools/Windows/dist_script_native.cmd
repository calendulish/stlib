@echo off
pushd %~dp0..\\.. || exit 1
::
:: Lara Maia <dev@lara.monster> 2015 ~ 2023
::
:: The stlib is free software: you can redistribute it and/or
:: modify it under the terms of the GNU General Public License as
:: published by the Free Software Foundation, either version 3 of
:: the License, or (at your option) any later version.
::
:: The stlib is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
:: See the GNU General Public License for more details.
::
:: You should have received a copy of the GNU General Public License
:: along with this program. If not, see http://www.gnu.org/licenses/.
::

for /f %%i in (
    'python -c "import sys;print(sys.implementation.cache_tag)" 2^>nul'
) do (
    set PYTHON_VERSION=%%i
)

for /d %%i in (%cd%) do (
    set RELEASE_NAME=%%~ni-WIN64-Python-%PYTHON_VERSION%
)

:: download steamworks
pushd src\\steamworks || exit 1

setlocal enabledelayedexpansion
if not exist steamworks-sdk.zip (
    set system32=%comspec%
    set system32=!system32:cmd.exe=!
    set curl="!system32!curl.exe"
    set certutil="!system32!certutil.exe"
    set steamworks="https://github.com/ShyPixie/Overlays/blob/master/dev-util/steamworks-sdk/files/steamworks_sdk_155.zip?raw=true"
    !curl! -o steamworks-sdk.zip -L !steamworks! || !certutil! -urlcache -split -f !steamworks! steamworks-sdk.zip || exit 1
)

if not exist sdk (
    7z x steamworks-sdk.zip || exit 1
)

endlocal
popd || exit 1

:: build project
python -m build --sdist --wheel || exit 1
pushd build || exit 1
move /y "lib.win-amd64-%PYTHON_VERSION%" "%RELEASE_NAME%" || exit 1

:: zip release
tar -vvcf "%RELEASE_NAME%.zip" "%RELEASE_NAME%" || exit 1
popd || exit 1

echo Done.
exit 0
