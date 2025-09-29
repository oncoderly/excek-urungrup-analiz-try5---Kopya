from pathlib import Path
lines = Path("excel_analyzer.py").read_text(encoding="utf-8").splitlines()
start = next(i for i,line in enumerate(lines) if '# Genel 80/20 Analizi - Tüm Ürünler' in line)
end = next(i for i in range(start, len(lines)) if 'group_ranking' in lines[i] and '=' in lines[i])
print(start, end)
