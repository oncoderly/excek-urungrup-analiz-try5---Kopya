# 🚀 Excel Analiz Uygulaması - Paket Program Yapma Kılavuzu

## 📋 Gereksinimler
- Windows işletim sistemi
- Python 3.8 veya üzeri yüklü olmalı
- İnternet bağlantısı (ilk kurulum için)

## 🎯 Yöntem 1: Otomatik EXE Oluşturma (Önerilen)

### Adım 1: Hazırlık
1. Tüm dosyaların aynı klasörde olduğundan emin olun:
   - `excel_analyzer.py`
   - `create_launcher.py`
   - `create_exe.bat`
   - `requirements.txt`

### Adım 2: EXE Dosyası Oluşturma
1. `create_exe.bat` dosyasına çift tıklayın
2. Script otomatik olarak:
   - Gerekli paketleri yükler
   - EXE dosyasını oluşturur
   - `dist` klasöründe hazırlar

### Adım 3: Dağıtım
- `dist/Excel_Analiz_Uygulamasi.exe` dosyanız hazır!
- Bu dosyayı istediğiniz yere kopyalayabilirsiniz
- Çift tıklayarak çalıştırın

---

## 🎯 Yöntem 2: Manuel PyInstaller Kurulumu

### Komut Satırı Adımları:
```bash
# Gerekli paketleri yükle
pip install pyinstaller streamlit pandas numpy plotly st-aggrid

# EXE dosyası oluştur
pyinstaller --onefile --windowed --name "Excel_Analiz_Uygulamasi" create_launcher.py

# EXE dosyasını test et
dist\Excel_Analiz_Uygulamasi.exe
```

---

## 🎯 Yöntem 3: Streamlit Sharing (Online Dağıtım)

### GitHub'da Paylaşım:
1. Kodları GitHub repository'sine yükleyin
2. https://share.streamlit.io adresine gidin
3. Repository'nizi bağlayın
4. Otomatik olarak online erişilebilir link alın

---

## 🔧 Sorun Giderme

### Problem: "Python bulunamadı" hatası
**Çözüm:** Python'i https://python.org adresinden indirip kurun

### Problem: "ModuleNotFoundError" hatası
**Çözüm:**
```bash
pip install -r requirements.txt
```

### Problem: EXE dosyası çok yavaş açılıyor
**Çözüm:** Normal davranış, ilk açılış 10-15 saniye sürebilir

---

## 📦 Dağıtım Önerileri

### Küçük Paket için:
- Sadece EXE dosyasını dağıtın
- 50-100 MB boyutunda olacaktır

### Kurulum Paketi için:
- NSIS veya Inno Setup kullanın
- Masaüstü kısayolu ekleyin
- Başlangıç menüsüne ekleyin

---

## 🎨 İkon Ekleme

EXE dosyasına özel ikon eklemek için:
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name "Excel_Analiz_Uygulamasi" create_launcher.py
```

`.ico` formatında ikon dosyanız olmalı.

---

## ✅ Test Checklist

- [ ] EXE dosyası çalışıyor
- [ ] Excel dosyası yükleme çalışıyor
- [ ] Tablolar düzgün görünüyor
- [ ] Grafikler düzgün oluşuyor
- [ ] Renkli tasarım düzgün
- [ ] Farklı bilgisayarlarda test edildi