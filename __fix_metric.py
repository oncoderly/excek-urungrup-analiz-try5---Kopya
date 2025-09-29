from pathlib import Path
text = Path("excel_analyzer.py").read_text(encoding="utf-8")
old = "                                    with col4:\n\n                                        total_genel = results_df['Genel Toplam'].sum()\n\n                                # Genel 80/20 Analizi - Tüm Ürünler"
new = "                                    with col4:\n\n                                        total_genel = results_df['Genel Toplam'].sum()\n                                        st.metric(\"Genel Toplam\", f\"{total_genel:,.2f} TL\".replace(\",\", \"X\").replace(\".\", \",\").replace(\"X\", \".\"))\n\n                                # Genel 80/20 Analizi - Tüm Ürünler"
if old not in text:
    raise SystemExit('pattern not found for metric insertion')
text = text.replace(old, new, 1)
Path("excel_analyzer.py").write_text(text, encoding="utf-8")
