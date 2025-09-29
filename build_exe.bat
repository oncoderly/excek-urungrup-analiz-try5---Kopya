@echo off
echo =====================================================
echo Excel Analiz Uygulamasi - EXE Olusturma
echo =====================================================
echo.

REM Python komutunu bul
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo HATA: Python bulunamadi!
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

REM Sanal ortam kontrol
if not exist "venv\Scripts\activate.bat" (
    echo Sanal ortam bulunamadi, olusturuluyor...
    %PYTHON_CMD% -m venv venv
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo Sanal ortam bulundu, etkinlestiriliyor...
    call venv\Scripts\activate.bat
)

echo.
echo PyInstaller ile EXE dosyasi olusturuluyor...
echo Bu islem birkaç dakika surebilir...
echo.

REM Onceki build'leri temizle
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM PyInstaller ile exe olustur
pyinstaller --onefile ^
    --name "ExcelAnalyzer" ^
    --add-data "venv\Lib\site-packages\streamlit\static;streamlit\static" ^
    --add-data "venv\Lib\site-packages\streamlit\runtime;streamlit\runtime" ^
    --hidden-import streamlit.runtime.scriptrunner.magic_funcs ^
    --hidden-import streamlit.runtime.caching ^
    --hidden-import streamlit.web.server.server ^
    --hidden-import plotly.graph_objs ^
    --hidden-import st_aggrid.shared ^
    --hidden-import pandas._libs.tslibs.timedeltas ^
    --hidden-import openpyxl.cell._writer ^
    --console ^
    launcher.py

if errorlevel 1 (
    echo.
    echo HATA: EXE dosyasi olusturulamadi!
    echo Detaylar icin yukardaki hata mesajlarini kontrol edin.
    pause
    exit /b 1
)

echo.
echo =====================================================
echo EXE dosyasi basariyla olusturuldu!
echo =====================================================
echo.
echo Dosya konumu: dist\ExcelAnalyzer.exe
echo.

REM Excel analyzer dosyasini dist klasorune kopyala
if exist "excel_analyzer.py" (
    copy "excel_analyzer.py" "dist\"
    echo excel_analyzer.py kopyalandi.
)

echo.
echo EXE dosyasini test etmek icin "dist\ExcelAnalyzer.exe" dosyasini cift tiklayin.
echo.
pause