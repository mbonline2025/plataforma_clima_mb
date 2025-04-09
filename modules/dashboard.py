import streamlit as st
import pandas as pd
import plotly.express as px

def show():
    st.title("Dashboard Geral - Versão Aprimorada")
    
    if st.session_state.get("df_unificado") is not None:
        df_unificado = st.session_state.df_unificado

        # Usando a sidebar para os filtros, deixando o layout principal mais limpo
        st.sidebar.header("Filtros")
        bases = df_unificado["BASE"].unique().tolist()
        selected_bases = st.sidebar.multiselect("Selecione as Bases", bases, default=bases)
        df_filtrado = df_unificado[df_unificado["BASE"].isin(selected_bases)]

        # Filtro para Superior Imediato, se a coluna existir
        superior_col = "Qual  o seu superior imediato?"
        if superior_col in df_unificado.columns:
            superiores = df_filtrado[superior_col].dropna().unique().tolist()
            selected_superior = st.sidebar.multiselect("Selecione o Superior Imediato", superiores, default=superiores)
            df_filtrado = df_filtrado[df_filtrado[superior_col].isin(selected_superior)]

        st.subheader("Dados Filtrados")
        st.dataframe(df_filtrado.head(10))

        st.markdown("---")
        st.subheader("Visualizações")

        # Dashboard A: Número de Respostas por Base (Gráfico de Barras)
        count_by_base = df_filtrado["BASE"].value_counts().reset_index()
        count_by_base.columns = ["BASE", "Contagem"]
        fig1 = px.bar(count_by_base, 
                      x="BASE", 
                      y="Contagem", 
                      title="Número de Respostas por Base", 
                      color="BASE",
                      color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig1)

        # Dashboard B: Nota Média por Base (Gráfico de Linhas)
        rating_col = "e)   De um modo geral qual a nota (0 a 10) atribuiria a sua experiência na empresa?"
        if rating_col in df_filtrado.columns:
            df_filtrado[rating_col] = pd.to_numeric(df_filtrado[rating_col], errors='coerce')
            avg_rating = df_filtrado.groupby("BASE")[rating_col].mean().reset_index()
            avg_rating.columns = ["BASE", "Nota Média"]
            fig2 = px.line(avg_rating, 
                           x="BASE", 
                           y="Nota Média", 
                           markers=True, 
                           title="Nota Média por Base",
                           color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig2)

        # Dashboard C: Distribuição das respostas de um Fator Específico por Base (Gráfico de Barras Agrupado)
        fator_options = [col for col in df_filtrado.columns if col.startswith(tuple("abcde)")) and "nota" not in col.lower()]
        if fator_options:
            selected_fator = st.selectbox("Selecione o Fator para Visualização", options=fator_options)
            fator_count = df_filtrado.groupby(["BASE", selected_fator]).size().reset_index(name="Contagem")
            fig3 = px.bar(fator_count, 
                          x="BASE", 
                          y="Contagem", 
                          color=selected_fator,
                          barmode="group", 
                          title=f"Distribuição das Respostas para '{selected_fator}' por Base",
                          color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig3)

        # Dashboard D: Comparação das Notas por Base (Gráfico Box)
        selected_comparison_bases = st.multiselect("Selecione as Bases para Comparação", options=bases, default=bases)
        if rating_col in df_filtrado.columns and selected_comparison_bases:
            df_comparison = df_filtrado[df_filtrado["BASE"].isin(selected_comparison_bases)]
            df_comparison[rating_col] = pd.to_numeric(df_comparison[rating_col], errors='coerce')
            fig4 = px.box(df_comparison, 
                          x="BASE", 
                          y=rating_col, 
                          title="Comparação das Notas por Base",
                          color="BASE",
                          color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig4)

        # Dashboard E: Proporção de Respostas por Base (Gráfico de Pizza)
        fig5 = px.pie(count_by_base, 
                      names="BASE", 
                      values="Contagem", 
                      title="Proporção de Respostas por Base",
                      color_discrete_sequence=px.colors.qualitative.Dark2)
        st.plotly_chart(fig5)

    else:
        st.warning("Nenhum dado unificado disponível. Por favor, faça o upload dos arquivos na seção 'Upload & Unificação'.")
