@echo off
echo =====================================================
echo Excel Analiz Uygulamasi - Portable Kurulum
echo =====================================================
echo.

REM Sanal ortam olusturma
echo Python sanal ortami olusturuluyor...
python -m venv venv
if errorlevel 1 (
    echo HATA: Python bulunamadi! Python'un yuklu oldugunu ve PATH'e eklendigini kontrol edin.
    pause
    exit /b 1
)

REM Sanal ortami etkinlestirme
echo Sanal ortam etkinlestiriliyor...
call venv\Scripts\activate.bat

REM Gereksinimleri yukleme
echo Gerekli kutuphaneler yukleniyor...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo HATA: Kutuphaneler yuklenemedi!
    pause
    exit /b 1
)

echo.
echo =====================================================
echo Kurulum tamamlandi!
echo =====================================================
echo.
echo Uygulamayi calistirmak icin "run_app.bat" dosyasini cift tiklayin.
echo.
pause