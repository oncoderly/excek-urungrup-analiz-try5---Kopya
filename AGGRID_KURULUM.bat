@echo off
echo =====================================================
echo st-aggrid ile Tam Kurulum
echo =====================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo HATA: Once BASIT_KURULUM.bat calistirin!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo st-aggrid farkli yontemlerle deneniyor...
echo.

echo 1. GitHub'dan direkt yukleme deneniyor...
pip install git+https://github.com/PablocFonseca/streamlit-aggrid.git
if not errorlevel 1 (
    echo ✓ st-aggrid GitHub'dan yuklendi!
    goto :test
)

echo.
echo 2. Alternatif PyPI kaynagi deneniyor...
pip install --index-url https://pypi.org/simple/ streamlit-aggrid
if not errorlevel 1 (
    echo ✓ st-aggrid alternatif kaynaktan yuklendi!
    goto :test
)

echo.
echo 3. Eski surum deneniyor...
pip install streamlit-aggrid==0.3.3
if not errorlevel 1 (
    echo ✓ st-aggrid eski surum yuklendi!
    goto :test
)

echo.
echo 4. En son surum deneniyor...
pip install streamlit-aggrid==0.3.4
if not errorlevel 1 (
    echo ✓ st-aggrid son surum yuklendi!
    goto :test
)

echo.
echo ✗ st-aggrid hicbir yontemle yuklenemedi.
echo Internet baglantinizi kontrol edin.
pause
exit /b 1

:test
echo.
echo st-aggrid test ediliyor...
python -c "from st_aggrid import AgGrid; print('st-aggrid BASARILI!')"
if errorlevel 1 (
    echo ✗ st-aggrid import edilemedi!
    pause
    exit /b 1
)

echo.
echo =====================================================
echo ✓ BASARILI! st-aggrid yuklendi
echo =====================================================
echo.
echo Orijinal uygulamayi baslatmak icin:
echo run_app.bat
echo.
echo EXE olusturmak icin:
echo build_exe.bat
echo.
pause