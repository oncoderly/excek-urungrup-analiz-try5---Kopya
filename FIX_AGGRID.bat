@echo off
echo =====================================================
echo st-aggrid Frontend Sorunu Cozucu
echo =====================================================
echo.

call venv\Scripts\activate.bat

echo 1. Mevcut st-aggrid kaldiriliyor...
pip uninstall -y st-aggrid streamlit-aggrid

echo.
echo 2. Cache temizleniyor...
pip cache purge

echo.
echo 3. Uyumlu surum yukleniyor...
pip install streamlit-aggrid==0.3.3

echo.
echo 4. Alternatif surum deneniyor...
if errorlevel 1 (
    pip install streamlit-aggrid==0.2.3
)

echo.
echo 5. Son care olarak GitHub'dan yukleme...
if errorlevel 1 (
    pip install git+https://github.com/PablocFonseca/streamlit-aggrid.git@main
)

echo.
echo 6. Test ediliyor...
python -c "from st_aggrid import AgGrid; print('st-aggrid BASARILI!')"
if errorlevel 1 (
    echo ✗ st-aggrid hala calisimiyor!
    goto :alternative
)

echo ✓ st-aggrid duzeltildi!
goto :end

:alternative
echo.
echo =====================================================
echo Alternatif Cozum: Basit surum kullan
echo =====================================================
echo.
echo st-aggrid sorunlu, basit surumu kullanin:
echo CALISTIR_BASIT.bat
echo.

:end
pause