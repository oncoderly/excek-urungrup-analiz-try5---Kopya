import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def start_streamlit():
    """Streamlit uygulamasını başlat"""
    # Excel analyzer'ı import et ve çalıştır
    try:
        # Mevcut dizini sys.path'e ekle
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # Streamlit'i subprocess ile başlat
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            'excel_analyzer.py',
            '--server.port=8501',
            '--server.headless=true',
            '--server.fileWatcherType=none',
            '--browser.gatherUsageStats=false'
        ]

        # Eğer executable içerisindeyse, geçici dizini kullan
        if getattr(sys, 'frozen', False):
            # PyInstaller bundle içerisindeyiz
            bundle_dir = sys._MEIPASS
            excel_analyzer_path = os.path.join(bundle_dir, 'excel_analyzer.py')
            if os.path.exists(excel_analyzer_path):
                cmd[-1] = excel_analyzer_path

        return subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    except Exception as e:
        print(f"Streamlit başlatılırken hata: {e}")
        return None

def open_browser():
    """3 saniye bekleyip tarayıcıyı aç"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:8501')
    except Exception as e:
        print(f"Tarayıcı açılırken hata: {e}")

def main():
    print("==============================================")
    print("Excel Analiz Uygulaması Başlatılıyor...")
    print("==============================================")
    print()
    print("Uygulama başlatılıyor, lütfen bekleyiniz...")
    print("Tarayıcınızda otomatik olarak açılacak.")
    print()
    print("Uygulamayı kapatmak için bu pencereyi kapatın.")
    print("==============================================")

    # Streamlit'i başlat
    process = start_streamlit()

    if process is None:
        print("HATA: Uygulama başlatılamadı!")
        input("Devam etmek için Enter'a basın...")
        return

    # Tarayıcıyı aç (ayrı thread'de)
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    try:
        # Process'i bekle
        process.wait()
    except KeyboardInterrupt:
        print("\nUygulama kapatılıyor...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"Beklenmedik hata: {e}")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()