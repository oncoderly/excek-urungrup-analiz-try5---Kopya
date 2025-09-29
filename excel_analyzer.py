import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from html import escape

# st-aggrid'i güvenli şekilde import et
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
    HAS_AGGRID = True
except ImportError:
    HAS_AGGRID = False

st.set_page_config(page_title="Excel Analiz Uygulaması", layout="wide")

# Modern CSS stil tanımlamaları
st.markdown("""
<style>
/* Ana tema renkleri ve değişkenler */
:root {
    --primary-color: #3b82f6;
    --primary-dark: #1e40af;
    --primary-light: #93c5fd;
    --secondary-color: #10b981;
    --secondary-dark: #059669;
    --accent-color: #f59e0b;
    --background-primary: #ffffff;
    --background-secondary: #f8fafc;
    --background-tertiary: #f1f5f9;
    --text-primary: #1e293b;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --border-color: #e2e8f0;
    --border-light: #f1f5f9;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}

/* Streamlit ana konteyner - gelişmiş padding */
.main .block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
}

/* Premium AgGrid tabloları için gelişmiş başlık tasarımı */
.ag-theme-material .ag-header {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%) !important;
    border: none !important;
    box-shadow: 0 6px 16px rgba(124,58,237,0.3), 0 4px 8px rgba(168,85,247,0.2) !important;
    position: relative !important;
}

.ag-theme-material .ag-header::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 4px !important;
    background: linear-gradient(90deg, #fbbf24, #f59e0b, #d97706, #92400e) !important;
}

.ag-theme-material .ag-header-cell {
    background: transparent !important;
    color: #ffffff !important;
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-weight: 800 !important;
    font-size: 16px !important;
    letter-spacing: 0.5px !important;
    text-align: center !important;
    text-transform: uppercase !important;
    padding: 20px 18px !important;
    border-right: 3px solid rgba(255,255,255,0.25) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
}

/* Kolon ayırıcı dikey çizgiler */
.ag-theme-material .ag-header-cell::after {
    content: '' !important;
    position: absolute !important;
    top: 15% !important;
    right: 0 !important;
    width: 1px !important;
    height: 70% !important;
    background: linear-gradient(180deg, transparent, rgba(255,255,255,0.6), transparent) !important;
    opacity: 0.8 !important;
}

.ag-theme-material .ag-cell::after {
    content: '' !important;
    position: absolute !important;
    top: 20% !important;
    right: 0 !important;
    width: 1px !important;
    height: 60% !important;
    background: linear-gradient(180deg, transparent, rgba(156,163,175,0.4), transparent) !important;
    opacity: 0.6 !important;
}

.ag-theme-material .ag-header-cell:hover {
    background: linear-gradient(135deg, rgba(192,132,252,0.3), rgba(168,85,247,0.2)) !important;
    transform: translateY(-1px) !important;
    color: #fef3ff !important;
}

.ag-theme-material .ag-cell {
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    text-align: center !important;
    padding: 16px 18px !important;
    border-bottom: 1px solid #e5e7eb !important;
    border-right: 2px solid #d1d5db !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    line-height: 1.4 !important;
    letter-spacing: 0.02em !important;
    position: relative !important;
}

.ag-theme-material .ag-row {
    border: none !important;
    transition: all 0.2s ease !important;
}

.ag-theme-material .ag-row:nth-child(even) .ag-cell {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
    color: #374151 !important;
}

.ag-theme-material .ag-row:nth-child(odd) .ag-cell {
    background: #ffffff !important;
    color: #1f2937 !important;
}

.ag-theme-material .ag-row:hover .ag-cell {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
    transform: translateY(-1px) scale(1.002) !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.15) !important;
    border-right: 2px solid #93c5fd !important;
}

/* Hover efektleri - doğru kolon isimleriyle */
.ag-theme-material .ag-row:hover .ag-cell[col-id="Malzeme Fiyatı"],
.ag-theme-material .ag-row:hover .ag-cell[col-id="Malzeme %"] {
    color: #065f46 !important;
    font-weight: 800 !important;
    transform: scale(1.05) !important;
}

.ag-theme-material .ag-row:hover .ag-cell[col-id="İşçilik Fiyatı"],
.ag-theme-material .ag-row:hover .ag-cell[col-id="İşçilik %"] {
    color: #1e3a8a !important;
    font-weight: 800 !important;
    transform: scale(1.05) !important;
}

.ag-theme-material .ag-row:hover .ag-cell[col-id="Genel Toplam"],
.ag-theme-material .ag-row:hover .ag-cell[col-id="Genel Toplam %"],
.ag-theme-material .ag-row:hover .ag-cell[col-id="Kümülatif Genel %"] {
    color: #991b1b !important;
    font-weight: 900 !important;
    transform: scale(1.08) !important;
    text-shadow: 0 2px 4px rgba(153,27,27,0.3) !important;
}

.ag-theme-material .ag-row:hover .ag-cell[col-id="GGK Fiyatı"],
.ag-theme-material .ag-row:hover .ag-cell[col-id="GGK %"] {
    color: #581c87 !important;
    font-weight: 800 !important;
    transform: scale(1.05) !important;
}

.ag-theme-material .ag-row:hover .ag-cell[col-id="Ürün Grubu"] {
    color: #1f2937 !important;
    font-weight: 900 !important;
    transform: scale(1.03) !important;
}

.ag-theme-material {
    border-radius: 20px !important;
    overflow: hidden !important;
    box-shadow: 0 20px 40px rgba(0,0,0,0.08), 0 8px 16px rgba(0,0,0,0.04) !important;
    border: 2px solid #e5e7eb !important;
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: #ffffff !important;
    position: relative !important;
}

.ag-theme-material::before {
    content: '' !important;
    position: absolute !important;
    top: -2px !important;
    left: -2px !important;
    right: -2px !important;
    bottom: -2px !important;
    background: linear-gradient(45deg, #3b82f6, #10b981, #8b5cf6, #f59e0b) !important;
    border-radius: 22px !important;
    z-index: -1 !important;
    opacity: 0.1 !important;
}

/* Gelişmiş kolon yeniden boyutlandırma ve taşıma özellikleri */
.ag-theme-material .ag-header-cell-resize::after {
    background: linear-gradient(180deg, rgba(124,58,237,0.9), rgba(168,85,247,0.8)) !important;
    width: 4px !important;
    opacity: 0.9 !important;
}

.ag-theme-material .ag-header-cell-moving {
    background: linear-gradient(135deg, rgba(59,130,246,0.3), rgba(16,185,129,0.2)) !important;
    box-shadow: 0 8px 16px rgba(0,0,0,0.15) !important;
    transform: rotate(1deg) scale(1.02) !important;
    border: 2px solid rgba(59,130,246,0.4) !important;
    border-radius: 8px !important;
    z-index: 1000 !important;
}

.ag-theme-material .ag-header-cell-resize:hover::after {
    background: linear-gradient(180deg, #7c3aed, #a855f7) !important;
    width: 5px !important;
    opacity: 1 !important;
    box-shadow: 0 0 12px rgba(124,58,237,0.6) !important;
}

/* Premium scrollbar tasarımı */
.ag-theme-material .ag-body-viewport::-webkit-scrollbar {
    width: 12px !important;
    height: 12px !important;
}

.ag-theme-material .ag-body-viewport::-webkit-scrollbar-track {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
    border-radius: 6px !important;
}

.ag-theme-material .ag-body-viewport::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #64748b, #475569) !important;
    border-radius: 6px !important;
    border: 2px solid #f8fafc !important;
    transition: all 0.2s ease !important;
}

.ag-theme-material .ag-body-viewport::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #3b82f6, #1e40af) !important;
    transform: scale(1.1) !important;
}

/* Güçlü CSS seçicileri - Gerçek kolon isimleriyle */

/* Malzeme Fiyatı kolonları için özel stil */
.ag-theme-material .ag-cell[col-id="Malzeme Fiyatı"],
.ag-theme-material .ag-cell[col-id="Malzeme %"],
.ag-theme-material [col-id="Malzeme Fiyatı"],
.ag-theme-material [col-id="Malzeme %"] {
    font-weight: 700 !important;
    color: #047857 !important;
    background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(5,150,105,0.06)) !important;
    border-left: 5px solid #10b981 !important;
}

.ag-theme-material .ag-header-cell[col-id="Malzeme Fiyatı"],
.ag-theme-material .ag-header-cell[col-id="Malzeme %"] {
    background: linear-gradient(135deg, rgba(16,185,129,0.4), rgba(5,150,105,0.3)) !important;
    color: #ffffff !important;
    text-shadow: 0 2px 6px rgba(16,185,129,0.7) !important;
    box-shadow: inset 0 0 20px rgba(16,185,129,0.2) !important;
}

/* İşçilik Fiyatı kolonları için özel stil */
.ag-theme-material .ag-cell[col-id="İşçilik Fiyatı"],
.ag-theme-material .ag-cell[col-id="İşçilik %"],
.ag-theme-material [col-id="İşçilik Fiyatı"],
.ag-theme-material [col-id="İşçilik %"] {
    font-weight: 700 !important;
    color: #1e40af !important;
    background: linear-gradient(135deg, rgba(59,130,246,0.12), rgba(29,78,216,0.06)) !important;
    border-left: 5px solid #3b82f6 !important;
}

.ag-theme-material .ag-header-cell[col-id="İşçilik Fiyatı"],
.ag-theme-material .ag-header-cell[col-id="İşçilik %"] {
    background: linear-gradient(135deg, rgba(59,130,246,0.4), rgba(29,78,216,0.3)) !important;
    color: #ffffff !important;
    text-shadow: 0 2px 6px rgba(59,130,246,0.7) !important;
    box-shadow: inset 0 0 20px rgba(59,130,246,0.2) !important;
}

/* Genel Toplam kolonları için özel stil */
.ag-theme-material .ag-cell[col-id="Genel Toplam"],
.ag-theme-material .ag-cell[col-id="Genel Toplam %"],
.ag-theme-material .ag-cell[col-id="Kümülatif Genel %"],
.ag-theme-material [col-id="Genel Toplam"],
.ag-theme-material [col-id="Genel Toplam %"],
.ag-theme-material [col-id="Kümülatif Genel %"] {
    font-weight: 800 !important;
    color: #b91c1c !important;
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(220,38,38,0.08)) !important;
    border-left: 6px solid #ef4444 !important;
    font-size: 16px !important;
}

.ag-theme-material .ag-header-cell[col-id="Genel Toplam"],
.ag-theme-material .ag-header-cell[col-id="Genel Toplam %"],
.ag-theme-material .ag-header-cell[col-id="Kümülatif Genel %"] {
    background: linear-gradient(135deg, rgba(239,68,68,0.5), rgba(220,38,38,0.4)) !important;
    color: #ffffff !important;
    text-shadow: 0 2px 6px rgba(239,68,68,0.8) !important;
    font-size: 17px !important;
    box-shadow: inset 0 0 20px rgba(239,68,68,0.3) !important;
}

/* GGK Fiyatı kolonları için özel stil */
.ag-theme-material .ag-cell[col-id="GGK Fiyatı"],
.ag-theme-material .ag-cell[col-id="GGK %"],
.ag-theme-material [col-id="GGK Fiyatı"],
.ag-theme-material [col-id="GGK %"] {
    font-weight: 700 !important;
    color: #6b21a8 !important;
    background: linear-gradient(135deg, rgba(139,92,246,0.12), rgba(124,58,237,0.06)) !important;
    border-left: 5px solid #8b5cf6 !important;
}

.ag-theme-material .ag-header-cell[col-id="GGK Fiyatı"],
.ag-theme-material .ag-header-cell[col-id="GGK %"] {
    background: linear-gradient(135deg, rgba(139,92,246,0.4), rgba(124,58,237,0.3)) !important;
    color: #ffffff !important;
    text-shadow: 0 2px 6px rgba(139,92,246,0.7) !important;
    box-shadow: inset 0 0 20px rgba(139,92,246,0.2) !important;
}

/* Tüm yüzde kolonları için genel stil */
.ag-theme-material .ag-cell[col-id$="%"],
.ag-theme-material [col-id$="%"] {
    font-style: italic !important;
    font-weight: 700 !important;
}

/* Ürün Grubu kolonu için özel stil */
.ag-theme-material .ag-cell[col-id="Ürün Grubu"],
.ag-theme-material [col-id="Ürün Grubu"] {
    font-weight: 800 !important;
    color: #374151 !important;
    background: linear-gradient(135deg, rgba(156,163,175,0.08), rgba(107,114,128,0.04)) !important;
    border-left: 4px solid #6b7280 !important;
}

.ag-theme-material .ag-header-cell[col-id="Ürün Grubu"] {
    background: linear-gradient(135deg, rgba(75,85,99,0.4), rgba(55,65,81,0.3)) !important;
    color: #ffffff !important;
    text-shadow: 0 2px 6px rgba(75,85,99,0.7) !important;
}

/* Modern metrikler için gelişmiş stil */
.metric-container {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    padding: 28px;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.metric-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: linear-gradient(90deg, #2563eb, #10b981, #7c3aed);
    border-radius: 20px 20px 0 0;
}

.metric-container:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0,0,0,0.12);
}

.metric-value {
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    color: #2563eb !important;
    margin-bottom: 12px !important;
    letter-spacing: -0.02em !important;
    text-shadow: 0 2px 4px rgba(37,99,235,0.1) !important;
}

.metric-label {
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* Modern başlıklar için gelişmiş stil */
.main-title {
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #2563eb, #10b981, #7c3aed) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    text-align: center;
    margin-bottom: 2.5rem;
    letter-spacing: -0.02em !important;
    text-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
}

.section-title {
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    color: #1e293b !important;
    margin: 2.5rem 0 1.5rem 0 !important;
    padding: 20px 24px !important;
    background: linear-gradient(135deg, #f8fafc, #e2e8f0) !important;
    border-radius: 12px !important;
    border-left: 6px solid #2563eb !important;
    position: relative !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    letter-spacing: -0.01em !important;
}

.section-title::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #2563eb, #10b981, #7c3aed);
    border-radius: 12px 12px 0 0;
}

.subsection-title {
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #374151 !important;
    margin: 2rem 0 1rem 0 !important;
    padding: 12px 20px !important;
    background: linear-gradient(135deg, #fef3c7, #fed7aa) !important;
    border-radius: 8px !important;
    border-left: 4px solid #f59e0b !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}

/* Modern kartlar için gelişmiş stil */
.info-card {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    margin: 20px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
}

.info-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.08);
    border-color: #93c5fd;
    background: linear-gradient(135deg, #fefefe, #f1f5f9);
}

/* Modern sidebar stilleri - gelişmiş gradyan */
.css-1d391kg {
    background: linear-gradient(180deg, #ffffff, #f8fafc, #e2e8f0) !important;
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
}

/* Modern butonlar için gelişmiş stil */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1e40af) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 20px rgba(37,99,235,0.4) !important;
    background: linear-gradient(135deg, #1d4ed8, #1e3a8a) !important;
}

/* Modern checkbox ve selectbox için gelişmiş stil */
.stCheckbox > label {
    color: #1e293b !important;
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    letter-spacing: 0.01em !important;
}

.stSelectbox > label {
    color: #1e293b !important;
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    letter-spacing: 0.02em !important;
    margin-bottom: 8px !important;
}

.stSelectbox > div > div {
    border-radius: 8px !important;
    border: 2px solid #e2e8f0 !important;
    transition: all 0.2s ease !important;
}

.stSelectbox > div > div:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}

/* Modern uyarı mesajları */
.stSuccess {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05)) !important;
    border: 1px solid var(--secondary-color) !important;
    border-radius: 8px !important;
    color: var(--secondary-dark) !important;
}

.stInfo {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05)) !important;
    border: 1px solid var(--primary-color) !important;
    border-radius: 8px !important;
    color: var(--primary-dark) !important;
}

.stWarning {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05)) !important;
    border: 1px solid var(--warning-color) !important;
    border-radius: 8px !important;
    color: #92400e !important;
}

.stError {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05)) !important;
    border: 1px solid var(--error-color) !important;
    border-radius: 8px !important;
    color: #dc2626 !important;
}
</style>
""", unsafe_allow_html=True)


