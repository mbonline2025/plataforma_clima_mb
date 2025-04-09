# filtros.py atualizado para filtros reutilizáveis e compatíveis com múltiplas bases

import pandas as pd
import streamlit as st

def aplicar_filtros_topbar(df: pd.DataFrame):
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        bases = df["BASE"].dropna().unique().tolist()
        selected_bases = st.multiselect("Bases", bases, default=bases)
    with col2:
        superior_col = "Qual  o seu superior imediato?"
        if superior_col in df.columns:
            superiores = df[superior_col].dropna().unique().tolist()
            selected_superior = st.multiselect("Superior Imediato", superiores, default=superiores)
        else:
            selected_superior = []
    with col3:
        termo_busca = st.text_input("Pesquisar texto (exato ou parcial)", "")

    df_filtrado = df[df["BASE"].isin(selected_bases)]
    if selected_superior:
        df_filtrado = df_filtrado[df_filtrado[superior_col].isin(selected_superior)]

    if termo_busca.strip():
        df_filtrado = df_filtrado[df_filtrado.apply(lambda row: row.astype(str).str.contains(termo_busca, case=False).any(), axis=1)]

    return df_filtrado
