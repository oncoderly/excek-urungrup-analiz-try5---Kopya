@echo off
title Excel Analiz Uygulamasi

echo =====================================================
echo Excel Analiz Uygulamasi - Hizli Baslatma
echo =====================================================
echo.

REM Mevcut sanal ortami kullan veya gerekli kutuphaneleri direkt yukle
if exist venv\Scripts\activate.bat (
    echo Mevcut sanal ortam kullaniliyor...
    call venv\Scripts\activate.bat
    goto :start_app
)

echo Sanal ortam bulunamadi, alternatif yontem deneniyor...
echo.

REM Python komutunu bul
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo HATA: Python bulunamadi!
        echo Microsoft Store'dan Python yukleyin.
        pause
        exit /b 1
    ) else (
        set PY_CMD=python
    )
) else (
    set PY_CMD=py
)

REM Kutuphaneleri kullanici alanina yukle (--user bayragi ile)
echo Kutuphaneler kullanici alanina yukleniyor...
%PY_CMD% -m pip install --user --quiet streamlit==1.28.1 pandas==2.0.3 numpy==1.24.3 plotly==5.17.0 st-aggrid==0.3.4 openpyxl==3.1.2 xlrd==2.0.1

:start_app
echo.
echo =====================================================
echo Uygulama baslatiliyor...
echo Tarayicinizda otomatik acilacak.
echo =====================================================
echo.

REM Streamlit'i baslat
if exist venv\Scripts\activate.bat (
    streamlit run excel_analyzer.py --server.headless true
) else (
    %PY_CMD% -m streamlit run excel_analyzer.py --server.headless true
)

echo.
echo Uygulama kapatildi.
pause