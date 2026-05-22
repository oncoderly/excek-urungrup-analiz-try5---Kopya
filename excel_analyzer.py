import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from html import escape
from io import BytesIO
from datetime import datetime, timedelta
from pathlib import Path
from app_styles import apply_global_styles

st.set_page_config(page_title="Excel Analiz Uygulaması", layout="wide")

# Modern CSS stil tanımlamaları
apply_global_styles(st)


from analyzer_core import *

COST_ANALYSIS_TONE_MAP = {
    "cobalt": {
        "background": "linear-gradient(135deg, #eff6ff, #dbeafe)",
        "border": "#2563eb",
        "eyebrow": "#1d4ed8",
        "title": "#1e3a8a",
        "subtitle": "#1d4ed8",
    },
    "emerald": {
        "background": "linear-gradient(135deg, #ecfdf5, #bbf7d0)",
        "border": "#10b981",
        "eyebrow": "#047857",
        "title": "#065f46",
        "subtitle": "#047857",
    },
    "amber": {
        "background": "linear-gradient(135deg, #fff7ed, #fed7aa)",
        "border": "#f59e0b",
        "eyebrow": "#b45309",
        "title": "#9a3412",
        "subtitle": "#92400e",
    },
    "violet": {
        "background": "linear-gradient(135deg, #f5f3ff, #ddd6fe)",
        "border": "#8b5cf6",
        "eyebrow": "#6d28d9",
        "title": "#5b21b6",
        "subtitle": "#6d28d9",
    },
    "rose": {
        "background": "linear-gradient(135deg, #fff1f2, #fecdd3)",
        "border": "#ef4444",
        "eyebrow": "#be123c",
        "title": "#9f1239",
        "subtitle": "#be123c",
    },
    "slate": {
        "background": "linear-gradient(135deg, #f8fafc, #e2e8f0)",
        "border": "#64748b",
        "eyebrow": "#475569",
        "title": "#0f172a",
        "subtitle": "#334155",
    },
}

