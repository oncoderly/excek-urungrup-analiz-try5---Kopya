@echo off
echo =====================================================
echo Excel Analiz Uygulamasi - Basit EXE Olusturma
echo =====================================================
echo.

REM Sanal ortam kontrol
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Once BASIT_KURULUM.bat dosyasini calistirin!
    pause
    exit /b 1
)

echo Sanal ortam etkinlestiriliyor...
call venv\Scripts\activate.bat

echo.
echo PyInstaller yukleniyor...
pip install pyinstaller

echo.
echo Eski build dosyalari temizleniyor...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo.
echo =====================================================
echo EXE dosyasi olusturuluyor...
echo Bu islem 3-5 dakika surebilir, lutfen bekleyin...
echo =====================================================
echo.

REM Basit launcher olustur
echo import os > simple_launcher.py
echo import sys >> simple_launcher.py
echo import subprocess >> simple_launcher.py
echo import webbrowser >> simple_launcher.py
echo import time >> simple_launcher.py
echo import threading >> simple_launcher.py
echo. >> simple_launcher.py
echo def open_browser(): >> simple_launcher.py
echo     time.sleep(3) >> simple_launcher.py
echo     try: >> simple_launcher.py
echo         webbrowser.open('http://localhost:8501') >> simple_launcher.py
echo     except: >> simple_launcher.py
echo         pass >> simple_launcher.py
echo. >> simple_launcher.py
echo def main(): >> simple_launcher.py
echo     print("Excel Analiz Uygulamasi baslatiliyor...") >> simple_launcher.py
echo     print("Tarayicida otomatik acilacak.") >> simple_launcher.py
echo     browser_thread = threading.Thread(target=open_browser) >> simple_launcher.py
echo     browser_thread.daemon = True >> simple_launcher.py
echo     browser_thread.start() >> simple_launcher.py
echo     import streamlit.web.cli as stcli >> simple_launcher.py
echo     sys.argv = ["streamlit", "run", "excel_analyzer_basit.py", "--server.headless", "true"] >> simple_launcher.py
echo     stcli.main() >> simple_launcher.py
echo. >> simple_launcher.py
echo if __name__ == "__main__": >> simple_launcher.py
echo     main() >> simple_launcher.py

REM PyInstaller ile tek dosya EXE olustur
pyinstaller --onefile ^
    --name "ExcelAnalyzer" ^
    --add-data "excel_analyzer_basit.py;." ^
    --hidden-import streamlit.web.cli ^
    --hidden-import streamlit.runtime.scriptrunner.magic_funcs ^
    --hidden-import streamlit.runtime.caching ^
    --hidden-import plotly.graph_objs ^
    --hidden-import plotly.express ^
    --console ^
    simple_launcher.py

if errorlevel 1 (
    echo.
    echo HATA: EXE dosyasi olusturulamadi!
    pause
    exit /b 1
)

echo.
echo excel_analyzer_basit.py dosyasini dist klasorune kopyalaniyor...
copy "excel_analyzer_basit.py" "dist\"

echo.
echo =====================================================
echo ✓ BASARILI! EXE dosyasi olusturuldu!
echo =====================================================
echo.
echo Dosya konumu: dist\ExcelAnalyzer.exe
echo Boyut:
dir dist\ExcelAnalyzer.exe
echo.
echo Bu dosyayi herhangi bir Windows bilgisayara kopyalayabilirsiniz.
echo Cift tiklayarak calistiracak ve tarayicida acilacak.
echo.
echo Test etmek icin: dist\ExcelAnalyzer.exe
echo.
pause