import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Função segura para ler arquivos Excel

def ler_excel_seguro(uploaded_file):
    try:
        return pd.read_excel(uploaded_file, sheet_name=0, engine="openpyxl")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {uploaded_file.name}:")
        st.exception(e)
        return None

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
        for uploaded_file in uploaded_files:
            df = ler_excel_seguro(uploaded_file)
            if df is None:
                continue

            # Extrai a base do nome do arquivo usando expressão regular
            padrao = r'PESQUISA DE CLIMA (.*?)\s*-\s*2025'
            match = re.search(padrao, uploaded_file.name)
            base = match.group(1).strip() if match else "Desconhecido"
            df["BASE"] = base
            dfs.append(df)

        if dfs:
            df_unificado = pd.concat(dfs, ignore_index=True).drop_duplicates()
            colunas = list(df_unificado.columns)
            if "BASE" in colunas:
                colunas.insert(0, colunas.pop(colunas.index("BASE")))
            df_unificado = df_unificado[colunas]
            st.session_state.df_unificado = df_unificado

            st.success("Dados unificados com sucesso!")
            st.dataframe(df_unificado.head(10))

            # Download do Excel Unificado
            towrite = BytesIO()
            df_unificado.to_excel(towrite, index=False, sheet_name="Unificado")
            towrite.seek(0)
            st.download_button("Download do Excel Unificado", data=towrite, file_name="unified_data.xlsx", mime="application/vnd.ms-excel")
        else:
            st.warning("Nenhum DataFrame foi processado corretamente.")
