=====================================================
Excel Analiz Uygulamasi - Portable EXE Dagitim
=====================================================

Bu klasorde Excel analiz uygulamanizi tek bir .exe dosyasi haline getirmek icin gerekli dosyalar bulunmaktadir.

DOSYA LISTESI:
=====================================================
- excel_analyzer.py         : Ana uygulama dosyasi
- launcher.py               : EXE icin baslangic dosyasi
- requirements.txt          : Gerekli kutuphaneler
- excel_analyzer.spec       : PyInstaller yapilandirma dosyasi
- build_exe.bat            : EXE olusturma scripti
- setup_portable.bat       : Sanal ortam kurulum scripti
- run_app.bat             : Normal Python calistirma scripti

EXE DOSYASI OLUSTURMA:
=====================================================
1. Once "setup_portable.bat" dosyasini calistirin (sadece bir kez)
2. Sonra "build_exe.bat" dosyasini calistirin
3. "dist" klasoru icinde "ExcelAnalyzer.exe" dosyasi olusacak
4. Bu tek dosyayi herhangi bir Windows bilgisayara gonderebilirsiniz

DAGITIM ICIN:
=====================================================
- Sadece "ExcelAnalyzer.exe" dosyasini gonderin
- Kullanici bu dosyayi cift tiklayarak calistiracak
- Herhangi bir kurulum gerektirmez
- Tarayicida otomatik olarak acilir
- 70-100 MB boyutunda olacak

NOTLAR:
=====================================================
- Ilk calisma biraz yavas olabilir (normal)
- Windows Defender uyarisi cikabilir (guvende)
- Antivirus yazilimi false positive verebilir
- Internet baglantisi sadece excel dosyasi indirmek icin gerekir

SORUN GIDERME:
=====================================================
- "Python bulunamadi" hatasi: Python 3.8+ yukleyin
- "PyInstaller bulunamadi" hatasi: requirements.txt'i kontrol edin
- EXE calismiyor: Windows 64-bit gerekir
- Yavas calisma: Normal, ilk acilista yavas

TEKNIK DETAYLAR:
=====================================================
- PyInstaller ile tek dosya halinde paketlendi
- Tum gerekli kutuphaneler icinde gomulu
- Gecici klasorde acilir ve calisir
- Streamlit web arayuzu kullanir
- Localhost:8501 portunda calisir

Surum: 1.0
Tarih: 2025
Boyut: ~80-100 MB (tek dosya)