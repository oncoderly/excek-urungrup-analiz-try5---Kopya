@echo off
echo =====================================================
echo DEBUG - Streamlit Test
echo =====================================================
echo.

echo Python versiyonu:
python --version

echo.
echo Sanal ortam etkinlestiriliyor...
call venv\Scripts\activate.bat

echo.
echo Python versiyonu (sanal ortamda):
python --version

echo.
echo Streamlit versiyonu:
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"

echo.
echo st-aggrid testi:
python -c "from st_aggrid import AgGrid; print('st-aggrid: OK')"

echo.
echo Excel analyzer dosyasi kontrol:
if exist "excel_analyzer.py" (
    echo ✓ excel_analyzer.py mevcut
) else (
    echo ✗ excel_analyzer.py bulunamadi!
)

echo.
echo =====================================================
echo Streamlit baslatiliyor (manuel mod)...
echo =====================================================
echo.
echo Tarayicida manuel olarak su adresi acin:
echo http://localhost:8501
echo.

python -m streamlit run excel_analyzer.py --server.port 8501

echo.
echo Uygulama kapatildi.
pause