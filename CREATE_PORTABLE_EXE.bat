@echo off
echo =====================================================
echo PORTABLE EXE OLUSTURUCU - Excel Analiz Uygulamasi
echo =====================================================
echo.

REM Sanal ortam kontrol
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Sanal ortam bulunamadi!
    echo Once kurulum scriptlerini calistirin.
    pause
    exit /b 1
)

echo Sanal ortam etkinlestiriliyor...
call venv\Scripts\activate.bat

echo.
echo PyInstaller kontrol ve yukleme...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller yukleniyor...
    pip install pyinstaller
)

echo.
echo Eski build dosyalari temizleniyor...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "__pycache__" rmdir /s /q __pycache__

echo.
echo =====================================================
echo EXE OLUSTURULUYOR - LUTFEN BEKLEYIN (3-5 dakika)
echo =====================================================
echo.

REM Launcher dosyasi olustur
echo import os > portable_launcher.py
echo import sys >> portable_launcher.py
echo import subprocess >> portable_launcher.py
echo import webbrowser >> portable_launcher.py
echo import time >> portable_launcher.py
echo import threading >> portable_launcher.py
echo from pathlib import Path >> portable_launcher.py
echo. >> portable_launcher.py
echo def open_browser(): >> portable_launcher.py
echo     time.sleep(4) >> portable_launcher.py
echo     try: >> portable_launcher.py
echo         webbrowser.open('http://localhost:8501') >> portable_launcher.py
echo     except Exception as e: >> portable_launcher.py
echo         print(f"Tarayici acilirken hata: {e}") >> portable_launcher.py
echo. >> portable_launcher.py
echo def main(): >> portable_launcher.py
echo     print("=====================================================") >> portable_launcher.py
echo     print("Excel Analiz Uygulamasi - Portable Surum") >> portable_launcher.py
echo     print("=====================================================") >> portable_launcher.py
echo     print() >> portable_launcher.py
echo     print("Uygulama baslatiliyor...") >> portable_launcher.py
echo     print("Tarayicida otomatik acilacak (4 saniye bekleyin)") >> portable_launcher.py
echo     print("Uygulamayi kapatmak icin bu pencereyi kapatin.") >> portable_launcher.py
echo     print() >> portable_launcher.py
echo     browser_thread = threading.Thread(target=open_browser) >> portable_launcher.py
echo     browser_thread.daemon = True >> portable_launcher.py
echo     browser_thread.start() >> portable_launcher.py
echo     try: >> portable_launcher.py
echo         import streamlit.web.cli as stcli >> portable_launcher.py
echo         sys.argv = ["streamlit", "run", "excel_analyzer.py", "--server.headless", "true", "--server.port", "8501"] >> portable_launcher.py
echo         stcli.main() >> portable_launcher.py
echo     except KeyboardInterrupt: >> portable_launcher.py
echo         print("Uygulama kapatiliyor...") >> portable_launcher.py
echo     except Exception as e: >> portable_launcher.py
echo         print(f"Hata: {e}") >> portable_launcher.py
echo         input("Enter'a basin...") >> portable_launcher.py
echo. >> portable_launcher.py
echo if __name__ == "__main__": >> portable_launcher.py
echo     main() >> portable_launcher.py

echo Launcher olusturuldu: portable_launcher.py

echo.
echo PyInstaller ile EXE olusturuluyor...

pyinstaller ^
    --onefile ^
    --name "ExcelAnalyzer" ^
    --add-data "excel_analyzer.py;." ^
    --add-data "venv\Lib\site-packages\streamlit;streamlit" ^
    --add-data "venv\Lib\site-packages\st_aggrid;st_aggrid" ^
    --hidden-import streamlit.web.cli ^
    --hidden-import streamlit.runtime.scriptrunner.magic_funcs ^
    --hidden-import streamlit.runtime.caching ^
    --hidden-import streamlit.runtime.secrets ^
    --hidden-import st_aggrid.AgGrid ^
    --hidden-import st_aggrid.shared ^
    --hidden-import plotly.graph_objs ^
    --hidden-import plotly.express ^
    --hidden-import pandas._libs.tslibs.timedeltas ^
    --hidden-import openpyxl.cell._writer ^
    --hidden-import xlrd.biffh ^
    --console ^
    --clean ^
    portable_launcher.py

if errorlevel 1 (
    echo.
    echo ✗ EXE olusturma BASARISIZ!
    echo Yukardaki hata mesajlarini kontrol edin.
    pause
    exit /b 1
)

echo.
echo Excel analyzer dosyasini dist klasorune kopyalaniyor...
copy "excel_analyzer.py" "dist\" >nul

echo.
echo =====================================================
echo ✓ PORTABLE EXE BASARIYLA OLUSTURULDU!
echo =====================================================
echo.

echo Dosya bilgileri:
dir "dist\ExcelAnalyzer.exe"

echo.
echo ✓ Konum: dist\ExcelAnalyzer.exe
echo ✓ Bu dosyayi herhangi bir Windows bilgisayara kopyalayabilirsiniz
echo ✓ Cift tiklayarak calistiracak ve tarayicida acilacak
echo ✓ Herhangi bir kurulum gerektirmez
echo ✓ Internet baglantisi sadece Excel dosyasi yukleme icin gerekir

echo.
echo Test etmek icin: dist\ExcelAnalyzer.exe dosyasini cift tiklayin
echo.

REM Temizlik
del portable_launcher.py 2>nul
del *.spec 2>nul

echo Portable EXE hazir!
pause