import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

PRICE_COLUMNS = ['Malzeme Fiyatı', 'İşçilik Fiyatı', 'GGK Fiyatı', 'Genel Toplam']

def format_currency_display(value):
    """Format numeric value as Turkish currency text for display without changing dtype."""
    if pd.isna(value):
        return ""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return str(value)
    if numeric_value == 0:
        return "0,00 TL"
    return f"{numeric_value:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percent_display(value):
    """Format numeric value as percent text for display without changing dtype."""
    if pd.isna(value):
        return ""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{numeric_value:.2f}%"

def normalize_excel_header_name(value):
    """Normalize Turkish column names for Excel style matching."""
    text = "" if value is None else str(value)
    tr_chars = {
        "ı": "i", "ğ": "g", "ü": "u", "ş": "s", "ö": "o", "ç": "c",
        "İ": "I", "Ğ": "G", "Ü": "U", "Ş": "S", "Ö": "O", "Ç": "C",
    }
    for tr, en in tr_chars.items():
        text = text.replace(tr, en)
    return text.upper().strip()

def prepare_dataframe_for_excel_export(dataframe):
    """Convert percent columns to fraction for native Excel % formatting."""
    export_df = dataframe.copy()
    percent_cols = [col for col in export_df.columns if "%" in str(col)]
    for col in percent_cols:
        numeric_series = pd.to_numeric(export_df[col], errors="coerce")
        valid_values = numeric_series.dropna()
        if valid_values.empty:
            continue
        if valid_values.abs().max() > 1:
            numeric_series = numeric_series / 100.0
        export_df[col] = numeric_series
    return export_df

def style_excel_sheet(worksheet):
    """Apply Excel-friendly formatting, colors, and fonts to exported sheets."""
    if worksheet.max_row < 1 or worksheet.max_column < 1:
        return

    header_default_fill = PatternFill(fill_type="solid", fgColor="7C3AED")
    thin_border = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB"),
    )
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    body_font = Font(name="Calibri", size=11, color="1F2937")
    body_font_bold = Font(name="Calibri", size=11, bold=True, color="111827")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_alignment = Alignment(horizontal="left", vertical="center")
    right_alignment = Alignment(horizontal="right", vertical="center")
    center_alignment = Alignment(horizontal="center", vertical="center")
    zebra_even_fill = PatternFill(fill_type="solid", fgColor="F8FAFC")
    zebra_odd_fill = PatternFill(fill_type="solid", fgColor="FFFFFF")

    palette = {
        "malzeme": {"header": "10B981", "body": "DCFCE7"},
        "iscilik": {"header": "3B82F6", "body": "DBEAFE"},
        "ggk": {"header": "8B5CF6", "body": "E9D5FF"},
        "genel": {"header": "EF4444", "body": "FEE2E2"},
        "grup": {"header": "6B7280", "body": "F3F4F6"},
    }

    worksheet.freeze_panes = "A2"
    worksheet.row_dimensions[1].height = 26

    max_col = worksheet.max_column
    max_row = worksheet.max_row

    for col_idx in range(1, max_col + 1):
        header_cell = worksheet.cell(row=1, column=col_idx)
        header_name = "" if header_cell.value is None else str(header_cell.value)
        normalized_header = normalize_excel_header_name(header_name)

        is_malzeme_col = "MALZEME" in normalized_header
        is_iscilik_col = "ISCILIK" in normalized_header
        is_ggk_col = "GGK" in normalized_header
        is_genel_col = ("GENEL TOPLAM" in normalized_header) or ("KUMULATIF GENEL" in normalized_header)
        is_group_col = "URUN GRUBU" in normalized_header
        is_percent_col = "%" in header_name
        is_currency_col = (
            any(token in normalized_header for token in ["MALZEME FIYATI", "ISCILIK FIYATI", "GGK FIYATI", "GENEL TOPLAM"])
            and not is_percent_col
        )
        is_integer_col = any(token in normalized_header for token in ["KAYIT SAYISI", "SIRA", "SATIR"])

        col_data_fill = None
        col_header_fill = header_default_fill
        if is_genel_col:
            col_header_fill = PatternFill(fill_type="solid", fgColor=palette["genel"]["header"])
            col_data_fill = PatternFill(fill_type="solid", fgColor=palette["genel"]["body"])
        elif is_malzeme_col:
            col_header_fill = PatternFill(fill_type="solid", fgColor=palette["malzeme"]["header"])
            col_data_fill = PatternFill(fill_type="solid", fgColor=palette["malzeme"]["body"])
        elif is_iscilik_col:
            col_header_fill = PatternFill(fill_type="solid", fgColor=palette["iscilik"]["header"])
            col_data_fill = PatternFill(fill_type="solid", fgColor=palette["iscilik"]["body"])
        elif is_ggk_col:
            col_header_fill = PatternFill(fill_type="solid", fgColor=palette["ggk"]["header"])
            col_data_fill = PatternFill(fill_type="solid", fgColor=palette["ggk"]["body"])
        elif is_group_col:
            col_header_fill = PatternFill(fill_type="solid", fgColor=palette["grup"]["header"])
            col_data_fill = PatternFill(fill_type="solid", fgColor=palette["grup"]["body"])

        header_cell.fill = col_header_fill
        header_cell.font = header_font
        header_cell.alignment = header_alignment
        header_cell.border = thin_border

        sample_last_row = min(max_row, 500)
        max_text_len = len(header_name)
        for row_idx in range(2, sample_last_row + 1):
            cell_value = worksheet.cell(row=row_idx, column=col_idx).value
            if cell_value is None:
                continue
            if isinstance(cell_value, (int, float, np.integer, np.floating)):
                cell_text = f"{cell_value:,.2f}"
            else:
                cell_text = str(cell_value)
            max_text_len = max(max_text_len, len(cell_text))

        min_width = 12
        if is_currency_col:
            min_width = 16
        elif is_percent_col:
            min_width = 14
        elif is_group_col:
            min_width = 20
        worksheet.column_dimensions[get_column_letter(col_idx)].width = min(max(max_text_len + 2, min_width), 45)

        for row_idx in range(2, max_row + 1):
            cell = worksheet.cell(row=row_idx, column=col_idx)
            worksheet.row_dimensions[row_idx].height = 20

            zebra_fill = zebra_even_fill if row_idx % 2 == 0 else zebra_odd_fill
            cell.fill = col_data_fill if col_data_fill is not None else zebra_fill
            cell.border = thin_border

            if is_group_col:
                cell.font = body_font_bold
            else:
                cell.font = body_font

            if is_percent_col:
                cell.number_format = "0.00%"
            elif is_currency_col:
                cell.number_format = '#,##0.00 "TL"'
            elif is_integer_col:
                cell.number_format = "#,##0"

            if is_currency_col or is_percent_col or is_integer_col:
                cell.alignment = right_alignment
            elif is_group_col or "URUN ACIKLAMASI" in normalized_header or "SAYFA" in normalized_header:
                cell.alignment = left_alignment
            else:
                cell.alignment = center_alignment

    worksheet.auto_filter.ref = worksheet.dimensions

def index_to_excel_column(index):
    """Convert zero-based column index to Excel column letter (A, B, AA)."""
    if index is None or index < 0:
        return "?"

    result = ""
    number = index + 1
    while number > 0:
        number, remainder = divmod(number - 1, 26)
        result = chr(ord('A') + remainder) + result
    return result

def get_sheet_columns(excel_file, sheet_name):
    """Read sheet columns robustly; fall back to positional columns if header row is empty."""
    try:
        header_df = excel_file.parse(sheet_name=sheet_name, nrows=0)
        columns = list(header_df.columns)
    except Exception as exc:
        return [], str(exc)

    if columns:
        return columns, None

    try:
        sample_df = excel_file.parse(sheet_name=sheet_name, header=None, nrows=1)
        col_count = int(sample_df.shape[1])
        if col_count > 0:
            return [f"Unnamed: {i}" for i in range(col_count)], None
    except Exception:
        pass

    return [], None

def derive_offer_code_from_filename(file_name):
    """Derive offer code from uploaded file name."""
    stem = Path(str(file_name)).stem.strip()
    if not stem:
        stem = f"TEKLIF-{datetime.now().strftime('%Y%m%d-%H%M')}"
    return stem

def get_offer_memory_paths():
    base_path = Path(__file__).resolve().parent
    return (
        base_path / "teklif_hafiza_grup.csv",
        base_path / "teklif_hafiza_urun.csv",
        base_path / "teklif_hafiza_sistem.csv",
    )

