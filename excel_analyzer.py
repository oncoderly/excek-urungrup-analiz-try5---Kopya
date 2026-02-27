import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from html import escape
from io import BytesIO
from datetime import datetime
from app_styles import apply_global_styles

st.set_page_config(page_title="Excel Analiz Uygulaması", layout="wide")

# Modern CSS stil tanımlamaları
apply_global_styles(st)


from analyzer_core import *

def main():
    st.markdown('<div class="main-title"> Excel Analiz Uygulaması</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card">Modern Excel analiz uygulaması ile dosyanızı yükleyip detaylı maliyet analizi yapın. Ürün grupları bazında karşılaştırmalar ve Pareto analizleri gerçekleştirin.</div>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown('<div class="sidebar-section-title">Dosya Yükleme</div>', unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader(
        "Excel dosyanızı seçin",
        type=['xlsx', 'xls'],
        help="Desteklenen formatlar: .xlsx, .xls"
    )

    if uploaded_file is not None:
        try:
            # Excel dosyasının tüm sayfalarını okuma
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names

            st.success(f"✅ Dosya başarıyla yüklendi! ({len(sheet_names)} sayfa bulundu)")

            def normalize_sheet_key(name):
                return turkce_ascii(str(name)).upper().strip()

            iskontolar_sheet_name = next(
                (s for s in sheet_names if normalize_sheet_key(s) == "ISKONTOLAR"),
                None
            )
            genel_gider_sheet_name = next(
                (s for s in sheet_names if normalize_sheet_key(s) == "GENEL GIDER ANALIZ"),
                None
            )

            excluded_sheet_names = {name for name in [iskontolar_sheet_name, genel_gider_sheet_name] if name}
            available_cost_sheets = [s for s in sheet_names if s not in excluded_sheet_names]

            st.sidebar.markdown('<div class="sidebar-section-title">Çalışma Sayfası</div>', unsafe_allow_html=True)
            page_mode = st.sidebar.radio(
                "Görünüm",
                options=["Maliyet Analizi", "Tutarlılık ve Geçmiş Kıyas", "Fiyat Revizyon Kıyas"],
                key="page_mode_selector"
            )

            st.sidebar.markdown('<div class="sidebar-modern-header">Analiz Ayarları</div>', unsafe_allow_html=True)
            st.sidebar.markdown('<div class="sidebar-section-title">Maliyet Analizi - Sayfa Seçimi</div>', unsafe_allow_html=True)
            cost_analysis_sheets = []
            if available_cost_sheets:
                for sheet in available_cost_sheets:
                    if st.sidebar.checkbox(sheet, key=f"cost_sheet_{sheet}"):
                        cost_analysis_sheets.append(sheet)
            else:
                st.sidebar.info("Analiz edilecek sayfa bulunamadı.")

            st.sidebar.markdown('<div class="sidebar-section-title">ğŸ’° Genel Gider Analiz</div>', unsafe_allow_html=True)
            genel_gider_enabled = False
            if genel_gider_sheet_name is not None:
                genel_gider_enabled = st.sidebar.checkbox("Genel Gider Analiz", key="genel_gider_sheet")
            else:
                st.sidebar.warning("Genel Gider Analiz sayfası bulunamadı")

            st.sidebar.markdown("---")
            st.sidebar.markdown('<div class="sidebar-section-title">Kolon Ayarları</div>', unsafe_allow_html=True)

            # Varsayılan kolon indexleri (mevcut şablon)
            iskontolar_group_col_index = 5
            data_group_col_index = 3      # D
            urun_aciklama_col_index = 4   # E
            malzeme_col_index = 21        # V
            iscilik_col_index = 23        # X
            ggk_col_index = 29            # AD
            genel_toplam_col_index = 31   # AF

            # İSKONTOLAR ürün grubu kolonu - dropdown
            if iskontolar_sheet_name is not None:
                iskontolar_columns, iskontolar_header_error = get_sheet_columns(excel_file, iskontolar_sheet_name)
                if iskontolar_header_error is not None:
                    st.sidebar.error(f"İSKONTOLAR başlıkları okunamadı: {str(iskontolar_header_error)}")

                if iskontolar_columns:
                    iskontolar_option_indices = list(range(len(iskontolar_columns)))

                    def format_iskontolar_column_option(col_idx):
                        raw_name = iskontolar_columns[col_idx]
                        raw_text = "" if pd.isna(raw_name) else str(raw_name).strip()
                        excel_col = index_to_excel_column(col_idx)
                        if not raw_text or raw_text.lower().startswith("unnamed"):
                            return f"{excel_col} (Başlık yok)"
                        return f"{raw_text} ({excel_col})"

                    iskontolar_group_col_index = st.sidebar.selectbox(
                        "İSKONTOLAR ürün grubu kolonu",
                        options=iskontolar_option_indices,
                        index=min(5, len(iskontolar_option_indices) - 1),
                        format_func=format_iskontolar_column_option,
                        key="iskontolar_group_col_selector"
                    )
                else:
                    st.sidebar.warning("İSKONTOLAR sayfasında seçilebilir kolon bulunamadı. Varsayılan F kolonu kullanılacak.")

            if available_cost_sheets:
                default_header_sheet_index = 0
                for candidate in ["KEŞİF", "KESİF", "KEŞIF", "KESIF"]:
                    if candidate in available_cost_sheets:
                        default_header_sheet_index = available_cost_sheets.index(candidate)
                        break
                else:
                    for idx, sheet_name in enumerate(available_cost_sheets):
                        if turkce_ascii(str(sheet_name)).upper() == "KESIF":
                            default_header_sheet_index = idx
                            break

                header_source_sheet = st.sidebar.selectbox(
                    "Maliyet kolon başlık kaynağı",
                    options=available_cost_sheets,
                    index=default_header_sheet_index,
                    key="header_source_sheet",
                    help="Açılır listedeki kolon adları bu sayfadan okunur."
                )

                cost_columns, header_error = get_sheet_columns(excel_file, header_source_sheet)
                if header_error is not None:
                    st.sidebar.error(f"Kolon başlıkları okunamadı: {str(header_error)}")

                if cost_columns:
                    option_indices = list(range(len(cost_columns)))

                    def format_column_option(col_idx):
                        raw_name = cost_columns[col_idx]
                        raw_text = "" if pd.isna(raw_name) else str(raw_name).strip()
                        excel_col = index_to_excel_column(col_idx)
                        if not raw_text or raw_text.lower().startswith("unnamed"):
                            return f"{excel_col} (Başlık yok)"
                        return f"{raw_text} ({excel_col})"

                    data_group_col_index = st.sidebar.selectbox(
                        "Maliyet sayfaları ürün grubu kolonu",
                        options=option_indices,
                        index=min(3, len(option_indices) - 1),
                        format_func=format_column_option,
                        key="data_group_col_selector"
                    )
                    urun_aciklama_col_index = st.sidebar.selectbox(
                        "Ürün Açıklaması kolonu",
                        options=option_indices,
                        index=min(4, len(option_indices) - 1),
                        format_func=format_column_option,
                        key="urun_aciklama_col_selector"
                    )
                    malzeme_col_index = st.sidebar.selectbox(
                        "Malzeme Fiyatı kolonu",
                        options=option_indices,
                        index=min(21, len(option_indices) - 1),
                        format_func=format_column_option,
                        key="malzeme_col_selector"
                    )
                    iscilik_col_index = st.sidebar.selectbox(
                        "İşçilik Fiyatı kolonu",
                        options=option_indices,
                        index=min(23, len(option_indices) - 1),
                        format_func=format_column_option,
                        key="iscilik_col_selector"
                    )
                    ggk_col_index = st.sidebar.selectbox(
                        "GGK Fiyatı kolonu",
                        options=option_indices,
                        index=min(29, len(option_indices) - 1),
                        format_func=format_column_option,
                        key="ggk_col_selector"
                    )
                    genel_toplam_col_index = st.sidebar.selectbox(
                        "Genel Toplam kolonu",
                        options=option_indices,
                        index=min(31, len(option_indices) - 1),
                        format_func=format_column_option,
                        key="genel_toplam_col_selector"
                    )

            iskontolar_start_row = int(st.sidebar.number_input(
                "İSKONTOLAR başlangıç satırı",
                min_value=1,
                value=3,
                step=1
            ))
            iskontolar_end_row = int(st.sidebar.number_input(
                "İSKONTOLAR bitiş satırı",
                min_value=1,
                value=27,
                step=1
            ))

            old_price_file = None
            if page_mode == "Fiyat Revizyon Kıyas":
                st.sidebar.markdown("---")
                st.sidebar.markdown('<div class="sidebar-section-title">Kıyas Dosyası</div>', unsafe_allow_html=True)
                old_price_file = st.sidebar.file_uploader(
                    "Eski fiyat çalışması dosyası",
                    type=['xlsx', 'xls'],
                    key="old_price_file_uploader",
                    help="Mevcut yüklenen dosya 'yeni fiyat', bu dosya 'eski fiyat' olarak kıyaslanır."
                )

            if page_mode == "Fiyat Revizyon Kıyas":
                if old_price_file is None:
                    st.info("Fiyat Revizyon Kıyas görünümü için yan panelden 'Eski fiyat çalışması dosyası' yükleyin.")
                    st.stop()

                render_price_revision_compare_module(
                    new_file=uploaded_file,
                    old_file=old_price_file,
                    selected_new_cost_sheets=cost_analysis_sheets,
                    iskontolar_group_col_index=iskontolar_group_col_index,
                    iskontolar_start_row=iskontolar_start_row,
                    iskontolar_end_row=iskontolar_end_row,
                    data_group_col_index=data_group_col_index,
                    urun_aciklama_col_index=urun_aciklama_col_index,
                    malzeme_col_index=malzeme_col_index,
                    iscilik_col_index=iscilik_col_index,
                    ggk_col_index=ggk_col_index,
                    genel_toplam_col_index=genel_toplam_col_index,
                )
                st.stop()
            # Tek sekme olduğu için direkt içeriği göster
            # Ana sayfa başlığı - Özel büyük kart
            st.markdown("""
            <div style="
                margin: 20px auto 40px auto;
                max-width: 1000px;
                padding: 45px 50px;
                background: linear-gradient(135deg, #7c3aed, #a855f7, #c084fc);
                border: 5px solid #8b5cf6;
                border-radius: 30px;
                text-align: center;
                box-shadow: 0 15px 40px rgba(124,58,237,0.4);
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 6px;
                    background: linear-gradient(90deg, #ef4444, #f59e0b, #10b981, #3b82f6);
                "></div>
                <div style="
                    font-family: 'Segoe UI', 'Inter', sans-serif;
                    font-size: 26px;
                    font-weight: 800;
                    color: #ffffff;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    text-shadow: 0 4px 10px rgba(0,0,0,0.6);
                    line-height: 1.1;
                "> Ürün Gruplarına Göre Maliyet Analizi</div>
            </div>
            """, unsafe_allow_html=True)

            # İSKONTOLAR sayfasından ürün gruplarını okuma
            if iskontolar_sheet_name is not None:
                try:
                    # İSKONTOLAR sayfasını oku
                    iskontolar_df = pd.read_excel(uploaded_file, sheet_name=iskontolar_sheet_name)

                    product_groups = []
                    if iskontolar_group_col_index is not None:
                        row_start = min(iskontolar_start_row, iskontolar_end_row) - 1
                        row_end = max(iskontolar_start_row, iskontolar_end_row)

                        for i in range(row_start, row_end):
                            try:
                                if i < len(iskontolar_df) and len(iskontolar_df.columns) > iskontolar_group_col_index:
                                    value = iskontolar_df.iloc[i, iskontolar_group_col_index]
                                    if pd.notna(value):
                                        str_value = str(value).strip()
                                        if str_value and str_value != 'nan':  # Boş olmayan ve nan olmayan hücreler
                                            product_groups.append(str_value)
                            except:
                                continue

                    # product_groups'un liste olduğunu ve boş olmadığını garantile
                    if not isinstance(product_groups, list) or len(product_groups) == 0:
                        product_groups = []

                    if product_groups:
                        st.write(f"**Bulunan Ürün Grupları ({len(product_groups)} adet):**")
                        st.write(", ".join(product_groups))

                        if cost_analysis_sheets:
                            # Tüm sayfalardan veriyi tek tabloda topla
                            all_data = []

                            # Seçilen sayfaları analiz et
                            for sheet_name in cost_analysis_sheets:
                                try:
                                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

                                    selected_indices = [
                                        data_group_col_index,
                                        urun_aciklama_col_index,
                                        malzeme_col_index,
                                        iscilik_col_index,
                                        ggk_col_index,
                                        genel_toplam_col_index
                                    ]
                                    required_max_col = max(idx for idx in selected_indices if idx is not None)

                                    if data_group_col_index is not None and len(df.columns) > required_max_col:  # Yeterli sütun olduğunu kontrol et
                                        for idx, row in df.iterrows():
                                            # Seçilen ürün grubu kolonu
                                            try:
                                                if pd.notna(row.iloc[data_group_col_index]):
                                                    product_group = str(row.iloc[data_group_col_index]).strip()

                                                    # Güvenli karşılaştırma - hem product_group hem de product_groups'un geçerli olduğundan emin ol
                                                    if (product_groups and
                                                        isinstance(product_groups, list) and
                                                        len(product_groups) > 0 and
                                                        product_group and
                                                        isinstance(product_group, str) and
                                                        len(product_group) > 0):
                                                        # Güvenli in operatörü
                                                        found_match = False
                                                        for pg in product_groups:
                                                            if isinstance(pg, str) and pg == product_group:
                                                                found_match = True
                                                                break

                                                        if found_match:
                                                            # Veri satırını kaydet
                                                            data_row = {
                                                                'Ürün Grubu': product_group,
                                                                'Sayfa': sheet_name,
                                                                'Satır': idx + 1,  # Excel satır numarası (1'den başlar)
                                                                'Ürün Açıklaması': str(row.iloc[urun_aciklama_col_index]).strip() if len(row) > urun_aciklama_col_index and pd.notna(row.iloc[urun_aciklama_col_index]) else '',
                                                                'Malzeme Fiyatı': float(row.iloc[malzeme_col_index]) if len(row) > malzeme_col_index and pd.notna(row.iloc[malzeme_col_index]) else 0,
                                                                'İşçilik Fiyatı': float(row.iloc[iscilik_col_index]) if len(row) > iscilik_col_index and pd.notna(row.iloc[iscilik_col_index]) else 0,
                                                                'GGK Fiyatı': float(row.iloc[ggk_col_index]) if len(row) > ggk_col_index and pd.notna(row.iloc[ggk_col_index]) else 0,
                                                                'Genel Toplam': float(row.iloc[genel_toplam_col_index]) if len(row) > genel_toplam_col_index and pd.notna(row.iloc[genel_toplam_col_index]) else 0
                                                            }
                                                            all_data.append(data_row)
                                            except Exception as row_error:
                                                # Satır işleminde hata olursa devam et
                                                continue

                                except Exception as e:
                                    st.warning(f"⚠ {sheet_name} sayfası analiz edilirken hata: {str(e)}")

                            if all_data:
                                # Tüm veriler tablosu
                                all_df = pd.DataFrame(all_data)

                                # Para formatı uygulama fonksiyonu
                                def format_currency(value):
                                    if pd.isna(value) or value == 0:
                                        return "0,00 TL"
                                    return f"{value:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")

                                # Ürün gruplarına göre toplam hesaplama
                                summary_data = all_df.groupby('Ürün Grubu').agg({
                                    'Malzeme Fiyatı': 'sum',
                                    'İşçilik Fiyatı': 'sum',
                                    'GGK Fiyatı': 'sum',
                                    'Genel Toplam': 'sum',
                                    'Sayfa': 'count'  # Kayıt sayısı
                                }).reset_index()

                                summary_data.rename(columns={'Sayfa': 'Bulunan Kayıt Sayısı'}, inplace=True)

                                # Yüzde hesaplamaları için toplam değerleri al
                                total_malzeme = summary_data['Malzeme Fiyatı'].sum()
                                total_iscilik = summary_data['İşçilik Fiyatı'].sum()
                                total_ggk = summary_data['GGK Fiyatı'].sum()
                                total_genel = summary_data['Genel Toplam'].sum()


                                # Genel toplam bazında sıralama
                                summary_data = summary_data.sort_values('Genel Toplam', ascending=False)

                                # Tekil ve kümülatif yüzdeler
                                if total_genel > 0:
                                    summary_data['Genel Toplam %'] = (summary_data['Genel Toplam'] / total_genel * 100).round(2)
                                    summary_data['Kümülatif Genel %'] = (summary_data['Genel Toplam'].cumsum() / total_genel * 100).round(2)
                                else:
                                    summary_data['Genel Toplam %'] = 0.0
                                    summary_data['Kümülatif Genel %'] = 0.0

                                if total_malzeme > 0:
                                    summary_data['Malzeme %'] = (summary_data['Malzeme Fiyatı'] / total_malzeme * 100).round(2)
                                    summary_data['Kümülatif Malzeme %'] = (summary_data['Malzeme Fiyatı'].cumsum() / total_malzeme * 100).round(2)
                                else:
                                    summary_data['Malzeme %'] = 0.0
                                    summary_data['Kümülatif Malzeme %'] = 0.0

                                if total_iscilik > 0:
                                    summary_data['İşçilik %'] = (summary_data['İşçilik Fiyatı'] / total_iscilik * 100).round(2)
                                    summary_data['Kümülatif İşçilik %'] = (summary_data['İşçilik Fiyatı'].cumsum() / total_iscilik * 100).round(2)
                                else:
                                    summary_data['İşçilik %'] = 0.0
                                    summary_data['Kümülatif İşçilik %'] = 0.0

                                if total_ggk > 0:
                                    summary_data['GGK %'] = (summary_data['GGK Fiyatı'] / total_ggk * 100).round(2)
                                    summary_data['Kümülatif GGK %'] = (summary_data['GGK Fiyatı'].cumsum() / total_ggk * 100).round(2)
                                else:
                                    summary_data['GGK %'] = 0.0
                                    summary_data['Kümülatif GGK %'] = 0.0

                                # Sütun sırasını yeniden düzenle
                                summary_data = summary_data[['Ürün Grubu', 'Genel Toplam', 'Genel Toplam %', 'Kümülatif Genel %',
                                                           'Malzeme Fiyatı', 'Malzeme %', 'Kümülatif Malzeme %',
                                                           'İşçilik Fiyatı', 'İşçilik %', 'Kümülatif İşçilik %',
                                                           'GGK Fiyatı', 'GGK %', 'Kümülatif GGK %',
                                                           'Bulunan Kayıt Sayısı']]

                                results_df = summary_data

                                # Özet tablosu (numerik değerler korunur; görsel format create_aggrid_table içinde uygulanır)
                                results_df_display = results_df.copy()

                                if page_mode == "Tutarlılık ve Geçmiş Kıyas":
                                    render_consistency_module(all_df, summary_data, cost_analysis_sheets, uploaded_file.name)
                                    st.stop()

                                # Maliyet analizi için çıktı alma aksiyonları (yazdır / PDF)
                                st.markdown(
                                    """
                                    <div style="
                                        margin: 10px auto 20px auto;
                                        padding: 14px 18px;
                                        background: linear-gradient(135deg, #eff6ff, #dbeafe);
                                        border: 1px solid #93c5fd;
                                        border-radius: 12px;
                                    ">
                                        <div style="
                                            font-weight: 700;
                                            color: #1e3a8a;
                                            margin-bottom: 6px;
                                        ">Maliyet Analizi Cikti</div>
                                        <div style="
                                            font-size: 13px;
                                            color: #334155;
                                        ">Tarayici yazdirma penceresi ile ekrani PDF olarak kaydedebilir veya detayli Excel ciktisi indirebilirsiniz.</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                                output_col1, output_col2 = st.columns(2)

                                with output_col1:
                                    if st.button("Yazdir / PDF Cikti Al", key="print_cost_analysis_view", use_container_width=True):
                                        components.html(
                                            """
                                            <script>
                                            setTimeout(function () {
                                                if (window.parent) {
                                                    window.parent.print();
                                                } else {
                                                    window.print();
                                                }
                                            }, 100);
                                            </script>
                                            """,
                                            height=0,
                                            width=0,
                                        )
                                        st.info("Tarayici yazdirma penceresi acildi. 'PDF olarak kaydet' secenegini kullanabilirsiniz.")

                                with output_col2:
                                    try:
                                        excel_buffer = BytesIO()
                                        excel_all_df = all_df.sort_values('Genel Toplam', ascending=False).copy()
                                        excel_top50_df = excel_all_df.head(50).copy()

                                        group_top50_list = []
                                        canonical_group_col = 'Ürün Grubu'
                                        if canonical_group_col not in excel_all_df.columns:
                                            fallback_group_cols = [
                                                col for col in excel_all_df.columns
                                                if "URUN GRUBU" in normalize_excel_header_name(col)
                                            ]
                                            if fallback_group_cols:
                                                canonical_group_col = fallback_group_cols[0]
                                            else:
                                                raise KeyError(canonical_group_col)
                                        for group_name, group_df_export in excel_all_df.groupby(canonical_group_col, sort=False):
                                            group_sorted = group_df_export.sort_values('Genel Toplam', ascending=False).head(50).copy()
                                            group_sorted.insert(0, 'Grup Ici Sira', range(1, len(group_sorted) + 1))
                                            group_top50_list.append(group_sorted)

                                        group_top50_df = pd.concat(group_top50_list, ignore_index=True) if group_top50_list else pd.DataFrame()
                                        excel_results_df = prepare_dataframe_for_excel_export(results_df)
                                        excel_top50_df = prepare_dataframe_for_excel_export(excel_top50_df)
                                        excel_all_df = prepare_dataframe_for_excel_export(excel_all_df)
                                        if not group_top50_df.empty:
                                            group_top50_df = prepare_dataframe_for_excel_export(group_top50_df)

                                        meta_df = pd.DataFrame([
                                            {'Alan': 'Kaynak Dosya', 'Deger': uploaded_file.name},
                                            {'Alan': 'Secilen Sayfalar', 'Deger': ', '.join(cost_analysis_sheets)},
                                            {'Alan': 'Rapor Tarihi', 'Deger': datetime.now().strftime('%d.%m.%Y %H:%M')},
                                            {'Alan': 'Toplam Kayit', 'Deger': len(excel_all_df)},
                                            {'Alan': 'Toplam Urun Grubu', 'Deger': len(results_df)},
                                        ])

                                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                            meta_df.to_excel(writer, sheet_name='Rapor_Bilgisi', index=False)
                                            excel_results_df.to_excel(writer, sheet_name='Ozet_Urun_Grubu', index=False)
                                            excel_top50_df.to_excel(writer, sheet_name='En_Pahali_50_Urun', index=False)
                                            excel_all_df.to_excel(writer, sheet_name='Tum_Kayitlar', index=False)
                                            if not group_top50_df.empty:
                                                group_top50_df.to_excel(writer, sheet_name='Grup_EnPahali50', index=False)
                                            for worksheet in writer.book.worksheets:
                                                style_excel_sheet(worksheet)

                                        excel_buffer.seek(0)
                                        st.download_button(
                                            label="Detayli Excel Ciktisi Indir",
                                            data=excel_buffer.getvalue(),
                                            file_name=f"maliyet_analizi_raporu_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            key="download_cost_analysis_excel",
                                            use_container_width=True,
                                        )
                                    except Exception as excel_error:
                                        st.warning(f"Excel ciktisi hazirlanamadi: {str(excel_error)}")

                                # Tablo üstü açıklama - başlıkla uyumlu renk
                                st.markdown("""
                                <div style="
                                    margin: 20px auto;
                                    padding: 15px 25px;
                                    background: linear-gradient(135deg, #e9d5ff, #c4b5fd);
                                    border: 2px solid #8b5cf6;
                                    border-radius: 12px;
                                    text-align: center;
                                    box-shadow: 0 4px 12px rgba(139,92,246,0.2);
                                ">
                                    <div style="
                                        font-family: 'Segoe UI', 'Inter', sans-serif;
                                        font-size: 16px;
                                        font-weight: 700;
                                        color: #6b21a8;
                                        letter-spacing: 1px;
                                    "> Ürün Gruplarına Göre Maliyet Analizi Sonuçları</div>
                                </div>
                                """, unsafe_allow_html=True)


                                # Kolon bazlı renk kodu ekle
                                st.markdown("""
                                <style>
                                /* Spesifik kolon renklendirme - Güçlü CSS */
                                .ag-theme-material .malzeme-header {
                                    background: linear-gradient(135deg, rgba(34,197,94,0.8), rgba(22,163,74,0.6)) !important;
                                }
                                .ag-theme-material .iscilik-header {
                                    background: linear-gradient(135deg, rgba(59,130,246,0.8), rgba(37,99,235,0.6)) !important;
                                }
                                .ag-theme-material .toplam-header {
                                    background: linear-gradient(135deg, rgba(239,68,68,0.8), rgba(220,38,38,0.6)) !important;
                                }
                                .ag-theme-material .ggk-header {
                                    background: linear-gradient(135deg, rgba(147,51,234,0.8), rgba(124,58,237,0.6)) !important;
                                }
                                .ag-theme-material .grup-header {
                                    background: linear-gradient(135deg, rgba(107,114,128,0.8), rgba(75,85,99,0.6)) !important;
                                }
                                </style>
                                """, unsafe_allow_html=True)

                                # Tablo gösterimi - AgGrid
                                create_aggrid_table(results_df_display, height=500)

                                # TOPLAM FİYATLAR - BÜYÜK PUNTOLARLA - DÜZELTİLMİ YERLEİM
                                st.markdown("""<div style='margin: 40px 0;'></div>""", unsafe_allow_html=True)

                                # Üç kategori yan yana
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.markdown(f"""
                                    <div style="
                                        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
                                        border: 4px solid #10b981;
                                        border-radius: 20px;
                                        padding: 30px 20px;
                                        text-align: center;
                                        box-shadow: 0 10px 25px rgba(16,185,129,0.3);
                                        margin: 10px;
                                        min-height: 150px;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: center;
                                    ">
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 25.5px;
                                            font-weight: 800;
                                            color: #047857;
                                            text-transform: uppercase;
                                            letter-spacing: 2px;
                                            margin-bottom: 15px;
                                        ">TOPLAM MALZEME</div>
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 26px;
                                            font-weight: 900;
                                            color: #059669;
                                            text-shadow: 0 3px 6px rgba(5,150,105,0.4);
                                            letter-spacing: -1px;
                                            line-height: 1.1;
                                        ">{total_malzeme:,.0f} TL</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                with col2:
                                    st.markdown(f"""
                                    <div style="
                                        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
                                        border: 4px solid #3b82f6;
                                        border-radius: 20px;
                                        padding: 30px 20px;
                                        text-align: center;
                                        box-shadow: 0 10px 25px rgba(59,130,246,0.3);
                                        margin: 10px;
                                        min-height: 150px;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: center;
                                    ">
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 25.5px;
                                            font-weight: 800;
                                            color: #1e40af;
                                            text-transform: uppercase;
                                            letter-spacing: 2px;
                                            margin-bottom: 15px;
                                        ">TOPLAM İÇİLİK</div>
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 26px;
                                            font-weight: 900;
                                            color: #1d4ed8;
                                            text-shadow: 0 3px 6px rgba(29,78,216,0.4);
                                            letter-spacing: -1px;
                                            line-height: 1.1;
                                        ">{total_iscilik:,.0f} TL</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                with col3:
                                    st.markdown(f"""
                                    <div style="
                                        background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
                                        border: 4px solid #8b5cf6;
                                        border-radius: 20px;
                                        padding: 30px 20px;
                                        text-align: center;
                                        box-shadow: 0 10px 25px rgba(139,92,246,0.3);
                                        margin: 10px;
                                        min-height: 150px;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: center;
                                    ">
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 25.5px;
                                            font-weight: 800;
                                            color: #7c3aed;
                                            text-transform: uppercase;
                                            letter-spacing: 2px;
                                            margin-bottom: 15px;
                                        ">TOPLAM GGK</div>
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 26px;
                                            font-weight: 900;
                                            color: #6b21a8;
                                            text-shadow: 0 3px 6px rgba(107,33,168,0.4);
                                            letter-spacing: -1px;
                                            line-height: 1.1;
                                        ">{total_ggk:,.0f} TL</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                # Genel Toplam ayrı satırda, daha büyük
                                st.markdown("""<div style='margin: 30px 0;'></div>""", unsafe_allow_html=True)
                                st.markdown(f"""
                                <div style="
                                    margin: 20px auto;
                                    max-width: 800px;
                                    padding: 24px 18px;
                                    background: linear-gradient(135deg, #fecaca, #fca5a5);
                                    border: 5px solid #ef4444;
                                    border-radius: 25px;
                                    text-align: center;
                                    box-shadow: 0 15px 35px rgba(239,68,68,0.4);
                                ">
                                    <div style="
                                        font-family: 'Segoe UI', 'Inter', sans-serif;
                                        font-size: 32.3px;
                                        font-weight: 900;
                                        color: #dc2626;
                                        text-transform: uppercase;
                                        letter-spacing: 2px;
                                        margin-bottom: 12px;
                                    ">GENEL TOPLAM</div>
                                    <div style="
                                        font-family: 'Segoe UI', 'Inter', sans-serif;
                                        font-size: 42px;
                                        font-weight: 900;
                                        color: #b91c1c;
                                        text-shadow: 0 4px 12px rgba(185,28,28,0.5);
                                        letter-spacing: -2px;
                                        line-height: 1.1;
                                    ">{total_genel:,.0f} TL</div>
                                </div>
                                """, unsafe_allow_html=True)

                                # Ana görselleştirmeler
                                render_section_heading("Genel Görselleştirmeler", icon="")

                                main_chart_mode = st.radio(
                                    "Maliyet dağılımı grafik türü",
                                    options=["Treemap", "Sankey"],
                                    horizontal=True,
                                    key="main_chart_mode"
                                )

                                section_title = " Maliyet Türlerine Göre Detaylı Treemap'ler" if main_chart_mode == "Treemap" else " Maliyet Türlerine Göre Sankey Akışları"
                                st.markdown(f"""
                                <div style="
                                    margin: 35px auto 25px auto;
                                    max-width: 800px;
                                    padding: 30px 35px;
                                    background: linear-gradient(135deg, #10b981, #059669, #047857);
                                    border: 3px solid #10b981;
                                    border-radius: 20px;
                                    text-align: center;
                                    box-shadow: 0 10px 25px rgba(16,185,129,0.3);
                                    position: relative;
                                ">
                                    <div style="
                                        position: absolute;
                                        top: 0;
                                        left: 0;
                                        right: 0;
                                        height: 4px;
                                        background: linear-gradient(90deg, #fbbf24, #10b981, #3b82f6);
                                    "></div>
                                    <div style="
                                        font-family: 'Segoe UI', 'Inter', sans-serif;
                                        font-size: 19px;
                                        font-weight: 800;
                                        color: #ffffff;
                                        text-transform: uppercase;
                                        letter-spacing: 2px;
                                        text-shadow: 0 2px 6px rgba(0,0,0,0.4);
                                    ">{section_title}</div>
                                </div>
                                """, unsafe_allow_html=True)

                                if main_chart_mode == "Treemap":
                                    # Malzeme Maliyeti Treemap
                                    st.markdown("""
                                    <div style="
                                        margin: 20px auto 15px auto;
                                        padding: 20px 25px;
                                        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
                                        border: 2px solid #22c55e;
                                        border-radius: 15px;
                                        text-align: center;
                                        box-shadow: 0 6px 15px rgba(34,197,94,0.2);
                                        max-width: 500px;
                                    ">
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 15px;
                                            font-weight: 700;
                                            color: #15803d;
                                            letter-spacing: 1px;
                                            text-shadow: 0 1px 3px rgba(21,128,61,0.2);
                                        "> Malzeme Maliyeti Dağılımı</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    fig_malzeme_treemap = px.treemap(
                                        summary_data,
                                        path=['Ürün Grubu'],
                                        values='Malzeme Fiyatı',
                                        title='Ürün Gruplarına Göre Malzeme Maliyeti Dağılımı',
                                        color='Malzeme Fiyatı',
                                        color_continuous_scale='Greens'
                                    )
                                    fig_malzeme_treemap.update_layout(
                                        height=450,
                                        paper_bgcolor='rgba(220,252,231,0.3)',
                                        plot_bgcolor='rgba(187,247,208,0.2)'
                                    )
                                    fig_malzeme_treemap.update_traces(
                                        texttemplate='<b>%{label}</b><br>%{value:,.0f} TL<br>%{percentParent}',
                                        textposition='middle center'
                                    )
                                    st.plotly_chart(fig_malzeme_treemap, use_container_width=True)

                                    # İşçilik Maliyeti Treemap
                                    st.markdown("""
                                    <div style="
                                        margin: 20px auto 15px auto;
                                        padding: 20px 25px;
                                        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
                                        border: 2px solid #3b82f6;
                                        border-radius: 15px;
                                        text-align: center;
                                        box-shadow: 0 6px 15px rgba(59,130,246,0.2);
                                        max-width: 500px;
                                    ">
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 15px;
                                            font-weight: 700;
                                            color: #1d4ed8;
                                            letter-spacing: 1px;
                                            text-shadow: 0 1px 3px rgba(29,78,216,0.2);
                                        "> İşçilik Maliyeti Dağılımı</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    fig_iscilik_treemap = px.treemap(
                                        summary_data,
                                        path=['Ürün Grubu'],
                                        values='İşçilik Fiyatı',
                                        title='Ürün Gruplarına Göre İşçilik Maliyeti Dağılımı',
                                        color='İşçilik Fiyatı',
                                        color_continuous_scale='Blues'
                                    )
                                    fig_iscilik_treemap.update_layout(
                                        height=450,
                                        paper_bgcolor='rgba(219,234,254,0.3)',
                                        plot_bgcolor='rgba(191,219,254,0.2)'
                                    )
                                    fig_iscilik_treemap.update_traces(
                                        texttemplate='<b>%{label}</b><br>%{value:,.0f} TL<br>%{percentParent}',
                                        textposition='middle center'
                                    )
                                    st.plotly_chart(fig_iscilik_treemap, use_container_width=True)

                                    # Genel Toplam Treemap
                                    st.markdown("""
                                    <div style="
                                        margin: 25px auto 15px auto;
                                        padding: 22px 30px;
                                        background: linear-gradient(135deg, #fecaca, #fca5a5);
                                        border: 2px solid #ef4444;
                                        border-radius: 15px;
                                        text-align: center;
                                        box-shadow: 0 6px 15px rgba(239,68,68,0.25);
                                        max-width: 600px;
                                    ">
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 26px;
                                            font-weight: 700;
                                            color: #dc2626;
                                            letter-spacing: 1px;
                                            text-shadow: 0 1px 3px rgba(220,38,38,0.2);
                                        "> Ürün Grupları - Genel Toplam Treemap</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    fig_main_treemap = px.treemap(
                                        summary_data,
                                        path=['Ürün Grubu'],
                                        values='Genel Toplam',
                                        title='Ürün Gruplarına Göre Genel Toplam Dağılımı',
                                        color='Genel Toplam',
                                        color_continuous_scale='Blues',
                                        labels={'values': 'Genel Toplam (TL)', 'labels': 'Ürün Grubu'}
                                    )
                                    fig_main_treemap.update_layout(
                                        height=500,
                                        paper_bgcolor='rgba(254,202,202,0.3)',
                                        plot_bgcolor='rgba(252,165,165,0.2)'
                                    )
                                    fig_main_treemap.update_traces(
                                        texttemplate='<b>%{label}</b><br>%{value:,.0f} TL<br>%{percentParent}',
                                        textposition='middle center'
                                    )
                                    st.plotly_chart(fig_main_treemap, use_container_width=True)
                                else:
                                    fig_malzeme_sankey = create_sankey_chart(
                                        summary_data,
                                        'Ürün Grubu',
                                        'Malzeme Fiyatı',
                                        'Toplam Malzeme',
                                        'Ürün Gruplarına Göre Malzeme Maliyeti Akışı',
                                        max_targets=25,
                                        height=450
                                    )
                                    if fig_malzeme_sankey is not None:
                                        st.plotly_chart(fig_malzeme_sankey, use_container_width=True)
                                    else:
                                        st.info("Malzeme Sankey grafiği için veri bulunamadı.")

                                    fig_iscilik_sankey = create_sankey_chart(
                                        summary_data,
                                        'Ürün Grubu',
                                        'İşçilik Fiyatı',
                                        'Toplam İşçilik',
                                        'Ürün Gruplarına Göre İşçilik Maliyeti Akışı',
                                        max_targets=25,
                                        height=450
                                    )
                                    if fig_iscilik_sankey is not None:
                                        st.plotly_chart(fig_iscilik_sankey, use_container_width=True)
                                    else:
                                        st.info("İşçilik Sankey grafiği için veri bulunamadı.")

                                    fig_genel_sankey = create_sankey_chart(
                                        summary_data,
                                        'Ürün Grubu',
                                        'Genel Toplam',
                                        'Genel Toplam',
                                        'Ürün Gruplarına Göre Genel Toplam Akışı',
                                        max_targets=25,
                                        height=500
                                    )
                                    if fig_genel_sankey is not None:
                                        st.plotly_chart(fig_genel_sankey, use_container_width=True)
                                    else:
                                        st.info("Genel Toplam Sankey grafiği için veri bulunamadı.")

                                # Maliyet türlerine göre karşılaştırma grafikleri
                                col1, col2 = st.columns(2)

                                with col1:
                                    # Karşılaştırma başlığı - mini kart
                                    st.markdown("""
                                    <div style="
                                        margin: 15px auto 10px auto;
                                        padding: 15px 20px;
                                        background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
                                        border: 2px solid #6b7280;
                                        border-radius: 12px;
                                        text-align: center;
                                        box-shadow: 0 4px 10px rgba(107,114,128,0.15);
                                    ">
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 16px;
                                            font-weight: 700;
                                            color: #374151;
                                            letter-spacing: 0.5px;
                                        "> Malzeme vs İşçilik vs GGK</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    fig_comparison = px.bar(
                                        summary_data,
                                        x='Ürün Grubu',
                                        y=['Malzeme Fiyatı', 'İşçilik Fiyatı', 'GGK Fiyatı'],
                                        title='Ürün Grupları Maliyet Karşılaştırması',
                                        color_discrete_map={
                                            'Malzeme Fiyatı': '#10b981',
                                            'İşçilik Fiyatı': '#3b82f6',
                                            'GGK Fiyatı': '#f59e0b'
                                        }
                                    )
                                    fig_comparison.update_layout(
                                        height=400,
                                        xaxis_tickangle=45,
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                        paper_bgcolor='rgba(243,244,246,0.3)',
                                        plot_bgcolor='rgba(229,231,235,0.2)'
                                    )
                                    st.plotly_chart(fig_comparison, use_container_width=True)

                                with col2:
                                    # Dağılım başlığı - mini kart
                                    st.markdown("""
                                    <div style="
                                        margin: 15px auto 10px auto;
                                        padding: 15px 20px;
                                        background: linear-gradient(135deg, #fef3c7, #fde68a);
                                        border: 2px solid #f59e0b;
                                        border-radius: 12px;
                                        text-align: center;
                                        box-shadow: 0 4px 10px rgba(245,158,11,0.15);
                                    ">
                                        <div style="
                                            font-family: 'Segoe UI', 'Inter', sans-serif;
                                            font-size: 16px;
                                            font-weight: 700;
                                            color: #92400e;
                                            letter-spacing: 0.5px;
                                        "> Grup Bazında Dağılım</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    fig_pie = px.pie(
                                        summary_data,
                                        values='Genel Toplam',
                                        names='Ürün Grubu',
                                        title='Ürün Grupları Genel Toplam Oranları',
                                        color_discrete_sequence=px.colors.qualitative.Set3
                                    )
                                    fig_pie.update_layout(
                                        height=400,
                                        paper_bgcolor='rgba(254,243,199,0.3)',
                                        plot_bgcolor='rgba(253,230,138,0.2)'
                                    )
                                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                                    st.plotly_chart(fig_pie, use_container_width=True)

                                # GGK Maliyeti Treemap
                                # GGK başlığı - küçük kart
                                st.markdown("""
                                <div style="
                                    margin: 20px auto 15px auto;
                                    padding: 20px 25px;
                                    background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
                                    border: 2px solid #8b5cf6;
                                    border-radius: 15px;
                                    text-align: center;
                                    box-shadow: 0 6px 15px rgba(139,92,246,0.2);
                                    max-width: 500px;
                                ">
                                    <div style="
                                        font-family: 'Segoe UI', 'Inter', sans-serif;
                                        font-size: 15px;
                                        font-weight: 700;
                                        color: #7c3aed;
                                        letter-spacing: 1px;
                                        text-shadow: 0 1px 3px rgba(124,58,237,0.2);
                                    ">⚙ GGK Maliyeti Dağılımı</div>
                                </div>
                                """, unsafe_allow_html=True)
                                fig_ggk_treemap = px.treemap(
                                    summary_data,
                                    path=['Ürün Grubu'],
                                    values='GGK Fiyatı',
                                    title='Ürün Gruplarına Göre GGK Maliyeti Dağılımı',
                                    color='GGK Fiyatı',
                                    color_continuous_scale='Oranges'
                                )
                                fig_ggk_treemap.update_layout(
                                    height=450,
                                    paper_bgcolor='rgba(243,232,255,0.3)',
                                    plot_bgcolor='rgba(233,213,255,0.2)'
                                )
                                fig_ggk_treemap.update_traces(
                                    texttemplate='<b>%{label}</b><br>%{value:,.0f} TL<br>%{percentParent}',
                                    textposition='middle center'
                                )
                                st.plotly_chart(fig_ggk_treemap, use_container_width=True)

                                # Kümülatif analiz grafiği
                                # Kümülatif analiz başlığı - orta kart
                                st.markdown("""
                                <div style="
                                    margin: 25px auto 15px auto;
                                    padding: 22px 30px;
                                    background: linear-gradient(135deg, #a78bfa, #8b5cf6);
                                    border: 2px solid #7c3aed;
                                    border-radius: 15px;
                                    text-align: center;
                                    box-shadow: 0 8px 20px rgba(124,58,237,0.25);
                                    max-width: 600px;
                                ">
                                    <div style="
                                        font-family: 'Segoe UI', 'Inter', sans-serif;
                                        font-size: 26px;
                                        font-weight: 800;
                                        color: #ffffff;
                                        letter-spacing: 1px;
                                        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                                    "> Kümülatif Maliyet Analizi</div>
                                </div>
                                """, unsafe_allow_html=True)
                                fig_cumulative = px.bar(
                                    summary_data,
                                    x='Ürün Grubu',
                                    y='Genel Toplam',
                                    title='Ürün Grupları Kümülatif Maliyet Analizi (Pareto)',
                                    color='Kümülatif Genel %',
                                    color_continuous_scale='viridis',
                                    hover_data=['Genel Toplam %', 'Kümülatif Genel %', 'Bulunan Kayıt Sayısı']
                                )

                                # Kümülatif yüzde çizgisi ekle
                                fig_cumulative.add_scatter(
                                    x=summary_data['Ürün Grubu'],
                                    y=summary_data['Kümülatif Genel %'] * total_genel / 100,
                                    mode='lines+markers',
                                    name='Kümülatif %',
                                    yaxis='y2',
                                    line=dict(color='red', width=3),
                                    marker=dict(size=8)
                                )

                                fig_cumulative.update_layout(
                                    height=500,
                                    xaxis_tickangle=45,
                                    yaxis2=dict(
                                        title='Kümülatif Yüzde (%)',
                                        overlaying='y',
                                        side='right',
                                        range=[0, 100]
                                    ),
                                    paper_bgcolor='rgba(167,139,250,0.2)',
                                    plot_bgcolor='rgba(139,92,246,0.1)'
                                )
                                st.plotly_chart(fig_cumulative, use_container_width=True)

                                # ABC Analizi bilgi kutusu
                                render_subsection_heading("ABC Analizi", icon="ğŸ¯")

                                # A, B, C grupları belirleme
                                a_groups = summary_data[summary_data['Kümülatif Genel %'] <= 80]
                                b_groups = summary_data[(summary_data['Kümülatif Genel %'] > 80) & (summary_data['Kümülatif Genel %'] <= 95)]
                                c_groups = summary_data[summary_data['Kümülatif Genel %'] > 95]

                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.markdown("""
                                    <div class="info-card" style="border-left: 4px solid #ef4444;">
                                        <h4 style="color: #dc2626; margin-bottom: 12px;">ğŸ…°ï¸ A Grubu (Kritik)</h4>
                                        <p style="font-size: 19px; color: #475569; margin-bottom: 8px;">Toplam maliyetin %80'ini oluşturan gruplar</p>
                                        <p style="font-weight: 600; color: #1e293b;">Grup Sayısı: {}</p>
                                    </div>
                                    """.format(len(a_groups)), unsafe_allow_html=True)

                                    if not a_groups.empty:
                                        for _, group in a_groups.iterrows():
                                            st.write(f"• {group['Ürün Grubu']} ({group['Genel Toplam %']:.1f}%)")

                                with col2:
                                    st.markdown("""
                                    <div class="info-card" style="border-left: 4px solid #f59e0b;">
                                        <h4 style="color: #d97706; margin-bottom: 12px;"> B Grubu (Önemli)</h4>
                                        <p style="font-size: 19px; color: #475569; margin-bottom: 8px;">%80-95 arası maliyeti oluşturan gruplar</p>
                                        <p style="font-weight: 600; color: #1e293b;">Grup Sayısı: {}</p>
                                    </div>
                                    """.format(len(b_groups)), unsafe_allow_html=True)

                                    if not b_groups.empty:
                                        for _, group in b_groups.iterrows():
                                            st.write(f"• {group['Ürün Grubu']} ({group['Genel Toplam %']:.1f}%)")

                                with col3:
                                    st.markdown("""
                                    <div class="info-card" style="border-left: 4px solid #10b981;">
                                        <h4 style="color: #059669; margin-bottom: 12px;"> C Grubu (Düşük)</h4>
                                        <p style="font-size: 19px; color: #475569; margin-bottom: 8px;">%95'in üzerindeki gruplar</p>
                                        <p style="font-weight: 600; color: #1e293b;">Grup Sayısı: {}</p>
                                    </div>
                                    """.format(len(c_groups)), unsafe_allow_html=True)

                                    if not c_groups.empty:
                                        for _, group in c_groups.iterrows():
                                            st.write(f"• {group['Ürün Grubu']} ({group['Genel Toplam %']:.1f}%)")

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

                                    render_subsection_heading("En Yüksek Maliyetli İlk 20 Ürün", icon="")
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
                                            f"""
                 <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(16, 185, 129, 0.05)); border-left: 4px solid #3b82f6; padding: 20px 24px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); transition: all 0.3s ease;">
                   <div style="font-weight: 700; font-size: 15px; color: #1e293b; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                     <span style="background: linear-gradient(135deg, #3b82f6, #10b981); color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 600;">{rank}</span>
                     {description}
                   </div>
                   <div style="font-size: 19px; color: #475569; margin-bottom: 6px; display: flex; gap: 24px; flex-wrap: wrap;">
                     <span style="background: rgba(16, 185, 129, 0.1); color: #059669; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 13px;"><strong>Genel Toplam:</strong> {formatted_total}</span>
                     <span style="background: rgba(59, 130, 246, 0.1); color: #1e40af; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 13px;"><strong>Kümülâtif %:</strong> {kum_percent}</span>
                   </div>
                   <div style="font-size: 12px; color: #64748b; display: flex; gap: 16px; flex-wrap: wrap;">
                     <span><strong>Grup:</strong> {group_label}</span>
                     <span><strong>Sayfa:</strong> {page_label}</span>
                     <span><strong>Satır:</strong> {row_label}</span>
                   </div>
                 </div>
                """,
                                            unsafe_allow_html=True,
                                        )
                                else:
                                    st.info('Tüm ürünler için pareto analizi oluşturulamadı.')

                                # Ürün grubu bazlı detaylı analiz
                                if product_groups:
                                    render_section_heading("Ürün Grupları Detay Analizi", icon="")

                                    unique_product_groups = list(dict.fromkeys(product_groups))
                                    detail_group_options = ["Tümü"] + unique_product_groups
                                    selected_group = st.selectbox(
                                        "Detayını görmek istediğiniz ürün grubunu seçin:",
                                        options=detail_group_options,
                                        key="group_selector"
                                    )

                                    if selected_group:
                                        # Seçilen gruba ait verileri filtrele
                                        selected_group_title = "Tüm Gruplar" if selected_group == "Tümü" else selected_group
                                        if selected_group == "Tümü":
                                            group_detail = all_df.copy()
                                        else:
                                            group_detail = all_df[all_df['Ürün Grubu'] == selected_group].copy()

                                        if not group_detail.empty:
                                            # Gruba göre sıralama
                                            group_detail_sorted = group_detail.sort_values('Genel Toplam', ascending=False)

                                            # Kümülatif yüzde hesaplama
                                            group_total = group_detail_sorted['Genel Toplam'].sum()
                                            if group_total > 0:
                                                group_detail_sorted['Genel Toplam %'] = (group_detail_sorted['Genel Toplam'] / group_total * 100).round(2)
                                                group_detail_sorted['Kümülâtif Genel %'] = (group_detail_sorted['Genel Toplam'].cumsum() / group_total * 100).round(2)
                                            else:
                                                group_detail_sorted['Genel Toplam %'] = 0
                                                group_detail_sorted['Kümülâtif Genel %'] = 0

                                            # Grup özet bilgileri
                                            col1, col2, col3, col4 = st.columns(4)
                                            with col1:
                                                st.metric("Toplam Kalem", len(group_detail))
                                            with col2:
                                                st.metric("Toplam Maliyet", f"{group_total:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
                                            with col3:
                                                avg_cost = group_detail['Genel Toplam'].mean()
                                                st.metric("Ortalama Maliyet", f"{avg_cost:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
                                            with col4:
                                                max_cost = group_detail['Genel Toplam'].max()
                                                st.metric("En Yüksek Maliyet", f"{max_cost:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))

                                            # Grup detay tablosu
                                            render_subsection_heading("Grup İçi Ürün Detayları", icon="")
                                            preferred_detail_columns = [
                                                'Ürün Grubu',
                                                'Sayfa',
                                                'Satır',
                                                'Ürün Açıklaması',
                                                'Malzeme Fiyatı',
                                                'İşçilik Fiyatı',
                                                'GGK Fiyatı',
                                                'Genel Toplam',
                                                'Genel Toplam %',
                                                'Kümülâtif Genel %'
                                            ]
                                            ordered_detail_columns = [col for col in preferred_detail_columns if col in group_detail_sorted.columns]
                                            remaining_detail_columns = [col for col in group_detail_sorted.columns if col not in ordered_detail_columns]
                                            group_detail_display = group_detail_sorted[ordered_detail_columns + remaining_detail_columns].copy()

                                            # Grup detay tablosu için renk kodları
                                            st.markdown("""
                                            <style>
                                            /* Grup detay tablosu için özel stiller */
                                            .ag-theme-material .ag-cell[col-id="Ürün Açıklaması"] {
                                                text-align: left !important;
                                                font-weight: 600 !important;
                                                background: rgba(249,250,251,0.8) !important;
                                            }
                                            </style>
                                            """, unsafe_allow_html=True)

                                            create_aggrid_table(group_detail_display, height=400)

                                            # Görselleştirmeler
                                            render_subsection_heading("Görselleştirmeler", icon="")

                                            group_chart_mode = st.radio(
                                                "Grup grafik türü",
                                                options=["Treemap", "Sankey"],
                                                horizontal=True,
                                                key="group_chart_mode"
                                            )

                                            if group_chart_mode == "Treemap":
                                                col1, col2 = st.columns(2)

                                                with col1:
                                                    fig_group_treemap_total = px.treemap(
                                                        group_detail_sorted,
                                                        path=['Ürün Açıklaması'],
                                                        values='Genel Toplam',
                                                        title=f'{selected_group_title} - Genel Toplam Dağılımı',
                                                        color='Genel Toplam',
                                                        color_continuous_scale='Blues'
                                                    )
                                                    fig_group_treemap_total.update_layout(height=400)
                                                    st.plotly_chart(fig_group_treemap_total, use_container_width=True)

                                                with col2:
                                                    fig_group_treemap_malzeme = px.treemap(
                                                        group_detail_sorted,
                                                        path=['Ürün Açıklaması'],
                                                        values='Malzeme Fiyatı',
                                                        title=f'{selected_group_title} - Malzeme Maliyeti Dağılımı',
                                                        color='Malzeme Fiyatı',
                                                        color_continuous_scale='Greens'
                                                    )
                                                    fig_group_treemap_malzeme.update_layout(height=400)
                                                    st.plotly_chart(fig_group_treemap_malzeme, use_container_width=True)

                                                fig_group_treemap_iscilik = px.treemap(
                                                    group_detail_sorted,
                                                    path=['Ürün Açıklaması'],
                                                    values='İşçilik Fiyatı',
                                                    title=f'{selected_group_title} - İşçilik Maliyeti Dağılımı',
                                                    color='İşçilik Fiyatı',
                                                    color_continuous_scale='Oranges'
                                                )
                                                fig_group_treemap_iscilik.update_layout(height=400)
                                                st.plotly_chart(fig_group_treemap_iscilik, use_container_width=True)
                                            else:
                                                col1, col2 = st.columns(2)

                                                with col1:
                                                    fig_group_sankey_total = create_sankey_chart(
                                                        group_detail_sorted,
                                                        'Ürün Açıklaması',
                                                        'Genel Toplam',
                                                        f'{selected_group_title} Genel Toplam',
                                                        f'{selected_group_title} - Genel Toplam Akışı',
                                                        max_targets=30,
                                                        height=400
                                                    )
                                                    if fig_group_sankey_total is not None:
                                                        st.plotly_chart(fig_group_sankey_total, use_container_width=True)
                                                    else:
                                                        st.info("Genel Toplam Sankey grafiği için veri bulunamadı.")

                                                with col2:
                                                    fig_group_sankey_malzeme = create_sankey_chart(
                                                        group_detail_sorted,
                                                        'Ürün Açıklaması',
                                                        'Malzeme Fiyatı',
                                                        f'{selected_group_title} Malzeme',
                                                        f'{selected_group_title} - Malzeme Maliyeti Akışı',
                                                        max_targets=30,
                                                        height=400
                                                    )
                                                    if fig_group_sankey_malzeme is not None:
                                                        st.plotly_chart(fig_group_sankey_malzeme, use_container_width=True)
                                                    else:
                                                        st.info("Malzeme Sankey grafiği için veri bulunamadı.")

                                                fig_group_sankey_iscilik = create_sankey_chart(
                                                    group_detail_sorted,
                                                    'Ürün Açıklaması',
                                                    'İşçilik Fiyatı',
                                                    f'{selected_group_title} İşçilik',
                                                    f'{selected_group_title} - İşçilik Maliyeti Akışı',
                                                    max_targets=30,
                                                    height=400
                                                )
                                                if fig_group_sankey_iscilik is not None:
                                                    st.plotly_chart(fig_group_sankey_iscilik, use_container_width=True)
                                                else:
                                                    st.info("İşçilik Sankey grafiği için veri bulunamadı.")

                                            # Min/Max analizi
                                            render_subsection_heading("Minimum ve Maximum Değerler", icon="")
                                            col_high, col_low = st.columns(2)
                                            with col_high:
                                                st.write("** En Yüksek Değerler:**")
                                                max_row = group_detail.loc[group_detail['Genel Toplam'].fillna(0).idxmax()]
                                                st.write(f"• Genel Toplam: {format_currency(max_row['Genel Toplam'])} ({max_row['Sayfa']} - Satır {max_row['Satır']})")
                                                max_malzeme_row = group_detail.loc[group_detail['Malzeme Fiyatı'].fillna(0).idxmax()]
                                                st.write(f"• Malzeme: {format_currency(max_malzeme_row['Malzeme Fiyatı'])} ({max_malzeme_row['Sayfa']} - Satır {max_malzeme_row['Satır']})")
                                            with col_low:
                                                st.write("** En Düşük Değerler:**")
                                                min_row = group_detail.loc[group_detail['Genel Toplam'].fillna(0).idxmin()]
                                                st.write(f"• Genel Toplam: {format_currency(min_row['Genel Toplam'])} ({min_row['Sayfa']} - Satır {min_row['Satır']})")
                                                min_malzeme_row = group_detail.loc[group_detail['Malzeme Fiyatı'].fillna(0).idxmin()]
                                                st.write(f"• Malzeme: {format_currency(min_malzeme_row['Malzeme Fiyatı'])} ({min_malzeme_row['Sayfa']} - Satır {min_malzeme_row['Satır']})")

                                            # Pareto analizi
                                            render_subsection_heading("Pareto Analizi (80/20 Kuralı)", icon="")
                                            pareto_data = group_detail_sorted[['Ürün Açıklaması', 'Genel Toplam', 'Kümülâtif Genel %']].copy()
                                            if len(pareto_data) > 0:
                                                fig_group_pareto = px.bar(
                                                    pareto_data,
                                                    x='Ürün Açıklaması',
                                                    y='Genel Toplam',
                                                    title=f'{selected_group_title} - Pareto Analizi (80/20)',
                                                    hover_data=['Kümülâtif Genel %'],
                                                    color='Genel Toplam',
                                                    color_continuous_scale='viridis'
                                                )
                                                fig_group_pareto.update_layout(
                                                    xaxis_tickangle=45,
                                                    height=500,
                                                    margin=dict(l=60, r=60, t=80, b=150)
                                                )
                                                st.plotly_chart(fig_group_pareto, use_container_width=True)

                                                items_80_percent = len(pareto_data[pareto_data['Kümülâtif Genel %'] <= 80])
                                                if items_80_percent > 0:
                                                    st.info(f" **80/20 Analizi:** Bu grupta toplam maliyetin %80'i **{items_80_percent} kalem** tarafından oluşturuluyor. (Toplam {len(pareto_data)} kalem)")
                                                else:
                                                    st.info(" **80/20 Analizi:** İlk kalem zaten %80'in üzerinde maliyet oluşturuyor.")
                                            else:
                                                st.info("Pareto analizi için yeterli veri bulunmuyor.")
                                        else:
                                            st.warning(f"Seçilen grup '{selected_group_title}' için veri bulunamadı.")
                            else:
                                st.info("Veri bulunamadı.")
                        else:
                            if page_mode == "Tutarlılık ve Geçmiş Kıyas":
                                st.info(" Tutarlılık kıyası için yan panelden en az bir maliyet sayfası seçin.")
                            else:
                                st.info(" Maliyet analizi için yan panelden en az bir sayfa seçin.")

                        # =====================================================
                        # GENEL GİDER ANALİZ BÖLÜMÜ
                        # =====================================================
                        if genel_gider_enabled:
                            st.markdown("---")
                            st.markdown("""
                            <div style="
                                margin: 20px auto 40px auto;
                                max-width: 1000px;
                                padding: 45px 50px;
                                background: linear-gradient(135deg, #059669, #10b981, #34d399);
                                border: 5px solid #10b981;
                                border-radius: 30px;
                                text-align: center;
                                box-shadow: 0 15px 40px rgba(16,185,129,0.4);
                                position: relative;
                                overflow: hidden;
                            ">
                                <div style="
                                    position: absolute;
                                    top: 0;
                                    left: 0;
                                    right: 0;
                                    height: 6px;
                                    background: linear-gradient(90deg, #fbbf24, #f59e0b, #d97706);
                                "></div>
                                <div style="
                                    font-family: 'Segoe UI', 'Inter', sans-serif;
                                    font-size: 26px;
                                    font-weight: 800;
                                    color: #ffffff;
                                    text-transform: uppercase;
                                    letter-spacing: 2px;
                                    text-shadow: 0 4px 10px rgba(0,0,0,0.6);
                                    line-height: 1.1;
                                ">ğŸ’° Genel Gider Analizi</div>
                            </div>
                            """, unsafe_allow_html=True)

                            try:
                                # Para formatı fonksiyonu
                                def format_currency_gider(value):
                                    if pd.isna(value) or value == 0:
                                        return "0,00 TL"
                                    return f"{value:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")

                                # Genel Gider Analiz sayfasını oku
                                gider_df = pd.read_excel(uploaded_file, sheet_name=genel_gider_sheet_name)

                                # A: Kategori, B: Gider Adı, C: Maliyet
                                if len(gider_df.columns) >= 3:
                                    # Sütun isimlerini belirle
                                    gider_df.columns = ['Kategori', 'Gider Adı', 'Maliyet'] + list(gider_df.columns[3:])

                                    # Sadece maliyet değeri olan satırları filtrele
                                    gider_df_filtered = gider_df[pd.to_numeric(gider_df['Maliyet'], errors='coerce').notna()].copy()
                                    gider_df_filtered['Maliyet'] = pd.to_numeric(gider_df_filtered['Maliyet'], errors='coerce')

                                    # Sıfır ve negatif maliyetleri de filtrele
                                    gider_df_filtered = gider_df_filtered[gider_df_filtered['Maliyet'] > 0]

                                    if len(gider_df_filtered) > 0:
                                        # Toplam maliyet
                                        toplam_gider_maliyet = gider_df_filtered['Maliyet'].sum()

                                        # Yüzdelik hesapla
                                        gider_df_filtered['Maliyet %'] = (gider_df_filtered['Maliyet'] / toplam_gider_maliyet * 100).round(2)

                                        # Maliyete göre sırala (büyükten küçüğe)
                                        gider_df_sorted = gider_df_filtered.sort_values('Maliyet', ascending=False).reset_index(drop=True)

                                        # Kümülatif yüzde hesapla
                                        gider_df_sorted['Kümülatif %'] = gider_df_sorted['Maliyet %'].cumsum().round(2)

                                        # İstatistikler
                                        col1, col2, col3, col4 = st.columns(4)

                                        with col1:
                                            st.markdown(f"""
                                            <div style="background: linear-gradient(135deg, #10b981, #059669); padding: 20px; border-radius: 15px; text-align: center; color: white;">
                                                <div style="font-size: 14px; opacity: 0.9;">Toplam Maliyet</div>
                                                <div style="font-size: 24px; font-weight: 800;">{format_currency_gider(toplam_gider_maliyet)}</div>
                                            </div>
                                            """, unsafe_allow_html=True)

                                        with col2:
                                            st.markdown(f"""
                                            <div style="background: linear-gradient(135deg, #3b82f6, #1e40af); padding: 20px; border-radius: 15px; text-align: center; color: white;">
                                                <div style="font-size: 14px; opacity: 0.9;">Gider Kalemi Sayısı</div>
                                                <div style="font-size: 24px; font-weight: 800;">{len(gider_df_sorted)}</div>
                                            </div>
                                            """, unsafe_allow_html=True)

                                        with col3:
                                            max_gider = gider_df_sorted.iloc[0]
                                            max_gider_adi = str(max_gider['Gider Adı'])[:30] if pd.notna(max_gider['Gider Adı']) else ''
                                            st.markdown(f"""
                                            <div style="background: linear-gradient(135deg, #ef4444, #dc2626); padding: 20px; border-radius: 15px; text-align: center; color: white;">
                                                <div style="font-size: 14px; opacity: 0.9;">En Yüksek Gider</div>
                                                <div style="font-size: 18px; font-weight: 800;">{format_currency_gider(max_gider['Maliyet'])}</div>
                                                <div style="font-size: 12px; opacity: 0.8;">{max_gider_adi}</div>
                                            </div>
                                            """, unsafe_allow_html=True)

                                        with col4:
                                            min_gider = gider_df_sorted.iloc[-1]
                                            min_gider_adi = str(min_gider['Gider Adı'])[:30] if pd.notna(min_gider['Gider Adı']) else ''
                                            st.markdown(f"""
                                            <div style="background: linear-gradient(135deg, #f59e0b, #d97706); padding: 20px; border-radius: 15px; text-align: center; color: white;">
                                                <div style="font-size: 14px; opacity: 0.9;">En Düşük Gider</div>
                                                <div style="font-size: 18px; font-weight: 800;">{format_currency_gider(min_gider['Maliyet'])}</div>
                                                <div style="font-size: 12px; opacity: 0.8;">{min_gider_adi}</div>
                                            </div>
                                            """, unsafe_allow_html=True)

                                        st.markdown("<br>", unsafe_allow_html=True)

                                        # ===== KATEGORİYE GÖRE ANALİZ =====
                                        render_subsection_heading("Kategoriye Göre Gider Dağılımı", icon="")

                                        # Kategoriye göre grupla
                                        kategori_grouped = gider_df_sorted.groupby('Kategori').agg({
                                            'Maliyet': 'sum',
                                            'Gider Adı': 'count'
                                        }).reset_index()
                                        kategori_grouped.columns = ['Kategori', 'Toplam Maliyet', 'Gider Sayısı']
                                        kategori_grouped['Maliyet %'] = (kategori_grouped['Toplam Maliyet'] / toplam_gider_maliyet * 100).round(2)
                                        kategori_grouped = kategori_grouped.sort_values('Toplam Maliyet', ascending=False)
                                        kategori_grouped['Kümülatif %'] = kategori_grouped['Maliyet %'].cumsum().round(2)

                                        col_chart1, col_chart2 = st.columns(2)

                                        with col_chart1:
                                            # Pasta grafik - Kategori dağılımı
                                            fig_pie_gider = px.pie(
                                                kategori_grouped,
                                                values='Toplam Maliyet',
                                                names='Kategori',
                                                title='Kategorilere Göre Maliyet Dağılımı',
                                                color_discrete_sequence=px.colors.qualitative.Set2
                                            )
                                            fig_pie_gider.update_traces(textposition='inside', textinfo='percent+label')
                                            fig_pie_gider.update_layout(height=400)
                                            st.plotly_chart(fig_pie_gider, use_container_width=True)

                                        with col_chart2:
                                            # Bar grafik - Kategori maliyetleri
                                            fig_bar_kat = px.bar(
                                                kategori_grouped,
                                                x='Kategori',
                                                y='Toplam Maliyet',
                                                title='Kategorilere Göre Toplam Maliyet',
                                                color='Maliyet %',
                                                color_continuous_scale='Greens',
                                                text='Maliyet %'
                                            )
                                            fig_bar_kat.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                                            fig_bar_kat.update_layout(height=400, xaxis_tickangle=45)
                                            st.plotly_chart(fig_bar_kat, use_container_width=True)

                                        # Kategori tablosu
                                        st.markdown("**Kategori Özet Tablosu:**")
                                        kategori_display = kategori_grouped.copy()
                                        kategori_display['Toplam Maliyet'] = kategori_display['Toplam Maliyet'].round(2)
                                        kategori_display['Maliyet %'] = kategori_display['Maliyet %'].round(2)
                                        kategori_display['Kümülatif %'] = kategori_display['Kümülatif %'].round(2)
                                        kategori_styler = kategori_display.style.format({
                                            'Toplam Maliyet': format_currency_display,
                                            'Maliyet %': format_percent_display,
                                            'Kümülatif %': format_percent_display
                                        }).hide(axis="index")
                                        st.dataframe(kategori_styler, use_container_width=True)

                                        st.markdown("<br>", unsafe_allow_html=True)

                                        # ===== GİDER ADINA GÖRE DETAYLI ANALİZ =====
                                        render_subsection_heading("Gider Kalemine Göre Detaylı Analiz", icon="")

                                        # En yüksekten en düşüğe sıralı tablo
                                        gider_display = gider_df_sorted[['Kategori', 'Gider Adı', 'Maliyet', 'Maliyet %', 'Kümülatif %']].copy()
                                        gider_display['Maliyet'] = gider_display['Maliyet'].round(2)
                                        gider_display['Maliyet %'] = gider_display['Maliyet %'].round(2)
                                        gider_display['Kümülatif %'] = gider_display['Kümülatif %'].round(2)
                                        gider_styler = gider_display.style.format({
                                            'Maliyet': format_currency_display,
                                            'Maliyet %': format_percent_display,
                                            'Kümülatif %': format_percent_display
                                        }).hide(axis="index")
                                        st.dataframe(gider_styler, use_container_width=True, height=400)

                                        # Pareto grafiği
                                        st.markdown("<br>", unsafe_allow_html=True)
                                        render_subsection_heading("Gider Pareto Analizi (80/20)", icon="ğŸ“Š")

                                        # Pareto için veri hazırla
                                        pareto_gider = gider_df_sorted.head(20).copy()  # İlk 20 kalem

                                        fig_pareto_gider = px.bar(
                                            pareto_gider,
                                            x='Gider Adı',
                                            y='Maliyet',
                                            title='Gider Kalemleri - Pareto Analizi (İlk 20)',
                                            color='Kümülatif %',
                                            color_continuous_scale='RdYlGn_r',
                                            hover_data=['Kategori', 'Maliyet %', 'Kümülatif %']
                                        )
                                        fig_pareto_gider.update_layout(
                                            xaxis_tickangle=45,
                                            height=500,
                                            margin=dict(l=60, r=60, t=80, b=150)
                                        )
                                        st.plotly_chart(fig_pareto_gider, use_container_width=True)

                                        # 80/20 analiz sonucu
                                        items_80_gider = len(gider_df_sorted[gider_df_sorted['Kümülatif %'] <= 80])
                                        if items_80_gider > 0:
                                            st.info(f" **80/20 Analizi:** Toplam giderlerin %80'i **{items_80_gider} kalem** tarafından oluşturuluyor. (Toplam {len(gider_df_sorted)} kalem)")
                                        else:
                                            st.info(" **80/20 Analizi:** İlk kalem zaten %80'in üzerinde maliyet oluşturuyor.")

                                        # En yüksek ve en düşük 5 gider
                                        col_top, col_bottom = st.columns(2)

                                        with col_top:
                                            st.markdown("** En Yüksek 5 Gider:**")
                                            top5 = gider_df_sorted.head(5)[['Kategori', 'Gider Adı', 'Maliyet', 'Maliyet %']].copy()
                                            top5['Maliyet'] = top5['Maliyet'].round(2)
                                            top5['Maliyet %'] = top5['Maliyet %'].round(2)
                                            top5_styler = top5.style.format({
                                                'Maliyet': format_currency_display,
                                                'Maliyet %': format_percent_display
                                            }).hide(axis="index")
                                            st.dataframe(top5_styler, use_container_width=True)

                                        with col_bottom:
                                            st.markdown("** En Düşük 5 Gider:**")
                                            bottom5 = gider_df_sorted.tail(5)[['Kategori', 'Gider Adı', 'Maliyet', 'Maliyet %']].copy()
                                            bottom5['Maliyet'] = bottom5['Maliyet'].round(2)
                                            bottom5['Maliyet %'] = bottom5['Maliyet %'].round(2)
                                            bottom5_styler = bottom5.style.format({
                                                'Maliyet': format_currency_display,
                                                'Maliyet %': format_percent_display
                                            }).hide(axis="index")
                                            st.dataframe(bottom5_styler, use_container_width=True)

                                    else:
                                        st.warning("⚠ Genel Gider Analiz sayfasında maliyet değeri olan satır bulunamadı.")
                                else:
                                    st.error(" Genel Gider Analiz sayfası en az 3 sütun içermelidir (Kategori, Gider Adı, Maliyet).")

                            except Exception as e:
                                st.error(f" Genel Gider Analiz sayfası okunurken hata: {str(e)}")

                    else:
                        st.info("Ürün grupları listesi oluşturulamadı.")

                except Exception as e:
                    st.error(f" İSKONTOLAR sayfası okunurken hata: {str(e)}")

            else:
                st.error(" İSKONTOLAR sayfası bulunamadı. Maliyet analizi için bu sayfa gereklidir.")

        except Exception as e:
            st.error(f" Dosya okuma hatası: {str(e)}")
            st.info("Lütfen geçerli bir Excel dosyası yüklediğinizden emin olun.")

    else:
        st.info(" Başlamak için yan panelden bir Excel dosyası yükleyin.")

        st.markdown('<div class="section-title"> Nasıl Kullanılır?</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card">
        <div style="display: flex; flex-direction: column; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 12px;">
            <span style="background: linear-gradient(135deg, #3b82f6, #1e40af); color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">1</span>
            <div>
                <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px;">Dosya Yükleme</div>
                <div style="font-size: 19px; color: #475569;">Sol panelden Excel dosyanızı (.xlsx veya .xls) seçin</div>
            </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
            <span style="background: linear-gradient(135deg, #10b981, #059669); color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">2</span>
            <div>
                <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px;">Sayfa Seçimi</div>
                <div style="font-size: 19px; color: #475569;">Maliyet analizine dahil etmek istediğiniz sayfaları yan panelden işaretleyin</div>
            </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
            <span style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">3</span>
            <div>
                <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px;">Maliyet Analizi</div>
                <div style="font-size: 19px; color: #475569;">Ürün gruplarına göre detaylı maliyet analizi ve Pareto grafikleri görüntüleyin</div>
            </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
            <span style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">4</span>
            <div>
                <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px;">Fiyat Revizyon Kıyas</div>
                <div style="font-size: 19px; color: #475569;">Yeni ve eski iki Excel dosyasını yükleyip indirim/zam farklarını karşılaştırın</div>
            </div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
