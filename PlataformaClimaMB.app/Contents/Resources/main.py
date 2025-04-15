import streamlit as st
from datetime import datetime
from modulos import uploader, dashboard, comentarios

st.set_page_config(
    page_title="MB Consultoria - Clima Organizacional",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔒 [Seção Ocultada do Front-End]
# Esta parte do código permite comparar resultados por questão específica.
# Está comentada temporariamente — pode ser reativada se necessário no futuro.
# Tema leve escuro
#modo = st.sidebar.selectbox("🌗 Tema", ["Claro", "Escuro"], index=0, key="modo_tema")
#if modo == "Escuro":
#    st.markdown("""
#       <style>
#            .stApp {
#               background-color: #2c2c2c !important;
#                color: #eaeaea !important;
#            }
#           .stMarkdown h3, .stMarkdown p, .stRadio label, .stSelectbox label, .stTextInput label {
#                color: #f1f1f1 !important;
#            }
#        </style>
#    """, unsafe_allow_html=True)

# Sidebar com logo e navegação
with st.sidebar:
    try:
        st.image("logo.png", width=180)
    except:
        st.warning("⚠️ Logo não encontrada")

    st.markdown("## 🧭 Navegação")
    pages = {
        "📤 Upload & Unificação": uploader.show,
        "📈 Dashboard Geral": dashboard.show,
        "💬 Análise de Comentários": comentarios.show
    }
    selection = st.radio("Escolha uma seção:", list(pages.keys()))
    st.markdown("---")
    st.caption(f"Desenvolvido por MB Consultoria | © {datetime.now().year}")
    st.markdown("<small><a href='https://www.mbconsultoria.com/' target='_blank'>www.mbconsultoria.com</a></small>", unsafe_allow_html=True)

st.markdown("---")
pages[selection]()
