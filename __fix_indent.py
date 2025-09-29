from pathlib import Path
lines = Path("excel_analyzer.py").read_text(encoding="utf-8").splitlines()
idx_col4 = next(i for i,line in enumerate(lines) if line.strip()=='with col4:')
lines[idx_col4] = '                                with col4:'
lines[idx_col4+1] = ''
lines[idx_col4+2] = "                                    total_genel = results_df['Genel Toplam'].sum()"
lines[idx_col4+3] = "                                    st.metric(\"Genel Toplam\", f\"{total_genel:,.2f} TL\".replace(\",\", \"X\").replace(\".\", \",\").replace(\"X\", \".\"))"
Path("excel_analyzer.py").write_text("\n".join(lines) + "\n", encoding='utf-8')
