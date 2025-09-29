from pathlib import Path
lines = Path("excel_analyzer.py").read_text(encoding="utf-8").splitlines()
for idx, line in enumerate(lines, start=1):
    if "Pareto" in line:
        print(idx, line)
