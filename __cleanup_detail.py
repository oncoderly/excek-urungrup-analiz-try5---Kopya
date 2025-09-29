from pathlib import Path
lines = Path("excel_analyzer.py").read_text(encoding="utf-8").splitlines()
start = next(i for i,line in enumerate(lines) if "# Ürün grubu detay analizi" in line)
# remove immediate redundant lines after start that contain st.divider() and st.write header
remove_indices = []
for offset in range(1,4):
    idx = start + offset
    if idx < len(lines) and ('st.divider()' in lines[idx] or 'Ürün Grubu Detay Analizi' in lines[idx]):
        remove_indices.append(idx)
new_lines = [line for i,line in enumerate(lines) if i not in remove_indices]
Path("excel_analyzer.py").write_text("\n".join(new_lines) + "\n", encoding='utf-8')
