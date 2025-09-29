@echo off
echo =====================================================
echo BASIT KURULUM - Excel Analiz Uygulamasi
echo =====================================================
echo.

echo Eski dosyalar temizleniyor...
if exist venv rmdir /s /q venv
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Python kontrolu...
py --version
if errorlevel 1 (
    echo HATA: Python bulunamadi! Microsoft Store'dan Python yukleyin.
    pause
    exit /b 1
)

echo.
echo 1. Setuptools yukleniyor...
py -m pip install --user setuptools wheel

echo.
echo 2. Sanal ortam olusturuluyor...
py -m venv venv

echo.
echo 3. Sanal ortam etkinlestiriliyor...
call venv\Scripts\activate.bat

echo.
echo 4. Temel kutuphaneler yukleniyor (basit surum)...
python -m pip install setuptools wheel
python -m pip install streamlit pandas numpy plotly openpyxl xlrd

echo.
echo 5. st-aggrid deneniyor...
python -m pip install st-aggrid || echo "st-aggrid yuklenemedi, devam ediliyor..."

if errorlevel 1 (
    echo Bazi kutuphaneler yuklenemedi ama temel islevsellik calisacak.
)

echo.
echo =====================================================
echo Kurulum tamamlandi! Uygulama test ediliyor...
echo =====================================================
echo.

echo Test ediliyor...
python -c "import streamlit; print('Streamlit OK')"
python -c "import pandas; print('Pandas OK')"
python -c "import plotly; print('Plotly OK')"

echo.
echo Uygulama baslatiliyor...
streamlit run excel_analyzer.py --server.headless true --server.fileWatcherType none

pause