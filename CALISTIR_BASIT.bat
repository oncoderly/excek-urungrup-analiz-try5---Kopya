@echo off
title Excel Analiz Uygulamasi (Basit)

echo =====================================================
echo Excel Analiz Uygulamasi - Basit Surum
echo =====================================================
echo.

if exist venv\Scripts\activate.bat (
    echo Sanal ortam bulundu, etkinlestiriliyor...
    call venv\Scripts\activate.bat
    streamlit run excel_analyzer_basit.py
) else (
    echo Sanal ortam bulunamadi, global Python kullaniliyor...
    py -m streamlit run excel_analyzer_basit.py
)

pause