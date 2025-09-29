@echo off
echo =====================================================
echo Streamlit Uygulamalarini Kapat
echo =====================================================
echo.

echo Calisir durumdaki Streamlit uygulamalari kapatiliyor...

REM Python ve Streamlit processlerini kapat
taskkill /F /IM python.exe 2>nul
taskkill /F /IM streamlit.exe 2>nul

REM Port 8501'i kullanan processleri kapat
echo Port 8501 temizleniyor...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501') do (
    taskkill /F /PID %%a 2>nul
)

REM Port 8502'yi kullanan processleri kapat
echo Port 8502 temizleniyor...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8502') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo ✓ Tum Streamlit uygulamalari kapatildi.
echo.
echo Simdi uygulamayi yeniden baslatabilirsiniz:
echo run_app.bat
echo.
pause