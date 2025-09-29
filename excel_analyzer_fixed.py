import importlib
import subprocess
import sys

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from datetime import datetime
from pathlib import Path
from typing import Optional


AgGrid = None
GridOptionsBuilder = None
GridUpdateMode = None
DataReturnMode = None
JsCode = None
_aggrid_import_error = None
_auto_install_attempted = False
_auto_install_succeeded = False
_fpdf_import_error = None
_fpdf_auto_install_attempted = False
_fpdf_auto_install_succeeded = False
FPDF = None


def ensure_aggrid_loaded() -> None:
    global AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
    global _aggrid_import_error, _auto_install_attempted, _auto_install_succeeded

    if AgGrid is not None or _aggrid_import_error:
        return

    try:
        aggrid_module = importlib.import_module('st_aggrid')
    except ModuleNotFoundError:
        _auto_install_attempted = True
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', 'streamlit-aggrid'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            aggrid_module = importlib.import_module('st_aggrid')
            _auto_install_succeeded = True
        except Exception as exc:
            _aggrid_import_error = exc
            return

    AgGrid = aggrid_module.AgGrid
    GridOptionsBuilder = aggrid_module.GridOptionsBuilder
    GridUpdateMode = aggrid_module.GridUpdateMode
    DataReturnMode = aggrid_module.DataReturnMode
    JsCode = aggrid_module.JsCode


def ensure_fpdf_loaded() -> None:
    global FPDF, _fpdf_import_error, _fpdf_auto_install_attempted, _fpdf_auto_install_succeeded

    if FPDF is not None or _fpdf_import_error:
        return

    try:
        from fpdf import FPDF as _LoadedFPDF
        FPDF = _LoadedFPDF
    except ModuleNotFoundError:
        _fpdf_auto_install_attempted = True
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', 'fpdf2'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            from fpdf import FPDF as _LoadedFPDF
            FPDF = _LoadedFPDF
            _fpdf_auto_install_succeeded = True
        except Exception as exc:
            _fpdf_import_error = exc


ensure_aggrid_loaded()
ensure_fpdf_loaded()



