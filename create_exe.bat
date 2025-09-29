@echo off
echo Excel Analiz Uygulamasi EXE Olusturucu
echo =====================================

echo Python ve pip kurulu olup olmadigini kontrol ediliyor...
python --version
if %errorlevel% neq 0 (
    echo HATA: Python bulunamadi! Lutfen Python'i yukleyin.
    pause
    exit /b 1
)

echo PyInstaller yukleniyor...
pip install pyinstaller streamlit pandas numpy plotly st-aggrid

echo EXE dosyasi olusturuluyor...
pyinstaller --onefile --windowed --name "Excel_Analiz_Uygulamasi" --add-data "excel_analyzer.py;." --hidden-import streamlit --hidden-import pandas --hidden-import numpy --hidden-import plotly --hidden-import st_aggrid create_launcher.py

echo EXE dosyasi dist klasorunde olusturuldu!
echo Dosya yolu: dist\Excel_Analiz_Uygulamasi.exe

pause