def render_cost_analysis_page_styles():
    st.markdown(
        """
        <style>
        .cost-hero {
            position: relative;
            margin: 12px auto 28px auto;
            max-width: 1200px;
            padding: 34px 36px;
            border-radius: 30px;
            overflow: hidden;
            background:
                radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 28%),
                radial-gradient(circle at bottom right, rgba(16,185,129,0.16), transparent 30%),
                linear-gradient(135deg, #f8fbff 0%, #eef6ff 40%, #fff8ef 100%);
            border: 1px solid rgba(37,99,235,0.12);
            box-shadow: 0 30px 70px rgba(15,23,42,0.10);
        }
        .cost-hero::after {
            content: "";
            position: absolute;
            top: -70px;
            right: -60px;
            width: 220px;
            height: 220px;
            background: rgba(249,115,22,0.10);
            border-radius: 50%;
            filter: blur(10px);
        }
        .cost-hero-eyebrow {
            display: inline-flex;
            align-items: center;
            padding: 8px 14px;
            border-radius: 999px;
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(148,163,184,0.18);
            color: #1d4ed8;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1.6px;
            text-transform: uppercase;
        }
        .cost-hero-title {
            margin: 18px 0 10px 0;
            color: #0f172a;
            font-size: 34px;
            font-weight: 900;
            line-height: 1.02;
            letter-spacing: -0.04em;
            max-width: 780px;
        }
        .cost-hero-subtitle {
            max-width: 760px;
            color: #334155;
            font-size: 14px;
            font-weight: 600;
            line-height: 1.7;
        }
        .cost-pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
        }
        .cost-pill {
            padding: 10px 14px;
            border-radius: 999px;
            background: rgba(255,255,255,0.84);
            border: 1px solid rgba(148,163,184,0.20);
            color: #0f172a;
            font-size: 12px;
            font-weight: 800;
            box-shadow: 0 10px 18px rgba(15,23,42,0.05);
        }
        .cost-banner {
            margin: 22px 0 16px 0;
            padding: 20px 22px;
            border-radius: 22px;
            border: 1px solid #dbeafe;
            box-shadow: 0 18px 36px rgba(15,23,42,0.06);
        }
        .cost-banner-eyebrow {
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 1.8px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .cost-banner-title {
            font-size: 22px;
            font-weight: 900;
            line-height: 1.08;
            margin-bottom: 6px;
        }
        .cost-banner-subtitle {
            font-size: 13px;
            font-weight: 600;
            line-height: 1.6;
        }
        .cost-chip-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }
        .cost-chip {
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,0.82);
            border: 1px solid rgba(148,163,184,0.20);
            color: #0f172a;
            font-size: 12px;
            font-weight: 700;
        }
        .cost-action-shell {
            margin: 12px 0 20px 0;
            padding: 18px 20px;
            border-radius: 22px;
            background: linear-gradient(135deg, #eff6ff, #eef2ff);
            border: 1px solid #bfdbfe;
            box-shadow: 0 18px 36px rgba(37,99,235,0.10);
        }
        .cost-action-title {
            color: #1e3a8a;
            font-size: 16px;
            font-weight: 900;
            letter-spacing: -0.02em;
            margin-bottom: 6px;
        }
        .cost-action-subtitle {
            color: #334155;
            font-size: 13px;
            font-weight: 600;
            line-height: 1.6;
        }
        .cost-metric-card {
            position: relative;
            min-height: 172px;
            padding: 24px 22px;
            border-radius: 24px;
            border: 1px solid #dbeafe;
            box-shadow: 0 18px 34px rgba(15,23,42,0.08);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .cost-metric-card::after {
            content: "";
            position: absolute;
            top: -26px;
            right: -16px;
            width: 92px;
            height: 92px;
            border-radius: 50%;
            background: rgba(255,255,255,0.34);
        }
        .cost-metric-label {
            position: relative;
            font-size: 18px;
            font-weight: 900;
            letter-spacing: 0.9px;
            text-transform: uppercase;
            margin-bottom: 16px;
        }
        .cost-metric-value {
            position: relative;
            font-size: 42px;
            font-weight: 900;
            line-height: 1.08;
            letter-spacing: -0.04em;
            margin-bottom: 0;
        }
        .cost-metric-detail {
            position: relative;
            font-size: 13px;
            font-weight: 600;
            line-height: 1.5;
        }
        .cost-feature-card {
            margin: 18px auto 10px auto;
            max-width: 900px;
            padding: 34px 28px;
            border-radius: 28px;
            background: linear-gradient(135deg, #fff1f2, #fecdd3);
            border: 1px solid #fb7185;
            text-align: center;
            box-shadow: 0 24px 44px rgba(244,63,94,0.16);
        }
        .cost-feature-eyebrow {
            color: #be123c;
            font-size: 18px;
            font-weight: 900;
            letter-spacing: 1.1px;
            text-transform: uppercase;
            margin-bottom: 12px;
        }
        .cost-feature-title {
            color: #9f1239;
            font-size: 68px;
            font-weight: 900;
            line-height: 1.06;
            letter-spacing: -0.04em;
            margin-bottom: 0;
        }
        .cost-feature-subtitle {
            color: #9f1239;
            font-size: 14px;
            font-weight: 600;
        }
        .cost-group-shell {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 8px 0 24px 0;
            padding: 18px;
            border-radius: 22px;
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            border: 1px solid #e2e8f0;
            box-shadow: 0 18px 34px rgba(15,23,42,0.05);
        }
        .cost-group-chip {
            padding: 9px 13px;
            border-radius: 999px;
            background: linear-gradient(135deg, #eff6ff, #f8fafc);
            border: 1px solid #bfdbfe;
            color: #1e3a8a;
            font-size: 12px;
            font-weight: 800;
            line-height: 1.2;
        }
        .cost-table-shell-title {
            color: #6d28d9;
            font-size: 13px;
            font-weight: 900;
            letter-spacing: 1.4px;
            text-transform: uppercase;
            margin-bottom: 12px;
        }
        div[data-testid="stRadio"] > div {
            padding: 14px 16px;
            border-radius: 20px;
            background: linear-gradient(135deg, #f8fbff, #eef6ff);
            border: 1px solid #dbeafe;
            box-shadow: 0 16px 30px rgba(37,99,235,0.08);
        }
        div[data-testid="stRadio"] label[data-baseweb="radio"] {
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,0.92);
            border: 1px solid rgba(191,219,254,0.95);
            margin-right: 8px;
        }
        div[data-testid="stRadio"] label[data-baseweb="radio"] p {
            color: #1e293b;
            font-weight: 700;
        }
        .stButton > button,
        .stDownloadButton > button {
            min-height: 52px;
            border-radius: 16px;
            border: 1px solid #cbd5e1;
            background: linear-gradient(135deg, #ffffff, #eff6ff);
            color: #0f172a;
            font-size: 14px;
            font-weight: 800;
            box-shadow: 0 16px 30px rgba(15,23,42,0.08);
            transition: all 0.18s ease;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: #93c5fd;
            color: #1d4ed8;
            transform: translateY(-1px);
            box-shadow: 0 18px 34px rgba(37,99,235,0.14);
        }
        div[data-testid="stAlert"] {
            border-radius: 18px;
            border: 1px solid rgba(148,163,184,0.22);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_cost_analysis_hero(source_file_name, selected_sheets, product_group_count=None):
    file_name = escape(str(source_file_name or "Dosya"))
    sheet_count = len(selected_sheets or [])
    product_group_text = (
        f"{int(product_group_count)} urun grubu bulundu"
        if product_group_count is not None
        else "Urun gruplari okunuyor"
    )
    st.markdown(
        f"""
        <div class="cost-hero">
            <div class="cost-hero-eyebrow">Maliyet Analizi</div>
            <div class="cost-hero-title">Maliyet dagilimi, ozet kartlar ve detayli grup analizi tek bakista daha okunur hale getirildi.</div>
            <div class="cost-hero-subtitle">
                Bu ekran yuklenen Excel dosyasini urun gruplari bazinda ayrisirir, ana maliyet katmanlarini renklerle ayirir
                ve kritik bolumler arasinda gecisi daha net gormeniz icin sayfayi bolum bazli bir tasarim diliyle sunar.
            </div>
            <div class="cost-pill-row">
                <div class="cost-pill">Kaynak Dosya: {file_name}</div>
                <div class="cost-pill">Secili Sayfa: {sheet_count}</div>
                <div class="cost-pill">{escape(product_group_text)}</div>
                <div class="cost-pill">Akis: Ozet > Gorsel > Detay</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_cost_analysis_banner(title, subtitle="", tone="cobalt", eyebrow="Analiz Bolumu", chips=None):
    palette = COST_ANALYSIS_TONE_MAP.get(tone, COST_ANALYSIS_TONE_MAP["cobalt"])
    chips_html = ""
    if chips:
        chip_markup = "".join(f"<div class='cost-chip'>{escape(str(chip))}</div>" for chip in chips if str(chip).strip())
        if chip_markup:
            chips_html = f"<div class='cost-chip-list'>{chip_markup}</div>"

    st.markdown(
        f"""
        <div class="cost-banner" style="background:{palette['background']}; border-color:{palette['border']};">
            <div class="cost-banner-eyebrow" style="color:{palette['eyebrow']};">{escape(str(eyebrow))}</div>
            <div class="cost-banner-title" style="color:{palette['title']};">{escape(str(title))}</div>
            <div class="cost-banner-subtitle" style="color:{palette['subtitle']};">{escape(str(subtitle))}</div>
            {chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_cost_summary_cards(total_malzeme, total_iscilik, total_ggk, total_genel):
    cards = [
        ("Toplam Malzeme", total_malzeme, "emerald"),
        ("Toplam Iscilik", total_iscilik, "cobalt"),
        ("Toplam GGK", total_ggk, "violet"),
    ]
    columns = st.columns(3)
    for column, (label, value, tone_name) in zip(columns, cards):
        tone = COST_ANALYSIS_TONE_MAP[tone_name]
        with column:
            st.markdown(
                f"""
                <div class="cost-metric-card" style="background:{tone['background']}; border-color:{tone['border']};">
                    <div class="cost-metric-label" style="color:{tone['eyebrow']};">{escape(label)}</div>
                    <div class="cost-metric-value" style="color:{tone['title']};">{format_integer_display(value)} TL</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div class="cost-feature-card">
            <div class="cost-feature-eyebrow">Genel Toplam</div>
            <div class="cost-feature-title">{format_integer_display(total_genel)} TL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_cost_analysis_group_catalog(items):
    cleaned_items = [str(item).strip() for item in (items or []) if str(item).strip()]
    if not cleaned_items:
        return

    chips_html = "".join(
        f"<div class='cost-group-chip'>{escape(item)}</div>"
        for item in cleaned_items
    )
    st.markdown(
        f"""
        <div class="cost-group-shell">
            {chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_cost_action_shell(title, subtitle):
    st.markdown(
        f"""
        <div class="cost-action-shell">
            <div class="cost-action-title">{escape(str(title))}</div>
            <div class="cost-action-subtitle">{escape(str(subtitle))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def parse_cash_numeric_value(value):
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    text_value = str(value).strip()
    if not text_value:
        return 0.0

    is_negative = False
    if text_value.startswith("(") and text_value.endswith(")"):
        is_negative = True
        text_value = text_value[1:-1]

    for token in ["TL", "TRY", "$", "€", "₺"]:
        text_value = text_value.replace(token, "")

    text_value = text_value.replace(" ", "").replace("\u00a0", "")
    if "," in text_value and "." in text_value:
        if text_value.rfind(",") > text_value.rfind("."):
            text_value = text_value.replace(".", "").replace(",", ".")
        else:
            text_value = text_value.replace(",", "")
    elif "," in text_value:
        text_value = text_value.replace(",", ".")

    try:
        parsed_value = float(text_value)
    except ValueError:
        return 0.0

    return -parsed_value if is_negative else parsed_value

def build_cash_flow_product_summary(
    uploaded_file,
    selected_sheets,
    data_group_col_index,
    malzeme_col_index,
    iscilik_col_index,
    ggk_col_index,
    genel_toplam_col_index,
):
    records = []
    issues = []

    required_indices = [
        idx
        for idx in [
            data_group_col_index,
            malzeme_col_index,
            iscilik_col_index,
            ggk_col_index,
            genel_toplam_col_index,
        ]
        if idx is not None
    ]

    if not required_indices:
        return pd.DataFrame(), ["Ürün grubu ve maliyet kolonları seçilmedi."]

    ignored_group_labels = {
        "",
        "0",
        "0.0",
        "NAN",
        "URUN GRUBU",
        "URUN GRUPLARI",
        "TOPLAM",
        "GENEL TOPLAM",
    }

    for sheet_name in selected_sheets or []:
        try:
            sheet_df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        except Exception as exc:
            issues.append(f"{sheet_name}: sayfa okunamadı ({exc})")
            continue

        if sheet_df.empty or len(sheet_df.columns) <= max(required_indices):
            issues.append(f"{sheet_name}: seçilen kolonlar bu sayfada bulunamadı.")
            continue

        for row_idx, row in sheet_df.iterrows():
            if data_group_col_index is None or len(row) <= data_group_col_index or pd.isna(row.iloc[data_group_col_index]):
                continue

            product_group = str(row.iloc[data_group_col_index]).strip()
            normalized_group = normalize_excel_header_name(product_group)
            if normalized_group in ignored_group_labels:
                continue

            malzeme = (
                parse_cash_numeric_value(row.iloc[malzeme_col_index])
                if malzeme_col_index is not None and len(row) > malzeme_col_index
                else 0.0
            )
            iscilik = (
                parse_cash_numeric_value(row.iloc[iscilik_col_index])
                if iscilik_col_index is not None and len(row) > iscilik_col_index
                else 0.0
            )
            ggk = (
                parse_cash_numeric_value(row.iloc[ggk_col_index])
                if ggk_col_index is not None and len(row) > ggk_col_index
                else 0.0
            )
            genel_toplam = (
                parse_cash_numeric_value(row.iloc[genel_toplam_col_index])
                if genel_toplam_col_index is not None and len(row) > genel_toplam_col_index
                else 0.0
            )
            if abs(genel_toplam) < 0.0001:
                genel_toplam = malzeme + iscilik + ggk

            if max(abs(malzeme), abs(iscilik), abs(ggk), abs(genel_toplam)) < 0.0001:
                continue

            records.append(
                {
                    "Ürün Grubu": product_group,
                    "Sayfa": sheet_name,
                    "Satır": row_idx + 2,
                    "Malzeme Tutarı": round(malzeme, 2),
                    "İşçilik Tutarı": round(iscilik, 2),
                    "GGK Tutarı": round(ggk, 2),
                    "Genel Toplam": round(genel_toplam, 2),
                }
            )

    if not records:
        return pd.DataFrame(), issues

    source_df = pd.DataFrame(records)
    summary_df = source_df.groupby("Ürün Grubu", as_index=False).agg(
        {
            "Malzeme Tutarı": "sum",
            "İşçilik Tutarı": "sum",
            "GGK Tutarı": "sum",
            "Genel Toplam": "sum",
            "Satır": "count",
        }
    )
    summary_df.rename(columns={"Satır": "Kayıt Sayısı"}, inplace=True)
    return summary_df.sort_values("Genel Toplam", ascending=False).reset_index(drop=True), issues

def build_project_cash_records(product_plan_df, collection_plan_df, advance_amount, advance_date, advance_deduction_rate, retention_rate):
    records = []

    if advance_amount > 0 and advance_date is not None:
        records.append(
            {
                "Tarih": advance_date,
                "Dönem": pd.Timestamp(advance_date).to_period("M").strftime("%Y-%m"),
                "Akış Tipi": "Alınan Avans",
                "Ürün Grubu": "Proje Geneli",
                "Açıklama": "Alınan avans",
                "Nakit Girişi": round(float(advance_amount), 2),
                "Nakit Çıkışı": 0.0,
                "Net Nakit Akışı": round(float(advance_amount), 2),
            }
        )

    for _, row in collection_plan_df.iterrows():
        raw_date = row.get("Tahsilat Tarihi")
        collection_date = pd.to_datetime(raw_date, errors="coerce")
        if pd.isna(collection_date):
            continue

        gross_amount = parse_cash_numeric_value(row.get("Tutar", 0.0))
        if abs(gross_amount) < 0.0001:
            continue

        label = str(row.get("Taksit", "")).strip() or "Tahsilat"
        date_value = collection_date.date()
        records.append(
            {
                "Tarih": date_value,
                "Dönem": collection_date.to_period("M").strftime("%Y-%m"),
                "Akış Tipi": "Tahsilat",
                "Ürün Grubu": "Proje Geneli",
                "Açıklama": label,
                "Nakit Girişi": round(gross_amount, 2),
                "Nakit Çıkışı": 0.0,
                "Net Nakit Akışı": round(gross_amount, 2),
            }
        )

        advance_deduction = gross_amount * float(advance_deduction_rate) / 100
        if advance_deduction > 0:
            records.append(
                {
                    "Tarih": date_value,
                    "Dönem": collection_date.to_period("M").strftime("%Y-%m"),
                    "Akış Tipi": "Avans Kesintisi",
                    "Ürün Grubu": "Proje Geneli",
                    "Açıklama": f"{label} avans kesintisi",
                    "Nakit Girişi": 0.0,
                    "Nakit Çıkışı": round(advance_deduction, 2),
                    "Net Nakit Akışı": round(-advance_deduction, 2),
                }
            )

        retention_deduction = gross_amount * float(retention_rate) / 100
        if retention_deduction > 0:
            records.append(
                {
                    "Tarih": date_value,
                    "Dönem": collection_date.to_period("M").strftime("%Y-%m"),
                    "Akış Tipi": "Teminat Kesintisi",
                    "Ürün Grubu": "Proje Geneli",
                    "Açıklama": f"{label} teminat kesintisi",
                    "Nakit Girişi": 0.0,
                    "Nakit Çıkışı": round(retention_deduction, 2),
                    "Net Nakit Akışı": round(-retention_deduction, 2),
                }
            )

    for _, row in product_plan_df.iterrows():
        product_group = str(row.get("Ürün Grubu", "")).strip()
        if not product_group:
            continue

        payment_specs = [
            ("Malzeme Ödemesi", "Malzeme Ödeme Tarihi", "Malzeme Tutarı"),
            ("İşçilik Ödemesi", "İşçilik Ödeme Tarihi", "İşçilik Tutarı"),
        ]
        for flow_type, date_col, amount_col in payment_specs:
            payment_date = pd.to_datetime(row.get(date_col), errors="coerce")
            amount = parse_cash_numeric_value(row.get(amount_col, 0.0))
            if pd.isna(payment_date) or amount <= 0:
                continue
            records.append(
                {
                    "Tarih": payment_date.date(),
                    "Dönem": payment_date.to_period("M").strftime("%Y-%m"),
                    "Akış Tipi": flow_type,
                    "Ürün Grubu": product_group,
                    "Açıklama": f"{product_group} - {flow_type}",
                    "Nakit Girişi": 0.0,
                    "Nakit Çıkışı": round(amount, 2),
                    "Net Nakit Akışı": round(-amount, 2),
                }
            )

    if not records:
        return pd.DataFrame()

    cash_df = pd.DataFrame(records)
    cash_df["Tarih"] = pd.to_datetime(cash_df["Tarih"])
    cash_df = cash_df.sort_values(["Tarih", "Akış Tipi", "Ürün Grubu"]).reset_index(drop=True)
    cash_df["Kümülatif Nakit"] = cash_df["Net Nakit Akışı"].cumsum().round(2)
    return cash_df

def render_uploaded_cash_flow_analysis_legacy(
    uploaded_file,
    selected_sheets,
    data_group_col_index,
    malzeme_col_index,
    iscilik_col_index,
    ggk_col_index,
    genel_toplam_col_index,
):
    render_cost_analysis_page_styles()
    render_cost_analysis_banner(
        title="Nakit Akış Analiz",
        subtitle="Seçili sayfalardaki tarih, açıklama, nakit giriş, nakit çıkış veya net tutar kolonları dönemsel nakit akışına çevrilir.",
        tone="emerald",
        eyebrow="Finansal Analiz",
        chips=[
            f"{len(selected_sheets or [])} seçili sayfa",
            "Aylık akış",
            "Kümülatif bakiye",
        ],
    )

    if not selected_sheets:
        st.info("Nakit akış analizi için yan panelden en az bir sayfa seçin.")
        return

    if date_col_index is None:
        st.warning("Nakit akış analizi için tarih kolonu seçin.")
        return

    if cash_in_col_index is None and cash_out_col_index is None and net_amount_col_index is None:
        st.warning("Nakit giriş, nakit çıkış veya net tutar kolonlarından en az birini seçin.")
        return

    records = []
    issues = []

    for sheet_name in selected_sheets:
        try:
            sheet_df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        except Exception as exc:
            issues.append(f"{sheet_name}: sayfa okunamadı ({exc})")
            continue

        required_indices = [
            idx
            for idx in [
                date_col_index,
                description_col_index,
                cash_in_col_index,
                cash_out_col_index,
                net_amount_col_index,
            ]
            if idx is not None
        ]
        if not required_indices or len(sheet_df.columns) <= max(required_indices):
            issues.append(f"{sheet_name}: seçilen kolonlar bu sayfada bulunamadı.")
            continue

        for row_idx, row in sheet_df.iterrows():
            raw_date = row.iloc[date_col_index] if len(row) > date_col_index else None
            parsed_date = pd.to_datetime(raw_date, errors="coerce", dayfirst=True)

            description = ""
            if description_col_index is not None and len(row) > description_col_index and pd.notna(row.iloc[description_col_index]):
                description = str(row.iloc[description_col_index]).strip()

            cash_in = (
                parse_cash_numeric_value(row.iloc[cash_in_col_index])
                if cash_in_col_index is not None and len(row) > cash_in_col_index
                else 0.0
            )
            cash_out = (
                parse_cash_numeric_value(row.iloc[cash_out_col_index])
                if cash_out_col_index is not None and len(row) > cash_out_col_index
                else 0.0
            )
            net_amount = (
                parse_cash_numeric_value(row.iloc[net_amount_col_index])
                if net_amount_col_index is not None and len(row) > net_amount_col_index
                else cash_in - cash_out
            )

            if abs(cash_in) < 0.0001 and abs(cash_out) < 0.0001 and abs(net_amount) < 0.0001:
                continue

            if pd.isna(parsed_date):
                issues.append(f"{sheet_name}: {row_idx + 2}. satırda tarih okunamadı.")
                continue

            if net_amount_col_index is not None:
                if cash_in_col_index is None and net_amount > 0:
                    cash_in = net_amount
                if cash_out_col_index is None and net_amount < 0:
                    cash_out = abs(net_amount)

            records.append(
                {
                    "Sayfa": sheet_name,
                    "Satır": row_idx + 2,
                    "Tarih": parsed_date.date(),
                    "Dönem": parsed_date.to_period("M").strftime("%Y-%m"),
                    "Açıklama": description,
                    "Nakit Girişi": round(cash_in, 2),
                    "Nakit Çıkışı": round(cash_out, 2),
                    "Net Nakit Akışı": round(net_amount, 2),
                }
            )

    if issues:
        st.info("Okuma notları: " + " | ".join(issues[:8]) + (" | ..." if len(issues) > 8 else ""))

    if not records:
        st.warning("Seçilen kolonlarla nakit akışına dahil edilecek satır bulunamadı.")
        return

    cash_df = pd.DataFrame(records)
    cash_df["Tarih"] = pd.to_datetime(cash_df["Tarih"])
    cash_df = cash_df.sort_values(["Tarih", "Sayfa", "Satır"]).reset_index(drop=True)
    cash_df["Kümülatif Nakit"] = cash_df["Net Nakit Akışı"].cumsum().round(2)

    total_in = float(cash_df["Nakit Girişi"].sum())
    total_out = float(cash_df["Nakit Çıkışı"].sum())
    total_net = float(cash_df["Net Nakit Akışı"].sum())
    final_balance = float(cash_df["Kümülatif Nakit"].iloc[-1])

    metric_cols = st.columns(4)
    metric_cols[0].metric("Toplam Nakit Girişi", format_currency_display(total_in))
    metric_cols[1].metric("Toplam Nakit Çıkışı", format_currency_display(total_out))
    metric_cols[2].metric("Net Nakit Akışı", format_currency_display(total_net))
    metric_cols[3].metric("Kümülatif Nakit", format_currency_display(final_balance))

    monthly_df = cash_df.groupby("Dönem", as_index=False).agg(
        {
            "Nakit Girişi": "sum",
            "Nakit Çıkışı": "sum",
            "Net Nakit Akışı": "sum",
            "Satır": "count",
        }
    )
    monthly_df.rename(columns={"Satır": "İşlem Sayısı"}, inplace=True)
    monthly_df = monthly_df.sort_values("Dönem").reset_index(drop=True)
    monthly_df["Kümülatif Nakit"] = monthly_df["Net Nakit Akışı"].cumsum().round(2)

    sheet_summary_df = cash_df.groupby("Sayfa", as_index=False).agg(
        {
            "Nakit Girişi": "sum",
            "Nakit Çıkışı": "sum",
            "Net Nakit Akışı": "sum",
            "Satır": "count",
        }
    )
    sheet_summary_df.rename(columns={"Satır": "İşlem Sayısı"}, inplace=True)
    sheet_summary_df = sheet_summary_df.sort_values("Net Nakit Akışı", ascending=False).reset_index(drop=True)

    render_cost_analysis_banner(
        title="Aylık Nakit Akışı",
        subtitle="Giriş, çıkış ve net hareketler dönem bazında gruplanır; kümülatif nakit bakiyesi zaman içinde takip edilir.",
        tone="cobalt",
        eyebrow="Dönemsel Özet",
        chips=[f"{len(monthly_df)} dönem", f"{len(cash_df)} işlem"],
    )

    monthly_flow_df = monthly_df.melt(
        id_vars=["Dönem"],
        value_vars=["Nakit Girişi", "Nakit Çıkışı", "Net Nakit Akışı"],
        var_name="Akış Tipi",
        value_name="Tutar",
    )
    flow_chart = px.bar(
        monthly_flow_df,
        x="Dönem",
        y="Tutar",
        color="Akış Tipi",
        barmode="group",
        title="Aylık Nakit Giriş / Çıkış / Net",
        color_discrete_map={
            "Nakit Girişi": "#059669",
            "Nakit Çıkışı": "#dc2626",
            "Net Nakit Akışı": "#2563eb",
        },
    )
    flow_chart.update_layout(height=430, legend_title_text="", yaxis_title="Tutar", xaxis_title="Dönem")
    st.plotly_chart(flow_chart, use_container_width=True)

    cumulative_chart = px.line(
        monthly_df,
        x="Dönem",
        y="Kümülatif Nakit",
        markers=True,
        title="Kümülatif Nakit Bakiyesi",
    )
    cumulative_chart.update_traces(line_color="#0f766e", line_width=4)
    cumulative_chart.update_layout(height=360, yaxis_title="Tutar", xaxis_title="Dönem")
    st.plotly_chart(cumulative_chart, use_container_width=True)

    render_cost_analysis_banner(
        title="Özet Tablolar",
        subtitle="Dönem ve sayfa kırılımında nakit akışı sonuçları.",
        tone="slate",
        eyebrow="Tablo",
    )
    table_col1, table_col2 = st.columns(2)
    with table_col1:
        st.markdown("**Aylık Özet**")
        create_aggrid_table(
            monthly_df,
            height=320,
            currency_cols=["Nakit Girişi", "Nakit Çıkışı", "Net Nakit Akışı", "Kümülatif Nakit"],
            integer_cols=["İşlem Sayısı"],
        )
    with table_col2:
        st.markdown("**Sayfa Özeti**")
        create_aggrid_table(
            sheet_summary_df,
            height=320,
            currency_cols=["Nakit Girişi", "Nakit Çıkışı", "Net Nakit Akışı"],
            integer_cols=["İşlem Sayısı"],
        )

    render_cost_analysis_banner(
        title="Detaylı Nakit Hareketleri",
        subtitle="Okunan tüm hareketler tarih sırasına göre listelenir.",
        tone="emerald",
        eyebrow="Detay",
    )
    create_aggrid_table(
        cash_df,
        height=420,
        currency_cols=["Nakit Girişi", "Nakit Çıkışı", "Net Nakit Akışı", "Kümülatif Nakit"],
        integer_cols=["Satır"],
    )

    export_buffer = BytesIO()
    with pd.ExcelWriter(export_buffer, engine="openpyxl") as writer:
        prepare_dataframe_for_excel_export(monthly_df).to_excel(writer, sheet_name="Aylik_Ozet", index=False)
        prepare_dataframe_for_excel_export(sheet_summary_df).to_excel(writer, sheet_name="Sayfa_Ozeti", index=False)
        export_detail_df = cash_df.copy()
        export_detail_df["Tarih"] = export_detail_df["Tarih"].dt.strftime("%d.%m.%Y")
        prepare_dataframe_for_excel_export(export_detail_df).to_excel(writer, sheet_name="Nakit_Hareketleri", index=False)
        for worksheet in writer.book.worksheets:
            style_excel_sheet(worksheet)

    export_buffer.seek(0)
    st.download_button(
        label="Nakit Akış Excel Çıktısı İndir",
        data=export_buffer.getvalue(),
        file_name=f"nakit_akis_analiz_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

def render_cash_flow_analysis(
    uploaded_file,
    selected_sheets,
    data_group_col_index,
    malzeme_col_index,
    iscilik_col_index,
    ggk_col_index,
    genel_toplam_col_index,
):
    render_cost_analysis_page_styles()
    render_cost_analysis_banner(
        title="Nakit Akış Analiz",
        subtitle="Excel içinde tarih aramadan, ürün grubu maliyetleri üzerinden proje tahsilat ve ödeme planını burada kurun.",
        tone="emerald",
        eyebrow="Finansal Analiz",
        chips=[
            f"{len(selected_sheets or [])} seçili sayfa",
            "Ürün grubu bazlı ödeme",
            "Avans / kesinti",
        ],
    )

    if not selected_sheets:
        st.info("Nakit akış analizi için yan panelden en az bir sayfa seçin.")
        return

    product_summary_df, issues = build_cash_flow_product_summary(
        uploaded_file=uploaded_file,
        selected_sheets=selected_sheets,
        data_group_col_index=data_group_col_index,
        malzeme_col_index=malzeme_col_index,
        iscilik_col_index=iscilik_col_index,
        ggk_col_index=ggk_col_index,
        genel_toplam_col_index=genel_toplam_col_index,
    )

    if issues:
        st.info("Okuma notları: " + " | ".join(issues[:8]) + (" | ..." if len(issues) > 8 else ""))

    if product_summary_df.empty:
        st.warning("Seçilen ürün grubu ve maliyet kolonlarıyla nakit akışına temel olacak ürün grubu bulunamadı.")
        return

    total_project = float(product_summary_df["Genel Toplam"].sum())
    total_material = float(product_summary_df["Malzeme Tutarı"].sum())
    total_labor = float(product_summary_df["İşçilik Tutarı"].sum())

    metric_cols = st.columns(4)
    metric_cols[0].metric("Proje Toplamı", format_currency_display(total_project))
    metric_cols[1].metric("Malzeme", format_currency_display(total_material))
    metric_cols[2].metric("İşçilik", format_currency_display(total_labor))
    metric_cols[3].metric("Ürün Grubu", f"{len(product_summary_df)}")

    today = datetime.now().date()
    render_cost_analysis_banner(
        title="Proje Plan Girişleri",
        subtitle="Malzeme ve işçilik ödeme tarihlerini tüm ürün grupları için tek değerle başlatabilir, tabloda ürün grubu bazında değiştirebilirsiniz.",
        tone="cobalt",
        eyebrow="Giriş",
    )

    plan_col1, plan_col2, plan_col3, plan_col4 = st.columns(4)
    with plan_col1:
        default_material_date = st.date_input("Tüm malzeme ödeme tarihi", value=today + timedelta(days=30), key="cash_default_material_date")
    with plan_col2:
        default_labor_date = st.date_input("Tüm işçilik ödeme tarihi", value=today + timedelta(days=45), key="cash_default_labor_date")
    with plan_col3:
        advance_amount = st.number_input("Alınan avans", min_value=0.0, value=0.0, step=1000.0, key="cash_advance_amount")
    with plan_col4:
        advance_date = st.date_input("Avans tarihi", value=today, key="cash_advance_date")

    deduction_col1, deduction_col2 = st.columns(2)
    with deduction_col1:
        advance_deduction_rate = st.number_input("Avans kesintisi (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="cash_advance_deduction_rate")
    with deduction_col2:
        retention_rate = st.number_input("Teminat kesintisi (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="cash_retention_rate")

    product_plan_df = product_summary_df.copy()
    product_plan_df["Malzeme Ödeme Tarihi"] = default_material_date
    product_plan_df["İşçilik Ödeme Tarihi"] = default_labor_date
    product_plan_df = product_plan_df[
        [
            "Ürün Grubu",
            "Malzeme Tutarı",
            "Malzeme Ödeme Tarihi",
            "İşçilik Tutarı",
            "İşçilik Ödeme Tarihi",
            "GGK Tutarı",
            "Genel Toplam",
            "Kayıt Sayısı",
        ]
    ]

    edited_product_plan_df = st.data_editor(
        product_plan_df,
        key="cash_product_payment_plan_editor",
        use_container_width=True,
        hide_index=True,
        height=360,
        column_config={
            "Malzeme Tutarı": st.column_config.NumberColumn("Malzeme Tutarı", format="%.2f TL"),
            "İşçilik Tutarı": st.column_config.NumberColumn("İşçilik Tutarı", format="%.2f TL"),
            "GGK Tutarı": st.column_config.NumberColumn("GGK Tutarı", format="%.2f TL"),
            "Genel Toplam": st.column_config.NumberColumn("Genel Toplam", format="%.2f TL"),
            "Kayıt Sayısı": st.column_config.NumberColumn("Kayıt Sayısı"),
            "Malzeme Ödeme Tarihi": st.column_config.DateColumn("Malzeme Ödeme Tarihi", format="DD.MM.YYYY"),
            "İşçilik Ödeme Tarihi": st.column_config.DateColumn("İşçilik Ödeme Tarihi", format="DD.MM.YYYY"),
        },
        disabled=["Ürün Grubu", "Malzeme Tutarı", "İşçilik Tutarı", "GGK Tutarı", "Genel Toplam", "Kayıt Sayısı"],
    )

    render_cost_analysis_banner(
        title="Tahsilat Taksitleri",
        subtitle="Tahsilatları proje genelinde tek tabloda girin. Tutar boşsa oran üzerinden proje toplamından hesaplanır.",
        tone="amber",
        eyebrow="Tahsilat",
    )

    default_collection_df = pd.DataFrame(
        [
            {"Taksit": "1. Taksit", "Tahsilat Tarihi": today + timedelta(days=15), "Oran %": 30.0, "Tutar": 0.0},
            {"Taksit": "2. Taksit", "Tahsilat Tarihi": today + timedelta(days=45), "Oran %": 40.0, "Tutar": 0.0},
            {"Taksit": "3. Taksit", "Tahsilat Tarihi": today + timedelta(days=75), "Oran %": 30.0, "Tutar": 0.0},
        ]
    )
    edited_collection_df = st.data_editor(
        default_collection_df,
        key="cash_collection_plan_editor",
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        height=230,
        column_config={
            "Tahsilat Tarihi": st.column_config.DateColumn("Tahsilat Tarihi", format="DD.MM.YYYY"),
            "Oran %": st.column_config.NumberColumn("Oran %", min_value=0.0, max_value=100.0, step=1.0),
            "Tutar": st.column_config.NumberColumn("Tutar", min_value=0.0, step=1000.0, format="%.2f TL"),
        },
    )

    collection_plan_df = edited_collection_df.copy()
    if not collection_plan_df.empty:
        collection_plan_df["Tutar"] = collection_plan_df.apply(
            lambda row: (
                parse_cash_numeric_value(row.get("Tutar", 0.0))
                if parse_cash_numeric_value(row.get("Tutar", 0.0)) > 0
                else total_project * parse_cash_numeric_value(row.get("Oran %", 0.0)) / 100
            ),
            axis=1,
        )

    cash_df = build_project_cash_records(
        product_plan_df=edited_product_plan_df,
        collection_plan_df=collection_plan_df,
        advance_amount=advance_amount,
        advance_date=advance_date,
        advance_deduction_rate=advance_deduction_rate,
        retention_rate=retention_rate,
    )

    if cash_df.empty:
        st.warning("Nakit akışı oluşturmak için en az bir tahsilat, avans veya ödeme tarihi/tutarı girin.")
        return

    total_in = float(cash_df["Nakit Girişi"].sum())
    total_out = float(cash_df["Nakit Çıkışı"].sum())
    total_net = float(cash_df["Net Nakit Akışı"].sum())
    final_balance = float(cash_df["Kümülatif Nakit"].iloc[-1])

    result_cols = st.columns(4)
    result_cols[0].metric("Toplam Nakit Girişi", format_currency_display(total_in))
    result_cols[1].metric("Toplam Nakit Çıkışı", format_currency_display(total_out))
    result_cols[2].metric("Net Nakit Akışı", format_currency_display(total_net))
    result_cols[3].metric("Kümülatif Nakit", format_currency_display(final_balance))

    monthly_df = cash_df.groupby("Dönem", as_index=False).agg(
        {
            "Nakit Girişi": "sum",
            "Nakit Çıkışı": "sum",
            "Net Nakit Akışı": "sum",
            "Akış Tipi": "count",
        }
    )
    monthly_df.rename(columns={"Akış Tipi": "İşlem Sayısı"}, inplace=True)
    monthly_df = monthly_df.sort_values("Dönem").reset_index(drop=True)
    monthly_df["Kümülatif Nakit"] = monthly_df["Net Nakit Akışı"].cumsum().round(2)

    render_cost_analysis_banner(
        title="Aylık Nakit Akışı",
        subtitle="Tahsilatlar, avans, kesintiler ve ürün grubu bazlı malzeme/işçilik ödemeleri dönem bazında gösterilir.",
        tone="cobalt",
        eyebrow="Dönemsel Özet",
        chips=[f"{len(monthly_df)} dönem", f"{len(cash_df)} hareket"],
    )

    monthly_flow_df = monthly_df.melt(
        id_vars=["Dönem"],
        value_vars=["Nakit Girişi", "Nakit Çıkışı", "Net Nakit Akışı"],
        var_name="Akış Tipi",
        value_name="Tutar",
    )
    flow_chart = px.bar(
        monthly_flow_df,
        x="Dönem",
        y="Tutar",
        color="Akış Tipi",
        barmode="group",
        title="Aylık Nakit Giriş / Çıkış / Net",
        color_discrete_map={
            "Nakit Girişi": "#059669",
            "Nakit Çıkışı": "#dc2626",
            "Net Nakit Akışı": "#2563eb",
        },
    )
    flow_chart.update_layout(height=430, legend_title_text="", yaxis_title="Tutar", xaxis_title="Dönem")
    st.plotly_chart(flow_chart, use_container_width=True)

    cumulative_chart = px.line(
        monthly_df,
        x="Dönem",
        y="Kümülatif Nakit",
        markers=True,
        title="Kümülatif Nakit Bakiyesi",
    )
    cumulative_chart.update_traces(line_color="#0f766e", line_width=4)
    cumulative_chart.update_layout(height=360, yaxis_title="Tutar", xaxis_title="Dönem")
    st.plotly_chart(cumulative_chart, use_container_width=True)

    flow_type_summary_df = cash_df.groupby("Akış Tipi", as_index=False).agg(
        {
            "Nakit Girişi": "sum",
            "Nakit Çıkışı": "sum",
            "Net Nakit Akışı": "sum",
        }
    ).sort_values("Net Nakit Akışı", ascending=False)

    table_col1, table_col2 = st.columns(2)
    with table_col1:
        st.markdown("**Aylık Özet**")
        create_aggrid_table(
            monthly_df,
            height=320,
            currency_cols=["Nakit Girişi", "Nakit Çıkışı", "Net Nakit Akışı", "Kümülatif Nakit"],
            integer_cols=["İşlem Sayısı"],
        )
    with table_col2:
        st.markdown("**Akış Tipi Özeti**")
        create_aggrid_table(
            flow_type_summary_df,
            height=320,
            currency_cols=["Nakit Girişi", "Nakit Çıkışı", "Net Nakit Akışı"],
        )

    render_cost_analysis_banner(
        title="Detaylı Nakit Hareketleri",
        subtitle="Planlanan tüm tahsilat, kesinti ve ödeme hareketleri tarih sırasına göre listelenir.",
        tone="emerald",
        eyebrow="Detay",
    )
    create_aggrid_table(
        cash_df,
        height=430,
        currency_cols=["Nakit Girişi", "Nakit Çıkışı", "Net Nakit Akışı", "Kümülatif Nakit"],
    )

    export_buffer = BytesIO()
    with pd.ExcelWriter(export_buffer, engine="openpyxl") as writer:
        prepare_dataframe_for_excel_export(monthly_df).to_excel(writer, sheet_name="Aylik_Ozet", index=False)
        prepare_dataframe_for_excel_export(flow_type_summary_df).to_excel(writer, sheet_name="Akis_Tipi_Ozeti", index=False)
        prepare_dataframe_for_excel_export(edited_product_plan_df).to_excel(writer, sheet_name="UrunGrubu_Odeme_Plani", index=False)
        prepare_dataframe_for_excel_export(collection_plan_df).to_excel(writer, sheet_name="Tahsilat_Plani", index=False)
        export_detail_df = cash_df.copy()
        export_detail_df["Tarih"] = export_detail_df["Tarih"].dt.strftime("%d.%m.%Y")
        prepare_dataframe_for_excel_export(export_detail_df).to_excel(writer, sheet_name="Nakit_Hareketleri", index=False)
        for worksheet in writer.book.worksheets:
            style_excel_sheet(worksheet)

    export_buffer.seek(0)
    st.download_button(
        label="Nakit Akış Excel Çıktısı İndir",
        data=export_buffer.getvalue(),
        file_name=f"nakit_akis_analiz_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

def get_customer_boq_debug_paths():
    base_path = Path(__file__).resolve().parent
    return (
        base_path / "boq_debug_latest.log",
        base_path / "boq_debug_latest.csv",
    )

def write_customer_boq_debug_outputs(
    uploaded_file_name,
    selected_sheets,
    column_config,
    memory_df,
    analysis_df,
    issues,
):
    log_path, csv_path = get_customer_boq_debug_paths()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_lines = [
        "=== CUSTOMER BOQ DEBUG LOG ===",
        f"Timestamp: {timestamp}",
        f"Source File: {uploaded_file_name}",
        f"Selected Sheets: {', '.join(selected_sheets) if selected_sheets else '-'}",
        (
            "Column Config: "
            f"Urun Aciklamasi={index_to_excel_column(column_config['urun_aciklama'])}, "
            f"Malzeme={index_to_excel_column(column_config['malzeme'])}, "
            f"Iscilik={index_to_excel_column(column_config['iscilik'])}, "
            f"GGK={index_to_excel_column(column_config['ggk'])}, "
            f"Genel Toplam={index_to_excel_column(column_config['genel_toplam'])}"
        ),
        "",
    ]

    if issues:
        log_lines.append("Issues:")
        for issue in issues:
            log_lines.append(f"- {issue}")
        log_lines.append("")

    if not memory_df.empty:
        row_type_counts = memory_df["Kayıt Tipi"].value_counts().to_dict()
        log_lines.append("Row Type Counts:")
        for row_type, count in row_type_counts.items():
            log_lines.append(f"- {row_type}: {count}")
        log_lines.append("")

        sheet_memory_summary = memory_df.groupby(["Sayfa", "Kayıt Tipi"], as_index=False).size()
        if not sheet_memory_summary.empty:
            log_lines.append("Sheet / Row Type Summary:")
            for _, row in sheet_memory_summary.iterrows():
                log_lines.append(f"- {row['Sayfa']} | {row['Kayıt Tipi']} | {int(row['size'])}")
            log_lines.append("")

    if not analysis_df.empty:
        sheet_summary_df = analysis_df.groupby("Sayfa", as_index=False).agg(
            {
                "Malzeme Fiyatı": "sum",
                "İşçilik Fiyatı": "sum",
                "GGK Fiyatı": "sum",
                "Excel Genel Toplam": "sum",
                "Analiz Genel Toplamı": "sum",
                "Excel Satır No": "count",
            }
        )
        sheet_summary_df.rename(columns={"Excel Satır No": "Bulunan Kayıt Sayısı"}, inplace=True)
        sheet_summary_df["Toplam Farkı"] = (
            sheet_summary_df["Excel Genel Toplam"] - sheet_summary_df["Analiz Genel Toplamı"]
        ).round(2)

        log_lines.append("Analysis Sheet Summary:")
        for _, row in sheet_summary_df.iterrows():
            log_lines.append(
                " | ".join(
                    [
                        str(row["Sayfa"]),
                        f"Kayit={int(row['Bulunan Kayıt Sayısı'])}",
                        f"Malzeme={format_currency_display(row['Malzeme Fiyatı'])}",
                        f"Iscilik={format_currency_display(row['İşçilik Fiyatı'])}",
                        f"GGK={format_currency_display(row['GGK Fiyatı'])}",
                        f"ExcelToplam={format_currency_display(row['Excel Genel Toplam'])}",
                        f"AnalizToplam={format_currency_display(row['Analiz Genel Toplamı'])}",
                        f"Fark={format_currency_display(row['Toplam Farkı'])}",
                    ]
                )
            )
        log_lines.append("")

        mismatch_df = analysis_df[
            (analysis_df["Excel Genel Toplam"].abs() > 0)
            & (analysis_df["Hesaplanan Satır Toplamı"].abs() > 0)
            & (analysis_df["Toplam Farkı"].abs() > 0.01)
        ].copy()
        mismatch_df = mismatch_df.sort_values("Toplam Farkı", key=lambda s: s.abs(), ascending=False)

        log_lines.append(f"Mismatch Row Count: {len(mismatch_df)}")
        if not mismatch_df.empty:
            log_lines.append("Top Mismatch Rows:")
            for _, row in mismatch_df.head(50).iterrows():
                log_lines.append(
                    " | ".join(
                        [
                            str(row["Sayfa"]),
                            f"Satir={int(row['Excel Satır No'])}",
                            f"Aciklama={str(row['Ürün Açıklaması'])}",
                            f"Malzeme={format_currency_display(row['Malzeme Fiyatı'])}",
                            f"Iscilik={format_currency_display(row['İşçilik Fiyatı'])}",
                            f"GGK={format_currency_display(row['GGK Fiyatı'])}",
                            f"ExcelToplam={format_currency_display(row['Excel Genel Toplam'])}",
                            f"Hesaplanan={format_currency_display(row['Hesaplanan Satır Toplamı'])}",
                            f"Fark={format_currency_display(row['Toplam Farkı'])}",
                        ]
                    )
                )
            log_lines.append("")

        top_rows_df = analysis_df.sort_values("Analiz Genel Toplamı", ascending=False).head(100)
        log_lines.append("Top Analysis Rows:")
        for _, row in top_rows_df.iterrows():
            log_lines.append(
                " | ".join(
                    [
                        str(row["Sayfa"]),
                        f"Satir={int(row['Excel Satır No'])}",
                        f"Aciklama={str(row['Ürün Açıklaması'])}",
                        f"AnalizToplam={format_currency_display(row['Analiz Genel Toplamı'])}",
                        f"ExcelToplam={format_currency_display(row['Excel Genel Toplam'])}",
                        f"KayitTipi={str(row['Kayıt Tipi'])}",
                    ]
                )
            )
        log_lines.append("")

    log_path.write_text("\n".join(log_lines), encoding="utf-8")

    if memory_df is not None and not memory_df.empty:
        memory_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    else:
        csv_path.write_text("", encoding="utf-8")

    return log_path, csv_path

def read_boq_numeric_cell(row, col_index):
    if col_index is None or col_index < 0 or len(row) <= col_index or pd.isna(row.iloc[col_index]):
        return 0.0

    cell_value = row.iloc[col_index]
    if isinstance(cell_value, (int, float)):
        return float(cell_value)

    text_value = str(cell_value).strip().replace(" ", "").replace("₺", "")
    text_value = text_value.replace("TL", "").replace("tl", "")
    if not text_value:
        return 0.0

    if "," in text_value and "." in text_value:
        if text_value.rfind(",") > text_value.rfind("."):
            text_value = text_value.replace(".", "").replace(",", ".")
        else:
            text_value = text_value.replace(",", "")
    elif "," in text_value:
        text_value = text_value.replace(",", ".")

    try:
        return float(text_value)
    except ValueError:
        return 0.0

def read_boq_text_cell(row, col_index):
    if col_index is None or col_index < 0 or len(row) <= col_index or pd.isna(row.iloc[col_index]):
        return ""
    return str(row.iloc[col_index]).strip()

def is_boq_numeric_like(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    if isinstance(value, (int, float)):
        return True

    text_value = str(value).strip().replace(" ", "").replace("₺", "")
    text_value = text_value.replace("TL", "").replace("tl", "").replace("%", "")
    if not text_value:
        return False

    if "," in text_value and "." in text_value:
        if text_value.rfind(",") > text_value.rfind("."):
            text_value = text_value.replace(".", "").replace(",", ".")
        else:
            text_value = text_value.replace(",", "")
    elif "," in text_value:
        text_value = text_value.replace(",", ".")

    try:
        float(text_value)
        return True
    except ValueError:
        return False

def score_boq_description_candidate(value):
    text_value = "" if value is None else str(value).strip()
    if not text_value:
        return -1000
    if is_boq_numeric_like(text_value):
        return -500

    normalized = normalize_excel_header_name(text_value)
    compact = " ".join(normalized.replace(":", " ").replace("-", " ").split())
    if not compact:
        return -1000

    if should_skip_boq_description(text_value):
        return 100

    score = 0
    if any(char.isalpha() for char in text_value):
        score += 14
    if " " in text_value:
        score += 5
    if len(text_value) >= 8:
        score += 4
    if len(text_value) >= 20:
        score += 3

    if compact in {"ADET", "PCS", "EA", "M", "M2", "M3", "KG", "MT", "SET", "LOT"}:
        score -= 12
    if len(compact.split()) == 1 and len(text_value) <= 4:
        score -= 8
    if any(token in compact for token in ["BIRIM", "MIKTAR", "QTY", "QUANTITY", "NO", "SIRA"]):
        score -= 10

    return score

def resolve_boq_description_from_row(row, preferred_col_index):
    preferred_text = read_boq_text_cell(row, preferred_col_index)
    if preferred_text:
        return preferred_text, preferred_col_index, "Seçilen Kolon"
    return "", preferred_col_index, "Boş"

def should_skip_boq_description(description):
    normalized = normalize_excel_header_name(description)
    normalized_compact = " ".join(normalized.replace(":", " ").replace("-", " ").split())
    skip_contains = [
        "TOPLAM",
        "TOPLAMI",
        "GENEL TOPLAM",
        "GENEL TOPLAMI",
        "ARA TOPLAM",
        "ARA TOPLAMI",
        "ALT TOPLAM",
        "ALT TOPLAMI",
        "SUBTOTAL",
        "GRAND TOTAL",
        "TOTAL",
        "PAGE TOTAL",
        "SAYFA TOPLAMI",
        "ITEM DESCRIPTION",
        "URUN ACIKLAMASI",
        "ACIKLAMA",
        "DESCRIPTION",
    ]
    for label in skip_contains:
        if label in normalized_compact:
            return True
    return False

def classify_customer_boq_row(description, excel_total, calculated_total):
    clean_description = str(description or "").strip()
    has_excel_total = abs(float(excel_total or 0.0)) > 0
    has_calculated_total = abs(float(calculated_total or 0.0)) > 0

    if not clean_description and not has_excel_total and not has_calculated_total:
        return "Boş"
    if should_skip_boq_description(clean_description):
        return "Toplam/Başlık"
    if not clean_description and (has_excel_total or has_calculated_total):
        return "Açıklama Eksik"
    if clean_description and not has_excel_total and not has_calculated_total:
        return "Metin"
    return "Veri"

def build_customer_boq_memory_table(
    excel_source,
    sheet_names,
    urun_aciklama_col_index,
    malzeme_col_index,
    iscilik_col_index,
    ggk_col_index,
    genel_toplam_col_index,
):
    selected_indices = [
        urun_aciklama_col_index,
        malzeme_col_index,
        iscilik_col_index,
        ggk_col_index,
        genel_toplam_col_index,
    ]
    selected_indices = [idx for idx in selected_indices if idx is not None]
    if not selected_indices:
        return pd.DataFrame(), ["Kolon seçimi yapılmadı."]

    required_max_col = max(selected_indices)
    all_rows = []
    issues = []

    for sheet_name in sheet_names:
        try:
            df = pd.read_excel(excel_source, sheet_name=sheet_name, header=None)
        except Exception as exc:
            issues.append(f"{sheet_name}: {str(exc)}")
            continue

        if urun_aciklama_col_index is None or len(df.columns) <= required_max_col:
            issues.append(f"{sheet_name}: seçilen kolonlar bu sayfada bulunamadı.")
            continue

        monetary_row_count = 0
        selected_blank_count = 0
        selected_numeric_like_count = 0
        fallback_description_count = 0
        total_label_row_count = 0

        for idx, row in df.iterrows():
            try:
                malzeme_fiyati = read_boq_numeric_cell(row, malzeme_col_index)
                iscilik_fiyati = read_boq_numeric_cell(row, iscilik_col_index)
                ggk_fiyati = read_boq_numeric_cell(row, ggk_col_index)
                excel_genel_toplam = read_boq_numeric_cell(row, genel_toplam_col_index)
                hesaplanan_satir_toplami = round(malzeme_fiyati + iscilik_fiyati + ggk_fiyati, 2)
                secilen_aciklama = read_boq_text_cell(row, urun_aciklama_col_index)
                urun_aciklamasi, aciklama_col_index, aciklama_kaynagi = resolve_boq_description_from_row(
                    row,
                    urun_aciklama_col_index,
                )
                kayit_tipi = classify_customer_boq_row(
                    urun_aciklamasi,
                    excel_genel_toplam,
                    hesaplanan_satir_toplami,
                )

                if abs(excel_genel_toplam) > 0 or abs(hesaplanan_satir_toplami) > 0:
                    monetary_row_count += 1
                    if not secilen_aciklama:
                        selected_blank_count += 1
                    elif is_boq_numeric_like(secilen_aciklama):
                        selected_numeric_like_count += 1
                    if aciklama_kaynagi == "Satır Taraması":
                        fallback_description_count += 1
                    elif aciklama_kaynagi == "Toplam/Başlık Etiketi":
                        total_label_row_count += 1

                if kayit_tipi == "Boş":
                    continue

                analiz_genel_toplam = excel_genel_toplam

                all_rows.append(
                    {
                        "Sayfa": sheet_name,
                        "Excel Satır No": idx + 1,
                        "Ürün Açıklaması": urun_aciklamasi,
                        "Açıklama Kaynağı": aciklama_kaynagi,
                        "Açıklama Kolonu": index_to_excel_column(aciklama_col_index),
                        "Malzeme Fiyatı": malzeme_fiyati,
                        "İşçilik Fiyatı": iscilik_fiyati,
                        "GGK Fiyatı": ggk_fiyati,
                        "Excel Genel Toplam": excel_genel_toplam,
                        "Hesaplanan Satır Toplamı": hesaplanan_satir_toplami,
                        "Analiz Genel Toplamı": analiz_genel_toplam,
                        "Toplam Farkı": round(excel_genel_toplam - hesaplanan_satir_toplami, 2),
                        "Kayıt Tipi": kayit_tipi,
                    }
                )
            except Exception:
                continue

        if monetary_row_count > 0:
            selected_problem_count = selected_blank_count + selected_numeric_like_count
            if selected_problem_count / monetary_row_count >= 0.5:
                issues.append(
                    f"{sheet_name}: seçilen açıklama kolonu "
                    f"{index_to_excel_column(urun_aciklama_col_index)} çoğunlukla boş/sayısal göründü "
                    f"({selected_problem_count}/{monetary_row_count}). "
                    f"{fallback_description_count} satır satır taramasıyla, "
                    f"{total_label_row_count} satır toplam etiketiyle çözüldü."
                )

    return pd.DataFrame(all_rows), issues

def render_customer_boq_analysis(
    uploaded_file,
    selected_sheets,
    urun_aciklama_col_index,
    malzeme_col_index,
    iscilik_col_index,
    ggk_col_index,
    genel_toplam_col_index,
):
    render_cost_analysis_page_styles()

    render_cost_analysis_banner(
        title="Müşteri BOQ Analiz",
        subtitle="Bu görünüm mevcut maliyet akışından ayrıdır. Seçtiğiniz ortak kolonlar tüm seçili sayfalara uygulanır ve her sayfa kendi bölümünde analiz edilir.",
        tone="amber",
        eyebrow="Yeni Görünüm",
        chips=[
            escape(str(uploaded_file.name)),
            f"{len(selected_sheets)} seçili sayfa",
            f"Açıklama: {index_to_excel_column(urun_aciklama_col_index)}",
            f"Toplam: {index_to_excel_column(genel_toplam_col_index)}",
        ],
    )

    if not selected_sheets:
        st.info("Müşteri BOQ Analiz için yan panelden en az bir sayfa seçin.")
        return

    memory_df, issues = build_customer_boq_memory_table(
        excel_source=uploaded_file,
        sheet_names=selected_sheets,
        urun_aciklama_col_index=urun_aciklama_col_index,
        malzeme_col_index=malzeme_col_index,
        iscilik_col_index=iscilik_col_index,
        ggk_col_index=ggk_col_index,
        genel_toplam_col_index=genel_toplam_col_index,
    )

    if issues:
        preview_text = " | ".join(issues[:4])
        if len(issues) > 4:
            preview_text += " | ..."
        st.warning(f"BOQ teşhis notları: {preview_text}")

    if memory_df.empty:
        st.warning("Seçilen kolonlarla analiz edilebilir BOQ satırı bulunamadı.")
        return

    analysis_df = memory_df[
        memory_df["Kayıt Tipi"].isin(["Veri", "Açıklama Eksik"])
    ].copy()
    if analysis_df.empty:
        st.warning("Hafıza tablosu oluşturuldu ancak analize girecek satır bulunamadı.")
        return

    row_type_counts = memory_df["Kayıt Tipi"].value_counts().to_dict()
    mismatch_mask = (
        (analysis_df["Excel Genel Toplam"].abs() > 0)
        & (analysis_df["Hesaplanan Satır Toplamı"].abs() > 0)
        & ((analysis_df["Toplam Farkı"].abs()) > 0.01)
    )
    mismatch_count = int(mismatch_mask.sum())

    render_cost_action_shell(
        title="Yeni BOQ hattı: önce hafıza tablosu, sonra analiz",
        subtitle=(
            f"Seçtiğiniz kolonlardaki veri satırları toplanıyor; metin ve toplam/başlık satırları analiz dışında bırakılıyor. "
            f"Genel toplam için seçilen {index_to_excel_column(genel_toplam_col_index)} kolonu kullanılıyor. "
            f"Veri: {row_type_counts.get('Veri', 0)} | "
            f"Toplam/Başlık: {row_type_counts.get('Toplam/Başlık', 0)} | "
            f"Açıklama Eksik: {row_type_counts.get('Açıklama Eksik', 0)} | "
            f"Metin: {row_type_counts.get('Metin', 0)}"
        ),
    )

    if mismatch_count > 0:
        st.warning(
            f"{mismatch_count} satırda Excel Genel Toplam ile Malzeme+İşçilik+GGK toplamı uyuşmuyor. "
            "Özetlerde doğrudan seçilen Genel Toplam kolonu kullanılıyor."
        )

    debug_log_path, debug_csv_path = write_customer_boq_debug_outputs(
        uploaded_file_name=uploaded_file.name,
        selected_sheets=selected_sheets,
        column_config={
            "urun_aciklama": urun_aciklama_col_index,
            "malzeme": malzeme_col_index,
            "iscilik": iscilik_col_index,
            "ggk": ggk_col_index,
            "genel_toplam": genel_toplam_col_index,
        },
        memory_df=memory_df,
        analysis_df=analysis_df,
        issues=issues,
    )

    debug_col1, debug_col2 = st.columns(2)
    with debug_col1:
        st.download_button(
            "BOQ Debug Log İndir",
            data=debug_log_path.read_text(encoding="utf-8"),
            file_name=debug_log_path.name,
            mime="text/plain",
            use_container_width=True,
            key="download_boq_debug_log",
        )
    with debug_col2:
        st.download_button(
            "BOQ Hafıza CSV İndir",
            data=debug_csv_path.read_bytes(),
            file_name=debug_csv_path.name,
            mime="text/csv",
            use_container_width=True,
            key="download_boq_debug_csv",
        )
    st.caption(f"Debug çıktıları yazıldı: {debug_log_path.name}, {debug_csv_path.name}")

    with st.expander("BOQ hafıza tablosu"):
        create_aggrid_table(
            memory_df[
                [
                    "Sayfa",
                    "Excel Satır No",
                    "Ürün Açıklaması",
                    "Açıklama Kaynağı",
                    "Açıklama Kolonu",
                    "Malzeme Fiyatı",
                    "İşçilik Fiyatı",
                    "GGK Fiyatı",
                    "Excel Genel Toplam",
                    "Hesaplanan Satır Toplamı",
                    "Analiz Genel Toplamı",
                    "Toplam Farkı",
                    "Kayıt Tipi",
                ]
            ],
            height=420,
            currency_cols=[
                "Malzeme Fiyatı",
                "İşçilik Fiyatı",
                "GGK Fiyatı",
                "Excel Genel Toplam",
                "Hesaplanan Satır Toplamı",
                "Analiz Genel Toplamı",
                "Toplam Farkı",
            ],
            integer_cols=["Excel Satır No"],
        )

    total_malzeme = float(analysis_df["Malzeme Fiyatı"].sum())
    total_iscilik = float(analysis_df["İşçilik Fiyatı"].sum())
    total_ggk = float(analysis_df["GGK Fiyatı"].sum())
    total_genel = float(analysis_df["Analiz Genel Toplamı"].sum())

    render_cost_summary_cards(total_malzeme, total_iscilik, total_ggk, total_genel)

    render_cost_analysis_banner(
        title="Sayfa Bazında Genel Özet",
        subtitle="Özetler satır hafıza tablosundan üretilir. Sayfa toplamı için seçilen Genel Toplam kolonu doğrudan kullanılır.",
        tone="cobalt",
        eyebrow="Özet Tablo",
    )

    sheet_summary_df = analysis_df.groupby("Sayfa", as_index=False).agg(
        {
            "Malzeme Fiyatı": "sum",
            "İşçilik Fiyatı": "sum",
            "GGK Fiyatı": "sum",
            "Excel Genel Toplam": "sum",
            "Analiz Genel Toplamı": "sum",
            "Excel Satır No": "count",
        }
    )
    sheet_summary_df.rename(columns={"Excel Satır No": "Bulunan Kayıt Sayısı"}, inplace=True)
    sheet_summary_df["Toplam Farkı"] = (
        sheet_summary_df["Excel Genel Toplam"] - sheet_summary_df["Analiz Genel Toplamı"]
    ).round(2)
    sheet_summary_df = sheet_summary_df.sort_values("Analiz Genel Toplamı", ascending=False).reset_index(drop=True)
    if total_genel > 0:
        sheet_summary_df["Genel Toplam %"] = (sheet_summary_df["Analiz Genel Toplamı"] / total_genel * 100).round(2)
    else:
        sheet_summary_df["Genel Toplam %"] = 0.0

    create_aggrid_table(
        sheet_summary_df,
        height=min(420, 140 + len(sheet_summary_df) * 42),
        currency_cols=[
            "Malzeme Fiyatı",
            "İşçilik Fiyatı",
            "GGK Fiyatı",
            "Excel Genel Toplam",
            "Analiz Genel Toplamı",
            "Toplam Farkı",
        ],
        percent_cols=["Genel Toplam %"],
        integer_cols=["Bulunan Kayıt Sayısı"],
    )

    if len(sheet_summary_df) > 1:
        fig_sheet_summary = px.bar(
            sheet_summary_df,
            x="Sayfa",
            y="Analiz Genel Toplamı",
            color="Genel Toplam %",
            color_continuous_scale="Blues",
            text="Genel Toplam %",
            title="Sayfalara Göre Genel Toplam Dağılımı",
        )
        fig_sheet_summary.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_sheet_summary.update_layout(height=420, xaxis_tickangle=0)
        st.plotly_chart(fig_sheet_summary, use_container_width=True)

    render_cost_analysis_banner(
        title="Tüm Sayfalarda Ürün Bazında Genel Özet",
        subtitle="Seçili tüm sayfaların ürün kalemleri birleştirilip açıklamaya göre gruplanır ve en yüksekten en aza sıralanır.",
        tone="violet",
        eyebrow="Tüm Sayfalar Birleşik",
    )

    all_aciklama_ozet_df = analysis_df[
        [
            "Sayfa",
            "Excel Satır No",
            "Ürün Açıklaması",
            "Malzeme Fiyatı",
            "İşçilik Fiyatı",
            "GGK Fiyatı",
            "Excel Genel Toplam",
            "Analiz Genel Toplamı",
        ]
    ].copy()
    all_aciklama_ozet_df["Toplam Farkı"] = (
        all_aciklama_ozet_df["Excel Genel Toplam"] - all_aciklama_ozet_df["Analiz Genel Toplamı"]
    ).round(2)
    all_aciklama_ozet_df = all_aciklama_ozet_df.sort_values("Analiz Genel Toplamı", ascending=False).reset_index(drop=True)
    if total_genel > 0:
        all_aciklama_ozet_df["Genel Toplam %"] = (all_aciklama_ozet_df["Analiz Genel Toplamı"] / total_genel * 100).round(2)
    else:
        all_aciklama_ozet_df["Genel Toplam %"] = 0.0

    top_all_chart_df = all_aciklama_ozet_df.head(20).copy()
    top_all_chart_df["Kısa Açıklama"] = top_all_chart_df["Ürün Açıklaması"].apply(
        lambda value: value if len(str(value)) <= 55 else f"{str(value)[:52]}..."
    )

    if not top_all_chart_df.empty:
        fig_all_items = px.bar(
            top_all_chart_df,
            x="Kısa Açıklama",
            y="Analiz Genel Toplamı",
            color="Genel Toplam %",
            color_continuous_scale="Purples",
            text="Genel Toplam %",
            title="Tüm Sayfalarda En Yüksek Genel Toplamlı Kalemler (İlk 20)",
        )
        fig_all_items.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_all_items.update_layout(height=480, xaxis_tickangle=-35)
        st.plotly_chart(fig_all_items, use_container_width=True)

    create_aggrid_table(
        all_aciklama_ozet_df[
            [
                "Sayfa",
                "Excel Satır No",
                "Ürün Açıklaması",
                "Malzeme Fiyatı",
                "İşçilik Fiyatı",
                "GGK Fiyatı",
                "Excel Genel Toplam",
                "Analiz Genel Toplamı",
                "Toplam Farkı",
                "Genel Toplam %",
            ]
        ],
        height=420,
        currency_cols=[
            "Malzeme Fiyatı",
            "İşçilik Fiyatı",
            "GGK Fiyatı",
            "Excel Genel Toplam",
            "Analiz Genel Toplamı",
            "Toplam Farkı",
        ],
        percent_cols=["Genel Toplam %"],
        integer_cols=["Excel Satır No"],
    )

    render_cost_analysis_banner(
        title="Sayfa Detayları",
        subtitle="Her seçili sayfa önce hafıza tablosunda saklanır, ardından yalnızca veri satırları ürün açıklamasına göre gruplanır.",
        tone="emerald",
        eyebrow="Detay Analiz",
    )

    for sheet_name in selected_sheets:
        sheet_memory_df = memory_df[memory_df["Sayfa"] == sheet_name].copy()
        sheet_df = analysis_df[analysis_df["Sayfa"] == sheet_name].copy()
        render_subsection_heading(f"{sheet_name} Sayfası", icon="")

        if sheet_memory_df.empty:
            st.info(f"{sheet_name} sayfasında seçilen kolonlarla gösterilecek satır bulunamadı.")
            continue

        if sheet_df.empty:
            st.info(f"{sheet_name} sayfasında hafıza tablosu oluştu ancak analize girecek veri satırı bulunamadı.")
            with st.expander(f"{sheet_name} hafıza tablosu"):
                create_aggrid_table(
                    sheet_memory_df[
                        [
                            "Excel Satır No",
                            "Ürün Açıklaması",
                            "Malzeme Fiyatı",
                            "İşçilik Fiyatı",
                            "GGK Fiyatı",
                            "Excel Genel Toplam",
                            "Hesaplanan Satır Toplamı",
                            "Toplam Farkı",
                            "Kayıt Tipi",
                        ]
                    ],
                    height=360,
                    currency_cols=[
                        "Malzeme Fiyatı",
                        "İşçilik Fiyatı",
                        "GGK Fiyatı",
                        "Excel Genel Toplam",
                        "Hesaplanan Satır Toplamı",
                        "Toplam Farkı",
                    ],
                    integer_cols=["Excel Satır No"],
                )
            continue

        sheet_total = float(sheet_df["Analiz Genel Toplamı"].sum())
        sheet_malzeme = float(sheet_df["Malzeme Fiyatı"].sum())
        sheet_iscilik = float(sheet_df["İşçilik Fiyatı"].sum())
        sheet_ggk = float(sheet_df["GGK Fiyatı"].sum())
        sheet_excel_total = float(sheet_df["Excel Genel Toplam"].sum())

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        metric_col1.metric("Kayıt Sayısı", format_integer_display(len(sheet_df)))
        metric_col2.metric("Malzeme", format_currency_display(sheet_malzeme))
        metric_col3.metric("İşçilik", format_currency_display(sheet_iscilik))
        metric_col4.metric("Genel Toplam", format_currency_display(sheet_total))

        st.caption(
            f"Excel Genel Toplam sütunu toplamı: {format_currency_display(sheet_excel_total)} | "
            f"Analizde kullanılan toplam: {format_currency_display(sheet_total)}"
        )

        aciklama_ozet_df = sheet_df[
            [
                "Excel Satır No",
                "Ürün Açıklaması",
                "Malzeme Fiyatı",
                "İşçilik Fiyatı",
                "GGK Fiyatı",
                "Excel Genel Toplam",
                "Analiz Genel Toplamı",
            ]
        ].copy()
        aciklama_ozet_df["Toplam Farkı"] = (
            aciklama_ozet_df["Excel Genel Toplam"] - aciklama_ozet_df["Analiz Genel Toplamı"]
        ).round(2)
        aciklama_ozet_df = aciklama_ozet_df.sort_values("Analiz Genel Toplamı", ascending=False).reset_index(drop=True)
        if sheet_total > 0:
            aciklama_ozet_df["Genel Toplam %"] = (aciklama_ozet_df["Analiz Genel Toplamı"] / sheet_total * 100).round(2)
        else:
            aciklama_ozet_df["Genel Toplam %"] = 0.0

        top_chart_df = aciklama_ozet_df.head(15).copy()
        top_chart_df["Kısa Açıklama"] = top_chart_df["Ürün Açıklaması"].apply(
            lambda value: value if len(str(value)) <= 55 else f"{str(value)[:52]}..."
        )

        if not top_chart_df.empty:
            fig_top_items = px.bar(
                top_chart_df,
                x="Kısa Açıklama",
                y="Analiz Genel Toplamı",
                color="Analiz Genel Toplamı",
                color_continuous_scale="Tealgrn",
                text="Genel Toplam %",
                title=f"{sheet_name} - En Yüksek Genel Toplamlı Kalemler",
            )
            fig_top_items.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_top_items.update_layout(height=460, xaxis_tickangle=-35)
            st.plotly_chart(fig_top_items, use_container_width=True)

        create_aggrid_table(
            aciklama_ozet_df[
                [
                    "Excel Satır No",
                    "Ürün Açıklaması",
                    "Malzeme Fiyatı",
                    "İşçilik Fiyatı",
                    "GGK Fiyatı",
                    "Excel Genel Toplam",
                    "Analiz Genel Toplamı",
                    "Toplam Farkı",
                    "Genel Toplam %",
                ]
            ],
            height=360,
            currency_cols=[
                "Malzeme Fiyatı",
                "İşçilik Fiyatı",
                "GGK Fiyatı",
                "Excel Genel Toplam",
                "Analiz Genel Toplamı",
                "Toplam Farkı",
            ],
            percent_cols=["Genel Toplam %"],
            integer_cols=["Excel Satır No"],
        )

        with st.expander(f"{sheet_name} hafıza tablosu"):
            raw_detail_df = sheet_memory_df[
                [
                    "Excel Satır No",
                    "Ürün Açıklaması",
                    "Malzeme Fiyatı",
                    "İşçilik Fiyatı",
                    "GGK Fiyatı",
                    "Excel Genel Toplam",
                    "Hesaplanan Satır Toplamı",
                    "Analiz Genel Toplamı",
                    "Toplam Farkı",
                    "Kayıt Tipi",
                ]
            ].sort_values("Analiz Genel Toplamı", ascending=False)
            create_aggrid_table(
                raw_detail_df,
                height=360,
                currency_cols=[
                    "Malzeme Fiyatı",
                    "İşçilik Fiyatı",
                    "GGK Fiyatı",
                    "Excel Genel Toplam",
                    "Hesaplanan Satır Toplamı",
                    "Analiz Genel Toplamı",
                    "Toplam Farkı",
                ],
                integer_cols=["Excel Satır No"],
            )

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
                options=["Maliyet Analizi", "Tutarlılık ve Geçmiş Kıyas", "Fiyat Revizyon Kıyas", "Müşteri BOQ ANALİZ", "Nakit Akış Analiz"],
                key="page_mode_selector"
            )
            is_customer_boq_mode = page_mode == "Müşteri BOQ ANALİZ"
            is_cash_flow_mode = page_mode == "Nakit Akış Analiz"

            st.sidebar.markdown('<div class="sidebar-modern-header">Analiz Ayarları</div>', unsafe_allow_html=True)
            if is_customer_boq_mode:
                sheet_selection_title = "Müşteri BOQ Analiz - Sayfa Seçimi"
            elif is_cash_flow_mode:
                sheet_selection_title = "Nakit Akış Analiz - Sayfa Seçimi"
            else:
                sheet_selection_title = "Maliyet Analizi - Sayfa Seçimi"
            st.sidebar.markdown(f'<div class="sidebar-section-title">{sheet_selection_title}</div>', unsafe_allow_html=True)
            cost_analysis_sheets = []
            if available_cost_sheets:
                for sheet in available_cost_sheets:
                    if st.sidebar.checkbox(sheet, key=f"cost_sheet_{sheet}"):
                        cost_analysis_sheets.append(sheet)
            else:
                st.sidebar.info("Analiz edilecek sayfa bulunamadı.")

            genel_gider_enabled = False
            if not is_customer_boq_mode and not is_cash_flow_mode:
                st.sidebar.markdown('<div class="sidebar-section-title">💰 Genel Gider Analiz</div>', unsafe_allow_html=True)
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
            miktar_col_index = 6          # G
            birim_col_index = 7           # H
            malzeme_col_index = 21        # V
            iscilik_col_index = 23        # X
            ggk_col_index = 29            # AD
            genel_toplam_col_index = 31   # AF
            boq_urun_aciklama_col_index = urun_aciklama_col_index
            boq_malzeme_col_index = malzeme_col_index
            boq_iscilik_col_index = iscilik_col_index
            boq_ggk_col_index = ggk_col_index
            boq_genel_toplam_col_index = genel_toplam_col_index
            cash_date_col_index = None
            cash_description_col_index = None
            cash_in_col_index = None
            cash_out_col_index = None
            cash_net_col_index = None

            # İSKONTOLAR ürün grubu kolonu - dropdown
            if not is_customer_boq_mode and not is_cash_flow_mode and iskontolar_sheet_name is not None:
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
                header_source_options = cost_analysis_sheets if cost_analysis_sheets else available_cost_sheets
                default_header_sheet_index = 0

                def score_header_source_sheet(sheet_name):
                    candidate_columns, candidate_header_error = get_sheet_columns(excel_file, sheet_name)
                    if candidate_header_error is not None or not candidate_columns:
                        return -1

                    normalized_columns = [
                        normalize_excel_header_name(column_name)
                        for column_name in candidate_columns
                    ]
                    normalized_column_set = set(normalized_columns)
                    score = 0

                    expected_headers = {
                        "URUN GRUBU": 35,
                        "YAPILACAK ISIN CINSI": 18,
                        "URUN ACIKLAMASI": 18,
                        "ACIKLAMA": 12,
                        "MIKTAR": 12,
                        "BIRIM": 8,
                        "MALZEME FIYATI": 14,
                        "ISCILIK FIYATI": 14,
                        "GGK FIYATI": 14,
                        "GENEL TOPLAM": 20,
                    }
                    for header_name, header_score in expected_headers.items():
                        if header_name in normalized_column_set:
                            score += header_score

                    # Mevcut maliyet şablonunda kritik kolonlar sabit yerlerde.
                    # Sayfa adına bakmadan, seçili sayfalar içinde bu düzeni taşıyanı öne al.
                    layout_checks = [
                        (3, "URUN GRUBU", 25),
                        (4, "YAPILACAK ISIN CINSI", 10),
                        (4, "URUN ACIKLAMASI", 10),
                        (31, "GENEL TOPLAM", 15),
                    ]
                    for column_index, expected_header, layout_score in layout_checks:
                        if len(normalized_columns) > column_index and normalized_columns[column_index] == expected_header:
                            score += layout_score

                    if len(candidate_columns) > genel_toplam_col_index:
                        score += 6
                    elif len(candidate_columns) > malzeme_col_index:
                        score += 3

                    return score

                header_source_scores = [
                    score_header_source_sheet(sheet_name)
                    for sheet_name in header_source_options
                ]
                if header_source_scores:
                    default_header_sheet_index = max(
                        range(len(header_source_scores)),
                        key=lambda idx: header_source_scores[idx],
                    )

                if is_customer_boq_mode:
                    header_source_label = "BOQ kolon başlık kaynağı"
                    header_source_key_prefix = "boq_header_source_sheet"
                elif is_cash_flow_mode:
                    header_source_label = "Nakit akış kolon başlık kaynağı"
                    header_source_key_prefix = "cash_flow_header_source_sheet"
                else:
                    header_source_label = "Maliyet kolon başlık kaynağı"
                    header_source_key_prefix = "header_source_sheet"
                header_source_scope = abs(hash((str(uploaded_file.name), tuple(header_source_options))))
                header_source_key = f"{header_source_key_prefix}_{header_source_scope}"
                header_source_sheet = st.sidebar.selectbox(
                    header_source_label,
                    options=header_source_options,
                    index=default_header_sheet_index,
                    key=header_source_key,
                    help="Kolon adları, seçtiğiniz sayfalardan otomatik seçilen bu sayfadan okunur."
                )

                cost_columns, header_error = get_sheet_columns(excel_file, header_source_sheet)
                if header_error is not None:
                    st.sidebar.error(f"Kolon başlıkları okunamadı: {str(header_error)}")

                if cost_columns:
                    option_indices = list(range(len(cost_columns)))
                    column_selector_scope = abs(hash((
                        str(uploaded_file.name),
                        header_source_sheet,
                        tuple(header_source_options),
                        tuple(str(column_name) for column_name in cost_columns),
                    )))

                    def find_column_index(candidates, fallback_index):
                        normalized_candidates = [normalize_excel_header_name(candidate) for candidate in candidates]
                        for idx, column_name in enumerate(cost_columns):
                            normalized_column = normalize_excel_header_name(column_name)
                            if any(candidate == normalized_column for candidate in normalized_candidates):
                                return idx
                        for idx, column_name in enumerate(cost_columns):
                            normalized_column = normalize_excel_header_name(column_name)
                            if any(candidate in normalized_column for candidate in normalized_candidates):
                                return idx
                        return min(fallback_index, len(option_indices) - 1)

                    def format_column_option(col_idx):
                        raw_name = cost_columns[col_idx]
                        raw_text = "" if pd.isna(raw_name) else str(raw_name).strip()
                        excel_col = index_to_excel_column(col_idx)
                        if not raw_text or raw_text.lower().startswith("unnamed"):
                            return f"{excel_col} (Başlık yok)"
                        return f"{raw_text} ({excel_col})"

                    def find_optional_column_index(candidates):
                        candidate_index = find_column_index(candidates, len(option_indices) - 1)
                        normalized_candidates = [normalize_excel_header_name(candidate) for candidate in candidates]
                        if candidate_index < len(cost_columns):
                            normalized_column = normalize_excel_header_name(cost_columns[candidate_index])
                            if any(candidate == normalized_column or candidate in normalized_column for candidate in normalized_candidates):
                                return optional_indices.index(candidate_index)
                        return 0

                    optional_indices = [None] + option_indices

                    def format_optional_column_option(col_idx):
                        if col_idx is None:
                            return "Seçilmedi"
                        return format_column_option(col_idx)

                    if is_customer_boq_mode:
                        boq_urun_aciklama_col_index = st.sidebar.selectbox(
                            "Ürün Açıklaması kolonu",
                            options=option_indices,
                            index=find_column_index(["ÜRÜN AÇIKLAMASI", "YAPILACAK İŞİN CİNSİ", "ISIN CINSI", "ACIKLAMA", "DESCRIPTION", "ITEM DESCRIPTION"], 4),
                            format_func=format_column_option,
                            key=f"boq_urun_aciklama_col_selector_{column_selector_scope}"
                        )
                        boq_malzeme_col_index = st.sidebar.selectbox(
                            "Malzeme Fiyatı kolonu",
                            options=option_indices,
                            index=find_column_index(["MALZEME FİYATI", "MALZEME", "MATERIAL"], 21),
                            format_func=format_column_option,
                            key=f"boq_malzeme_col_selector_{column_selector_scope}"
                        )
                        boq_iscilik_col_index = st.sidebar.selectbox(
                            "İşçilik Fiyatı kolonu",
                            options=option_indices,
                            index=find_column_index(["İŞÇİLİK FİYATI", "ISCILIK", "LABOR"], 23),
                            format_func=format_column_option,
                            key=f"boq_iscilik_col_selector_{column_selector_scope}"
                        )
                        boq_ggk_col_index = st.sidebar.selectbox(
                            "GGK Fiyatı kolonu",
                            options=option_indices,
                            index=find_column_index(["GGK FİYATI", "GGK", "OVERHEAD"], 29),
                            format_func=format_column_option,
                            key=f"boq_ggk_col_selector_{column_selector_scope}"
                        )
                        boq_genel_toplam_col_index = st.sidebar.selectbox(
                            "Genel Toplam kolonu",
                            options=option_indices,
                            index=find_column_index(["GENEL TOPLAM", "TOPLAM", "TOTAL"], 31),
                            format_func=format_column_option,
                            key=f"boq_genel_toplam_col_selector_{column_selector_scope}"
                        )
                    elif False and is_cash_flow_mode:
                        cash_date_col_index = st.sidebar.selectbox(
                            "Tarih kolonu",
                            options=option_indices,
                            index=find_column_index(["TARİH", "TARIH", "DATE", "VADE", "ÖDEME TARİHİ", "ODEME TARIHI"], 0),
                            format_func=format_column_option,
                            key=f"cash_date_col_selector_{column_selector_scope}"
                        )
                        cash_description_col_index = st.sidebar.selectbox(
                            "Açıklama kolonu",
                            options=optional_indices,
                            index=find_optional_column_index(["AÇIKLAMA", "ACIKLAMA", "DESCRIPTION", "CARİ", "CARI", "FİRMA", "FIRMA", "MÜŞTERİ", "MUSTERI"]),
                            format_func=format_optional_column_option,
                            key=f"cash_description_col_selector_{column_selector_scope}"
                        )
                        cash_in_col_index = st.sidebar.selectbox(
                            "Nakit girişi kolonu",
                            options=optional_indices,
                            index=find_optional_column_index(["NAKİT GİRİŞ", "NAKIT GIRIS", "GİRİŞ", "GIRIS", "TAHSİLAT", "TAHSILAT", "GELİR", "GELIR", "BORÇ", "BORC"]),
                            format_func=format_optional_column_option,
                            key=f"cash_in_col_selector_{column_selector_scope}"
                        )
                        cash_out_col_index = st.sidebar.selectbox(
                            "Nakit çıkışı kolonu",
                            options=optional_indices,
                            index=find_optional_column_index(["NAKİT ÇIKIŞ", "NAKIT CIKIS", "ÇIKIŞ", "CIKIS", "ÖDEME", "ODEME", "GİDER", "GIDER", "ALACAK"]),
                            format_func=format_optional_column_option,
                            key=f"cash_out_col_selector_{column_selector_scope}"
                        )
                        cash_net_col_index = st.sidebar.selectbox(
                            "Net tutar kolonu",
                            options=optional_indices,
                            index=find_optional_column_index(["NET TUTAR", "NET", "TUTAR", "TUTARI", "BAKİYE", "BAKIYE", "AMOUNT"]),
                            format_func=format_optional_column_option,
                            key=f"cash_net_col_selector_{column_selector_scope}",
                            help="Giriş/çıkış ayrı kolonlarda değilse net tutar kolonunu seçin. Pozitif değer giriş, negatif değer çıkış kabul edilir."
                        )
                    else:
                        data_group_col_index = st.sidebar.selectbox(
                            "Maliyet sayfaları ürün grubu kolonu",
                            options=option_indices,
                            index=find_column_index(["ÜRÜN GRUBU", "URUN GRUBU", "PRODUCT GROUP"], 3),
                            format_func=format_column_option,
                            key=f"data_group_col_selector_{column_selector_scope}"
                        )
                        urun_aciklama_col_index = st.sidebar.selectbox(
                            "Ürün Açıklaması kolonu",
                            options=option_indices,
                            index=find_column_index(["ÜRÜN AÇIKLAMASI", "YAPILACAK İŞİN CİNSİ", "ISIN CINSI", "ACIKLAMA", "DESCRIPTION"], 4),
                            format_func=format_column_option,
                            key=f"urun_aciklama_col_selector_{column_selector_scope}"
                        )
                        miktar_col_index = st.sidebar.selectbox(
                            "Miktar kolonu",
                            options=option_indices,
                            index=find_column_index(["MİKTAR", "MIKTAR", "QTY", "QUANTITY", "MKT"], 6),
                            format_func=format_column_option,
                            key=f"miktar_col_selector_{column_selector_scope}"
                        )
                        default_birim_col_index = find_column_index(
                            ["BİRİM", "BIRIM", "UNIT"],
                            min(miktar_col_index + 1, len(option_indices) - 1),
                        )
                        birim_selector_key = f"birim_col_selector_{column_selector_scope}"
                        birim_auto_default_key = f"birim_col_selector_auto_default_{column_selector_scope}"
                        previous_auto_birim_index = st.session_state.get(birim_auto_default_key)
                        current_birim_index = st.session_state.get(birim_selector_key)
                        if current_birim_index is None:
                            st.session_state[birim_selector_key] = default_birim_col_index
                        elif previous_auto_birim_index is not None and current_birim_index == previous_auto_birim_index:
                            st.session_state[birim_selector_key] = default_birim_col_index
                        st.session_state[birim_auto_default_key] = default_birim_col_index
                        birim_col_index = st.sidebar.selectbox(
                            "Birim kolonu",
                            options=option_indices,
                            index=default_birim_col_index,
                            format_func=format_column_option,
                            key=birim_selector_key
                        )
                        malzeme_col_index = st.sidebar.selectbox(
                            "Malzeme Fiyatı kolonu",
                            options=option_indices,
                            index=find_column_index(["MALZEME FİYATI", "MALZEME", "MATERIAL"], 21),
                            format_func=format_column_option,
                            key=f"malzeme_col_selector_{column_selector_scope}"
                        )
                        iscilik_col_index = st.sidebar.selectbox(
                            "İşçilik Fiyatı kolonu",
                            options=option_indices,
                            index=find_column_index(["İŞÇİLİK FİYATI", "ISCILIK", "LABOR"], 23),
                            format_func=format_column_option,
                            key=f"iscilik_col_selector_{column_selector_scope}"
                        )
                        ggk_col_index = st.sidebar.selectbox(
                            "GGK Fiyatı kolonu",
                            options=option_indices,
                            index=find_column_index(["GGK FİYATI", "GGK", "OVERHEAD"], 29),
                            format_func=format_column_option,
                            key=f"ggk_col_selector_{column_selector_scope}"
                        )
                        genel_toplam_col_index = st.sidebar.selectbox(
                            "Genel Toplam kolonu",
                            options=option_indices,
                            index=find_column_index(["GENEL TOPLAM", "TOPLAM", "TOTAL"], 31),
                            format_func=format_column_option,
                            key=f"genel_toplam_col_selector_{column_selector_scope}"
                        )

            iskontolar_start_row = 3
            iskontolar_end_row = 27
            if not is_customer_boq_mode and not is_cash_flow_mode:
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
            if is_cash_flow_mode:
                render_cash_flow_analysis(
                    uploaded_file=uploaded_file,
                    selected_sheets=cost_analysis_sheets,
                    data_group_col_index=data_group_col_index,
                    malzeme_col_index=malzeme_col_index,
                    iscilik_col_index=iscilik_col_index,
                    ggk_col_index=ggk_col_index,
                    genel_toplam_col_index=genel_toplam_col_index,
                )
                st.stop()
            if is_customer_boq_mode:
                render_customer_boq_analysis(
                    uploaded_file=uploaded_file,
                    selected_sheets=cost_analysis_sheets,
                    urun_aciklama_col_index=boq_urun_aciklama_col_index,
                    malzeme_col_index=boq_malzeme_col_index,
                    iscilik_col_index=boq_iscilik_col_index,
                    ggk_col_index=boq_ggk_col_index,
                    genel_toplam_col_index=boq_genel_toplam_col_index,
                )
                st.stop()
            # Tek sekme olduğu için direkt içeriği göster
            # Ana sayfa başlığı - Özel büyük kart
            render_cost_analysis_page_styles()

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
                    else:
                        cleaned_product_groups = []
                        ignored_group_labels = {"", "0", "0.0", "NAN", "ÜRÜN GRUPLARI", "URUN GRUPLARI", "GENEL TOPLAM"}
                        for group_name in product_groups:
                            group_text = str(group_name).strip()
                            normalized_group_text = normalize_excel_header_name(group_text)
                            if normalized_group_text in ignored_group_labels:
                                continue
                            if group_text not in cleaned_product_groups:
                                cleaned_product_groups.append(group_text)
                        product_groups = cleaned_product_groups

                    render_cost_analysis_hero(
                        source_file_name=uploaded_file.name,
                        selected_sheets=cost_analysis_sheets,
                        product_group_count=len(product_groups),
                    )

                    if product_groups:
                        render_cost_analysis_banner(
                            title="Bulunan Urun Gruplari",
                            subtitle="ISKONTOLAR sayfasinda eslesen urun gruplari bu analiz havuzuna dahil edildi.",
                            tone="slate",
                            eyebrow="Kaynak Tarama",
                            chips=[
                                f"{len(product_groups)} urun grubu",
                                f"{len(cost_analysis_sheets)} secili sayfa",
                            ],
                        )
                        render_cost_analysis_group_catalog(product_groups)

                        if cost_analysis_sheets:
                            # Tüm sayfalardan veriyi tek tabloda topla
                            all_data = []

                            def read_numeric_cell(row, col_index):
                                if col_index is None or len(row) <= col_index or pd.isna(row.iloc[col_index]):
                                    return 0.0
                                cell_value = row.iloc[col_index]
                                if isinstance(cell_value, (int, float)):
                                    return float(cell_value)
                                text_value = str(cell_value).strip().replace(" ", "")
                                if not text_value:
                                    return 0.0
                                if "," in text_value and "." in text_value:
                                    if text_value.rfind(",") > text_value.rfind("."):
                                        text_value = text_value.replace(".", "").replace(",", ".")
                                    else:
                                        text_value = text_value.replace(",", "")
                                elif "," in text_value:
                                    text_value = text_value.replace(",", ".")
                                try:
                                    return float(text_value)
                                except ValueError:
                                    return 0.0

                            def read_text_cell(row, col_index):
                                if col_index is None or len(row) <= col_index or pd.isna(row.iloc[col_index]):
                                    return ""
                                return str(row.iloc[col_index]).strip()

                            def resolve_product_group_column(df, selected_col_index, allowed_groups):
                                if not allowed_groups or df is None or df.empty:
                                    return selected_col_index, 0

                                allowed_set = set(str(group).strip() for group in allowed_groups)

                                def count_matches(col_index):
                                    if col_index is None or col_index < 0 or len(df.columns) <= col_index:
                                        return 0
                                    return int(
                                        df.iloc[:, col_index]
                                        .dropna()
                                        .astype(str)
                                        .str.strip()
                                        .isin(allowed_set)
                                        .sum()
                                    )

                                selected_match_count = count_matches(selected_col_index)
                                if selected_match_count > 0:
                                    return selected_col_index, selected_match_count

                                best_col_index = selected_col_index
                                best_match_count = 0
                                scan_limit = min(len(df.columns), 12)
                                for candidate_col_index in range(scan_limit):
                                    candidate_match_count = count_matches(candidate_col_index)
                                    if candidate_match_count > best_match_count:
                                        best_col_index = candidate_col_index
                                        best_match_count = candidate_match_count

                                return best_col_index, best_match_count

                            auto_group_column_notes = []

                            # Seçilen sayfaları analiz et
                            for sheet_name in cost_analysis_sheets:
                                try:
                                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                                    sheet_group_col_index, sheet_group_match_count = resolve_product_group_column(
                                        df,
                                        data_group_col_index,
                                        product_groups,
                                    )
                                    if (
                                        sheet_group_match_count > 0
                                        and sheet_group_col_index != data_group_col_index
                                    ):
                                        auto_group_column_notes.append(
                                            f"{sheet_name}: ürün grubu kolonu "
                                            f"{index_to_excel_column(data_group_col_index)} yerine "
                                            f"{index_to_excel_column(sheet_group_col_index)} kullanıldı "
                                            f"({sheet_group_match_count} eşleşme)."
                                        )

                                    selected_indices = [
                                        sheet_group_col_index,
                                        urun_aciklama_col_index,
                                        miktar_col_index,
                                        birim_col_index,
                                        malzeme_col_index,
                                        iscilik_col_index,
                                        ggk_col_index,
                                        genel_toplam_col_index
                                    ]
                                    required_max_col = max(idx for idx in selected_indices if idx is not None)

                                    if sheet_group_col_index is not None and len(df.columns) > required_max_col:  # Yeterli sütun olduğunu kontrol et
                                        for idx, row in df.iterrows():
                                            # Seçilen ürün grubu kolonu
                                            try:
                                                if pd.notna(row.iloc[sheet_group_col_index]):
                                                    product_group = str(row.iloc[sheet_group_col_index]).strip()

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
                                                                'Ürün Açıklaması': read_text_cell(row, urun_aciklama_col_index),
                                                                'Miktar': read_numeric_cell(row, miktar_col_index),
                                                                'Birim': read_text_cell(row, birim_col_index),
                                                                'Malzeme Fiyatı': read_numeric_cell(row, malzeme_col_index),
                                                                'İşçilik Fiyatı': read_numeric_cell(row, iscilik_col_index),
                                                                'GGK Fiyatı': read_numeric_cell(row, ggk_col_index),
                                                                'Genel Toplam': read_numeric_cell(row, genel_toplam_col_index)
                                                            }
                                                            all_data.append(data_row)
                                            except Exception as row_error:
                                                # Satır işleminde hata olursa devam et
                                                continue

                                except Exception as e:
                                    st.warning(f"⚠ {sheet_name} sayfası analiz edilirken hata: {str(e)}")

                            if all_data:
                                if auto_group_column_notes:
                                    st.info(
                                        "Bazı sayfalarda seçili ürün grubu kolonu eşleşme vermediği için "
                                        "ürün grubu kolonu otomatik düzeltildi: "
                                        + " | ".join(auto_group_column_notes[:6])
                                        + (" | ..." if len(auto_group_column_notes) > 6 else "")
                                    )

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
                                summary_data = summary_data.sort_values('Genel Toplam', ascending=False, kind='mergesort')

                                # Tekil yüzdeler ve her maliyet kolonunun kendi sırasına göre kümülatif yüzdeler
                                if total_genel > 0:
                                    summary_data['Genel Toplam %'] = (summary_data['Genel Toplam'] / total_genel * 100).round(2)
                                    summary_data['Kümülatif Genel %'] = calculate_cumulative_percent_by_descending_value(
                                        summary_data,
                                        'Genel Toplam',
                                        total_genel,
                                    )
                                else:
                                    summary_data['Genel Toplam %'] = 0.0
                                    summary_data['Kümülatif Genel %'] = 0.0

                                if total_malzeme > 0:
                                    summary_data['Malzeme %'] = (summary_data['Malzeme Fiyatı'] / total_malzeme * 100).round(2)
                                    summary_data['Kümülatif Malzeme %'] = calculate_cumulative_percent_by_descending_value(
                                        summary_data,
                                        'Malzeme Fiyatı',
                                        total_malzeme,
                                    )
                                else:
                                    summary_data['Malzeme %'] = 0.0
                                    summary_data['Kümülatif Malzeme %'] = 0.0

                                if total_iscilik > 0:
                                    summary_data['İşçilik %'] = (summary_data['İşçilik Fiyatı'] / total_iscilik * 100).round(2)
                                    summary_data['Kümülatif İşçilik %'] = calculate_cumulative_percent_by_descending_value(
                                        summary_data,
                                        'İşçilik Fiyatı',
                                        total_iscilik,
                                    )
                                else:
                                    summary_data['İşçilik %'] = 0.0
                                    summary_data['Kümülatif İşçilik %'] = 0.0

                                if total_ggk > 0:
                                    summary_data['GGK %'] = (summary_data['GGK Fiyatı'] / total_ggk * 100).round(2)
                                    summary_data['Kümülatif GGK %'] = calculate_cumulative_percent_by_descending_value(
                                        summary_data,
                                        'GGK Fiyatı',
                                        total_ggk,
                                    )
                                else:
                                    summary_data['GGK %'] = 0.0
                                    summary_data['Kümülatif GGK %'] = 0.0

                                # Sütun sırasını yeniden düzenle
                                summary_data = summary_data[['Ürün Grubu', 'Genel Toplam', 'Genel Toplam %', 'Kümülatif Genel %',
                                                           'Malzeme Fiyatı', 'Malzeme %', 'Kümülatif Malzeme %',
                                                           'İşçilik Fiyatı', 'İşçilik %', 'Kümülatif İşçilik %',
                                                           'GGK Fiyatı', 'GGK %', 'Kümülatif GGK %',
                                                           'Bulunan Kayıt Sayısı']]

                                def build_unit_price_analysis_df(source_df, group_columns):
                                    if source_df.empty:
                                        return pd.DataFrame()

                                    aggregated_df = source_df.groupby(group_columns, as_index=False).agg(**{
                                        'Toplam Miktar': ('Miktar', 'sum'),
                                        'Toplam Malzeme': ('Malzeme Fiyatı', 'sum'),
                                        'Toplam İşçilik': ('İşçilik Fiyatı', 'sum'),
                                        'Toplam GGK': ('GGK Fiyatı', 'sum'),
                                        'Toplam Genel Toplam': ('Genel Toplam', 'sum'),
                                        'Kayıt Sayısı': ('Miktar', 'size')
                                    })

                                    aggregated_df['Malzeme Birim Fiyatı'] = (
                                        aggregated_df['Toplam Malzeme'] / aggregated_df['Toplam Miktar']
                                    ).round(4)
                                    aggregated_df['İşçilik Birim Fiyatı'] = (
                                        aggregated_df['Toplam İşçilik'] / aggregated_df['Toplam Miktar']
                                    ).round(4)
                                    aggregated_df['GGK Birim Fiyatı'] = (
                                        aggregated_df['Toplam GGK'] / aggregated_df['Toplam Miktar']
                                    ).round(4)
                                    aggregated_df['Genel Toplam Birim Fiyatı'] = (
                                        aggregated_df['Toplam Genel Toplam'] / aggregated_df['Toplam Miktar']
                                    ).round(4)

                                    return aggregated_df.sort_values(
                                        'Genel Toplam Birim Fiyatı',
                                        ascending=False
                                    ).reset_index(drop=True)

                                unit_price_df = pd.DataFrame()
                                product_group_unit_price_df = pd.DataFrame()
                                unit_price_base_source = all_df.copy()
                                if {'Ürün Grubu', 'Miktar', 'Malzeme Fiyatı', 'İşçilik Fiyatı', 'GGK Fiyatı', 'Genel Toplam'}.issubset(unit_price_base_source.columns):
                                    unit_price_base_source['Miktar'] = pd.to_numeric(unit_price_base_source['Miktar'], errors='coerce').fillna(0.0)
                                    unit_price_base_source = unit_price_base_source[
                                        unit_price_base_source['Miktar'] > 0
                                    ].copy()

                                    if 'Birim' in unit_price_base_source.columns:
                                        unit_price_base_source['Birim'] = unit_price_base_source['Birim'].fillna('').astype(str).str.strip()
                                        unit_specific_source = unit_price_base_source[
                                            (unit_price_base_source['Birim'] != '') &
                                            (unit_price_base_source['Birim'].str.lower() != 'nan')
                                        ].copy()
                                        if not unit_specific_source.empty:
                                            unit_price_df = build_unit_price_analysis_df(
                                                unit_specific_source,
                                                ['Ürün Grubu', 'Birim']
                                            )

                                    if not unit_price_base_source.empty:
                                        product_group_unit_price_df = build_unit_price_analysis_df(
                                            unit_price_base_source,
                                            ['Ürün Grubu']
                                        )

                                results_df = summary_data

                                # Özet tablosu (numerik değerler korunur; görsel format create_aggrid_table içinde uygulanır)
                                results_df_display = results_df.copy()

                                if page_mode == "Tutarlılık ve Geçmiş Kıyas":
                                    render_consistency_module(all_df, summary_data, cost_analysis_sheets, uploaded_file.name)
                                    st.stop()

                                # Maliyet analizi için çıktı alma aksiyonları (yazdır / PDF)
                                render_cost_analysis_banner(
                                    title="Maliyet Analizi Ciktilari",
                                    subtitle="Tarayici yazdirma penceresi ile mevcut gorunumu PDF olarak kaydedebilir veya detayli Excel raporunu indirebilirsiniz.",
                                    tone="cobalt",
                                    eyebrow="Raporlama",
                                    chips=[
                                        "Tarayici PDF",
                                        "Detayli Excel",
                                        f"{len(cost_analysis_sheets)} sayfa",
                                    ],
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
                                        excel_unit_price_df = unit_price_df.copy()
                                        excel_product_group_unit_price_df = product_group_unit_price_df.copy()

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
                                        if not excel_unit_price_df.empty:
                                            excel_unit_price_df = prepare_dataframe_for_excel_export(excel_unit_price_df)
                                        if not excel_product_group_unit_price_df.empty:
                                            excel_product_group_unit_price_df = prepare_dataframe_for_excel_export(excel_product_group_unit_price_df)
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
                                            if not excel_unit_price_df.empty:
                                                excel_unit_price_df.to_excel(writer, sheet_name='Birim_Fiyat_Analizi', index=False)
                                            if not excel_product_group_unit_price_df.empty:
                                                excel_product_group_unit_price_df.to_excel(writer, sheet_name='UrunGrubu_Birimsiz_BFiyat', index=False)
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
                                render_cost_analysis_banner(
                                    title="Urun Gruplarina Gore Maliyet Analizi Sonuclari",
                                    subtitle="Toplam maliyet, yuzde dagilim ve kumulatif etki tek tabloda birlikte sunulur.",
                                    tone="violet",
                                    eyebrow="Ozet Tablo",
                                    chips=[
                                        f"{len(results_df_display)} urun grubu",
                                        f"{len(all_df)} kayit",
                                        f"{len(cost_analysis_sheets)} sayfa",
                                    ],
                                )


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
                                st.markdown(
                                    '<div class="cost-table-shell-title">Ana Ozet Tablosu</div>',
                                    unsafe_allow_html=True,
                                )
                                st.caption("Kolon baslik ayiraclarini surukleyerek bu tablo ve diger tablolardaki kolon genisliklerini manuel ayarlayabilirsiniz.")
                                create_aggrid_table(results_df_display, height=500)

                                st.markdown("""<div style='margin: 22px 0 12px 0;'></div>""", unsafe_allow_html=True)
                                render_cost_summary_cards(
                                    total_malzeme=total_malzeme,
                                    total_iscilik=total_iscilik,
                                    total_ggk=total_ggk,
                                    total_genel=total_genel,
                                )

                                if not product_group_unit_price_df.empty or not unit_price_df.empty:
                                    unit_price_currency_cols = [
                                        'Toplam Malzeme',
                                        'Toplam İşçilik',
                                        'Toplam GGK',
                                        'Toplam Genel Toplam',
                                        'Malzeme Birim Fiyatı',
                                        'İşçilik Birim Fiyatı',
                                        'GGK Birim Fiyatı',
                                        'Genel Toplam Birim Fiyatı',
                                    ]
                                    unit_price_integer_cols = ['Kayıt Sayısı']

                                    total_unit_price_quantity = (
                                        unit_price_base_source['Miktar'].sum()
                                        if not unit_price_base_source.empty
                                        else 0
                                    )
                                    render_cost_analysis_banner(
                                        title="Birim Fiyat Analizi",
                                        subtitle="Miktar ve birim kolonlari kullanilarak urun grubu bazli birim maliyet katmani olusturuldu.",
                                        tone="amber",
                                        eyebrow="Miktar Katmani",
                                        chips=[
                                            f"{format_integer_display(total_unit_price_quantity)} toplam miktar",
                                            f"{len(unit_price_df)} birim satiri" if not unit_price_df.empty else "Birim bazli veri yok",
                                            f"{len(product_group_unit_price_df)} grup ozeti",
                                        ],
                                    )
                                    render_cost_action_shell(
                                        title="Sifirdan buyuk miktari olan kayitlar bu bolume dahil edildi.",
                                        subtitle="Birim dolu olan satirlar ayri, sadece urun grubuna dayali toplulastirma ise ikinci sekmede sunuluyor.",
                                    )

                                    unit_price_tab_with_unit, unit_price_tab_group_only = st.tabs(
                                        ["Urun Grubu + Birim", "Sadece Urun Grubu"]
                                    )

                                    with unit_price_tab_with_unit:
                                        if unit_price_df.empty:
                                            st.info("Birim bilgisi dolu ve miktari sifirdan buyuk kayit bulunamadi.")
                                        else:
                                            st.markdown(
                                                '<div class="cost-table-shell-title">Birim Bazli Birim Fiyat Ozeti</div>',
                                                unsafe_allow_html=True,
                                            )
                                            create_aggrid_table(
                                                unit_price_df,
                                                height=360,
                                                currency_cols=unit_price_currency_cols,
                                                integer_cols=unit_price_integer_cols,
                                            )

                                            top_unit_price_df = unit_price_df.head(min(len(unit_price_df), 15)).copy()
                                            fig_unit_price = px.bar(
                                                top_unit_price_df,
                                                x='Ürün Grubu',
                                                y='Genel Toplam Birim Fiyatı',
                                                color='Birim',
                                                title='Birim Bazli Genel Toplam Birim Fiyati',
                                                hover_data=[
                                                    'Toplam Miktar',
                                                    'Toplam Genel Toplam',
                                                    'Malzeme Birim Fiyatı',
                                                    'İşçilik Birim Fiyatı',
                                                    'GGK Birim Fiyatı',
                                                ],
                                                text='Genel Toplam Birim Fiyatı',
                                            )
                                            fig_unit_price.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                                            fig_unit_price.update_layout(height=420, xaxis_tickangle=35)
                                            st.plotly_chart(fig_unit_price, use_container_width=True)

                                    with unit_price_tab_group_only:
                                        if product_group_unit_price_df.empty:
                                            st.info("Miktari sifirdan buyuk urun grubu bazli kayit bulunamadi.")
                                        else:
                                            st.markdown(
                                                '<div class="cost-table-shell-title">Urun Grubu Bazli Birim Fiyat Ozeti</div>',
                                                unsafe_allow_html=True,
                                            )
                                            create_aggrid_table(
                                                product_group_unit_price_df,
                                                height=360,
                                                currency_cols=unit_price_currency_cols,
                                                integer_cols=unit_price_integer_cols,
                                            )

                                            top_group_unit_price_df = product_group_unit_price_df.head(
                                                min(len(product_group_unit_price_df), 15)
                                            ).copy()
                                            fig_group_unit_price = px.bar(
                                                top_group_unit_price_df,
                                                x='Ürün Grubu',
                                                y='Genel Toplam Birim Fiyatı',
                                                color='Genel Toplam Birim Fiyatı',
                                                color_continuous_scale='YlOrRd',
                                                title='Urun Grubu Bazli Genel Toplam Birim Fiyati',
                                                hover_data=[
                                                    'Toplam Miktar',
                                                    'Toplam Genel Toplam',
                                                    'Kayıt Sayısı',
                                                ],
                                                text='Toplam Miktar',
                                            )
                                            fig_group_unit_price.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                                            fig_group_unit_price.update_layout(height=420, xaxis_tickangle=35)
                                            st.plotly_chart(fig_group_unit_price, use_container_width=True)

                                # Ana görselleştirmeler
                                render_section_heading("Genel Görselleştirmeler", icon="")

                                main_chart_mode = st.radio(
                                    "Maliyet dağılımı grafik türü",
                                    options=["Treemap", "Sankey"],
                                    horizontal=True,
                                    key="main_chart_mode"
                                )

                                section_title = (
                                    "Maliyet Turlerine Gore Detayli Treemap'ler"
                                    if main_chart_mode == "Treemap"
                                    else "Maliyet Turlerine Gore Sankey Akislari"
                                )
                                render_cost_analysis_banner(
                                    title=section_title,
                                    subtitle="Secili grafik turu ile malzeme, iscilik, GGK ve genel toplam katmanlarini ayni akis icinde inceleyin.",
                                    tone="emerald" if main_chart_mode == "Treemap" else "amber",
                                    eyebrow="Gorsel Katman",
                                    chips=[main_chart_mode, "Malzeme", "Iscilik", "GGK", "Genel Toplam"],
                                )

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
                                render_subsection_heading("ABC Analizi", icon="🎯")

                                # A, B, C grupları belirleme
                                a_groups = summary_data[summary_data['Kümülatif Genel %'] <= 80]
                                b_groups = summary_data[(summary_data['Kümülatif Genel %'] > 80) & (summary_data['Kümülatif Genel %'] <= 95)]
                                c_groups = summary_data[summary_data['Kümülatif Genel %'] > 95]

                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.markdown("""
                                    <div class="info-card" style="border-left: 4px solid #ef4444;">
                                        <h4 style="color: #dc2626; margin-bottom: 12px;">🅰️ A Grubu (Kritik)</h4>
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
                                                group_detail_sorted['Kümülâtif Genel %'] = calculate_cumulative_percent_by_descending_value(
                                                    group_detail_sorted,
                                                    'Genel Toplam',
                                                    group_total,
                                                )
                                            else:
                                                group_detail_sorted['Genel Toplam %'] = 0
                                                group_detail_sorted['Kümülâtif Genel %'] = 0

                                            group_malzeme_total = group_detail_sorted['Malzeme Fiyatı'].sum()
                                            if group_malzeme_total > 0:
                                                group_detail_sorted['Malzeme %'] = (group_detail_sorted['Malzeme Fiyatı'] / group_malzeme_total * 100).round(2)
                                                group_detail_sorted['Kümülatif Malzeme %'] = calculate_cumulative_percent_by_descending_value(
                                                    group_detail_sorted,
                                                    'Malzeme Fiyatı',
                                                    group_malzeme_total,
                                                )
                                            else:
                                                group_detail_sorted['Malzeme %'] = 0.0
                                                group_detail_sorted['Kümülatif Malzeme %'] = 0.0

                                            group_iscilik_total = group_detail_sorted['İşçilik Fiyatı'].sum()
                                            if group_iscilik_total > 0:
                                                group_detail_sorted['İşçilik %'] = (group_detail_sorted['İşçilik Fiyatı'] / group_iscilik_total * 100).round(2)
                                                group_detail_sorted['Kümülatif İşçilik %'] = calculate_cumulative_percent_by_descending_value(
                                                    group_detail_sorted,
                                                    'İşçilik Fiyatı',
                                                    group_iscilik_total,
                                                )
                                            else:
                                                group_detail_sorted['İşçilik %'] = 0.0
                                                group_detail_sorted['Kümülatif İşçilik %'] = 0.0

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
                                                'Miktar',
                                                'Birim',
                                                'Malzeme Fiyatı',
                                                'Malzeme %',
                                                'Kümülatif Malzeme %',
                                                'İşçilik Fiyatı',
                                                'İşçilik %',
                                                'Kümülatif İşçilik %',
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
                                ">💰 Genel Gider Analizi</div>
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
                                        render_subsection_heading("Gider Pareto Analizi (80/20)", icon="📊")

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
                    st.error(f" İSKONTOLAR / maliyet analiz akışında hata: {str(e)}")

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
