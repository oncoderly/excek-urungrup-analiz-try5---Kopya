@echo off
echo =====================================================
echo TEMIZ KURULUM - Sifirdan Basla
echo =====================================================
echo.

echo Eski sanal ortam temizleniyor...
if exist venv (
    rmdir /s /q venv
    echo ✓ Eski sanal ortam silindi
)

echo.
echo Python kontrol ediliyor...
py --version
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    pause
    exit /b 1
)

echo.
echo Yeni sanal ortam olusturuluyor...
py -m venv venv

echo.
echo Sanal ortam etkinlestiriliyor...
call venv\Scripts\activate.bat

echo.
echo Kutuphaneler yukleniyor (pip guncellenmeden)...
python -m pip install streamlit==1.28.1 pandas==2.0.3 numpy==1.24.3 plotly==5.17.0 st-aggrid==0.3.4 openpyxl==3.1.2 xlrd==2.0.1

if errorlevel 1 (
    echo HATA: Kutuphaneler yuklenemedi!
    pause
    exit /b 1
)

echo.
echo =====================================================
echo Kurulum tamamlandi! Uygulama baslatiliyor...
echo =====================================================
echo.

streamlit run excel_analyzer.py

pause