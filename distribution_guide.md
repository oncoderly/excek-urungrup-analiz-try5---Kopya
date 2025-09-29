# Dagitim Paketi Rehberi

Bu uygulamayi cift tiklayarak calistirilabilir hale getirmek icin asagidaki adimlari izleyin.

## 1. Paket Olusturma

1. Windows Dosya Gezgini'nde projenin ana klasorune gidin.
2. build_windows_release.bat dosyasina cift tiklayin.
3. Betik otomatik olarak gecici bir sanal ortam olusturur, gerekli kutuphaneleri kurar ve PyInstaller ile ExcelAnaliz.exe dosyasini uretir.
4. Islemin sonunda release/ExcelAnalizApp.zip arsivi olusur.

## 2. Dagitim

- Olusan zip dosyasini paylasin veya arsivden ExcelAnaliz.exe dosyasini cikararak hedef kullaniciya gonderin.
- Karsi taraf zip'i actiktan sonra ExcelAnaliz.exe dosyasina cift tiklayarak Streamlit arayuzunu otomatik olarak acabilir.

## 3. Notlar

- Betik ilk calistirildiginda paketler indirilecegi icin internet baglantisi gerekebilir ve sure biraz uzayabilir.
- Ayni dizinde README.md ve requirements.txt dosyalarini bulundurmaya devam edin; bu dosyalar referans icindir.
- Yeni bir surum yayinladiginizda betigi tekrar calistirarak guncel exe ve zip arsivini olusturun.
