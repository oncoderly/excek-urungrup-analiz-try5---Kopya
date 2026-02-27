def apply_global_styles(st):
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
    
    /* Sidebar modern görünüm */
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        border-right: 1px solid #dbeafe;
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    [data-testid="stSidebar"] .stTextInput > div > div,
    [data-testid="stSidebar"] .stNumberInput > div > div,
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        background: #ffffff !important;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04) !important;
    }
    
    [data-testid="stSidebar"] .stTextInput > label,
    [data-testid="stSidebar"] .stNumberInput > label,
    [data-testid="stSidebar"] .stSelectbox > label,
    [data-testid="stSidebar"] .stCheckbox > label {
        color: #334155 !important;
        font-weight: 600 !important;
    }
    
    .sidebar-modern-header {
        margin: 0 0 12px 0;
        padding: 12px 14px;
        border-radius: 12px;
        border: 1px solid #bfdbfe;
        background: linear-gradient(135deg, #dbeafe, #eff6ff);
        color: #1e3a8a;
        font-size: 17px;
        font-weight: 800;
        letter-spacing: 0.2px;
    }
    
    .sidebar-section-title {
        margin: 12px 0 8px 0;
        padding: 10px 12px;
        border-radius: 10px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        color: #0f172a;
        font-size: 14px;
        font-weight: 700;
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
    
    /* Sankey etiketlerini sadeleştir: sadece siyah yazı, çizgi/gölge yok */
    .js-plotly-plot .sankey text {
        fill: #000000 !important;
        stroke: none !important;
        text-shadow: none !important;
    }
    }
    </style>
    """, unsafe_allow_html=True)
