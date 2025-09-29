from pathlib import Path

path = Path("excel_analyzer.py")
text = path.read_text(encoding="utf-8")
block = "        st.write(\"**\\U0001f4c8 Grafikleri:**\")\n        chart_col1, chart_col2 = st.columns(2)\n        with chart_col1:\n            fig_group_total = px.bar(\n                group_detail_sorted,\n                x='Ürün Açıklaması',\n                y='Genel Toplam',\n                title=f'{selected_group} - Ürün Bazında Genel Toplam'\n            )\n            fig_group_total.update_layout(xaxis_tickangle=45)\n            st.plotly_chart(fig_group_total, use_container_width=True)\n        with chart_col2:\n            cost_melt = group_detail_sorted.melt(\n                id_vars=['Ürün Açıklaması'],\n                value_vars=['Malzeme Fiyatı', 'İşçilik Fiyatı', 'GGK Fiyatı'],\n                var_name='Maliyet Türü',\n                value_name='Tutar'\n            )\n            fig_group_costs = px.bar(\n                cost_melt,\n                x='Ürün Açıklaması',\n                y='Tutar',\n                color='Maliyet Türü',\n                title=f'{selected_group} - Maliyet Türleri Karşılaştırması'\n            )\n            fig_group_costs.update_layout(xaxis_tickangle=45)\n            st.plotly_chart(fig_group_costs, use_container_width=True)\n\n"
if block not in text:
    raise SystemExit("block not found")
text = text.replace(block, "")
path.write_text(text, encoding="utf-8")
