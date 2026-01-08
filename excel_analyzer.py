import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from html import escape
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
from datetime import datetime

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
    font-weight: 800 !important;
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

/* Yazdırma stilleri */
@media print {
    /* Sidebar'ı tamamen gizle - tüm olası selector'lar */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"],
    .css-1d391kg,
    .sidebar,
    aside,
    nav,
    header,
    footer,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    .stDeployButton,
    button,
    [data-testid="collapsedControl"],
    .css-1cypcdb,
    .css-17lntkn {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
    }

    /* Ana içeriği tam genişlik yap ve sola kaydır */
    .main,
    .main .block-container,
    section.main > div,
    [data-testid="stAppViewContainer"] {
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 1rem !important;
        margin-left: 0 !important;
    }

    /* Streamlit container'ını düzenle */
    .appview-container {
        margin-left: 0 !important;
    }

    /* Sayfa boyutu ve kenar boşlukları */
    @page {
        size: A4 landscape;
        margin: 1cm;
    }

    /* Body'yi düzenle */
    body {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Tablo ve grafiklerin sayfa sığması */
    .ag-theme-material,
    div[data-testid="stDataFrame"],
    .stPlotlyChart {
        page-break-inside: avoid;
        width: 100% !important;
    }

    /* Renkli arka planları koru */
    * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
        color-adjust: exact !important;
    }

    /* Ana başlığı görünür tut */
    .main-title {
        display: block !important;
        page-break-after: avoid;
    }

    /* İçerik alanını genişlet */
    .css-18e3th9,
    .css-1d391kg {
        padding-left: 0 !important;
        margin-left: 0 !important;
    }
}
</style>
""", unsafe_allow_html=True)


PRICE_COLUMNS = ['Malzeme Fiyatı', 'İşçilik Fiyatı', 'GGK Fiyatı', 'Genel Toplam']

def create_aggrid_table(dataframe, height=400, selection_mode='single', fit_columns_on_grid_load=True):
    """Render dataframe table with modern design and column-specific styling."""

    # Sütun tabanlı styling için dataframe'i styled DataFrame'e çevir
    def style_dataframe(df):
        """Apply column-specific styling to dataframe"""

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

            # Genel Toplam ve Kümülatif sütunları - Kırmızı
            toplam_cols = [col for col in df.columns if 'Genel Toplam' in str(col) or 'Kümülatif' in str(col)]
            for col in toplam_cols:
                styler = styler.map(lambda x: 'background-color: #fecaca; color: #dc2626; font-weight: 800; font-size: 15px', subset=[col])

            # Ürün Grubu sütunları - Gri
            grup_cols = [col for col in df.columns if 'Ürün Grubu' in str(col)]
            for col in grup_cols:
                styler = styler.map(lambda x: 'background-color: #f3f4f6; color: #374151; font-weight: 800', subset=[col])

            return styler

        return df.style.pipe(apply_column_styles)

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
        detail_title_data = [[f"Detayli Kayitlar (Ilk {min(50, len(group_df))} Kayit)"]]
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

        for idx, (_, row) in enumerate(group_df.head(50).iterrows()):
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
            note_data = [[f"Not: Bu urun grubunda toplam {len(group_df)} kayit bulunmaktadir. Ilk 50 kayit gosterilmistir."]]
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

                        # İSKONTOLAR ve Genel Gider Analiz sayfalarını hariç tut
                        available_sheets = [s for s in sheet_names if s not in ["İSKONTOLAR", "Genel Gider Analiz"]]

                        for sheet in available_sheets:
                            if st.sidebar.checkbox(sheet, key=f"cost_sheet_{sheet}"):
                                cost_analysis_sheets.append(sheet)

                        # Genel Gider Analiz sayfası seçimi
                        st.sidebar.markdown("---")
                        st.sidebar.header("💰 Genel Gider Analiz")
                        genel_gider_enabled = False
                        if "Genel Gider Analiz" in sheet_names:
                            genel_gider_enabled = st.sidebar.checkbox("Genel Gider Analiz", key="genel_gider_sheet")
                        else:
                            st.sidebar.warning("Genel Gider Analiz sayfası bulunamadı")

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
                                gider_df = pd.read_excel(uploaded_file, sheet_name="Genel Gider Analiz")

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
                                        render_subsection_heading("Kategoriye Göre Gider Dağılımı", icon="📁")

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
                                        kategori_display['Toplam Maliyet'] = kategori_display['Toplam Maliyet'].apply(format_currency_gider)
                                        kategori_display['Maliyet %'] = kategori_display['Maliyet %'].apply(lambda x: f"%{x:.2f}")
                                        kategori_display['Kümülatif %'] = kategori_display['Kümülatif %'].apply(lambda x: f"%{x:.2f}")
                                        st.dataframe(kategori_display, use_container_width=True, hide_index=True)

                                        st.markdown("<br>", unsafe_allow_html=True)

                                        # ===== GİDER ADINA GÖRE DETAYLI ANALİZ =====
                                        render_subsection_heading("Gider Kalemine Göre Detaylı Analiz", icon="📋")

                                        # En yüksekten en düşüğe sıralı tablo
                                        gider_display = gider_df_sorted[['Kategori', 'Gider Adı', 'Maliyet', 'Maliyet %', 'Kümülatif %']].copy()
                                        gider_display['Maliyet'] = gider_df_sorted['Maliyet'].apply(format_currency_gider)
                                        gider_display['Maliyet %'] = gider_df_sorted['Maliyet %'].apply(lambda x: f"%{x:.2f}")
                                        gider_display['Kümülatif %'] = gider_df_sorted['Kümülatif %'].apply(lambda x: f"%{x:.2f}")

                                        st.dataframe(gider_display, use_container_width=True, hide_index=True, height=400)

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
                                            st.info(f"📈 **80/20 Analizi:** Toplam giderlerin %80'i **{items_80_gider} kalem** tarafından oluşturuluyor. (Toplam {len(gider_df_sorted)} kalem)")
                                        else:
                                            st.info("📈 **80/20 Analizi:** İlk kalem zaten %80'in üzerinde maliyet oluşturuyor.")

                                        # En yüksek ve en düşük 5 gider
                                        col_top, col_bottom = st.columns(2)

                                        with col_top:
                                            st.markdown("**🔴 En Yüksek 5 Gider:**")
                                            top5 = gider_df_sorted.head(5)[['Kategori', 'Gider Adı', 'Maliyet', 'Maliyet %']].copy()
                                            top5['Maliyet'] = gider_df_sorted.head(5)['Maliyet'].apply(format_currency_gider)
                                            top5['Maliyet %'] = gider_df_sorted.head(5)['Maliyet %'].apply(lambda x: f"%{x:.2f}")
                                            st.dataframe(top5, use_container_width=True, hide_index=True)

                                        with col_bottom:
                                            st.markdown("**🟢 En Düşük 5 Gider:**")
                                            bottom5 = gider_df_sorted.tail(5)[['Kategori', 'Gider Adı', 'Maliyet', 'Maliyet %']].copy()
                                            bottom5['Maliyet'] = gider_df_sorted.tail(5)['Maliyet'].apply(format_currency_gider)
                                            bottom5['Maliyet %'] = gider_df_sorted.tail(5)['Maliyet %'].apply(lambda x: f"%{x:.2f}")
                                            st.dataframe(bottom5, use_container_width=True, hide_index=True)

                                    else:
                                        st.warning("⚠️ Genel Gider Analiz sayfasında maliyet değeri olan satır bulunamadı.")
                                else:
                                    st.error("❌ Genel Gider Analiz sayfası en az 3 sütun içermelidir (Kategori, Gider Adı, Maliyet).")

                            except Exception as e:
                                st.error(f"❌ Genel Gider Analiz sayfası okunurken hata: {str(e)}")

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
