import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from html import escape

# st-aggrid'i opsiyonel yap
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
    HAS_AGGRID = True
except ImportError:
    HAS_AGGRID = False
    st.warning("⚠️ st-aggrid bulunamadı. Tablo görünümü basit modda çalışacak.")

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

/* Basit tablo stilleri */
.stDataFrame {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border-color);
}

/* Başlık stilleri */
h1, h2, h3 {
    color: var(--primary-color) !important;
    font-weight: 700 !important;
}

/* Metrik kutular */
.metric-container {
    background: linear-gradient(135deg, #f8fafc, #ffffff);
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

def show_dataframe(df, title="Veri Tablosu"):
    """DataFrame gösterimi - st-aggrid varsa onu kullan, yoksa basit tablo"""
    st.subheader(title)

    if HAS_AGGRID:
        # AgGrid ile gelişmiş tablo
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_selection('single')
        gridOptions = gb.build()

        AgGrid(
            df,
            gridOptions=gridOptions,
            data_return_mode=DataReturnMode.AS_INPUT,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
            height=400,
            theme='material'
        )
    else:
        # Basit Streamlit tablosu
        st.dataframe(
            df,
            use_container_width=True,
            height=400,
            hide_index=True
        )

# Ana uygulama başlığı
st.title("📊 Excel Analiz Uygulaması")
st.markdown("Excel dosyalarınızı yükleyin ve detaylı analizler yapın.")

# Dosya yükleme
uploaded_file = st.file_uploader(
    "Excel dosyanızı seçin",
    type=['xlsx', 'xls'],
    help="Excel formatında dosya yükleyebilirsiniz"
)

if uploaded_file is not None:
    try:
        # Dosyayı okuma
        with st.spinner('Dosya okunuyor...'):
            df = pd.read_excel(uploaded_file)

        st.success(f"✅ Dosya başarıyla yüklendi! ({len(df)} satır, {len(df.columns)} sütun)")

        # Temel bilgiler
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Toplam Satır", len(df))
        with col2:
            st.metric("Toplam Sütun", len(df.columns))
        with col3:
            st.metric("Boş Hücreler", df.isnull().sum().sum())
        with col4:
            st.metric("Dosya Boyutu", f"{uploaded_file.size / 1024:.1f} KB")

        # Sekme menüleri
        tab1, tab2, tab3 = st.tabs(["📋 Veri Görünümü", "📊 İstatistikler", "📈 Grafikler"])

        with tab1:
            show_dataframe(df, "Excel Verileri")

            # Sütun bilgileri
            st.subheader("Sütun Bilgileri")
            col_info = pd.DataFrame({
                'Sütun Adı': df.columns,
                'Veri Tipi': df.dtypes.astype(str),
                'Boş Değer': df.isnull().sum().values,
                'Benzersiz Değer': df.nunique().values
            })
            st.dataframe(col_info, use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("İstatistiksel Özet")

            # Sayısal sütunlar için istatistik
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.write("**Sayısal Sütunlar için İstatistikler:**")
                show_dataframe(df[numeric_cols].describe().round(2), "İstatistiksel Özet")
            else:
                st.info("Sayısal sütun bulunamadı.")

            # Kategorik sütunlar için özet
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                st.write("**Kategorik Sütunlar için Özet:**")
                cat_summary = []
                for col in categorical_cols[:5]:  # İlk 5 kategorik sütun
                    top_values = df[col].value_counts().head(3)
                    cat_summary.append({
                        'Sütun': col,
                        'En Sık Değer': top_values.index[0] if len(top_values) > 0 else 'N/A',
                        'Frekans': top_values.iloc[0] if len(top_values) > 0 else 0,
                        'Benzersiz': df[col].nunique()
                    })

                if cat_summary:
                    show_dataframe(pd.DataFrame(cat_summary), "Kategorik Sütun Özeti")

        with tab3:
            st.subheader("Veri Görselleştirme")

            if len(numeric_cols) > 0:
                # Histogram
                selected_col = st.selectbox("Histogram için sütun seçin:", numeric_cols)
                if selected_col:
                    fig = px.histogram(df, x=selected_col, title=f"{selected_col} Dağılımı")
                    fig.update_layout(
                        template="plotly_white",
                        title_font_size=16,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Korelasyon matrisi (sadece sayısal sütunlar için)
                if len(numeric_cols) > 1:
                    st.write("**Korelasyon Matrisi:**")
                    corr_matrix = df[numeric_cols].corr()
                    fig_corr = px.imshow(
                        corr_matrix,
                        title="Sütunlar Arası Korelasyon",
                        color_continuous_scale="RdBu_r",
                        aspect="auto"
                    )
                    fig_corr.update_layout(height=500)
                    st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("Grafik için sayısal sütun bulunamadı.")

            # Kategorik veriler için bar chart
            if len(categorical_cols) > 0:
                cat_col = st.selectbox("Bar grafik için kategorik sütun seçin:", categorical_cols)
                if cat_col:
                    value_counts = df[cat_col].value_counts().head(10)
                    fig_bar = px.bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        title=f"{cat_col} - En Sık 10 Değer",
                        labels={'x': cat_col, 'y': 'Frekans'}
                    )
                    fig_bar.update_layout(
                        template="plotly_white",
                        height=400,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

    except Exception as e:
        st.error(f"Dosya okunurken hata oluştu: {str(e)}")
        st.info("Lütfen geçerli bir Excel dosyası yüklediğinizden emin olun.")

else:
    # Yükleme talimatları
    st.info("👆 Lütfen analiz yapmak için bir Excel dosyası yükleyin")

    with st.expander("ℹ️ Nasıl kullanılır?"):
        st.write("""
        1. **Excel Dosyası Yükleyin**: Yukarıdaki alana Excel dosyanızı sürükleyin veya seçin
        2. **Veri Görünümü**: Yüklenen verilerinizi tabloda inceleyin
        3. **İstatistikler**: Verilerinizin istatistiksel özetini görün
        4. **Grafikler**: Verilerinizi görsel olarak analiz edin

        **Desteklenen formatlar**: .xlsx, .xls
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 2rem;'>"
    "📊 Excel Analiz Uygulaması - Verilerinizi kolayca analiz edin"
    "</div>",
    unsafe_allow_html=True
)