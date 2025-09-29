@echo off
echo =====================================================
echo Alternatif AgGrid Kurulumu
echo =====================================================
echo.

call venv\Scripts\activate.bat

echo Eski st-aggrid kaldiriliyor...
pip uninstall -y st-aggrid streamlit-aggrid

echo.
echo Streamlit surum kontrol:
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"

echo.
echo Streamlit 1.50+ icin uyumlu aggrid yukleniyor...

REM Streamlit 1.28 ile uyumlu olan surumleri dene
pip install streamlit-aggrid==0.3.4 --force-reinstall --no-deps
pip install streamlit==1.28.1 --force-reinstall

echo.
echo Ya da tamamen farkli bir yaklasin - streamlit-dataframe-editor:
pip install streamlit-dataframe-editor

echo.
echo Test ediliyor...
python -c "
try:
    from st_aggrid import AgGrid
    print('st-aggrid: BASARILI')
except Exception as e:
    print('st-aggrid HATASI:', e)
    try:
        import streamlit_dataframe_editor
        print('streamlit-dataframe-editor: BASARILI')
    except:
        print('Her iki kutuphane de sorunlu')
"

pause