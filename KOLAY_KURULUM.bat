@echo off
echo =====================================================
echo KOLAY KURULUM - Excel Analiz Uygulamasi
echo =====================================================
echo.

echo Bu script otomatik olarak uygulamayi hazirlar ve calistirir.
echo.
pause

REM Farkli Python komutlarini dene
set PYTHON_FOUND=0

echo [1/4] Python araniyor...
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    echo ✓ Python bulundu: python
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    set PYTHON_FOUND=1
    echo ✓ Python bulundu: py
    goto :python_found
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    set PYTHON_FOUND=1
    echo ✓ Python bulundu: py -3
    goto :python_found
)

:python_not_found
echo ✗ Python bulunamadi!
echo.
echo PYTHON YUKLEMEK ICIN:
echo 1. Microsoft Store'da "Python" aratip yukleyin, VEYA
echo 2. https://python.org adresinden Python 3.8+ indirin
echo.
echo Yukleme sonrasi bu dosyayi tekrar calistirin.
pause
exit /b 1

:python_found
echo.
echo [2/4] Sanal ortam olusturuluyor...
if exist venv (
    echo ✓ Sanal ortam zaten mevcut
) else (
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo ✗ Sanal ortam olusturulamadi!
        pause
        exit /b 1
    )
    echo ✓ Sanal ortam olusturuldu
)

echo.
echo [3/4] Kutuphaneler yukleniyor...
call venv\Scripts\activate.bat

REM Pip guncellemesini atla, dogrudan kutuphaneleri yukle
echo Gerekli kutuphaneler yukleniyor...
pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo ✗ Kutuphaneler yuklenemedi!
    echo Internet baglantinizi kontrol edin.
    pause
    exit /b 1
)
echo ✓ Kutuphaneler yuklendi

echo.
echo [4/4] Uygulama baslatiliyor...
echo ✓ Hazir! Tarayicinizda acilacak...
echo.
streamlit run excel_analyzer.py
pause