def ensure_utf8_rendering() -> None:
    st.markdown(
        """
        <script>
        (function() {
            const ensureMeta = () => {
                const existing = document.querySelector('meta[charset]');
                if (existing) {
                    existing.setAttribute('charset', 'utf-8');
                } else {
                    const meta = document.createElement('meta');
                    meta.setAttribute('charset', 'utf-8');
                    document.head.appendChild(meta);
                }
            };

            const decodeText = (value) => {
                try {
                    return decodeURIComponent(escape(value));
                } catch (err) {
                    return value;
                }
            };

            const processNode = (node) => {
                if (!node) {
                    return;
                }
                if (node.nodeType === Node.TEXT_NODE) {
                    const updated = decodeText(node.nodeValue);
                    if (updated !== node.nodeValue) {
                        node.nodeValue = updated;
                    }
                } else if (node.nodeType === Node.ELEMENT_NODE) {
                    node.childNodes.forEach(processNode);
                }
            };

            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach(processNode);
                });
            });

            const run = () => {
                ensureMeta();
                processNode(document.body);
                observer.observe(document.body, { childList: true, subtree: true });
            };

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', run);
            } else {
                run();
            }

            window.addEventListener('load', () => {
                processNode(document.body);
            });
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

def load_local_css(path: str) -> None:
    try:
        with open(path, encoding='utf-8') as css_file:
            st.markdown(f'<style>{css_file.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f'CSS file not found: {path}')


FONT_SEARCH_PATHS = [
    Path(__file__).parent / "fonts" / "DejaVuSans.ttf",
    Path(__file__).with_name("DejaVuSans.ttf"),
    Path(r"C:\\Windows\\Fonts\\DejaVuSans.ttf"),
    Path(r"C:\\Windows\\Fonts\\arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
]

def format_currency(value) -> str:
    if value is None or (isinstance(value, (float, int)) and pd.isna(value)):
        return "0,00 TL"
    try:
        return f"{float(value):,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value) -> str:
    if value is None or (isinstance(value, (float, int)) and pd.isna(value)):
        return "0%"
    try:
        return f"{float(value):.2f}%".replace(".", ",")
    except (ValueError, TypeError):
        return str(value)

def safe_text(text_value: object) -> str:
    if text_value is None:
        return ""
    if isinstance(text_value, (float, np.floating)) and np.isnan(text_value):
        return ""
    return str(text_value)

def find_font_path() -> Optional[Path]:
    for candidate in FONT_SEARCH_PATHS:
        if candidate.exists():
            return candidate
    return None

def generate_pdf_report(
    summary_df: pd.DataFrame,
    totals: dict[str, str],
    *,
    selected_group: Optional[str] = None,
    group_detail: Optional[pd.DataFrame] = None,
    filters: Optional[dict[str, str]] = None,
) -> bytes:
    ensure_fpdf_loaded()
    if FPDF is None:
        raise RuntimeError("PDF olusturmak icin 'fpdf2' kutuphanesi bulunamadi. Terminalde 'pip install fpdf2' komutunu calistirip tekrar deneyin.")

    pdf = FPDF()
    font_path = find_font_path()
    font_family = "Helvetica"
    if font_path:
        pdf.add_font("DejaVu", "", str(font_path), uni=True)
        pdf.add_font("DejaVu", "B", str(font_path), uni=True)
        font_family = "DejaVu"

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font(font_family, "B", 16)
    pdf.cell(0, 10, safe_text("Excel Analiz Raporu"), ln=True, align="C")

    pdf.set_font(font_family, "", 10)
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(0, 6, safe_text(f"Oluturma Zamanı: {timestamp}"), ln=True)

    if filters:
        for label, value in filters.items():
            if value:
                pdf.cell(0, 6, safe_text(f"{label}: {value}"), ln=True)

    pdf.ln(4)
    pdf.set_font(font_family, "B", 12)
    pdf.cell(0, 8, safe_text("zet Metrikler"), ln=True)
    pdf.set_font(font_family, "", 10)
    for label, value in totals.items():
        pdf.cell(0, 6, safe_text(f"{label}: {value}"), ln=True)

    pdf.ln(4)
    pdf.set_font(font_family, "B", 12)
    pdf.cell(0, 8, safe_text("Ürün Grubu Analizi"), ln=True)
    pdf.set_font(font_family, "", 10)

    for _, row in summary_df.iterrows():
        pdf.set_font(font_family, "B", 11)
        pdf.cell(0, 6, safe_text(str(row["Ürün Grubu"])), ln=True)
        pdf.set_font(font_family, "", 10)
        pdf.multi_cell(
            0,
            6,
            safe_text(
                " | ".join(
                    [
                        f"Genel: {format_currency(row['Genel Toplam'])}",
                        f"Malzeme: {format_currency(row['Malzeme Fiyatı'])}",
                        f"İçilik: {format_currency(row['İçilik Fiyatı'])}",
                        f"GGK: {format_currency(row['GGK Fiyatı'])}",
                    ]
                )
            ),
        )
        pdf.multi_cell(
            0,
            6,
            safe_text(
                " | ".join(
                    [
                        f"Genel %: {format_percentage(row['Genel Toplam %'])}",
                        f"Kümülatif %: {format_percentage(row['Kümülatif Genel %'])}",
                        f"Malzeme %: {format_percentage(row['Malzeme %'])}",
                        f"İçilik %: {format_percentage(row['İçilik %'])}",
                        f"GGK %: {format_percentage(row['GGK %'])}",
                    ]
                )
            ),
        )
        pdf.cell(
            0,
            6,
            safe_text(f"Kayıt Sayısı: {int(row['Bulunan Kayıt Sayısı'])}"),
            ln=True,
        )
        pdf.ln(1)

    if selected_group and group_detail is not None and not group_detail.empty:
        pdf.ln(2)
        pdf.set_font(font_family, "B", 12)
        pdf.cell(0, 8, safe_text(f"{selected_group} - Detaylı Kayıtlar"), ln=True)
        pdf.set_font(font_family, "", 10)

        top_items = group_detail.sort_values(by="Genel Toplam", ascending=False).head(10)
        pdf.cell(0, 6, safe_text("En yüksek maliyetli ilk 10 kalem:"), ln=True)
        for _, detail_row in top_items.iterrows():
            pdf.multi_cell(
                0,
                6,
                safe_text(
                    f"{detail_row.get('Ürün Açıklaması', '')} | "
                    f"Genel: {format_currency(detail_row.get('Genel Toplam', 0))} | "
                    f"Malzeme: {format_currency(detail_row.get('Malzeme Fiyatı', 0))} | "
                    f"İçilik: {format_currency(detail_row.get('İçilik Fiyatı', 0))}"
                ),
            )

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return output


st.set_page_config(page_title="Excel Analiz Uygulaması", layout="wide")

# CSS stil tanımlamaları
load_local_css('styles.css')

def create_aggrid_table(dataframe, height=400, selection_mode='single', fit_columns_on_grid_load=True):
    """AgGrid tablosu oluturma fonksiyonu"""
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_pagination(enabled=False)  # Sayfalama tamamen kapalı
    gb.configure_side_bar()
    gb.configure_selection(selection_mode, use_checkbox=False)
    gb.configure_default_column(
        groupable=True,
        value=True,
        enableRowGroup=True,
        aggFunc='sum',
        editable=False,
        sortable=True,
        filter=True,
        resizable=True,
        floatingFilter=False
    )

    gb.configure_grid_options(
        animateRows=True,
        rowHeight=38,
        headerHeight=56,
        suppressScrollOnNewData=True
    )

    # Para kolonları için özel format
    price_columns = ['Malzeme Fiyatı', 'İçilik Fiyatı', 'GGK Fiyatı', 'Genel Toplam']
    for col in price_columns:
        if col in dataframe.columns:
            gb.configure_column(col, type=["numericColumn"],
                              cellStyle={'textAlign': 'right', 'fontWeight': 'bold'})

    # Yüzde kolonları için format
    percent_columns = [col for col in dataframe.columns if '%' in col]
    for col in percent_columns:
        gb.configure_column(col, type=["numericColumn"],
                          cellStyle={'textAlign': 'center', 'color': '#0066cc'})

    gridOptions = gb.build()

    return AgGrid(
        dataframe,
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        height=height,
        theme='streamlit',
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True,
        custom_css={
            ".ag-theme-streamlit": {
                "height": f"{height}px !important",
                "box-sizing": "border-box !important",
                "--ag-background-color": "#f8fafc",
                "--ag-odd-row-background-color": "#eef2ff",
                "--ag-header-background-color": "#f1f5f9",
                "--ag-border-color": "#d8dee9",
                "--ag-font-size": "13px",
                "--ag-font-family": "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
            },
            ".ag-header": {
                "height": "56px !important",
                "border-bottom": "1px solid #d0d7e2 !important"
            },
            ".ag-header-cell": {
                "display": "flex !important",
                "align-items": "center !important",
                "justify-content": "center !important",
                "padding": "0 12px !important",
                "text-transform": "uppercase",
                "letter-spacing": "0.04em",
                "font-weight": "600"
            },
            ".ag-header-cell-text": {
                "color": "#1f2937 !important"
            },
            ".ag-body-viewport": {
                "overflow-y": "scroll !important",
                "overflow-x": "auto !important",
                "height": f"{height-120}px !important",
                "max-height": f"{height-120}px !important"
            },
            ".ag-row": {
                "height": "38px !important",
                "border-bottom": "1px solid #e5e7eb !important"
            },
            ".ag-row-hover": {
                "background-color": "#e2e8f0 !important"
            },
            ".ag-row-selected": {
                "background-color": "#bfdbfe !important",
                "color": "#1f2937 !important"
            },
            ".ag-cell": {
                "display": "flex !important",
                "align-items": "center !important",
                "padding": "0 12px !important",
                "color": "#0f172a !important"
            },
            ".ag-body-vertical-scroll": {
                "width": "14px !important"
            },
            ".ag-body-horizontal-scroll": {
                "height": "14px !important"
            }
        }
    )

def main():
    if _aggrid_import_error:
        st.error('Gerekli `streamlit-aggrid` kutuphanesi yuklenemedi.')
        st.info('Terminalde `pip install streamlit-aggrid` komutunu calistirdiktan sonra uygulamayi yeniden baslatin.')
        st.stop()

    if _auto_install_succeeded:
        st.success('Eksik `streamlit-aggrid` paketi otomatik olarak yuklendi.')

    if _fpdf_import_error:
        st.error('Gerekli `fpdf2` kutuphanesi yuklenemedi.')
        st.info('Terminalde `pip install fpdf2` komutunu calistirdiktan sonra uygulamayi yeniden baslatin.')
        st.stop()

    if _fpdf_auto_install_succeeded:
        st.success('Eksik `fpdf2` paketi otomatik olarak yuklendi.')

    ensure_utf8_rendering()

    st.markdown('<h1 class="main-title">🔬 Excel Analiz Uygulaması</h1>', unsafe_allow_html=True)
    st.markdown("Excel dosyanızı yükleyip sayfalarını göÜrüntüleyin ve analiz yapın.")

    # Sidebar
    st.sidebar.header("Dosya Yükleme")
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

            st.success(f" Dosya baarıyla yüklendi! ({len(sheet_names)} sayfa bulundu)")

            # Ana sekmeleri olutur

            st.markdown('<h2 class="section-title">📊 Ürün Gruplarına Göre Maliyet Analizi</h2>', unsafe_allow_html=True)

            # İSKONTOLAR sayfasından üÜrün gruplarını okuma
            if "İSKONTOLAR" in sheet_names:
                try:
                    # İSKONTOLAR sayfasını oku
                    iskontolar_df = pd.read_excel(uploaded_file, sheet_name="İSKONTOLAR")

                    # F3:F27 aralığından üÜrün gruplarını al (Excel'de F sütunu index 5)
                    # pandas'ta satır indexi 0'dan balar, Excel'de 3. satır pandas'ta index 2
                    product_groups = []
                    for i in range(2, 27):  # F3:F27 -> index 2:26
                        if i < len(iskontolar_df) and len(iskontolar_df.columns) > 5:
                            value = iskontolar_df.iloc[i, 5]  # F sütunu (index 5)
                            if pd.notna(value) and str(value).strip():  # Bo olmayan hücreler
                                product_groups.append(str(value).strip())

                    if product_groups:
                        st.write(f"**Bulunan Ürün Grupları ({len(product_groups)} adet):**")
                        st.write(", ".join(product_groups))

                        # Maliyet analizi için sayfa seçimi
                        st.sidebar.header("Maliyet Analizi - Sayfa Seçimi")
                        cost_analysis_sheets = []

                        # İSKONTOLAR sayfasını hariç tut
                        available_sheets = [s for s in sheet_names if s != "İSKONTOLAR"]

                        for sheet in available_sheets:
                            if st.sidebar.checkbox(sheet, key=f"cost_sheet_{sheet}"):
                                cost_analysis_sheets.append(sheet)

                        if cost_analysis_sheets:
                            # Tüm sayfalardan veriyi tek tabloda topla
                            all_data = []

                            # Seçilen sayfaları analiz et
                            for sheet_name in cost_analysis_sheets:
                                try:
                                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

                                    if len(df.columns) > 30:  # Yeterli sütun olduunu kontrol et
                                        for idx, row in df.iterrows():
                                            # C sütunu (index 2) üÜrün grubu
                                            if pd.notna(row.iloc[2]):
                                                product_group = str(row.iloc[2]).strip()

                                                if product_group in product_groups:
                                                    # Veri satırını kaydet
                                                    data_row = {
                                                        'Ürün Grubu': product_group,
                                                        'Sayfa': sheet_name,
                                                        'Satır': idx + 1,  # Excel satır numarası (1'den balar)
                                                        'Ürün Açıklaması': str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else '',  # D sütunu (index 3)
                                                        'Malzeme Fiyatı': float(row.iloc[20]) if len(row) > 20 and pd.notna(row.iloc[20]) else 0,
                                                        'İçilik Fiyatı': float(row.iloc[22]) if len(row) > 22 and pd.notna(row.iloc[22]) else 0,
                                                        'GGK Fiyatı': float(row.iloc[28]) if len(row) > 28 and pd.notna(row.iloc[28]) else 0,
                                                        'Genel Toplam': float(row.iloc[30]) if len(row) > 30 and pd.notna(row.iloc[30]) else 0
                                                    }
                                                    all_data.append(data_row)

                                except Exception as e:
                                    st.warning(f"️ {sheet_name} sayfası analiz edilirken hata: {str(e)}")

                            if all_data:
                                # Tüm veriler tablosu
                                all_df = pd.DataFrame(all_data)

                                # Para formatı uygulama fonksiyonu
                                # (global format_currency fonksiyonu kullanılıyor)

                                # Detay tablosunu formatla
                                all_df_display = all_df.copy()
                                price_columns = ['Malzeme Fiyatı', 'İçilik Fiyatı', 'GGK Fiyatı', 'Genel Toplam']
                                for col in price_columns:
                                    all_df_display[col] = all_df_display[col].apply(format_currency)

                                # Ürün gruplarına göre toplam hesaplama
                                summary_data = all_df.groupby('Ürün Grubu').agg({
                                    'Malzeme Fiyatı': 'sum',
                                    'İçilik Fiyatı': 'sum',
                                    'GGK Fiyatı': 'sum',
                                    'Genel Toplam': 'sum',
                                    'Sayfa': 'count'  # Kayıt sayısı
                                }).reset_index()

                                summary_data.rename(columns={'Sayfa': 'Bulunan Kayıt Sayısı'}, inplace=True)

                                # Yüzde hesaplamaları için toplam değerleri al
                                total_malzeme = summary_data['Malzeme Fiyatı'].sum()
                                total_iscilik = summary_data['İçilik Fiyatı'].sum()
                                total_ggk = summary_data['GGK Fiyatı'].sum()
                                total_genel = summary_data['Genel Toplam'].sum()

                                # Genel toplam bazında sıralama
                                summary_data = summary_data.sort_values('Genel Toplam', ascending=False)

                                # Tekil yüzdeler
                                summary_data['Genel Toplam %'] = (summary_data['Genel Toplam'] / total_genel * 100).round(2)
                                summary_data['Kümülatif Genel %'] = (summary_data['Genel Toplam'].cumsum() / total_genel * 100).round(2)
                                summary_data['Malzeme %'] = (summary_data['Malzeme Fiyatı'] / total_malzeme * 100).round(2)
                                summary_data['İçilik %'] = (summary_data['İçilik Fiyatı'] / total_iscilik * 100).round(2)
                                summary_data['GGK %'] = (summary_data['GGK Fiyatı'] / total_ggk * 100).round(2)

                                # Sütun sırasını yeniden düzenle
                                summary_data = summary_data[['Ürün Grubu', 'Genel Toplam', 'Genel Toplam %', 'Kümülatif Genel %',
                                                           'Malzeme Fiyatı', 'Malzeme %', 'İçilik Fiyatı', 'İçilik %',
                                                           'GGK Fiyatı', 'GGK %', 'Bulunan Kayıt Sayısı']]

                                results_df = summary_data

                                # zet tablosunu formatla
                                results_df_display = results_df.copy()
                                for col in price_columns:
                                    results_df_display[col] = results_df_display[col].apply(format_currency)

                                # Yüzde sütunlarına % sembolü ekle
                                percent_columns = [col for col in results_df_display.columns if '%' in col]
                                for col in percent_columns:
                                    results_df_display[col] = results_df_display[col].astype(str) + '%'

                                st.markdown('<h3 class="subsection-title">📊 Maliyet Analizi Sonuçları</h3>', unsafe_allow_html=True)

                                # Tablo gösterimi - AgGrid
                                create_aggrid_table(results_df_display, height=500)

                                # Görselletirme
                                st.markdown('<h3 class="subsection-title">📈 Maliyet Dağılımı Grafikleri</h3>', unsafe_allow_html=True)

                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    # Ürün gruplarına göre genel toplam
                                    fig_total = px.bar(results_df,
                                                     x='Ürün Grubu',
                                                     y='Genel Toplam',
                                                     title='Ürün Gruplarına Göre Genel Toplam')
                                    fig_total.update_layout(xaxis_tickangle=45)
                                    st.plotly_chart(fig_total, use_container_width=True)

                                with col2:
                                    # Maliyet türlerinin karılatırması
                                    fig_comparison = px.bar(results_df,
                                                          x='Ürün Grubu',
                                                          y=['Malzeme Fiyatı', 'İçilik Fiyatı', 'GGK Fiyatı'],
                                                          title='Maliyet Türleri Karılatırması')
                                    fig_comparison.update_layout(xaxis_tickangle=45)
                                    st.plotly_chart(fig_comparison, use_container_width=True)

                                # Treemap grafikleri
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    # Genel toplam treemap
                                    fig_treemap_total = px.treemap(results_df,
                                                                  path=['Ürün Grubu'],
                                                                  values='Genel Toplam',
                                                                  title='Genel Toplam - Treemap')
                                    st.plotly_chart(fig_treemap_total, use_container_width=True)

                                with col2:
                                    # Malzeme fiyatı treemap
                                    fig_treemap_malzeme = px.treemap(results_df,
                                                                    path=['Ürün Grubu'],
                                                                    values='Malzeme Fiyatı',
                                                                    title='Malzeme Fiyatları - Treemap')
                                    st.plotly_chart(fig_treemap_malzeme, use_container_width=True)

                                with col3:
                                    # Iscilik fiyati treemap
                                    fig_treemap_iscilik = px.treemap(
                                        results_df,
                                        path=[results_df.columns[0]],
                                        values=price_columns[1],
                                        title='Iscilik Fiyatlari - Treemap'
                                    )
                                    st.plotly_chart(fig_treemap_iscilik, use_container_width=True)

                                # zet bilgiler
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    total_malzeme = results_df['Malzeme Fiyatı'].sum()
                                    st.metric("Toplam Malzeme", f"{total_malzeme:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
                                with col2:
                                    total_iscilik = results_df['İçilik Fiyatı'].sum()
                                    st.metric("Toplam İçilik", f"{total_iscilik:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
                                with col3:
                                    total_ggk = results_df['GGK Fiyatı'].sum()
                                    st.metric("Toplam GGK", f"{total_ggk:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
                                with col4:
                                    total_genel = results_df['Genel Toplam'].sum()
                                    st.metric("Genel Toplam", f"{total_genel:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))

                                # Genel 80/20 Analizi - Tüm Ürünler
                                st.divider()
                                st.markdown('<h3 class="subsection-title">🎯 Genel Pareto Analizi (80/20)</h3>', unsafe_allow_html=True)

                                # Tüm üÜrünleri genel toplam bazında sırala
                                all_products_sorted = all_df.sort_values('Genel Toplam', ascending=False).copy()

                                # Tüm üÜrünler için kümülatif yüzde hesapla
                                total_all_products = all_products_sorted['Genel Toplam'].sum()
                                all_products_sorted['Kümülatif %'] = (all_products_sorted['Genel Toplam'].cumsum() / total_all_products * 100).round(2)

                                # İlk 20 üÜrünü al
                                top_20_products = all_products_sorted.head(20).copy()

                                color_palette = px.colors.qualitative.Safe
                                unique_groups = top_20_products['Ürün Grubu'].dropna().unique()
                                group_colors = {group: color_palette[idx % len(color_palette)] for idx, group in enumerate(unique_groups)}

                                st.markdown('<h3 class="subsection-title">🏆 En Yüksek Maliyetli İlk 20 Ürün</h3>', unsafe_allow_html=True)

                                for rank, item in enumerate(top_20_products.to_dict('records'), start=1):
                                    group = item['Ürün Grubu']
                                    color = group_colors.get(group, "#e5e7eb")
                                    formatted_total = format_currency(item['Genel Toplam'])
                                    kum_percent = f"{item['Kümülatif %']:.2f}%"
                                    st.markdown(
                                        f'''
<div style="background-color:{color}20; border-left:6px solid {color}; padding:12px 16px; border-radius:10px; margin-bottom:12px;">
  <div style="font-weight:700; font-size:16px; color:#111827;">{rank}. {item['Ürün Açıklaması']}</div>
  <div style="font-size:13px; color:#374151; margin-top:6px;">
    <strong>Grup:</strong> {group} &middot; <strong>Sayfa:</strong> {item['Sayfa']} &middot; <strong>Satır:</strong> {item['Satır']}
  </div>
  <div style="font-size:13px; color:#1f2937; margin-top:4px;">
    <strong>Genel Toplam:</strong> {formatted_total} &middot; <strong>Kümülatif %:</strong> {kum_percent}
  </div>
</div>
''',
                                        unsafe_allow_html=True,
                                    )

                                # 80% analizi özeti - Tüm üÜrünler için
                                items_80_percent_all = len(all_products_sorted[all_products_sorted['Kümülatif %'] <= 80])
                                if items_80_percent_all > 0:
                                    st.info(f" **80/20 Analizi:** Toplam maliyetin %80'i **{items_80_percent_all} üÜrün** tarafından oluşturuluyor. (Toplam {len(all_products_sorted)} üÜrün)")
                                else:
                                    st.info(" **80/20 Analizi:** İlk üÜrün zaten %80'in üzerinde maliyet oluturuyor.")

                                # Ürün grubu detay analizi
                                st.divider()
                                st.markdown('<h3 class="subsection-title">🔍 Ürün Grubu Detay Analizi</h3>', unsafe_allow_html=True)

                                # Ürün grubu seçimi
                                available_groups = list(results_df['Ürün Grubu'].unique())
                                selected_group = st.selectbox(
                                    "Detayını görmek istediğiniz üÜrün grubunu seçin:",
                                    ["Grup seçin..."] + available_groups,
                                    key="group_detail_select"
                                )

                                if selected_group != "Grup seçin...":
                                    # Seçilen grubun detaylarını filtrele
                                    group_detail = all_df[all_df['Ürün Grubu'] == selected_group].copy()

                                    st.write(f"** {selected_group} - Detaylı Analiz ({len(group_detail)} kayıt):**")

                                    # Sıralama seçenekleri
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        sort_by = st.selectbox(
                                            "Sıralama kriteri:",
                                            ['Genel Toplam', 'Malzeme Fiyatı', 'İçilik Fiyatı', 'GGK Fiyatı'],
                                            key="sort_criteria"
                                        )
                                    with col2:
                                        sort_order = st.selectbox(
                                            "Sıralama yönü:",
                                            ['Yüksekten Düşüğe', 'Düşükten Yükseğe'],
                                            key="sort_order"
                                        )

                                    # Sıralama ilemi
                                    ascending = True if sort_order == 'Düşükten Yükseğe' else False
                                    group_detail_sorted = group_detail.sort_values(by=sort_by, ascending=ascending)

                                    group_detail_for_pdf = group_detail_sorted

                                    selected_group_for_pdf = selected_group

                                    # Yüzde hesaplamaları için toplam değerleri al
                                    total_malzeme_group = group_detail_sorted['Malzeme Fiyatı'].sum()
                                    total_iscilik_group = group_detail_sorted['İçilik Fiyatı'].sum()
                                    total_ggk_group = group_detail_sorted['GGK Fiyatı'].sum()
                                    total_genel_group = group_detail_sorted['Genel Toplam'].sum()

                                    # Tekil yüzdeler ekle
                                    group_detail_sorted['Malzeme %'] = (group_detail_sorted['Malzeme Fiyatı'] / total_malzeme_group * 100).round(2)
                                    group_detail_sorted['İçilik %'] = (group_detail_sorted['İçilik Fiyatı'] / total_iscilik_group * 100).round(2)
                                    group_detail_sorted['GGK %'] = (group_detail_sorted['GGK Fiyatı'] / total_ggk_group * 100).round(2)
                                    group_detail_sorted['Genel Toplam %'] = (group_detail_sorted['Genel Toplam'] / total_genel_group * 100).round(2)

                                    # Kümülatif yüzdeler ekle
                                    group_detail_sorted['Kümülatif Malzeme %'] = (group_detail_sorted['Malzeme Fiyatı'].cumsum() / total_malzeme_group * 100).round(2)
                                    group_detail_sorted['Kümülatif İçilik %'] = (group_detail_sorted['İçilik Fiyatı'].cumsum() / total_iscilik_group * 100).round(2)
                                    group_detail_sorted['Kümülatif GGK %'] = (group_detail_sorted['GGK Fiyatı'].cumsum() / total_ggk_group * 100).round(2)
                                    group_detail_sorted['Kümülatif Genel %'] = (group_detail_sorted['Genel Toplam'].cumsum() / total_genel_group * 100).round(2)

                                    # Formatlanmı tablo
                                    group_detail_display = group_detail_sorted.copy()
                                    for col in price_columns:
                                        group_detail_display[col] = group_detail_display[col].apply(format_currency)

                                    # Yüzde sütunlarına % sembolü ekle
                                    percent_columns_group = [col for col in group_detail_display.columns if '%' in col]
                                    for col in percent_columns_group:
                                        group_detail_display[col] = group_detail_display[col].astype(str) + '%'

                                    create_aggrid_table(group_detail_display, height=350)

                                    # Grup istatistikleri
                                    st.write(f"** {selected_group} - İstatistikler:**")
                                    col1, col2, col3, col4 = st.columns(4)

                                    with col1:
                                        total_malzeme_group = group_detail['Malzeme Fiyatı'].sum()
                                        st.metric("Malzeme Toplam", f"{total_malzeme_group:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))

                                    with col2:
                                        total_iscilik_group = group_detail['İçilik Fiyatı'].sum()
                                        st.metric("İçilik Toplam", f"{total_iscilik_group:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))

                                    with col3:
                                        total_ggk_group = group_detail['GGK Fiyatı'].sum()
                                        st.metric("GGK Toplam", f"{total_ggk_group:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))

                                    with col4:
                                        total_genel_group = group_detail['Genel Toplam'].sum()
                                        st.metric("Genel Toplam", f"{total_genel_group:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))

                                    # En yüksek ve en düük deerler
                                    col1, col2, col3 = st.columns(3)

                                    with col1:
                                        st.write("** En Yüksek Değerler:**")
                                        max_genel = group_detail['Genel Toplam'].max()
                                        max_row = group_detail[group_detail['Genel Toplam'] == max_genel].iloc[0]
                                        st.write(f" Genel Toplam: {format_currency(max_genel)} ({max_row['Sayfa']} - Satır {max_row['Satır']})")

                                        max_malzeme = group_detail['Malzeme Fiyatı'].max()
                                        max_malzeme_row = group_detail[group_detail['Malzeme Fiyatı'] == max_malzeme].iloc[0]
                                        st.write(f" Malzeme: {format_currency(max_malzeme)} ({max_malzeme_row['Sayfa']} - Satır {max_malzeme_row['Satır']})")

                                    with col2:
                                        st.write("** En Düşük Değerler:**")
                                        min_genel = group_detail['Genel Toplam'].min()
                                        min_row = group_detail[group_detail['Genel Toplam'] == min_genel].iloc[0]
                                        st.write(f" Genel Toplam: {format_currency(min_genel)} ({min_row['Sayfa']} - Satır {min_row['Satır']})")

                                        min_malzeme = group_detail['Malzeme Fiyatı'].min()
                                        min_malzeme_row = group_detail[group_detail['Malzeme Fiyatı'] == min_malzeme].iloc[0]
                                        st.write(f" Malzeme: {format_currency(min_malzeme)} ({min_malzeme_row['Sayfa']} - Satır {min_malzeme_row['Satır']})")

                                    # Pareto analizi grafii (80/20 analizi) - Sadece Bar Chart
                                    st.write(f"** {selected_group} - Pareto Analizi (80/20):**")

                                    # Pareto grafii için veri hazırlama
                                    pareto_data = group_detail_sorted[['Ürün Açıklaması', 'Genel Toplam', 'Kümülatif Genel %']].copy()

                                    if len(pareto_data) > 0:
                                        # Sadece Bar chart
                                        fig_pareto = px.bar(
                                            pareto_data,
                                            x='Ürün Açıklaması',
                                            y='Genel Toplam',
                                            title=f'{selected_group} - Pareto Analizi (Büyükten Küçüe)',
                                            hover_data=['Kümülatif Genel %']
                                        )

                                        fig_pareto.update_layout(
                                            xaxis_tickangle=45,
                                            height=500,
                                            margin=dict(l=60, r=60, t=80, b=150)
                                        )

                                        st.plotly_chart(fig_pareto, use_container_width=True)

                                        # 80% analizi özeti
                                        items_80_percent = len(pareto_data[pareto_data['Kümülatif Genel %'] <= 80])
                                        if items_80_percent > 0:
                                            st.info(f" **80/20 Analizi:** Bu grupta toplam maliyetin %80'i **{items_80_percent} kalem** tarafından oluşturuluyor. (Toplam {len(pareto_data)} kalem)")
                                        else:
                                            st.info(" **80/20 Analizi:** İlk kalem zaten %80'in üzerinde maliyet oluturuyor.")

                                    else:
                                        st.info("Pareto analizi için yeterli veri bulunmuyor.")

                                else:
                                    st.info(" Detaylı analiz için bir üÜrün grubu seçin.")

                                pdf_filters = {
                                    "Dosya": getattr(uploaded_file, "name", ""),
                                    "Seçilen Sayfalar": ", ".join(cost_analysis_sheets),
                                }
                                try:
                                    pdf_bytes = generate_pdf_report(
                                        summary_df=results_df,
                                        totals={
                                            "Toplam Malzeme": format_currency(total_malzeme),
                                            "Toplam İçilik": format_currency(total_iscilik),
                                            "Toplam GGK": format_currency(total_ggk),
                                            "Genel Toplam": format_currency(total_genel),
                                        },
                                        selected_group=selected_group_for_pdf,
                                        group_detail=group_detail_for_pdf,
                                        filters={k: v for k, v in pdf_filters.items() if v},
                                    )
                                    st.download_button(
                                        " Analizi PDF Olarak İndir",
                                        data=pdf_bytes,
                                        file_name=f"excel_analiz_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True,
                                    )
                                except Exception as pdf_error:
                                    st.error(f"PDF oluturulurken hata olutu: {pdf_error}")


                                st.divider()
                                st.write("** Tüm Veriler Detayı:**")
                                create_aggrid_table(all_df_display, height=400)
                            else:
                                st.warning("️ Seçilen sayfalarda üÜrün grubu verisi bulunamadı.")

                        else:
                            st.info(" Maliyet analizi için yan panelden en az bir sayfa seçin.")

                    else:
                        st.warning("️ İSKONTOLAR sayfasının F4:F27 aralığında üÜrün grubu bulunamadı.")

                except Exception as e:
                    st.error(f" İSKONTOLAR sayfası okunurken hata: {str(e)}")

            else:
                st.error(" İSKONTOLAR sayfası bulunamadı. Maliyet analizi için bu sayfa gereklidir.")

        except Exception as e:
            st.error(f" Dosya okuma hatası: {str(e)}")
            st.info("Lütfen geçerli bir Excel dosyası yüklediinizden emin olun.")

    else:
        st.info(" Balamak için yan panelden bir Excel dosyası yükleyin.")

        st.markdown("###  Nasıl Kullanılır?")
        st.markdown("""
        1. **Dosya Yükleme:** Sol panelden Excel dosyanızı (.xlsx veya .xls) seçin
        2. **Maliyet Analizi:** Ürün gruplarına göre detaylı maliyet analizi yapın
        """)

if __name__ == "__main__":
    main()



