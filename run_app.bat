@echo off
title Excel Analiz Uygulamasi

REM Sanal ortamin var olup olmadigini kontrol et
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Sanal ortam bulunamadi!
    echo Lutfen once "setup_portable.bat" dosyasini calistirin.
    echo.
    pause
    exit /b 1
)

echo =====================================================
echo Excel Analiz Uygulamasi Baslatiliyor...
echo =====================================================
echo.
echo Uygulama baslatildiginda tarayicinizda otomatik olarak acilacak.
echo Uygulamayi kapatmak icin bu pencereyi kapatin.
echo.

REM Sanal ortami etkinlestir
call venv\Scripts\activate.bat

echo Streamlit baslatiliyor...
echo Tarayici otomatik acilacak (2-3 saniye bekleyin)
echo.

REM Streamlit uygulamasini baslat
streamlit run excel_analyzer.py --server.headless false --server.runOnSave true --server.port 8501

if errorlevel 1 (
    echo.
    echo HATA: Streamlit baslatilirken sorun olustu!
    echo.
    pause
)

echo.
echo Uygulama kapatildi.
pause