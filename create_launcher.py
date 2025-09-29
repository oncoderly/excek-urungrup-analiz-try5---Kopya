import os
import sys
import subprocess
import webbrowser
import threading
import time
import socket
from pathlib import Path

def find_free_port():
    """Boş port bulma"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def run_streamlit_app():
    """Streamlit uygulamasını çalıştır"""
    # Mevcut dizini al
    current_dir = Path(__file__).parent
    app_file = current_dir / "excel_analyzer.py"

    # Eğer exe içindeyse geçici dizinde ara
    if not app_file.exists():
        if hasattr(sys, '_MEIPASS'):
            temp_dir = Path(sys._MEIPASS)
            app_file = temp_dir / "excel_analyzer.py"

    # Port bul
    port = find_free_port()

    # Streamlit komutunu hazırla
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_file),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false"
    ]

    # Streamlit'i çalıştır
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    # Biraz bekle ve tarayıcıyı aç
    time.sleep(5)
    webbrowser.open(f"http://localhost:{port}")

    return process

def main():
    """Ana fonksiyon"""
    print("Excel Analiz Uygulaması başlatılıyor...")
    print("Lütfen bekleyiniz...")

    try:
        # Streamlit uygulamasını başlat
        process = run_streamlit_app()

        print(f"Uygulama çalışıyor! Tarayıcınızda otomatik açılacak.")
        print("Uygulamayı kapatmak için bu pencereyi kapatın.")

        # Process'in bitmesini bekle
        process.wait()

    except Exception as e:
        print(f"Hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    main()