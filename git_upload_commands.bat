@echo off
echo ================================================
echo    GITHUB YUKLEME KOMUTLARI - OTOMATIK SCRIPT
echo ================================================

cd /d "C:\Users\sosmanli\Documents\GitHub\excek-urungrup-analiz-try5 - Kopya"

echo.
echo 1. Git repository baslatiliyor...
git init

echo.
echo 2. Gerekli dosyalar ekleniyor...
git add excel_analyzer.py
git add streamlit_requirements.txt
git add README.md

echo.
echo 3. .gitignore dosyasi olusturuluyor...
echo __pycache__/ > .gitignore
echo *.pyc >> .gitignore
echo .env >> .gitignore
echo dist/ >> .gitignore
echo build/ >> .gitignore

git add .gitignore

echo.
echo 4. Ilk commit yapiliyor...
git commit -m "İlk versiyon: Excel analiz uygulaması eklendi"

echo.
echo 5. Ana branch main olarak ayarlaniyor...
git branch -M main

echo.
echo ================================================
echo   SIMDI GITHUB'DA REPOSITORY OLUSTURUN:
echo   1. github.com 'a gidin
echo   2. New repository butonuna tiklayin
echo   3. Repository adi: excel-analiz-uygulamasi
echo   4. Public secili olsun
echo   5. README eklemeyin (zaten var)
echo   6. Create repository tiklayin
echo.
echo   SONRA ASAGIDAKI KOMUTU CALISTIRIN:
echo   (REPOSITORY_URL'i kendi linkinizle degistirin)
echo.
echo   git remote add origin https://github.com/KULLANICI_ADI/excel-analiz-uygulamasi.git
echo   git push -u origin main
echo ================================================

pause