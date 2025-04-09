# Atualizações para o dashboard.py com filtro por categoria e melhorias na visualização

import streamlit as st
import pandas as pd
import plotly.express as px

# Mapeamento de categorias baseado nas perguntas
dimensoes = {
    "Colaboração": [
        "a) Existe o estímulo a colaboração em nossa empresa?",
        "b) Há cooperação entre as pessoas do meu setor?",
        "c)  A colaboração resulta no alcance das nossas metas/objetivos?",
        "d)  A colaboração tem favorecido um clima de trabalho positivo no meu setor?",
        "e) Sinto-me à vontade para pedir ajuda nas minhas atividades, sempre que preciso?"
    ],
    "Comunicação": [
        "a) Os canais de comunicação interna contribuem para manter todos informados?",
        "b) As informações fluem bem entre as áreas da empresa?",
        "c) A comunicação na empresa, reflete confiança e respeito?",
        "d) Costumo receber respostas (feedback) sempre que necessário?",
        "e) Sou bem informado sobre as metas e resultados da empresa?"
    ],
    "Informações Essenciais": [
        "a)  Recebo informações suficientes sobre os Valores e Políticas da empresa?",
        "b) Percebo ações, na prática, voltadas ao atendimento ao cliente?",
        "c) Recebo informações e direcionamentos suficientes sobre as minhas atividades?",
        "d) A empresa incentiva a aprendizagem e inovação?",
        "e. A empresa possui um Código de Ética claro e divulgado?"
    ],
    "Liderança": [
        "a) Tenho abertura para comunicar-me com meu gestor(a)?",
        "b) Meu gestor(a) me possibilita assumir desafios e crescer profissionalmente?",
        "c) Meu gestor (a) estimula a colaboração e o trabalho em equipe?",
        "d) Meu gestor(a) promove um ambiente de trabalho respeitoso e inclusivo?",
        "e) Considero adequado o estilo de liderança do meu gestor(a)?"
    ],
    "Motivação": [
        "a) As ferramentas disponíveis contribuem para o bom desempenho do meu trabalho?",
        "b)  Meu trabalho permite equilibrar vida pessoal e profissional?",
        "c)  A minha remuneração e benefícios são justos?",
        "d) Sinto-me estimulado a dar o meu melhor no ambiente de trabalho?",
        "e.  As refeições oferecidas na empresa são satisfatórias?"
    ],
    "Organização": [
        "a) A empresa possui uma boa direção e gestão estratégica?",
        "b)  A empresa tem uma cultura forte e positiva?",
        "c)  A imagem e a marca da empresa são bem conceituadas?",
        "d)  Percebo que a organização se preocupa com o bem-estar dos colaboradores?",
        "e) Compreendo como o meu trabalho contribui para os resultados da empresa?"
    ],
    "Trabalho": [
        "a)  As condições físicas de trabalho no meu setor são adequadas?",
        "b)   Recebo treinamentos e instruções suficientes, para a realização do meu trabalho?",
        "c)  Eu tenho acesso aos materiais, Epis e/ou equipamentos necessários para fazer bem o meu trabalho?",
        "d) Sinto que posso contribuir com ideias e soluções no meu trabalho?",
        "e) Sei o que é esperado do meu trabalho?"
    ],
    "Felicidade": [
        "a) Sinto que sou valorizado e reconhecido no meu ambiente de trabalho?",
        "b) Sinto orgulho de trabalhar nesta empresa?",
        "c) Sinto que o meu trabalho é estimulante e gratificante?",
        "d) Que sugestões você daria para tornar nossa empresa um lugar ainda melhor para se trabalhar?",
        "e)   De um modo geral qual a nota (0 a 10) atribuiria a sua experiência na empresa?"
    ]
}

def show():
    st.title("Dashboard Geral - Versão Aprimorada")

    if st.session_state.get("df_unificado") is not None:
        df_unificado = st.session_state.df_unificado

        st.sidebar.header("Filtros")
        bases = df_unificado["BASE"].unique().tolist()
        selected_bases = st.sidebar.multiselect("Selecione as Bases", bases, default=bases)
        df_filtrado = df_unificado[df_unificado["BASE"].isin(selected_bases)]

        superior_col = "Qual  o seu superior imediato?"
        if superior_col in df_unificado.columns:
            superiores = df_filtrado[superior_col].dropna().unique().tolist()
            selected_superior = st.sidebar.multiselect("Selecione o Superior Imediato", superiores, default=superiores)
            df_filtrado = df_filtrado[df_filtrado[superior_col].isin(selected_superior)]

        # Novo filtro por categoria (dimensão)
        st.sidebar.markdown("---")
        selected_dimensao = st.sidebar.selectbox("Selecione a Categoria", ["Todas"] + list(dimensoes.keys()))

        if selected_dimensao != "Todas":
            colunas_perguntas = dimensoes[selected_dimensao]
            colunas_validas = [col for col in colunas_perguntas if col in df_filtrado.columns]
            df_filtrado = df_filtrado[colunas_validas + ["BASE"]]

        st.subheader("Dados Filtrados")
        st.dataframe(df_filtrado, use_container_width=True, height=500)

        st.markdown("---")
        st.subheader("Análise por Categoria/Questão")

        if selected_dimensao != "Todas" and colunas_validas:
            for coluna in colunas_validas:
                fig = px.histogram(
                    df_filtrado,
                    x=coluna,
                    color="BASE",
                    barmode="group",
                    title=f"Distribuição das Respostas - {coluna}"
                )
                st.plotly_chart(fig, use_container_width=True)

        # Resultado Geral (quando Todas ou nenhuma dim. filtrada)
        if selected_dimensao == "Todas":
            count_by_base = df_filtrado["BASE"].value_counts().reset_index()
            count_by_base.columns = ["BASE", "Contagem"]
            fig1 = px.bar(count_by_base, x="BASE", y="Contagem", title="Número de Respostas por Base")
            st.plotly_chart(fig1, use_container_width=True)

    else:
        st.warning("Nenhum dado unificado disponível. Por favor, faça o upload dos arquivos na seção 'Upload & Unificação'.")
