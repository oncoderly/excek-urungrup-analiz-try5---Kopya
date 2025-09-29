@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%"

set BUILD_ENV=.build_env
set DIST_DIR=dist
set BUILD_DIR=build
set RELEASE_DIR=release
set APP_FOLDER=%RELEASE_DIR%\ExcelAnalizApp
set ZIP_NAME=%RELEASE_DIR%\ExcelAnalizApp.zip

if not exist "%SCRIPT_DIR%requirements.txt" (
    echo HATA: requirements.txt bulunamadi.
    popd
    exit /b 1
)

if exist "%BUILD_ENV%" (
    rmdir /s /q "%BUILD_ENV%"
)

python -m venv "%BUILD_ENV%"
if %errorlevel% neq 0 (
    echo HATA: Sanal ortam olusturulamadi. Lutfen Python 3.8+ yuklu olsun.
    popd
    exit /b 1
)

call "%BUILD_ENV%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo HATA: Sanal ortam etkinlestirilemedi.
    popd
    exit /b 1
)

python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt >nul
python -m pip install pyinstaller >nul

if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"

pyinstaller --noconfirm --clean --onefile --windowed ^
    --name "ExcelAnaliz" ^
    --add-data "excel_analyzer.py;." ^
    create_launcher.py

if %errorlevel% neq 0 (
    echo HATA: PyInstaller paketleme basarisiz oldu.
    popd
    exit /b 1
)

if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
mkdir "%APP_FOLDER%"

copy "%DIST_DIR%\ExcelAnaliz.exe" "%APP_FOLDER%\ExcelAnaliz.exe" >nul
copy README.md "%APP_FOLDER%\README.md" >nul
copy requirements.txt "%APP_FOLDER%\requirements.txt" >nul

powershell -NoLogo -Command "Compress-Archive -Path '%APP_FOLDER%\*' -DestinationPath '%ZIP_NAME%' -Force" >nul

deactivate >nul 2>&1
rmdir /s /q "%BUILD_ENV%"

if exist "%ZIP_NAME%" (
    echo.
    echo Paket hazir! Dagitim paketi: %ZIP_NAME%
    echo Icindeki ExcelAnaliz.exe dosyasini calistirarak uygulamayi acabilirsiniz.
) else (
    echo HATA: Zip dosyasi olusturulamadi.
)

echo.
pause

popd
