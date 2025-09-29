from pathlib import Path
text = Path("excel_analyzer.py").read_text(encoding="utf-8")
print('connector=dict(' in text)
