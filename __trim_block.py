from pathlib import Path
lines = Path("excel_analyzer.py").read_text(encoding="utf-8").splitlines()
start = next(i for i,line in enumerate(lines) if '# Genel 80/20 Analizi' in line)
end = next(i for i in range(start, len(lines)) if 'group_ranking = group_detail' in lines[i])
new_lines = lines[:start] + lines[end:]
Path("excel_analyzer.py").write_text("\n".join(new_lines) + "\n", encoding="utf-8")
