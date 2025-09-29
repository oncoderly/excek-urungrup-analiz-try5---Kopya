from pathlib import Path

path = Path("excel_analyzer.py")
text = path.read_text(encoding="utf-8")
start_marker = "                # Tablo gösterimi - AgGrid\n"
end_marker = "                # Görselleştirme\n"
start_idx = text.find(start_marker)
if start_idx == -1:
    raise SystemExit('start marker not found')
end_idx = text.find(end_marker, start_idx)
if end_idx == -1:
    raise SystemExit('end marker not found')
new_block = """                # Tablo gösterimi - AgGrid
                create_aggrid_table(results_df_display, height=500)

                # Tüm ürünler için Pareto analizi özeti
                all_products_sorted = all_df.sort_values('Genel Toplam', ascending=False).copy()
                if not all_products_sorted.empty:
                    total_products = len(all_products_sorted)
                    total_cost = all_products_sorted['Genel Toplam'].sum()
                    if total_cost > 0:
                        all_products_sorted['Kümülâtif %'] = (all_products_sorted['Genel Toplam'].cumsum() / total_cost * 100).round(2)
                    else:
                        all_products_sorted['Kümülâtif %'] = 0

                    items_80_percent_all = len(all_products_sorted[all_products_sorted['Kümülâtif %'] <= 80])
                    if items_80_percent_all == 0 and total_products > 0:
                        items_80_percent_all = 1

                    st.info(f"80/20 Analizi (Tüm Ürünler): Toplam {total_products} ürünün ilk {items_80_percent_all} tanesi toplam maliyetin %80'ini oluşturuyor.")

                    render_subsection_heading("En Yüksek Maliyetli İlk 20 Ürün", icon="🏆")
                    top_20_products = all_products_sorted.head(20)
                    for rank, item in enumerate(top_20_products.to_dict('records'), start=1):
                        formatted_total = format_currency(item.get('Genel Toplam', 0))
                        kum_value = item.get('Kümülâtif %', 0)
                        kum_percent = f"{float(kum_value):.2f}%" if isinstance(kum_value, (int, float)) and not pd.isna(kum_value) else escape(str(kum_value))
                        description = escape(str(item.get('Ürün Açıklaması', '')))
                        group_label = escape(str(item.get('Ürün Grubu', '')))
                        page_label = escape(str(item.get('Sayfa', '')))
                        row_label = escape(str(item.get('Satır', '')))

                        st.markdown(
                            f'<div style="background-color:#0ea5e910; border-left:6px solid #0ea5e9; padding:12px 16px; border-radius:10px; margin-bottom:12px;"><div style="font-weight:700; font-size:16px; color:#111827;">{rank}. {description}</div><div style="font-size:13px; color:#374151; margin-top:6px;"><strong>Genel Toplam:</strong> {formatted_total} &middot; <strong>Kümülâtif %:</strong> {kum_percent}</div><div style="font-size:12px; color:#4b5563; margin-top:4px;"><strong>Grup:</strong> {group_label} &middot; <strong>Sayfa:</strong> {page_label} &middot; <strong>Satır:</strong> {row_label}</div></div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.info('Tüm ürünler için pareto analizi oluşturulamadı.')

                # Görselleştirme
"""
text = text[:start_idx] + new_block + text[end_idx:]
path.write_text(text, encoding='utf-8')