PRICE_COLUMNS = ['Malzeme Fiyatı', 'İşçilik Fiyatı', 'GGK Fiyatı', 'Genel Toplam']

def create_aggrid_table(dataframe, height=400, selection_mode='single', fit_columns_on_grid_load=True):
    """Render dataframe table with modern design - using st.dataframe for compatibility."""

    # CSS stillerini dataframe için optimize et
    st.markdown("""
    <style>
    /* Modern dataframe stilleri */
    div[data-testid="stDataFrame"] {
        font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
        border: 3px solid #8b5cf6 !important;
    }

    div[data-testid="stDataFrame"] table {
        border-collapse: collapse !important;
        width: 100% !important;
    }

    div[data-testid="stDataFrame"] th {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 12px 16px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
        border-right: 2px solid rgba(255,255,255,0.2) !important;
    }

    div[data-testid="stDataFrame"] td {
        font-family: 'Segoe UI', 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
        border-right: 1px solid #e5e7eb !important;
        border-bottom: 1px solid #e5e7eb !important;
        text-align: center !important;
    }

    div[data-testid="stDataFrame"] tr:nth-child(even) td {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
    }

    div[data-testid="stDataFrame"] tr:nth-child(odd) td {
        background: #ffffff !important;
    }

    div[data-testid="stDataFrame"] tr:hover td {
        background: linear-gradient(135deg, #ede9fe, #ddd6fe) !important;
        transition: all 0.2s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # st.dataframe kullanarak tabloyu göster
    return st.dataframe(dataframe, height=height, use_container_width=True)


def render_section_heading(title: str, icon: str = "") -> None:
    display_title = f"{icon} {title}".strip() if icon else title
    st.markdown(f"<div class='section-title'>{display_title}</div>", unsafe_allow_html=True)


def render_subsection_heading(title: str, icon: str = "") -> None:
    display_title = f"{icon} {title}".strip() if icon else title
    st.markdown(f"<div class='subsection-title'>{display_title}</div>", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-title">📊 Excel Analiz Uygulaması</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card">Modern Excel analiz uygulaması ile dosyanızı yükleyip detaylı maliyet analizi yapın. Ürün grupları bazında karşılaştırmalar ve Pareto analizleri gerçekleştirin.</div>', unsafe_allow_html=True)

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

            st.success(f"✅ Dosya başarıyla yüklendi! ({len(sheet_names)} sayfa bulundu)")

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
                ">📊 Ürün Gruplarına Göre Maliyet Analizi</div>
            </div>
            """, unsafe_allow_html=True)

            # İSKONTOLAR sayfasından ürün gruplarını okuma
            if "İSKONTOLAR" in sheet_names:
                try:
                    # İSKONTOLAR sayfasını oku
                    iskontolar_df = pd.read_excel(uploaded_file, sheet_name="İSKONTOLAR")

                    # F3:F27 aralığından ürün gruplarını al (Excel'de F sütunu index 5)
                    # pandas'ta satır indexi 0'dan başlar, Excel'de 3. satır pandas'ta index 2
                    product_groups = []
                    for i in range(2, 27):  # F3:F27 -> index 2:26
                        try:
                            if i < len(iskontolar_df) and len(iskontolar_df.columns) > 5:
                                value = iskontolar_df.iloc[i, 5]  # F sütunu (index 5)
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

                                    if len(df.columns) > 30:  # Yeterli sütun olduğunu kontrol et
                                        for idx, row in df.iterrows():
                                            # C sütunu (index 2) ürün grubu
                                            try:
                                                if pd.notna(row.iloc[2]):
                                                    product_group = str(row.iloc[2]).strip()

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
                                                                'Ürün Açıklaması': str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else '',  # D sütunu (index 3)
                                                                'Malzeme Fiyatı': float(row.iloc[20]) if len(row) > 20 and pd.notna(row.iloc[20]) else 0,
                                                                'İşçilik Fiyatı': float(row.iloc[22]) if len(row) > 22 and pd.notna(row.iloc[22]) else 0,
                                                                'GGK Fiyatı': float(row.iloc[28]) if len(row) > 28 and pd.notna(row.iloc[28]) else 0,
                                                                'Genel Toplam': float(row.iloc[30]) if len(row) > 30 and pd.notna(row.iloc[30]) else 0
                                                            }
                                                            all_data.append(data_row)
                                            except Exception as row_error:
                                                # Satır işleminde hata olursa devam et
                                                continue

                                except Exception as e:
                                    st.warning(f"⚠️ {sheet_name} sayfası analiz edilirken hata: {str(e)}")

                            if all_data:
                                # Tüm veriler tablosu
                                all_df = pd.DataFrame(all_data)

                                # Para formatı uygulama fonksiyonu
                                def format_currency(value):
                                    if pd.isna(value) or value == 0:
                                        return "0,00 TL"
                                    return f"{value:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")

                                # Detay tablosunu formatla
                                all_df_display = all_df.copy()
                                for col in PRICE_COLUMNS:
                                    if col in all_df_display.columns:
                                        all_df_display[col] = all_df_display[col].apply(format_currency)

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

                                # Tekil yüzdeler
                                summary_data['Genel Toplam %'] = (summary_data['Genel Toplam'] / total_genel * 100).round(2)
                                summary_data['Kümülatif Genel %'] = (summary_data['Genel Toplam'].cumsum() / total_genel * 100).round(2)
                                summary_data['Malzeme %'] = (summary_data['Malzeme Fiyatı'] / total_malzeme * 100).round(2)
                                summary_data['İşçilik %'] = (summary_data['İşçilik Fiyatı'] / total_iscilik * 100).round(2)
                                summary_data['GGK %'] = (summary_data['GGK Fiyatı'] / total_ggk * 100).round(2)

                                # Sütun sırasını yeniden düzenle
                                summary_data = summary_data[['Ürün Grubu', 'Genel Toplam', 'Genel Toplam %', 'Kümülatif Genel %',
                                                           'Malzeme Fiyatı', 'Malzeme %', 'İşçilik Fiyatı', 'İşçilik %',
                                                           'GGK Fiyatı', 'GGK %', 'Bulunan Kayıt Sayısı']]

                                results_df = summary_data

                                # Özet tablosunu formatla
                                results_df_display = results_df.copy()
                                for col in PRICE_COLUMNS:
                                    if col in results_df_display.columns:
                                        results_df_display[col] = results_df_display[col].apply(format_currency)

                                # Yüzde sütunlarına % sembolü ekle
                                percent_columns = [col for col in results_df_display.columns if '%' in col]
                                for col in percent_columns:
                                    results_df_display[col] = results_df_display[col].astype(str) + '%'

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
                                    ">📊 Ürün Gruplarına Göre Maliyet Analizi Sonuçları</div>
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

                                # TOPLAM FİYATLAR - BÜYÜK PUNTOLARLA - DÜZELTİLMİŞ YERLEŞİM
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
                                            font-size: 15px;
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
                                            font-size: 15px;
                                            font-weight: 800;
                                            color: #1e40af;
                                            text-transform: uppercase;
                                            letter-spacing: 2px;
                                            margin-bottom: 15px;
                                        ">TOPLAM İŞÇİLİK</div>
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
                                            font-size: 15px;
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
                                        font-size: 19px;
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
                                render_section_heading("Genel Görselleştirmeler", icon="📊")

                                # Malzeme ve İşçilik treemap'leri
                                # Treemap bölüm başlığı
                                st.markdown("""
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
                                    ">🔍 Maliyet Türlerine Göre Detaylı Treemap'ler</div>
                                </div>
                                """, unsafe_allow_html=True)

                                # Malzeme Maliyeti Treemap
                                # Malzeme başlığı - küçük kart
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
                                    ">💎 Malzeme Maliyeti Dağılımı</div>
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
                                # İşçilik başlığı - küçük kart
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
                                    ">👷 İşçilik Maliyeti Dağılımı</div>
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

                                # Ürün gruplarına göre treemap - Genel Toplam
                                # Genel toplam treemap başlığı
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
                                    ">🌳 Ürün Grupları - Genel Toplam Treemap</div>
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
                                        ">💰 Malzeme vs İşçilik vs GGK</div>
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
                                        ">📈 Grup Bazında Dağılım</div>
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
                                    ">⚙️ GGK Maliyeti Dağılımı</div>
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
                                    ">📈 Kümülatif Maliyet Analizi</div>
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
                                        <h4 style="color: #d97706; margin-bottom: 12px;">🅱️ B Grubu (Önemli)</h4>
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
                                        <h4 style="color: #059669; margin-bottom: 12px;">🅲 C Grubu (Düşük)</h4>
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
                                    render_section_heading("Ürün Grupları Detay Analizi", icon="🔍")

                                    selected_group = st.selectbox(
                                        "Detayını görmek istediğiniz ürün grubunu seçin:",
                                        options=product_groups,
                                        key="group_selector"
                                    )

                                    if selected_group:
                                        # Seçilen gruba ait verileri filtrele
                                        group_detail = all_df[all_df['Ürün Grubu'] == selected_group].copy()

                                        if not group_detail.empty:
                                            # Gruba göre sıralama
                                            group_detail_sorted = group_detail.sort_values('Genel Toplam', ascending=False)

                                            # Kümülatif yüzde hesaplama
                                            group_total = group_detail_sorted['Genel Toplam'].sum()
                                            if group_total > 0:
                                                group_detail_sorted['Kümülâtif Genel %'] = (group_detail_sorted['Genel Toplam'].cumsum() / group_total * 100).round(2)
                                            else:
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
                                            render_subsection_heading("Grup İçi Ürün Detayları", icon="📋")
                                            group_detail_display = group_detail_sorted.copy()
                                            for col in PRICE_COLUMNS:
                                                if col in group_detail_display.columns:
                                                    group_detail_display[col] = group_detail_display[col].apply(format_currency)

                                            # Yüzde sütunlarını formatla
                                            percent_columns = [col for col in group_detail_display.columns if '%' in col]
                                            for col in percent_columns:
                                                group_detail_display[col] = group_detail_display[col].astype(str) + '%'

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
                                            render_subsection_heading("Görselleştirmeler", icon="📊")

                                            # Treemap grafikleri
                                            col1, col2 = st.columns(2)

                                            with col1:
                                                fig_group_treemap_total = px.treemap(
                                                    group_detail_sorted,
                                                    path=['Ürün Açıklaması'],
                                                    values='Genel Toplam',
                                                    title=f'{selected_group} - Genel Toplam Dağılımı',
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
                                                    title=f'{selected_group} - Malzeme Maliyeti Dağılımı',
                                                    color='Malzeme Fiyatı',
                                                    color_continuous_scale='Greens'
                                                )
                                                fig_group_treemap_malzeme.update_layout(height=400)
                                                st.plotly_chart(fig_group_treemap_malzeme, use_container_width=True)

                                            # İşçilik treemap
                                            fig_group_treemap_iscilik = px.treemap(
                                                group_detail_sorted,
                                                path=['Ürün Açıklaması'],
                                                values='İşçilik Fiyatı',
                                                title=f'{selected_group} - İşçilik Maliyeti Dağılımı',
                                                color='İşçilik Fiyatı',
                                                color_continuous_scale='Oranges'
                                            )
                                            fig_group_treemap_iscilik.update_layout(height=400)
                                            st.plotly_chart(fig_group_treemap_iscilik, use_container_width=True)

                                            # Min/Max analizi
                                            render_subsection_heading("Minimum ve Maximum Değerler", icon="📈")
                                            col_high, col_low = st.columns(2)
                                            with col_high:
                                                st.write("**🔺 En Yüksek Değerler:**")
                                                max_row = group_detail.loc[group_detail['Genel Toplam'].fillna(0).idxmax()]
                                                st.write(f"• Genel Toplam: {format_currency(max_row['Genel Toplam'])} ({max_row['Sayfa']} - Satır {max_row['Satır']})")
                                                max_malzeme_row = group_detail.loc[group_detail['Malzeme Fiyatı'].fillna(0).idxmax()]
                                                st.write(f"• Malzeme: {format_currency(max_malzeme_row['Malzeme Fiyatı'])} ({max_malzeme_row['Sayfa']} - Satır {max_malzeme_row['Satır']})")
                                            with col_low:
                                                st.write("**🔻 En Düşük Değerler:**")
                                                min_row = group_detail.loc[group_detail['Genel Toplam'].fillna(0).idxmin()]
                                                st.write(f"• Genel Toplam: {format_currency(min_row['Genel Toplam'])} ({min_row['Sayfa']} - Satır {min_row['Satır']})")
                                                min_malzeme_row = group_detail.loc[group_detail['Malzeme Fiyatı'].fillna(0).idxmin()]
                                                st.write(f"• Malzeme: {format_currency(min_malzeme_row['Malzeme Fiyatı'])} ({min_malzeme_row['Sayfa']} - Satır {min_malzeme_row['Satır']})")

                                            # Pareto analizi
                                            render_subsection_heading("Pareto Analizi (80/20 Kuralı)", icon="📊")
                                            pareto_data = group_detail_sorted[['Ürün Açıklaması', 'Genel Toplam', 'Kümülâtif Genel %']].copy()
                                            if len(pareto_data) > 0:
                                                fig_group_pareto = px.bar(
                                                    pareto_data,
                                                    x='Ürün Açıklaması',
                                                    y='Genel Toplam',
                                                    title=f'{selected_group} - Pareto Analizi (80/20)',
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
                                                    st.info(f"📈 **80/20 Analizi:** Bu grupta toplam maliyetin %80'i **{items_80_percent} kalem** tarafından oluşturuluyor. (Toplam {len(pareto_data)} kalem)")
                                                else:
                                                    st.info("📈 **80/20 Analizi:** İlk kalem zaten %80'in üzerinde maliyet oluşturuyor.")
                                            else:
                                                st.info("Pareto analizi için yeterli veri bulunmuyor.")
                                        else:
                                            st.warning(f"Seçilen grup '{selected_group}' için veri bulunamadı.")
                            else:
                                st.info("Veri bulunamadı.")
                        else:
                            st.info("👈 Maliyet analizi için yan panelden en az bir sayfa seçin.")
                    else:
                        st.info("Ürün grupları listesi oluşturulamadı.")

                except Exception as e:
                    st.error(f"❌ İSKONTOLAR sayfası okunurken hata: {str(e)}")

            else:
                st.error("❌ İSKONTOLAR sayfası bulunamadı. Maliyet analizi için bu sayfa gereklidir.")

        except Exception as e:
            st.error(f"❌ Dosya okuma hatası: {str(e)}")
            st.info("Lütfen geçerli bir Excel dosyası yüklediğinizden emin olun.")

    else:
        st.info("👆 Başlamak için yan panelden bir Excel dosyası yükleyin.")

        st.markdown('<div class="section-title">📝 Nasıl Kullanılır?</div>', unsafe_allow_html=True)
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
        </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
