@echo off
echo =====================================================
echo Excel Analiz Uygulamasi - Portable Kurulum
echo =====================================================
echo.

REM Python'u kontrol et - farkli yollardan dene
echo Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python bulunamadi, alternatif yollar deneniyor...
    py --version >nul 2>&1
    if errorlevel 1 (
        echo HATA: Python bulunamadi!
        echo.
        echo Cozum 1: Python'u microsoft store'dan yukleyin
        echo Cozum 2: python.org'dan Python 3.8+ yukleyin
        echo Cozum 3: "py" komutu ile deneyin
        echo.
        pause
        exit /b 1
    ) else (
        echo Python "py" komutu ile bulundu
        set PYTHON_CMD=py
    )
) else (
    echo Python "python" komutu ile bulundu
    set PYTHON_CMD=python
)

REM Sanal ortam olusturma
echo Python sanal ortami olusturuluyor...
%PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo HATA: Sanal ortam olusturulamadi!
    pause
    exit /b 1
)

REM Sanal ortami etkinlestirme
echo Sanal ortam etkinlestiriliyor...
call venv\Scripts\activate.bat

REM Gereksinimleri yukleme
echo Gerekli kutuphaneler yukleniyor...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo HATA: Kutuphaneler yuklenemedi!
    pause
    exit /b 1
)

echo.
echo =====================================================
echo Kurulum tamamlandi!
echo =====================================================
echo.
echo Uygulamayi calistirmak icin "run_app.bat" dosyasini cift tiklayin.
echo.
pause