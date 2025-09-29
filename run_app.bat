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

REM Streamlit uygulamasini baslat
streamlit run excel_analyzer.py --server.headless true --server.runOnSave true

echo.
echo Uygulama kapatildi.
pause