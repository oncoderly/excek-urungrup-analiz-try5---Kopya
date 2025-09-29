from pathlib import Path
import re
path = Path("excel_analyzer.py")
text = path.read_text(encoding="utf-8")
pattern = r"\s*# Genel 80/20 Analizi -.*?st\.info\(\"Genel maliyet verisi bulunamadı\.\"\)\r?\n"
new_text, count = re.subn(pattern, "\n", text, flags=re.S)
if count == 0:
    raise SystemExit("pattern not found")
path.write_text(new_text, encoding="utf-8")
