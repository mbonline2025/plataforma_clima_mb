import streamlit as st
import pandas as pd
import re
from io import BytesIO
from components.excel_formatador import exportar_excel_formatado

colunas_essenciais = [
    "Qual  o seu superior imediato?",
    "e)   De um modo geral qual a nota (0 a 10) atribuiria a sua experiência na empresa?"
]

def ler_excel_seguro(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {uploaded_file.name}:")
        st.exception(e)
        return None

def validar_colunas(df, nome_arquivo):
    faltantes = [col for col in colunas_essenciais if col not in df.columns]
    if faltantes:
        st.warning(f"⚠️ Arquivo '{nome_arquivo}' está faltando colunas essenciais: {faltantes}")
        return False
    return True

def show():
    st.header("Upload & Unificação de Pesquisas de Clima - 2025")
    st.markdown("""
    Faça o upload dos arquivos Excel das pesquisas de clima.  
    Os arquivos devem ter nomes no formato:  
    `PESQUISA DE CLIMA [BASE] - 2025 (respostas).xlsx`
    """)

    uploaded_files = st.file_uploader("Selecione os arquivos Excel", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files:
        dfs = []
        total_linhas = 0
        for uploaded_file in uploaded_files:
            df = ler_excel_seguro(uploaded_file)
            if df is None:
                continue

            padrao = r'PESQUISA DE CLIMA (.*?)\s*-\s*2025'
            match = re.search(padrao, uploaded_file.name)
            base = match.group(1).strip() if match else "Desconhecido"
            df["BASE"] = base

            if not validar_colunas(df, uploaded_file.name):
                continue

            total_linhas += len(df)
            dfs.append(df)
            st.success(f"✅ {uploaded_file.name} carregado com sucesso. {len(df)} registros da base '{base}'")

        if dfs:
            df_unificado = pd.concat(dfs, ignore_index=True).drop_duplicates()
            colunas = list(df_unificado.columns)
            if "BASE" in colunas:
                colunas.insert(0, colunas.pop(colunas.index("BASE")))
            df_unificado = df_unificado[colunas]
            st.session_state.df_unificado = df_unificado

            st.markdown(f"### Dados Unificados ({total_linhas} respostas)")
            st.dataframe(df_unificado.head(20), use_container_width=True, height=400)

            excel_formatado = exportar_excel_formatado(df_unificado)
            st.download_button(
                "📥 Download Excel Personalizado",
                data=excel_formatado,
                file_name="dados_unificados_formatado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhum dado foi unificado. Verifique se os arquivos possuem as colunas esperadas.")