def load_memory_dataframe(file_path):
    if not Path(file_path).exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
    except Exception:
        return pd.DataFrame()

    for date_col in ["Teklif Tarihi", "Kayıt Zamanı"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    return df

def upsert_memory_dataframe(file_path, dataframe, key_columns):
    def build_row_keys(df, columns):
        key_frame = df.loc[:, columns].copy()
        if isinstance(key_frame, pd.Series):
            key_frame = key_frame.to_frame()
        key_frame = key_frame.fillna("").astype(str)
        return key_frame.apply(lambda row: "|".join(row.tolist()), axis=1)

    dataframe = dataframe.copy()
    key_columns = list(dict.fromkeys(key_columns))
    existing_df = load_memory_dataframe(file_path)
    if existing_df.empty:
        final_df = dataframe.copy()
    else:
        # Aynı dosya adıyla (Teklif Kodu) tekrar yüklenirse eski kaydı komple silip son yüklemeyi bırak.
        if "Teklif Kodu" in dataframe.columns:
            incoming_offer_codes = set(
                dataframe["Teklif Kodu"].astype(str).str.strip().replace("", np.nan).dropna().tolist()
            )
            if incoming_offer_codes and "Teklif Kodu" in existing_df.columns:
                existing_df = existing_df[
                    ~existing_df["Teklif Kodu"].astype(str).str.strip().isin(incoming_offer_codes)
                ].copy()

        for key_col in key_columns:
            if key_col not in existing_df.columns:
                existing_df[key_col] = ""
            if key_col not in dataframe.columns:
                dataframe[key_col] = ""
        existing_keys = build_row_keys(existing_df, key_columns)
        incoming_keys = build_row_keys(dataframe, key_columns)
        final_df = pd.concat(
            [
                existing_df[~existing_keys.isin(set(incoming_keys.tolist()))],
                dataframe
            ],
            ignore_index=True
        )
    final_df.to_csv(file_path, index=False, encoding="utf-8-sig")

def apply_context_filter(memory_df, bina_tipi, ana_cihaz_durumu, is_konumu, bina_alt_tipi=None):
    if memory_df.empty:
        return memory_df.copy()
    filtered_df = memory_df.copy()
    for col_name, selected_value in [
        ("Bina Tipi", bina_tipi),
        ("Bina Alt Tipi", bina_alt_tipi),
        ("Ana Cihaz Durumu", ana_cihaz_durumu),
        ("İş Konumu", is_konumu),
    ]:
        if selected_value is not None and col_name in filtered_df.columns:
            if col_name == "Bina Alt Tipi":
                col_text = filtered_df[col_name].astype(str).str.strip()
                filtered_df = filtered_df[(col_text == str(selected_value)) | (col_text == "") | (col_text.str.lower() == "nan")]
            else:
                filtered_df = filtered_df[filtered_df[col_name] == selected_value]
    return filtered_df

def normalize_sheet_name(name):
    return turkce_ascii(str(name)).upper().strip()

def get_cost_sheet_names(sheet_names):
    excluded = {"ISKONTOLAR", "GENEL GIDER ANALIZ"}
    return [sheet for sheet in sheet_names if normalize_sheet_name(sheet) not in excluded]

def map_sheet_names_by_normalized(sheet_names):
    mapping = {}
    for sheet in sheet_names:
        normalized = normalize_sheet_name(sheet)
        if normalized not in mapping:
            mapping[normalized] = sheet
    return mapping

def read_product_groups_from_iskontolar(
    excel_source,
    iskontolar_sheet_name,
    group_col_index,
    start_row,
    end_row,
):
    if not iskontolar_sheet_name:
        return []

    try:
        iskontolar_df = pd.read_excel(excel_source, sheet_name=iskontolar_sheet_name)
    except Exception:
        return []

    if group_col_index is None or group_col_index < 0:
        return []
    if len(iskontolar_df.columns) <= group_col_index:
        return []

    row_start = max(min(int(start_row), int(end_row)) - 1, 0)
    row_end = max(int(start_row), int(end_row))

    groups = []
    for i in range(row_start, row_end):
        if i >= len(iskontolar_df):
            continue
        value = iskontolar_df.iloc[i, group_col_index]
        if pd.isna(value):
            continue
        text = str(value).strip()
        if text and text.lower() != "nan":
            groups.append(text)
    return list(dict.fromkeys(groups))

def build_cost_dataframe_from_sheets(
    excel_source,
    sheet_names,
    allowed_product_groups,
    data_group_col_index,
    urun_aciklama_col_index,
    malzeme_col_index,
    iscilik_col_index,
    ggk_col_index,
    genel_toplam_col_index,
):
    all_data = []
    selected_indices = [
        data_group_col_index,
        urun_aciklama_col_index,
        malzeme_col_index,
        iscilik_col_index,
        ggk_col_index,
        genel_toplam_col_index,
    ]
    selected_indices = [idx for idx in selected_indices if idx is not None]
    if not selected_indices:
        return pd.DataFrame()

    required_max_col = max(selected_indices)
    allowed_set = set(allowed_product_groups or [])

    for sheet_name in sheet_names:
        try:
            df = pd.read_excel(excel_source, sheet_name=sheet_name)
        except Exception:
            continue

        if data_group_col_index is None or len(df.columns) <= required_max_col:
            continue

        for idx, row in df.iterrows():
            try:
                if pd.isna(row.iloc[data_group_col_index]):
                    continue
                product_group = str(row.iloc[data_group_col_index]).strip()
                if not product_group or product_group.lower() == "nan":
                    continue
                if allowed_set and product_group not in allowed_set:
                    continue

                all_data.append(
                    {
                        "Ürün Grubu": product_group,
                        "Sayfa": sheet_name,
                        "Satır": idx + 1,
                        "Ürün Açıklaması": str(row.iloc[urun_aciklama_col_index]).strip()
                        if len(row) > urun_aciklama_col_index and pd.notna(row.iloc[urun_aciklama_col_index])
                        else "",
                        "Malzeme Fiyatı": float(row.iloc[malzeme_col_index])
                        if len(row) > malzeme_col_index and pd.notna(row.iloc[malzeme_col_index])
                        else 0.0,
                        "İşçilik Fiyatı": float(row.iloc[iscilik_col_index])
                        if len(row) > iscilik_col_index and pd.notna(row.iloc[iscilik_col_index])
                        else 0.0,
                        "GGK Fiyatı": float(row.iloc[ggk_col_index])
                        if len(row) > ggk_col_index and pd.notna(row.iloc[ggk_col_index])
                        else 0.0,
                        "Genel Toplam": float(row.iloc[genel_toplam_col_index])
                        if len(row) > genel_toplam_col_index and pd.notna(row.iloc[genel_toplam_col_index])
                        else 0.0,
                    }
                )
            except Exception:
                continue

    return pd.DataFrame(all_data)

def render_price_revision_compare_module(
    new_file,
    old_file,
    selected_new_cost_sheets,
    iskontolar_group_col_index,
    iskontolar_start_row,
    iskontolar_end_row,
    data_group_col_index,
    urun_aciklama_col_index,
    malzeme_col_index,
    iscilik_col_index,
    ggk_col_index,
    genel_toplam_col_index,
):
    render_section_heading("Fiyat Revizyon Kıyas", icon="")
    st.caption("Yeni ve eski fiyat çalışması dosyaları satır/sayfa/ürün grubu bazında karşılaştırılır.")

    try:
        new_excel = pd.ExcelFile(new_file)
        old_excel = pd.ExcelFile(old_file)
    except Exception as exc:
        st.error(f"Dosyalar okunamadı: {str(exc)}")
        return

    new_sheet_map = map_sheet_names_by_normalized(new_excel.sheet_names)
    old_sheet_map = map_sheet_names_by_normalized(old_excel.sheet_names)

    requested_new_sheets = selected_new_cost_sheets if selected_new_cost_sheets else get_cost_sheet_names(new_excel.sheet_names)
    sheet_pairs = []
    missing_old_sheets = []
    for new_sheet in requested_new_sheets:
        normalized = normalize_sheet_name(new_sheet)
        if normalized in ("ISKONTOLAR", "GENEL GIDER ANALIZ"):
            continue
        old_sheet = old_sheet_map.get(normalized)
        if old_sheet:
            sheet_pairs.append((new_sheet, old_sheet))
        else:
            missing_old_sheets.append(new_sheet)

    if missing_old_sheets:
        st.warning(
            "Eski dosyada bulunamayan sayfalar kıyasa dahil edilmedi: "
            + ", ".join(missing_old_sheets[:8])
            + (" ..." if len(missing_old_sheets) > 8 else "")
        )

    if not sheet_pairs:
        st.error("Karşılaştırılacak ortak maliyet sayfası bulunamadı.")
        return

    new_iskontolar_sheet = new_sheet_map.get("ISKONTOLAR")
    old_iskontolar_sheet = old_sheet_map.get("ISKONTOLAR")

    new_groups = read_product_groups_from_iskontolar(
        new_file,
        new_iskontolar_sheet,
        iskontolar_group_col_index,
        iskontolar_start_row,
        iskontolar_end_row,
    )
    old_groups = read_product_groups_from_iskontolar(
        old_file,
        old_iskontolar_sheet,
        iskontolar_group_col_index,
        iskontolar_start_row,
        iskontolar_end_row,
    )

    if not new_groups:
        st.info("Yeni dosyada ISKONTOLAR ürün grupları bulunamadı. Maliyet sayfalarındaki tüm ürün grupları kullanılacak.")
    if not old_groups:
        st.info("Eski dosyada ISKONTOLAR ürün grupları bulunamadı. Maliyet sayfalarındaki tüm ürün grupları kullanılacak.")

    new_df = build_cost_dataframe_from_sheets(
        new_file,
        [new_sheet for new_sheet, _ in sheet_pairs],
        new_groups,
        data_group_col_index,
        urun_aciklama_col_index,
        malzeme_col_index,
        iscilik_col_index,
        ggk_col_index,
        genel_toplam_col_index,
    )
    old_df = build_cost_dataframe_from_sheets(
        old_file,
        [old_sheet for _, old_sheet in sheet_pairs],
        old_groups,
        data_group_col_index,
        urun_aciklama_col_index,
        malzeme_col_index,
        iscilik_col_index,
        ggk_col_index,
        genel_toplam_col_index,
    )

    if not new_df.empty:
        new_df["Sayfa"] = new_df["Sayfa"].apply(normalize_sheet_name)
    if not old_df.empty:
        old_df["Sayfa"] = old_df["Sayfa"].apply(normalize_sheet_name)

    if new_df.empty and old_df.empty:
        st.error("Her iki dosyada da karşılaştırılabilir maliyet satırı bulunamadı.")
        return

    key_cols = ["Ürün Grubu", "Sayfa", "Ürün Açıklaması"]
    cost_cols = ["Malzeme Fiyatı", "İşçilik Fiyatı", "GGK Fiyatı", "Genel Toplam"]

    def aggregate_for_compare(dataframe, prefix):
        output_cols = key_cols + [f"{prefix} Excel Satır No"] + [f"{prefix} {col}" for col in cost_cols]
        if dataframe.empty:
            return pd.DataFrame(columns=output_cols)
        aggregated = dataframe.groupby(key_cols, as_index=False).agg(
            {
                "Satır": "min",
                "Malzeme Fiyatı": "sum",
                "İşçilik Fiyatı": "sum",
                "GGK Fiyatı": "sum",
                "Genel Toplam": "sum",
            }
        )
        return aggregated.rename(
            columns={
                "Satır": f"{prefix} Excel Satır No",
                "Malzeme Fiyatı": f"{prefix} Malzeme Fiyatı",
                "İşçilik Fiyatı": f"{prefix} İşçilik Fiyatı",
                "GGK Fiyatı": f"{prefix} GGK Fiyatı",
                "Genel Toplam": f"{prefix} Genel Toplam",
            }
        )

    old_agg = aggregate_for_compare(old_df, "Eski")
    new_agg = aggregate_for_compare(new_df, "Yeni")

    compare_df = old_agg.merge(new_agg, on=key_cols, how="outer")
    for col in [f"Eski {name}" for name in cost_cols] + [f"Yeni {name}" for name in cost_cols]:
        compare_df[col] = pd.to_numeric(compare_df[col], errors="coerce").fillna(0.0)
    compare_df["Eski Excel Satır No"] = pd.to_numeric(compare_df["Eski Excel Satır No"], errors="coerce")
    compare_df["Yeni Excel Satır No"] = pd.to_numeric(compare_df["Yeni Excel Satır No"], errors="coerce")
    compare_df["Excel Satır No"] = (
        compare_df["Yeni Excel Satır No"]
        .combine_first(compare_df["Eski Excel Satır No"])
        .round()
        .astype("Int64")
    )

    compare_df["Genel Toplam Farkı"] = (compare_df["Yeni Genel Toplam"] - compare_df["Eski Genel Toplam"]).round(2)
    compare_df["İndirim Tutarı"] = np.where(compare_df["Genel Toplam Farkı"] < 0, -compare_df["Genel Toplam Farkı"], 0).round(2)
    compare_df["Zam Tutarı"] = np.where(compare_df["Genel Toplam Farkı"] > 0, compare_df["Genel Toplam Farkı"], 0).round(2)

    def pct_change(old_series, new_series):
        return np.where(
            old_series > 0,
            ((new_series - old_series) / old_series * 100),
            np.where(new_series > 0, 100.0, 0.0),
        ).round(2)

    compare_df["Değişim %"] = pct_change(compare_df["Eski Genel Toplam"], compare_df["Yeni Genel Toplam"])
    compare_df["Malzeme Değişim %"] = pct_change(compare_df["Eski Malzeme Fiyatı"], compare_df["Yeni Malzeme Fiyatı"])
    compare_df["İşçilik Değişim %"] = pct_change(compare_df["Eski İşçilik Fiyatı"], compare_df["Yeni İşçilik Fiyatı"])

    def detect_change_type(row):
        old_val = float(row["Eski Genel Toplam"])
        new_val = float(row["Yeni Genel Toplam"])
        if old_val == 0 and new_val > 0:
            return "Yeni Kalem"
        if old_val > 0 and new_val == 0:
            return "Kaldırılan Kalem"
        if new_val < old_val:
            return "İndirim"
        if new_val > old_val:
            return "Zam"
        return "Değişmedi"

    compare_df["Durum"] = compare_df.apply(detect_change_type, axis=1)

    total_old = float(compare_df["Eski Genel Toplam"].sum())
    total_new = float(compare_df["Yeni Genel Toplam"].sum())
    net_change = total_new - total_old
    total_discount = float(compare_df["İndirim Tutarı"].sum())
    total_increase = float(compare_df["Zam Tutarı"].sum())
    net_change_pct = (net_change / total_old * 100) if total_old > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Eski Toplam", format_currency_display(total_old))
    with col2:
        st.metric("Yeni Toplam", format_currency_display(total_new))
    with col3:
        st.metric("Net Fark", format_currency_display(net_change), delta=f"{net_change_pct:.2f}%")
    with col4:
        st.metric("Toplam İndirim", format_currency_display(total_discount), delta=f"Zam: {format_currency_display(total_increase)}")

    status_options = ["İndirim", "Zam", "Yeni Kalem", "Kaldırılan Kalem", "Değişmedi"]
    selected_statuses = st.multiselect(
        "Durum filtresi",
        options=status_options,
        default=["İndirim", "Zam", "Yeni Kalem", "Kaldırılan Kalem"],
        key="price_compare_status_filter",
    )

    filtered_df = compare_df[compare_df["Durum"].isin(selected_statuses)].copy()
    filtered_df = filtered_df.sort_values("Genel Toplam Farkı", key=lambda s: s.abs(), ascending=False)

    st.markdown("### Ürün/Satır Bazında Fiyat Değişimi")
    if filtered_df.empty:
        st.info("Seçilen filtreye uygun kayıt bulunamadı.")
    else:
        detail_cols = [
            "Durum",
            "Ürün Grubu",
            "Sayfa",
            "Excel Satır No",
            "Ürün Açıklaması",
            "Eski Genel Toplam",
            "Yeni Genel Toplam",
            "Genel Toplam Farkı",
            "Değişim %",
            "İndirim Tutarı",
            "Zam Tutarı",
            "Eski Malzeme Fiyatı",
            "Yeni Malzeme Fiyatı",
            "Malzeme Değişim %",
            "Eski İşçilik Fiyatı",
            "Yeni İşçilik Fiyatı",
            "İşçilik Değişim %",
            "Eski GGK Fiyatı",
            "Yeni GGK Fiyatı",
        ]
        detail_currency_cols = [
            "Eski Genel Toplam",
            "Yeni Genel Toplam",
            "Genel Toplam Farkı",
            "İndirim Tutarı",
            "Zam Tutarı",
            "Eski Malzeme Fiyatı",
            "Yeni Malzeme Fiyatı",
            "Eski İşçilik Fiyatı",
            "Yeni İşçilik Fiyatı",
            "Eski GGK Fiyatı",
            "Yeni GGK Fiyatı",
        ]
        create_sortable_numeric_table(
            filtered_df[detail_cols],
            height=520,
            currency_cols=detail_currency_cols,
            percent_cols=["Değişim %", "Malzeme Değişim %", "İşçilik Değişim %"],
        )

    st.markdown("### Ürün Grubu Bazında Özet Kıyas")
    group_summary = (
        compare_df.groupby("Ürün Grubu", as_index=False)[
            [
                "Eski Genel Toplam",
                "Yeni Genel Toplam",
                "Genel Toplam Farkı",
                "İndirim Tutarı",
                "Zam Tutarı",
                "Eski Malzeme Fiyatı",
                "Yeni Malzeme Fiyatı",
                "Eski İşçilik Fiyatı",
                "Yeni İşçilik Fiyatı",
            ]
        ]
        .sum()
        .sort_values("Genel Toplam Farkı", key=lambda s: s.abs(), ascending=False)
    )
    group_summary["Genel Toplam Farkı %"] = pct_change(group_summary["Eski Genel Toplam"], group_summary["Yeni Genel Toplam"])
    group_summary["Malzeme Değişim %"] = pct_change(group_summary["Eski Malzeme Fiyatı"], group_summary["Yeni Malzeme Fiyatı"])
    group_summary["İşçilik Değişim %"] = pct_change(group_summary["Eski İşçilik Fiyatı"], group_summary["Yeni İşçilik Fiyatı"])

    if group_summary.empty:
        st.info("Ürün grubu bazında kıyaslanacak veri bulunamadı.")
    else:
        group_summary_display = group_summary[
            [
                "Ürün Grubu",
                "Eski Genel Toplam",
                "Yeni Genel Toplam",
                "Genel Toplam Farkı",
                "Genel Toplam Farkı %",
                "İndirim Tutarı",
                "Zam Tutarı",
                "Eski Malzeme Fiyatı",
                "Yeni Malzeme Fiyatı",
                "Malzeme Değişim %",
                "Eski İşçilik Fiyatı",
                "Yeni İşçilik Fiyatı",
                "İşçilik Değişim %",
            ]
        ]
        create_sortable_numeric_table(
            group_summary_display,
            height=380,
            currency_cols=[
                "Eski Genel Toplam",
                "Yeni Genel Toplam",
                "Genel Toplam Farkı",
                "İndirim Tutarı",
                "Zam Tutarı",
                "Eski Malzeme Fiyatı",
                "Yeni Malzeme Fiyatı",
                "Eski İşçilik Fiyatı",
                "Yeni İşçilik Fiyatı",
            ],
            percent_cols=["Genel Toplam Farkı %", "Malzeme Değişim %", "İşçilik Değişim %"],
        )
SYSTEM_TYPE_DEFINITIONS = {
    "HVAC SİSTEM TİPİ": [
        {"tip": "Chiller + Klima Santrali (Merkezi Sistem)", "keywords": ["chiller", "klima santrali", "ahu", "air handling unit"]},
        {"tip": "VRF / VRV Sistem", "keywords": ["vrf", "vrv"]},
        {"tip": "Rooftop Sistem", "keywords": ["rooftop", "paket klima"]},
        {"tip": "Fancoil + Kazan", "keywords": ["fancoil", "fan coil", "kazan", "boiler"]},
        {"tip": "Isı Pompası Sistemi", "keywords": ["isi pompasi", "ısı pompası", "heat pump"]},
        {"tip": "District Heating / Cooling bağlantılı", "keywords": ["district heating", "district cooling", "bolgesel isitma", "bölgesel ısıtma", "bolgesel sogutma", "bölgesel soğutma"]},
        {"tip": "Precision Cooling (Data Center tipi)", "keywords": ["precision cooling", "close control", "datacenter cooling", "data center cooling"]},
    ],
    "HAVALANDIRMA SİSTEM TİPİ": [
        {"tip": "Konfor havalandırma", "keywords": ["konfor havalandirma", "konfor havalandırma"]},
        {"tip": "Hijyenik havalandırma (Hastane Class)", "keywords": ["hijyenik havalandirma", "hijyenik havalandırma", "hepa", "ameliyathane havalandirma"]},
        {"tip": "Endüstriyel havalandırma", "keywords": ["endustriyel havalandirma", "endüstriyel havalandırma"]},
        {"tip": "Duman tahliye sistemi", "keywords": ["duman tahliye", "smoke exhaust"]},
        {"tip": "Basınçlandırma sistemi", "keywords": ["basinclandirma", "basınçlandırma", "pressure fan"]},
        {"tip": "Mutfak egzoz sistemi (Restaurant/Cafe için kritik)", "keywords": ["mutfak egzoz", "kitchen exhaust", "davlumbaz egzoz"]},
    ],
    "YANGIN TESİSATI SİSTEM TİPİ": [
        {"tip": "Sprinkler sistemi", "keywords": ["sprinkler"]},
        {"tip": "Kuru sistem", "keywords": ["kuru sistem", "dry pipe"]},
        {"tip": "Köpüklü sistem", "keywords": ["kopuklu", "köpüklü", "foam system"]},
        {"tip": "Yangın dolap hattı", "keywords": ["yangin dolap", "yangın dolap"]},
        {"tip": "Hidrant hattı", "keywords": ["hidrant"]},
        {"tip": "Yangın pompa istasyonu", "keywords": ["yangin pompa", "yangın pompa", "fire pump"]},
        {"tip": "Gazlı söndürme (FM200, Novec)", "keywords": ["fm200", "novec", "gazli sondurme", "gazlı söndürme"]},
        {"tip": "Davlumbaz içi söndürme (Restaurant için önemli)", "keywords": ["davlumbaz ici sondurme", "davlumbaz içi söndürme", "hood suppression"]},
    ],
    "SIHHİ TESİSAT SİSTEM TİPİ": [
        {"tip": "Standart temiz su + pis su", "keywords": ["temiz su", "pis su", "atik su", "atık su"]},
        {"tip": "Sıcak su sirkülasyon sistemi", "keywords": ["sicak su sirkulasyon", "sıcak su sirkülasyon"]},
        {"tip": "Gri su sistemi", "keywords": ["gri su", "gray water"]},
        {"tip": "Yağ tutucu sistemi (Restaurant için kritik)", "keywords": ["yag tutucu", "yağ tutucu", "grease trap"]},
        {"tip": "Atık su arıtma", "keywords": ["atik su aritma", "atık su arıtma"]},
        {"tip": "Hidrofor sistemi", "keywords": ["hidrofor", "booster pump"]},
    ],
    "PROSES TESİSATI (Varsa)": [
        {"tip": "Buhar hattı", "keywords": ["buhar hatti", "buhar hattı", "steam line"]},
        {"tip": "Basınçlı hava", "keywords": ["basincli hava", "basınçlı hava", "compressed air"]},
        {"tip": "Proses suyu", "keywords": ["proses suyu", "process water"]},
        {"tip": "Chilled water özel proses hattı", "keywords": ["chilled water", "ozel proses hatti", "özel proses hattı"]},
        {"tip": "Kimyasal hatlar", "keywords": ["kimyasal hat", "chemical line"]},
        {"tip": "Medikal gaz sistemi (Hastane)", "keywords": ["medikal gaz", "medical gas", "medikla gaz"]},
    ],
    "OTOMASYON VE KONTROL": [
        {"tip": "BMS (Building Management System)", "keywords": ["bms", "building management system"]},
        {"tip": "Otomasyonlu HVAC", "keywords": ["otomasyonlu hvac", "hvac otomasyon"]},
        {"tip": "Enerji izleme sistemi", "keywords": ["enerji izleme", "energy monitoring"]},
        {"tip": "SCADA bağlantısı", "keywords": ["scada"]},
        {"tip": "Zon kontrollü sistem", "keywords": ["zon kontrollu", "zon kontrollü", "zone control"]},
    ],
}

BUILDING_TYPE_TREE = {
    "Endüstriyel Tesisler": [
        "Fabrikalar",
        "Üretim tesisleri",
        "Lojistik ve depo merkezleri",
        "Enerji üretim tesisleri",
        "Veri merkezleri (Data Center)",
    ],
    "Ticari ve Karma Kullanımlı Yapılar": [
        "A Sınıfı ofis binaları",
        "İş kuleleri",
        "Karma projeler (ofis + konut + ticari alan)",
        "Rezidans kompleksleri",
        "Restaurant & Cafe",
    ],
    "Sağlık Yapıları": [
        "Şehir hastaneleri",
        "Özel hastane kompleksleri",
        "Üniversite hastaneleri",
        "Sağlık kampüsleri",
    ],
    "Alışveriş ve Büyük Perakende Yapıları": [
        "Alışveriş merkezleri (AVM)",
        "Outlet ve ticari yaşam merkezleri",
    ],
    "Otel ve Turizm Yapıları": [
        "4-5 yıldızlı şehir otelleri",
        "Resort ve tatil köyleri",
        "Kongre otelleri",
    ],
    "Eğitim ve Kampüs Yapıları": [
        "Üniversite kampüsleri",
        "Fakülte ve araştırma binaları",
    ],
    "Kamu ve İdari Yapılar": [
        "Bakanlık ve kamu hizmet binaları",
        "Adliye sarayları",
        "Büyük ölçekli idari kompleksler",
    ],
    "Spor ve Kültür Yapıları": [
        "Stadyumlar",
        "Spor kompleksleri",
        "Kongre ve fuar merkezleri",
    ],
}

def normalize_text_for_match(value):
    text = str(value)
    tr_chars = {
        "ı": "i", "ğ": "g", "ü": "u", "ş": "s", "ö": "o", "ç": "c",
        "İ": "I", "Ğ": "G", "Ü": "U", "Ş": "S", "Ö": "O", "Ç": "C",
    }
    for tr, en in tr_chars.items():
        text = text.replace(tr, en)
    return text.lower().strip()

def get_all_system_type_rows():
    rows = []
    for category, definitions in SYSTEM_TYPE_DEFINITIONS.items():
        for definition in definitions:
            system_type = definition["tip"]
            rows.append(
                {
                    "Sistem Kategori": category,
                    "Sistem Tipi": system_type,
                    "Sistem Etiket": f"{category} / {system_type}",
                    "keywords": [normalize_text_for_match(k) for k in definition.get("keywords", [])],
                }
            )
    return rows

SYSTEM_TYPE_ROWS = get_all_system_type_rows()

def detect_system_classification(row):
    combined_text = " ".join(
        [
            str(row.get("Ürün Açıklaması", "")),
            str(row.get("Ürün Grubu", "")),
            str(row.get("Sayfa", "")),
        ]
    )
    normalized_text = normalize_text_for_match(combined_text)
    for entry in SYSTEM_TYPE_ROWS:
        if any(keyword in normalized_text for keyword in entry["keywords"]):
            return entry["Sistem Kategori"], entry["Sistem Tipi"], entry["Sistem Etiket"]
    return None, None, None

def build_system_distribution(all_df):
    system_df = all_df.copy()
    classifications = system_df.apply(detect_system_classification, axis=1, result_type="expand")
    classifications.columns = ["Sistem Kategori", "Sistem Tipi", "Sistem Etiket"]
    system_df = pd.concat([system_df, classifications], axis=1)
    system_df = system_df[system_df["Sistem Etiket"].notna()].copy()

    total_quote = pd.to_numeric(all_df["Genel Toplam"], errors="coerce").fillna(0).sum()
    all_types_df = pd.DataFrame(SYSTEM_TYPE_ROWS)[
        ["Sistem Kategori", "Sistem Tipi", "Sistem Etiket"]
    ]

    if system_df.empty:
        distribution = all_types_df.copy()
        distribution["Sistem Toplam"] = 0.0
        distribution["Sistem %"] = 0.0
        distribution["Sistem"] = distribution["Sistem Etiket"]
        return distribution

    grouped = (
        system_df.groupby(["Sistem Kategori", "Sistem Tipi", "Sistem Etiket"], as_index=False)["Genel Toplam"]
        .sum()
        .rename(columns={"Genel Toplam": "Sistem Toplam"})
    )
    grouped = all_types_df.merge(grouped, on=["Sistem Kategori", "Sistem Tipi", "Sistem Etiket"], how="left")
    grouped["Sistem Toplam"] = grouped["Sistem Toplam"].fillna(0.0)
    if total_quote > 0:
        grouped["Sistem %"] = (grouped["Sistem Toplam"] / total_quote * 100).round(2)
    else:
        grouped["Sistem %"] = 0.0
    grouped["Sistem"] = grouped["Sistem Etiket"]
    return grouped

def render_consistency_module(all_df, summary_data, selected_sheets, source_file_name):
    render_section_heading("Tutarlılık ve Geçmiş Kıyas Modülü", icon="")
    st.markdown(
        '<div class="info-card">Bu modül teklif verilerini hafızaya kaydeder, geçmiş tekliflerle kıyaslar ve olası eksik maliyet girişlerini anomali olarak işaretler.</div>',
        unsafe_allow_html=True,
    )

    col_meta1, col_meta2, col_meta3 = st.columns(3)
    with col_meta1:
        bina_tipi = st.selectbox(
            "Bina Tipi Ana Kategori",
            list(BUILDING_TYPE_TREE.keys()),
            key="memory_bina_tipi",
        )
        alt_options = BUILDING_TYPE_TREE[bina_tipi]
        if st.session_state.get("memory_bina_alt_tipi") not in alt_options:
            st.session_state["memory_bina_alt_tipi"] = alt_options[0]
        bina_alt_tipi = st.selectbox(
            "Bina Tipi Alt Kategori",
            alt_options,
            key="memory_bina_alt_tipi",
        )
    with col_meta2:
        ana_cihaz_durumu = st.selectbox("Ana Cihaz Maliyeti", ["Dahil", "Dahil Değil"], key="memory_ana_cihaz")
    with col_meta3:
        is_konumu = st.selectbox("İş Konumu", ["Yurt İçi", "Yurt Dışı"], key="memory_is_konumu")

    teklif_kodu = derive_offer_code_from_filename(source_file_name)
    teklif_tarihi = datetime.now().date()
    col_meta4, col_meta5 = st.columns(2)
    with col_meta4:
        st.text_input(
            "Teklif Kodu (Dosya Adından)",
            value=teklif_kodu,
            key="memory_teklif_kodu_display",
            disabled=True,
        )
    with col_meta5:
        st.caption("Teklif Tarihi kayıtta otomatik olarak bugünün tarihi kullanılır.")

    group_memory_path, item_memory_path, system_memory_path = get_offer_memory_paths()
    history_groups = load_memory_dataframe(group_memory_path)
    history_items = load_memory_dataframe(item_memory_path)
    history_systems = load_memory_dataframe(system_memory_path)

    context_groups = apply_context_filter(history_groups, bina_tipi, ana_cihaz_durumu, is_konumu, bina_alt_tipi)
    context_items = apply_context_filter(history_items, bina_tipi, ana_cihaz_durumu, is_konumu, bina_alt_tipi)
    context_systems = apply_context_filter(history_systems, bina_tipi, ana_cihaz_durumu, is_konumu, bina_alt_tipi)
    # Ana kategori bazlı tek havuz kıyasları (alt kategori ayrışmasız)
    context_groups_main_category = apply_context_filter(history_groups, bina_tipi, ana_cihaz_durumu, is_konumu, None)
    # Geçmiş dönem ürün/sayfa kıyasında alt kategori ayrışmasını kaldır:
    # Aynı ana bina tipi altında tüm alt tipler tek havuzda kıyaslansın.
    context_items_main_category = apply_context_filter(history_items, bina_tipi, ana_cihaz_durumu, is_konumu, None)
    context_systems_main_category = apply_context_filter(history_systems, bina_tipi, ana_cihaz_durumu, is_konumu, None)

    st.caption(
        f"Hafızadaki kayıtlar: Grup {len(context_groups)} satır, "
        f"Ürün {len(context_items)} satır, Sistem {len(context_systems)} satır"
    )

    current_group_snapshot = summary_data[
        ["Ürün Grubu", "Malzeme Fiyatı", "İşçilik Fiyatı", "GGK Fiyatı", "Genel Toplam", "Bulunan Kayıt Sayısı", "Malzeme %", "İşçilik %", "GGK %", "Genel Toplam %"]
    ].copy()
    current_group_snapshot["Bina Tipi"] = bina_tipi
    current_group_snapshot["Bina Alt Tipi"] = bina_alt_tipi
    current_group_snapshot["Ana Cihaz Durumu"] = ana_cihaz_durumu
    current_group_snapshot["İş Konumu"] = is_konumu
    current_group_snapshot["Teklif Kodu"] = teklif_kodu
    current_group_snapshot["Teklif Tarihi"] = pd.to_datetime(teklif_tarihi)
    current_group_snapshot["Seçilen Sayfalar"] = " | ".join(selected_sheets)
    current_group_snapshot["Kayıt Zamanı"] = pd.Timestamp.now()

    current_item_snapshot = all_df[
        ["Ürün Grubu", "Sayfa", "Ürün Açıklaması", "Malzeme Fiyatı", "İşçilik Fiyatı", "GGK Fiyatı", "Genel Toplam"]
    ].copy()
    current_item_snapshot = current_item_snapshot.groupby(
        ["Ürün Grubu", "Sayfa", "Ürün Açıklaması"], as_index=False
    ).agg(
        {
            "Malzeme Fiyatı": "sum",
            "İşçilik Fiyatı": "sum",
            "GGK Fiyatı": "sum",
            "Genel Toplam": "sum",
        }
    )
    current_item_snapshot["Bina Tipi"] = bina_tipi
    current_item_snapshot["Bina Alt Tipi"] = bina_alt_tipi
    current_item_snapshot["Ana Cihaz Durumu"] = ana_cihaz_durumu
    current_item_snapshot["İş Konumu"] = is_konumu
    current_item_snapshot["Teklif Kodu"] = teklif_kodu
    current_item_snapshot["Teklif Tarihi"] = pd.to_datetime(teklif_tarihi)
    current_item_snapshot["Kayıt Zamanı"] = pd.Timestamp.now()

    st.markdown("### Mevcut Teklif Yüzdelik Dağılım")
    toplam_malzeme = pd.to_numeric(all_df["Malzeme Fiyatı"], errors="coerce").fillna(0).sum()
    toplam_iscilik = pd.to_numeric(all_df["İşçilik Fiyatı"], errors="coerce").fillna(0).sum()
    toplam_ggk = pd.to_numeric(all_df["GGK Fiyatı"], errors="coerce").fillna(0).sum()
    toplam_genel = pd.to_numeric(all_df["Genel Toplam"], errors="coerce").fillna(0).sum()
    mevcut_dagilim_df = pd.DataFrame(
        [
            {"Kalem": "Malzeme", "Tutar": toplam_malzeme},
            {"Kalem": "İşçilik", "Tutar": toplam_iscilik},
            {"Kalem": "GGK", "Tutar": toplam_ggk},
        ]
    )
    if toplam_genel > 0:
        mevcut_dagilim_df["Teklif İçindeki %"] = (mevcut_dagilim_df["Tutar"] / toplam_genel * 100).round(2)
    else:
        mevcut_dagilim_df["Teklif İçindeki %"] = 0.0
    st.dataframe(mevcut_dagilim_df, use_container_width=True, hide_index=True, height=180)

    st.markdown("### Tesisat/Sistem Dağılımı ve Medyan Kıyas")
    current_system_snapshot = build_system_distribution(all_df)
    selected_system_labels = []
    for category in SYSTEM_TYPE_DEFINITIONS.keys():
        category_options = current_system_snapshot[
            current_system_snapshot["Sistem Kategori"] == category
        ]["Sistem Tipi"].tolist()
        selector_key = f"included_systems_{normalize_text_for_match(category).replace(' ', '_')}"
        selected_types = st.multiselect(
            category,
            options=category_options,
            default=category_options,
            key=selector_key,
        )
        for selected_type in selected_types:
            selected_system_labels.append(f"{category} / {selected_type}")

    if not selected_system_labels:
        st.warning("En az bir sistem tipi seçilmediği için tüm sistem tipleri üzerinden devam ediliyor.")
        selected_system_labels = current_system_snapshot["Sistem Etiket"].tolist()

    selected_system_set = set(selected_system_labels)
    current_system_view = current_system_snapshot[
        current_system_snapshot["Sistem Etiket"].isin(selected_system_labels)
    ].copy()
    selected_system_total = current_system_view["Sistem Toplam"].sum()
    if selected_system_total > 0:
        current_system_view["Seçilen Sistem Seti %"] = (
            current_system_view["Sistem Toplam"] / selected_system_total * 100
        ).round(2)
    else:
        current_system_view["Seçilen Sistem Seti %"] = 0.0

    st.dataframe(
        current_system_view[
            ["Sistem Kategori", "Sistem Tipi", "Sistem Toplam", "Sistem %", "Seçilen Sistem Seti %"]
        ].sort_values("Sistem Toplam", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=320,
    )

    sistem_eslesen_toplam = current_system_snapshot["Sistem Toplam"].sum()
    sistem_eslesme_yuzde = (sistem_eslesen_toplam / toplam_genel * 100) if toplam_genel > 0 else 0.0
    st.caption(
        f"Sistem eşleşme kapsaması: {format_currency_display(sistem_eslesen_toplam)} "
        f"({sistem_eslesme_yuzde:.2f}%) / Toplam {format_currency_display(toplam_genel)}"
    )
    if toplam_genel > 0 and sistem_eslesen_toplam <= 0:
        st.info("Sistem dağılımı anahtar kelime eşleşmesi bulamadı. Ürün açıklamalarında sistem anahtarları geçmiyor olabilir.")

    current_system_snapshot["Teklife Dahil"] = current_system_snapshot["Sistem Etiket"].isin(selected_system_set)
    current_system_snapshot["Sistem"] = current_system_snapshot["Sistem Etiket"]
    current_system_snapshot["Bina Tipi"] = bina_tipi
    current_system_snapshot["Bina Alt Tipi"] = bina_alt_tipi
    current_system_snapshot["Ana Cihaz Durumu"] = ana_cihaz_durumu
    current_system_snapshot["İş Konumu"] = is_konumu
    current_system_snapshot["Teklif Kodu"] = teklif_kodu
    current_system_snapshot["Teklif Tarihi"] = pd.to_datetime(teklif_tarihi)
    current_system_snapshot["Seçilen Sayfalar"] = " | ".join(selected_sheets)
    current_system_snapshot["Kayıt Zamanı"] = pd.Timestamp.now()

    system_ratio_threshold = st.slider(
        "Sistem dağılımı düşük oran eşiği (%)",
        min_value=5,
        max_value=60,
        value=20,
        step=5,
        key="system_ratio_threshold",
    )

    st.caption("Sistem medyan kıyası Bina Tipi Ana Kategori bazında yapılır; alt kategori ayrıştırılmaz.")
    if not context_systems_main_category.empty:
        reference_systems = context_systems_main_category[context_systems_main_category["Teklif Kodu"] != teklif_kodu].copy()
    else:
        reference_systems = pd.DataFrame()

    if not reference_systems.empty:
        if "Teklife Dahil" in reference_systems.columns:
            included_mask = (
                reference_systems["Teklife Dahil"]
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["true", "1", "evet", "yes"])
            )
            reference_systems = reference_systems[included_mask]

        if "Sistem Etiket" not in reference_systems.columns:
            if "Sistem" in reference_systems.columns:
                reference_systems["Sistem Etiket"] = reference_systems["Sistem"].astype(str)
            elif "Sistem Kategori" in reference_systems.columns and "Sistem Tipi" in reference_systems.columns:
                reference_systems["Sistem Etiket"] = (
                    reference_systems["Sistem Kategori"].astype(str) + " / " + reference_systems["Sistem Tipi"].astype(str)
                )
            else:
                reference_systems["Sistem Etiket"] = ""

        reference_systems = reference_systems[reference_systems["Sistem Etiket"].isin(selected_system_labels)].copy()
        if reference_systems.empty:
            st.info("Seçilen sistemler için bu bağlamda referans teklif verisi henüz yok.")
        else:
            system_medians = reference_systems.groupby("Sistem Etiket")["Sistem %"].median().reset_index(name="Sistem % Medyan")
            system_reference_counts = reference_systems.groupby("Sistem Etiket")["Teklif Kodu"].nunique().reset_index(name="Referans Teklif Sayısı")

            system_compare = current_system_view[
                ["Sistem Kategori", "Sistem Tipi", "Sistem Etiket", "Sistem %"]
            ].rename(columns={"Sistem %": "Sistem % Mevcut"})
            system_compare = system_compare.merge(system_medians, on="Sistem Etiket", how="left")
            system_compare = system_compare.merge(system_reference_counts, on="Sistem Etiket", how="left")
            system_compare["Referans Teklif Sayısı"] = system_compare["Referans Teklif Sayısı"].fillna(0).astype(int)

            global_system_median = reference_systems["Sistem %"].median()
            system_compare["Sistem % Medyan"] = system_compare["Sistem % Medyan"].fillna(global_system_median).round(2)
            system_compare["Sistem % Sapma"] = (system_compare["Sistem % Mevcut"] - system_compare["Sistem % Medyan"]).round(2)
            system_compare["Düşük Oran"] = system_compare["Sistem % Mevcut"] < (
                system_compare["Sistem % Medyan"] * (1 - system_ratio_threshold / 100)
            )
            system_compare = system_compare.sort_values(["Düşük Oran", "Sistem % Sapma"], ascending=[False, True])

            st.markdown("#### Sistem Dağılımı: Mevcut vs Geçmiş Medyan")
            st.dataframe(
                system_compare[
                    ["Sistem Kategori", "Sistem Tipi", "Sistem % Mevcut", "Sistem % Medyan", "Sistem % Sapma", "Referans Teklif Sayısı", "Düşük Oran"]
                ],
                use_container_width=True,
                hide_index=True,
                height=320
            )

            low_systems = system_compare[system_compare["Düşük Oran"]].copy()
            if low_systems.empty:
                st.success("Seçilen tesisat/sistem dağılımında kritik düşük oran tespit edilmedi.")
            else:
                st.warning(f"{len(low_systems)} sistemde medyana göre düşük oran anomalisi tespit edildi.")
                st.dataframe(low_systems, use_container_width=True, hide_index=True, height=260)
    else:
        st.info("Sistem dağılımı medyan kıyası için bu bağlamda hafıza verisi henüz yok.")

    st.markdown("### Teklifler Arası Ürün Grubu % Kıyas")
    st.caption("Ürün grubu % kıyası Bina Tipi Ana Kategori bazında yapılır; alt kategori ayrıştırılmaz.")
    if not context_groups_main_category.empty:
        historical_groups = context_groups_main_category[context_groups_main_category["Teklif Kodu"] != teklif_kodu].copy()
    else:
        historical_groups = pd.DataFrame()

    if historical_groups.empty:
        st.info("Kıyaslama için geçmiş teklif verisi henüz yok. Önce teklifleri hafızaya kaydedin.")
    else:
        ratio_cols = ["Genel Toplam %", "Malzeme %", "İşçilik %", "GGK %"]
        offer_dates = historical_groups.groupby("Teklif Kodu", as_index=False)["Teklif Tarihi"].max()
        historical_offer_table = historical_groups.pivot_table(
            index="Teklif Kodu",
            columns="Ürün Grubu",
            values="Genel Toplam %",
            aggfunc="sum",
            fill_value=0.0
        ).reset_index()
        historical_offer_table = historical_offer_table.merge(offer_dates, on="Teklif Kodu", how="left")
        ordered_cols = ["Teklif Kodu", "Teklif Tarihi"] + [
            col for col in historical_offer_table.columns if col not in ["Teklif Kodu", "Teklif Tarihi"]
        ]

        st.markdown("#### Geçmiş Tekliflerin Ürün Grubu Yüzdeleri")
        st.dataframe(
            historical_offer_table[ordered_cols].sort_values("Teklif Tarihi", ascending=False),
            use_container_width=True,
            hide_index=True,
            height=280
        )

        compare_mode = st.radio(
            "Kıyas Kaynağı",
            options=["Tüm geçmiş teklifler ortalaması", "Seçilen teklifler"],
            horizontal=True,
            key="offer_compare_mode",
        )
        if compare_mode == "Seçilen teklifler":
            offer_options = historical_offer_table["Teklif Kodu"].astype(str).tolist()
            selected_offers = st.multiselect(
                "Kıyas için teklif seçin",
                options=offer_options,
                default=offer_options[:1] if offer_options else [],
                key="selected_offer_codes",
            )
            benchmark_groups = historical_groups[historical_groups["Teklif Kodu"].astype(str).isin(selected_offers)].copy()
        else:
            benchmark_groups = historical_groups.copy()

        if benchmark_groups.empty:
            st.warning("Seçilen kıyas kaynağında veri yok.")
        else:
            benchmark_avg = benchmark_groups.groupby("Ürün Grubu")[ratio_cols].mean().reset_index()
            benchmark_count = benchmark_groups.groupby("Ürün Grubu")["Teklif Kodu"].nunique().reset_index(name="Referans Teklif Sayısı")

            comparison_table = current_group_snapshot[["Ürün Grubu"] + ratio_cols].merge(
                benchmark_avg,
                on="Ürün Grubu",
                how="left",
                suffixes=(" Mevcut", " Ortalama")
            )
            comparison_table = comparison_table.merge(benchmark_count, on="Ürün Grubu", how="left")
            comparison_table["Referans Teklif Sayısı"] = comparison_table["Referans Teklif Sayısı"].fillna(0).astype(int)

            global_avg = benchmark_groups[ratio_cols].mean()
            for ratio_col in ratio_cols:
                comparison_table[f"{ratio_col} Ortalama"] = comparison_table[f"{ratio_col} Ortalama"].fillna(global_avg.get(ratio_col, np.nan))
                comparison_table[f"{ratio_col} Fark"] = (
                    comparison_table[f"{ratio_col} Mevcut"] - comparison_table[f"{ratio_col} Ortalama"]
                ).round(2)

            deviation_threshold = st.slider(
                "Genel Toplam % sapma eşiği (puan)",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                key="offer_ratio_deviation_threshold",
            )
            comparison_table["Yüksek Sapma"] = comparison_table["Genel Toplam % Fark"].abs() >= deviation_threshold
            comparison_table = comparison_table.sort_values("Genel Toplam % Fark", key=lambda s: s.abs(), ascending=False)

            st.markdown("#### Mevcut Teklif vs Kıyas Kaynağı (Ortalama)")
            st.markdown(
                """
                <div style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:8px;">
                  <span style="background:#dbeafe; color:#1e3a8a; padding:4px 10px; border-radius:999px; font-weight:700;">Mevcut %</span>
                  <span style="background:#dcfce7; color:#166534; padding:4px 10px; border-radius:999px; font-weight:700;">Kıyas Ortalama %</span>
                  <span style="background:#ffedd5; color:#9a3412; padding:4px 10px; border-radius:999px; font-weight:700;">Fark % Puan</span>
                  <span style="background:#fee2e2; color:#991b1b; padding:4px 10px; border-radius:999px; font-weight:700;">Yüksek Sapma</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            comparison_display = comparison_table.copy()
            comparison_display["Sapma Durumu"] = np.where(comparison_display["Yüksek Sapma"], "Yüksek Sapma", "Normal")

            ordered_cols = ["Ürün Grubu"]
            for ratio_col in ratio_cols:
                ordered_cols.extend([f"{ratio_col} Mevcut", f"{ratio_col} Ortalama", f"{ratio_col} Fark"])
            ordered_cols.extend(["Referans Teklif Sayısı", "Sapma Durumu", "Yüksek Sapma"])
            comparison_display = comparison_display[ordered_cols]

            percent_cols = [col for col in comparison_display.columns if "%" in col]
            formatters = {}
            for col in percent_cols:
                if col.endswith(" Fark"):
                    formatters[col] = lambda v: f"{float(v):+.2f} puan" if pd.notna(v) else ""
                else:
                    formatters[col] = lambda v: f"{float(v):.2f}%" if pd.notna(v) else ""

            def style_offer_comparison(df):
                styles = pd.DataFrame("", index=df.index, columns=df.columns)
                for col in df.columns:
                    if col.endswith(" Mevcut"):
                        styles[col] = "background-color: #dbeafe; color: #1e3a8a; font-weight: 700; text-align:center;"
                    elif col.endswith(" Ortalama"):
                        styles[col] = "background-color: #dcfce7; color: #166534; font-weight: 700; text-align:center;"
                    elif col.endswith(" Fark"):
                        styles[col] = df[col].apply(
                            lambda x: "background-color: #fee2e2; color: #991b1b; font-weight: 800; text-align:center;"
                            if pd.notna(x) and float(x) >= 0
                            else "background-color: #dcfce7; color: #166534; font-weight: 800; text-align:center;"
                        )
                    elif col == "Sapma Durumu":
                        styles[col] = df["Yüksek Sapma"].apply(
                            lambda is_high: "background-color: #fee2e2; color: #991b1b; font-weight: 800; text-align:center;"
                            if bool(is_high)
                            else "background-color: #f8fafc; color: #334155; font-weight: 700; text-align:center;"
                        )
                    elif "%" in col:
                        styles[col] = "text-align:center; font-weight:700;"
                return styles

            styled_comparison = (
                comparison_display.style
                .apply(style_offer_comparison, axis=None)
                .format(formatters)
            )
            st.dataframe(
                styled_comparison,
                use_container_width=True,
                hide_index=True,
                height=420
            )

            high_deviation_rows = comparison_table[comparison_table["Yüksek Sapma"]]
            if high_deviation_rows.empty:
                st.success("Genel Toplam % açısından yüksek sapma tespit edilmedi.")
            else:
                st.warning(f"{len(high_deviation_rows)} ürün grubunda yüksek sapma tespit edildi.")

    st.markdown("### Geçmiş Dönem Kıyaslaması (Aynı Ürün/Sayfa)")
    st.caption("Bu kıyas Bina Tipi Ana Kategori bazında yapılır; alt kategori ayrıştırılmaz.")
    drop_threshold = st.slider("Sert düşüş eşiği (%)", min_value=5, max_value=80, value=20, step=5, key="drop_threshold")

    if not context_items_main_category.empty:
        reference_items = context_items_main_category[context_items_main_category["Teklif Kodu"] != teklif_kodu].copy()
    else:
        reference_items = pd.DataFrame()

    if not reference_items.empty:
        key_cols = ["Ürün Grubu", "Sayfa", "Ürün Açıklaması"]
        reference_items = reference_items.sort_values("Teklif Tarihi")
        latest_reference = reference_items.groupby(key_cols, as_index=False).tail(1)
        latest_reference = latest_reference[key_cols + ["Genel Toplam", "Teklif Kodu", "Teklif Tarihi"]].rename(
            columns={
                "Genel Toplam": "Önceki Genel Toplam",
                "Teklif Kodu": "Önceki Teklif Kodu",
                "Teklif Tarihi": "Önceki Teklif Tarihi",
            }
        )

        comparison_df = current_item_snapshot[key_cols + ["Genel Toplam"]].rename(columns={"Genel Toplam": "Mevcut Genel Toplam"})
        comparison_df = comparison_df.merge(latest_reference, on=key_cols, how="left")
        comparison_df = comparison_df[comparison_df["Önceki Genel Toplam"].notna()].copy()

        if comparison_df.empty:
            st.info("Aynı ürün/sayfa için kıyaslanacak geçmiş kayıt bulunamadı.")
        else:
            comparison_df["Değişim %"] = ((comparison_df["Mevcut Genel Toplam"] - comparison_df["Önceki Genel Toplam"]) / comparison_df["Önceki Genel Toplam"] * 100).round(2)
            comparison_df["Sert Düşüş"] = comparison_df["Değişim %"] <= (-drop_threshold)
            sharp_drops = comparison_df[comparison_df["Sert Düşüş"]].sort_values("Değişim %")

            if sharp_drops.empty:
                st.success("Sert düşüş eşiğini aşan anomali tespit edilmedi.")
            else:
                st.warning(f"{len(sharp_drops)} kalemde geçmiş döneme göre sert düşüş tespit edildi.")
                st.dataframe(sharp_drops, use_container_width=True, hide_index=True, height=360)
    else:
        st.info("Geçmiş dönem kıyaslaması için bu bağlamda hafıza verisi henüz yok.")

    st.markdown("### Teklif Hafızasına Kaydet")
    st.caption("Kaydedilen kayıtlar ileride aynı kriterlerle otomatik kıyaslamada kullanılacaktır.")

    if st.button("Bu Teklifi Hafızaya Kaydet", key="save_offer_memory"):
        if not teklif_kodu:
            st.error("Lütfen geçerli bir Teklif Kodu girin.")
        else:
            try:
                upsert_memory_dataframe(
                    group_memory_path,
                    current_group_snapshot,
                    key_columns=["Teklif Kodu", "Ürün Grubu", "Bina Tipi", "Bina Alt Tipi", "Ana Cihaz Durumu", "İş Konumu"],
                )
                upsert_memory_dataframe(
                    item_memory_path,
                    current_item_snapshot,
                    key_columns=["Teklif Kodu", "Ürün Grubu", "Sayfa", "Ürün Açıklaması", "Bina Tipi", "Bina Alt Tipi", "Ana Cihaz Durumu", "İş Konumu"],
                )
                upsert_memory_dataframe(
                    system_memory_path,
                    current_system_snapshot,
                    key_columns=["Teklif Kodu", "Sistem Etiket", "Bina Tipi", "Bina Alt Tipi", "Ana Cihaz Durumu", "İş Konumu"],
                )
                st.success("Teklif hafızaya kaydedildi ve mevcut kayıtlar güncellendi.")
            except Exception as save_error:
                st.error(f"Hafıza kaydı sırasında hata: {str(save_error)}")

def create_sankey_chart(dataframe, label_col, value_col, source_label, title, max_targets=20, height=450):
    """Create a compact single-source Sankey chart from label/value columns."""
    sankey_df = dataframe[[label_col, value_col]].copy()
    sankey_df[value_col] = pd.to_numeric(sankey_df[value_col], errors='coerce').fillna(0)
    sankey_df = sankey_df[sankey_df[value_col] > 0]

    if sankey_df.empty:
        return None

    sankey_df[label_col] = sankey_df[label_col].astype(str).str.strip()
    sankey_df = sankey_df[sankey_df[label_col] != ""]
    sankey_df = sankey_df[sankey_df[label_col].str.lower() != "nan"]
    sankey_df = sankey_df.groupby(label_col, as_index=False)[value_col].sum()
    sankey_df = sankey_df.sort_values(value_col, ascending=False)

    if len(sankey_df) > max_targets:
        top_df = sankey_df.head(max_targets).copy()
        other_total = sankey_df.iloc[max_targets:][value_col].sum()
        if other_total > 0:
            top_df.loc[len(top_df)] = {label_col: "Diğer", value_col: other_total}
        sankey_df = top_df

    labels = [source_label] + sankey_df[label_col].tolist()
    sources = [0] * len(sankey_df)
    targets = list(range(1, len(sankey_df) + 1))
    values = sankey_df[value_col].tolist()
    color_palette = [
        "#2563eb", "#16a34a", "#f59e0b", "#ef4444", "#8b5cf6",
        "#06b6d4", "#ec4899", "#84cc16", "#f97316", "#14b8a6",
    ]
    target_node_colors = [color_palette[i % len(color_palette)] for i in range(len(sankey_df))]

    def hex_to_rgba(hex_color, alpha=0.45):
        hex_clean = hex_color.lstrip("#")
        if len(hex_clean) != 6:
            return f"rgba(59,130,246,{alpha})"
        red = int(hex_clean[0:2], 16)
        green = int(hex_clean[2:4], 16)
        blue = int(hex_clean[4:6], 16)
        return f"rgba({red},{green},{blue},{alpha})"

    link_colors = [hex_to_rgba(color, 0.38) for color in target_node_colors]

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                textfont=dict(
                    family="Arial, sans-serif",
                    size=14,
                    color="#000000",
                ),
                node=dict(
                    pad=15,
                    thickness=18,
                    line=dict(color="rgba(0,0,0,0)", width=0),
                    label=labels,
                    color=["#1d4ed8"] + target_node_colors,
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color=link_colors,
                ),
            )
        ]
    )
    fig.update_layout(
        title=dict(text=title, font=dict(family="Arial, sans-serif", size=18, color="#000000")),
        height=height,
        font=dict(family="Arial, sans-serif", size=13, color="#000000"),
        hoverlabel=dict(
            font=dict(family="Arial, sans-serif", size=12, color="#000000"),
            bgcolor="#ffffff",
            bordercolor="rgba(0,0,0,0)"
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig

def create_sortable_numeric_table(dataframe, height=400, currency_cols=None, percent_cols=None):
    """Render sortable numeric tables with the same visual style as analysis tables."""
    currency_cols = set(currency_cols or [])
    percent_cols = set(percent_cols or [])

    display_df = dataframe.copy()
    for col in currency_cols.union(percent_cols):
        if col in display_df.columns:
            display_df[col] = pd.to_numeric(display_df[col], errors="coerce")

    def apply_column_styles(styler):
        malzeme_cols = []
        iscilik_cols = []
        ggk_cols = []
        toplam_cols = []
        grup_cols = []

        for col in display_df.columns:
            normalized = normalize_excel_header_name(col)
            if "MALZEME" in normalized:
                malzeme_cols.append(col)
            if "ISCILIK" in normalized:
                iscilik_cols.append(col)
            if "GGK" in normalized:
                ggk_cols.append(col)
            if "GENEL TOPLAM" in normalized or "KUMULATIF GENEL" in normalized:
                toplam_cols.append(col)
            if "URUN GRUBU" in normalized:
                grup_cols.append(col)

        for col in malzeme_cols:
            styler = styler.map(lambda _: "background-color: #dcfce7; color: #15803d; font-weight: 700", subset=[col])
        for col in iscilik_cols:
            styler = styler.map(lambda _: "background-color: #dbeafe; color: #1d4ed8; font-weight: 700", subset=[col])
        for col in ggk_cols:
            styler = styler.map(lambda _: "background-color: #e9d5ff; color: #7c3aed; font-weight: 700", subset=[col])
        for col in toplam_cols:
            styler = styler.map(lambda _: "background-color: #fecaca; color: #dc2626; font-weight: 800; font-size: 15px", subset=[col])
        for col in grup_cols:
            styler = styler.map(lambda _: "background-color: #f3f4f6; color: #374151; font-weight: 800", subset=[col])

        # Satır bazında İndirim/Zam vurgusu: detay tabloda Durum'a göre, özet tabloda fark işaretine göre.
        status_target_cols = [
            col
            for col in ["Durum", "Genel Toplam Farkı", "Genel Toplam Farkı %", "Değişim %", "İndirim Tutarı", "Zam Tutarı"]
            if col in display_df.columns
        ]
        if "Durum" in display_df.columns and status_target_cols:
            def style_status_row(row):
                status_text = turkce_ascii(str(row.get("Durum", ""))).upper().strip()
                if status_text == "INDIRIM":
                    style = "color: #15803d; font-weight: 800"
                elif status_text == "ZAM":
                    style = "color: #dc2626; font-weight: 800"
                else:
                    style = ""
                return [style for _ in status_target_cols]

            styler = styler.apply(style_status_row, axis=1, subset=status_target_cols)
        elif "Genel Toplam Farkı" in display_df.columns:
            summary_target_cols = [
                col
                for col in ["Genel Toplam Farkı", "Genel Toplam Farkı %", "İndirim Tutarı", "Zam Tutarı"]
                if col in display_df.columns
            ]
            if summary_target_cols:
                def style_change_row(row):
                    fark = pd.to_numeric(row.get("Genel Toplam Farkı"), errors="coerce")
                    if pd.isna(fark) or fark == 0:
                        style = ""
                    elif fark < 0:
                        style = "color: #15803d; font-weight: 800"
                    else:
                        style = "color: #dc2626; font-weight: 800"
                    return [style for _ in summary_target_cols]

                styler = styler.apply(style_change_row, axis=1, subset=summary_target_cols)

        return styler

    st.markdown("""
    <style>
    div[data-testid="stDataFrame"] {
        border: 2px solid #000000 !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
    }
    div[data-testid="stDataFrame"] th {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 18px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 15px 18px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
        text-align: center !important;
    }
    div[data-testid="stDataFrame"] td {
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 12px 16px !important;
        text-align: center !important;
    }
    @media print {
        div[data-testid="stDataFrame"] {
            overflow: visible !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            width: 100% !important;
            max-width: 100% !important;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        div[data-testid="stDataFrame"] * {
            max-height: none !important;
        }
        div[data-testid="stDataFrame"] table {
            width: 100% !important;
            table-layout: auto !important;
        }
        div[data-testid="stDataFrame"] th,
        div[data-testid="stDataFrame"] td {
            font-size: 10px !important;
            padding: 4px 6px !important;
            white-space: normal !important;
            word-break: break-word !important;
            line-height: 1.2 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    styler = display_df.style.pipe(apply_column_styles)
    formatters = {}
    for col in currency_cols:
        if col in display_df.columns:
            formatters[col] = format_currency_display
    for col in percent_cols:
        if col in display_df.columns:
            formatters[col] = format_percent_display
    if formatters:
        styler = styler.format(formatters)

    return st.dataframe(
        styler,
        height=height,
        use_container_width=True,
        hide_index=True,
    )

def create_aggrid_table(dataframe, height=400, selection_mode='single', fit_columns_on_grid_load=True):
    """Render dataframe table with modern design and column-specific styling."""

    def is_currency_column(col_name):
        text = str(col_name)
        if "%" in text:
            return False
        if text in PRICE_COLUMNS:
            return True

        normalized = normalize_excel_header_name(text)
        exclude_tokens = ["SAYISI", "SATIR", "SAYFA", "SIRA", "TARIH", "KODU"]
        if any(token in normalized for token in exclude_tokens):
            return False

        currency_tokens = ["FIYATI", "GENEL TOPLAM", "TUTARI", "MALIYET", "FARKI", "NET FARK"]
        return any(token in normalized for token in currency_tokens)

    # Sütun tabanlı styling için dataframe'i styled DataFrame'e çevir
    def style_dataframe(df):
        """Apply column-specific styling and display formatting without changing numeric dtype."""

        def apply_column_styles(styler):
            # Malzeme sütunları - Yeşil
            malzeme_cols = [col for col in df.columns if 'Malzeme' in str(col)]
            for col in malzeme_cols:
                styler = styler.map(lambda x: 'background-color: #dcfce7; color: #15803d; font-weight: 700', subset=[col])

            # İşçilik sütunları - Mavi
            iscilik_cols = [col for col in df.columns if 'İşçilik' in str(col)]
            for col in iscilik_cols:
                styler = styler.map(lambda x: 'background-color: #dbeafe; color: #1d4ed8; font-weight: 700', subset=[col])

            # GGK sütunları - Mor
            ggk_cols = [col for col in df.columns if 'GGK' in str(col)]
            for col in ggk_cols:
                styler = styler.map(lambda x: 'background-color: #e9d5ff; color: #7c3aed; font-weight: 700', subset=[col])

            # Genel Toplam ve sadece Kümülatif Genel sütunu - Kırmızı
            toplam_cols = [
                col for col in df.columns
                if 'Genel Toplam' in str(col) or str(col) == 'Kümülatif Genel %'
            ]
            for col in toplam_cols:
                styler = styler.map(lambda x: 'background-color: #fecaca; color: #dc2626; font-weight: 800; font-size: 15px', subset=[col])

            # Ürün Grubu sütunları - Gri
            grup_cols = [col for col in df.columns if 'Ürün Grubu' in str(col)]
            for col in grup_cols:
                styler = styler.map(lambda x: 'background-color: #f3f4f6; color: #374151; font-weight: 800', subset=[col])

            return styler

        styler = df.style.pipe(apply_column_styles)

        formatters = {}
        for col in df.columns:
            col_name = str(col)
            if is_currency_column(col_name):
                formatters[col] = format_currency_display
            elif '%' in col_name:
                formatters[col] = format_percent_display

        if formatters:
            styler = styler.format(formatters)

        return styler

    # CSS stillerini dataframe için optimize et - Basit mor çerçeve
    st.markdown("""
    <style>
    /* BASİT SİYAH ÇERÇEVE */
    div[data-testid="stDataFrame"] {
        border: 2px solid #000000 !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
    }

    /* BAŞLIK STİLLERİ */
    div[data-testid="stDataFrame"] th {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 18px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 15px 18px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
        text-align: center !important;
    }

    /* VERİ HÜCRELERİ */
    div[data-testid="stDataFrame"] td {
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 12px 16px !important;
        text-align: center !important;
    }

    /* Yazdırmada tablo taşmalarını gizleme (sağ sütunlar kesilmesin) */
    @media print {
        div[data-testid="stDataFrame"] {
            overflow: visible !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            width: 100% !important;
            max-width: 100% !important;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }

        div[data-testid="stDataFrame"] * {
            max-height: none !important;
        }

        div[data-testid="stDataFrame"] table {
            width: 100% !important;
            table-layout: auto !important;
        }

        div[data-testid="stDataFrame"] th,
        div[data-testid="stDataFrame"] td {
            font-size: 10px !important;
            padding: 4px 6px !important;
            white-space: normal !important;
            word-break: break-word !important;
            line-height: 1.2 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Styled dataframe kullanarak tabloyu göster
    try:
        styled_df = style_dataframe(dataframe)
        return st.dataframe(styled_df, height=height, use_container_width=True)
    except Exception as e:
        # Styling hatası durumunda normal dataframe göster
        st.warning(f"Tablo stillendirilirken hata oluştu, standart format kullanılıyor: {str(e)}")
        return st.dataframe(dataframe, height=height, use_container_width=True)


def render_section_heading(title: str, icon: str = "") -> None:
    display_title = f"{icon} {title}".strip() if icon else title
    st.markdown(f"<div class='section-title'>{display_title}</div>", unsafe_allow_html=True)


def render_subsection_heading(title: str, icon: str = "") -> None:
    display_title = f"{icon} {title}".strip() if icon else title
    st.markdown(f"<div class='subsection-title'>{display_title}</div>", unsafe_allow_html=True)

def turkce_ascii(text):
    """Türkçe karakterleri ASCII'ye çevir"""
    if not isinstance(text, str):
        return str(text)
    tr_chars = {'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
                'İ': 'I', 'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'Ö': 'O', 'Ç': 'C'}
    for tr, en in tr_chars.items():
        text = text.replace(tr, en)
    return text

def generate_pdf_report(combined_df, selected_sheets):
    """
    PDF raporu oluşturur - tüm ürün gruplarının detaylı analizi
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                           rightMargin=1*cm, leftMargin=1*cm,
                           topMargin=1.5*cm, bottomMargin=1.5*cm)

    # PDF elemanları
    elements = []

    # Başlık tablosu
    title_data = [['URUN GRUPLARINA GORE MALIYET ANALIZI RAPORU']]
    title_table = Table(title_data, colWidths=[26*cm])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 18),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(title_table)

    # Tarih
    date_data = [[f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}"]]
    date_table = Table(date_data, colWidths=[26*cm])
    date_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(date_table)
    elements.append(Spacer(1, 0.5*cm))

    # Genel Özet başlık
    section_data = [['GENEL OZET']]
    section_table = Table(section_data, colWidths=[26*cm])
    section_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(section_table)
    elements.append(Spacer(1, 0.3*cm))

    total_malzeme = combined_df['Malzeme Fiyatı'].sum()
    total_iscilik = combined_df['İşçilik Fiyatı'].sum()
    total_ggk = combined_df['GGK Fiyatı'].sum()
    total_genel = combined_df['Genel Toplam'].sum()

    summary_data = [
        ['Kategori', 'Tutar (TL)', 'Yuzde (%)'],
        ['Toplam Malzeme', f'{total_malzeme:,.2f}', f'{(total_malzeme/total_genel*100):.2f}%'],
        ['Toplam Iscilik', f'{total_iscilik:,.2f}', f'{(total_iscilik/total_genel*100):.2f}%'],
        ['Toplam GGK', f'{total_ggk:,.2f}', f'{(total_ggk/total_genel*100):.2f}%'],
        ['GENEL TOPLAM', f'{total_genel:,.2f}', '100.00%']
    ]

    summary_table = Table(summary_data, colWidths=[8*cm, 6*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fecaca')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#dc2626')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 1*cm))

    # Ürün Gruplarına Göre Detaylı Analiz
    section_data2 = [['URUN GRUPLARINA GORE DETAYLI ANALIZ']]
    section_table2 = Table(section_data2, colWidths=[26*cm])
    section_table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(section_table2)
    elements.append(Spacer(1, 0.3*cm))

    # Tüm verileri gruplandır
    grouped = combined_df.groupby('Ürün Grubu').agg({
        'Malzeme Fiyatı': 'sum',
        'İşçilik Fiyatı': 'sum',
        'GGK Fiyatı': 'sum',
        'Genel Toplam': 'sum',
        'Sayfa': 'count'  # Kayıt sayısını say
    }).reset_index()

    # Sütun adını değiştir
    grouped.rename(columns={'Sayfa': 'Bulunan Kayıt Sayısı'}, inplace=True)

    grouped = grouped.sort_values('Genel Toplam', ascending=False)
    grouped['Genel Toplam %'] = (grouped['Genel Toplam'] / grouped['Genel Toplam'].sum() * 100)
    grouped['Kümülatif Genel %'] = grouped['Genel Toplam %'].cumsum()

    # Ana tablo verileri - Kısa başlıklar
    main_table_data = [['Urun Grubu', 'G.Toplam', 'G.Top %', 'Kum %',
                        'Malzeme', 'Mlz %', 'Iscilik', 'Isc %',
                        'GGK', 'GGK %', 'Adet']]

    for _, row in grouped.iterrows():
        main_table_data.append([
            turkce_ascii(str(row['Ürün Grubu']))[:25],  # Kısa isim
            f"{row['Genel Toplam']:,.0f}",
            f"{row['Genel Toplam %']:.1f}%",
            f"{row['Kümülatif Genel %']:.1f}%",
            f"{row['Malzeme Fiyatı']:,.0f}",
            f"{(row['Malzeme Fiyatı']/row['Genel Toplam']*100):.1f}%",
            f"{row['İşçilik Fiyatı']:,.0f}",
            f"{(row['İşçilik Fiyatı']/row['Genel Toplam']*100):.1f}%",
            f"{row['GGK Fiyatı']:,.0f}",
            f"{(row['GGK Fiyatı']/row['Genel Toplam']*100):.1f}%",
            f"{int(row['Bulunan Kayıt Sayısı'])}"
        ])

    # Tablo genişlikleri - Daha dengeli dağılım
    col_widths = [4.2*cm, 2.4*cm, 1.9*cm, 1.8*cm, 2.4*cm, 1.6*cm, 2.4*cm, 1.6*cm, 2.4*cm, 1.6*cm, 1.8*cm]

    main_table = Table(main_table_data, colWidths=col_widths, repeatRows=1)
    main_table.setStyle(TableStyle([
        # Başlık satırı
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('WORDWRAP', (0, 0), (-1, -1), True),
        # Genel Toplam sütunları vurgula
        ('BACKGROUND', (1, 1), (3, -1), colors.HexColor('#fecaca')),
        ('TEXTCOLOR', (1, 1), (3, -1), colors.HexColor('#dc2626')),
        ('FONTNAME', (1, 1), (3, -1), 'Helvetica-Bold'),
        # Malzeme sütunları
        ('BACKGROUND', (4, 1), (5, -1), colors.HexColor('#d1fae5')),
        ('TEXTCOLOR', (4, 1), (5, -1), colors.HexColor('#047857')),
        # İşçilik sütunları
        ('BACKGROUND', (6, 1), (7, -1), colors.HexColor('#dbeafe')),
        ('TEXTCOLOR', (6, 1), (7, -1), colors.HexColor('#1e40af')),
        # GGK sütunları
        ('BACKGROUND', (8, 1), (9, -1), colors.HexColor('#e9d5ff')),
        ('TEXTCOLOR', (8, 1), (9, -1), colors.HexColor('#7c3aed')),
    ]))

    elements.append(main_table)
    elements.append(Spacer(1, 0.5*cm))

    # Tum teklif icin en pahali 50 urun
    top_products_title_data = [['EN PAHALI 50 URUN (GENEL TOPLAM)']]
    top_products_title_table = Table(top_products_title_data, colWidths=[26*cm])
    top_products_title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#b91c1c')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(top_products_title_table)
    elements.append(Spacer(1, 0.2*cm))

    top_products_df = combined_df.sort_values('Genel Toplam', ascending=False).head(50).copy()
    top_products_data = [['#', 'Urun Grubu', 'Urun Aciklamasi', 'Sayfa', 'Satir', 'Genel Toplam (TL)']]

    for rank, (_, row) in enumerate(top_products_df.iterrows(), start=1):
        top_products_data.append([
            str(rank),
            turkce_ascii(str(row.get('Ürün Grubu', '')))[:24],
            turkce_ascii(str(row.get('Ürün Açıklaması', '')))[:46],
            turkce_ascii(str(row.get('Sayfa', '')))[:16],
            str(row.get('Satır', '')),
            f"{float(row.get('Genel Toplam', 0) or 0):,.2f}",
        ])

    top_products_table = Table(
        top_products_data,
        colWidths=[1.1*cm, 4.0*cm, 9.1*cm, 3.0*cm, 2.0*cm, 5.0*cm],
        repeatRows=1
    )
    top_products_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7f1d1d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (5, 1), (5, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (5, 1), (5, -1), colors.HexColor('#b91c1c')),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elements.append(top_products_table)
    elements.append(PageBreak())

    # Her ürün grubu için detaylı sayfa
    for _, group_row in grouped.iterrows():
        urun_grubu = group_row['Ürün Grubu']

        # Ürün grubu başlığı
        group_title_data = [[f"URUN GRUBU DETAYI: {turkce_ascii(str(urun_grubu))}"]]
        group_title_table = Table(group_title_data, colWidths=[26*cm])
        group_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(group_title_table)
        elements.append(Spacer(1, 0.3*cm))

        # Bu ürün grubuna ait tüm kayıtları getir
        group_df = combined_df[combined_df['Ürün Grubu'] == urun_grubu].copy()

        # Özet bilgiler
        group_summary_data = [
            ['Metrik', 'Deger'],
            ['Toplam Kayit Sayisi', f"{len(group_df)}"],
            ['Toplam Maliyet', f"{group_row['Genel Toplam']:,.2f} TL"],
            ['Malzeme Maliyeti', f"{group_row['Malzeme Fiyatı']:,.2f} TL ({(group_row['Malzeme Fiyatı']/group_row['Genel Toplam']*100):.1f}%)"],
            ['Iscilik Maliyeti', f"{group_row['İşçilik Fiyatı']:,.2f} TL ({(group_row['İşçilik Fiyatı']/group_row['Genel Toplam']*100):.1f}%)"],
            ['GGK Maliyeti', f"{group_row['GGK Fiyatı']:,.2f} TL ({(group_row['GGK Fiyatı']/group_row['Genel Toplam']*100):.1f}%)"],
        ]

        group_summary_table = Table(group_summary_data, colWidths=[8*cm, 10*cm])
        group_summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(group_summary_table)
        elements.append(Spacer(1, 0.5*cm))

        # Detaylı kayıt tablosu (ilk 50 kayıt)
        group_df_sorted = group_df.sort_values('Genel Toplam', ascending=False).copy()
        detail_title_data = [[f"Detayli Kayitlar (En Pahali {min(50, len(group_df_sorted))} Kayit)"]]
        detail_title_table = Table(detail_title_data, colWidths=[26*cm])
        detail_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(detail_title_table)
        elements.append(Spacer(1, 0.2*cm))

        detail_data = [['Sayfa', 'Satir', 'Malzeme (TL)', 'Iscilik (TL)', 'GGK (TL)', 'Genel Toplam (TL)']]

        for idx, (_, row) in enumerate(group_df_sorted.head(50).iterrows()):
            detail_data.append([
                turkce_ascii(str(row.get('Sayfa', ''))),
                str(row.get('Satır', '')),
                f"{row['Malzeme Fiyatı']:,.2f}",
                f"{row['İşçilik Fiyatı']:,.2f}",
                f"{row['GGK Fiyatı']:,.2f}",
                f"{row['Genel Toplam']:,.2f}"
            ])

        detail_table = Table(detail_data, colWidths=[3*cm, 3*cm, 4*cm, 4*cm, 4*cm, 4.5*cm])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6b21a8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(detail_table)

        if len(group_df) > 50:
            elements.append(Spacer(1, 0.3*cm))
            note_data = [[f"Not: Bu urun grubunda toplam {len(group_df)} kayit bulunmaktadir. En pahali 50 kayit gosterilmistir."]]
            note_table = Table(note_data, colWidths=[26*cm])
            note_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Oblique'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
            ]))
            elements.append(note_table)

        elements.append(PageBreak())

    # PDF'i oluştur
    doc.build(elements)
    buffer.seek(0)
    return buffer

