@echo off
title Excel Analiz Uygulamasi - Hizli Baslatici
color 0A

echo.
echo  ╔═══════════════════════════════════════╗
echo  ║       Excel Analiz Uygulamasi        ║
echo  ║         Hizli Baslatici v1.0         ║
echo  ╚═══════════════════════════════════════╝
echo.

echo Python ve gerekli paketler kontrol ediliyor...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ HATA: Python bulunamadi!
    echo 📥 Lutfen Python'i yukleyin: https://python.org
    pause
    exit /b 1
)

echo ✅ Python bulundu.

echo 📦 Gerekli paketler yukleniyor...
pip install -q streamlit pandas numpy plotly st-aggrid openpyxl xlrd

echo 🚀 Uygulama baslatiliyor...
echo 🌐 Tarayicinizda otomatik acilacak...
echo ❌ Uygulamayi kapatmak icin Ctrl+C basin

streamlit run excel_analyzer.py --server.headless true

pause