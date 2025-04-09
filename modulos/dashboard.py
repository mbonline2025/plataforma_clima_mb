import streamlit as st
import pandas as pd
import plotly.express as px
from components.filtros import aplicar_filtros_topbar
from components.visualizacoes import (
    grafico_respostas_por_base,
    grafico_nota_media_por_base,
    grafico_distribuicao_por_questao,
    grafico_boxplot_notas,
    grafico_pizza_respostas,
    grafico_respostas_por_fator
)

dimensoes = {
    "Colaboração": [
        "a) Existe o estímulo a colaboração em nossa empresa?",
        "b) Há cooperação entre as pessoas do meu setor?",
        "c)  A colaboração resulta no alcance das nossas metas/objetivos?",
        "d)  A colaboração tem favorecido um clima de trabalho positivo no meu setor?",
        "e) Sinto-me à vontade para pedir ajuda nas minhas atividades, sempre que preciso?"
    ],
    "Comunicação": [
        "a) Os canais de comunicação interna contribuem para nos manter informados. (workplace, aplicativo do Colaborador, murais, email etc)?",
        "b) As informações fluem bem entre as áreas da organização?",
        "c) A comunicação na empresa, reflete confiança e respeito?",
        "d) Costumo receber respostas (feedback) sempre que preciso?",
        "e) Sou bem informado sobre as metas e resultados da minha área. (reuniões/divulgações do Mapa Estratégico - BSC)?"
    ],
    "Informações Essenciais": [
        "a)  Recebo informações suficientes sobre os Valores e Princípios Organizacionais (integridade, respeito, econonia, energia  e melhoria contínua)?",
        "b) Percebo ações, na prática, voltadas ao atendimento normativo e de segurança na empresa?",
        "c) Recebo informações e direcionamentos suficientes  para a realização das minhas atividades?",
        "d) A empresa incentiva a aprendizagem e inovação ?",
        "e. A empresa possui um Código de Ética claro e amplamente divulgado?"
    ],
    "Liderança": [
        "a) Tenho abertura para comunicar-me com meu gestor(a)?",
        "b) Meu gestor(a) me possibilita assumir desafios e responsabilidades?",
        "c) Meu gestor (a) estimula a colaboração e o trabalho em equipe?",
        "d) Meu gestor(a) promove um ambiente de trabalho agradável e respeitoso?",
        "e) Considero adequado o estilo de liderança do meu gestor (a)"
    ],
    "Motivação": [
        "a) As ferramentas disponíveis contribuem para o meu desenvolvimento profissional (Internet / Ensino a distância,GUPY,  por exemplo)?",
        "b)  Meu trabalho permite equilibrar vida pessoal e profissional?",
        "c)  A minha remuneração e benefícios são justos em relação às minhas atividades/mercado de trabalho?",
        "d) Sinto-me estimulado a dar o meu melhor no ambiente de trabalho?",
        "e.  As refeições oferecidas na empresa são satisfatórias?"
    ],
    "Organização": [
        "a) A empresa possui uma boa direção e gestão estratégica?",
        "b)  A empresa tem uma cultura forte e positiva?",
        "c)  A imagem e a marca da empresa são bem conceituadas?",
        "d)  Percebo que a organização se preocupa com o bem estar dos colaboradores?",
        "e) Compreendo como o meu trabalho contribui para a realização da estratégia da empresa?"
    ],
    "Trabalho": [
        "a)  As condições físicas de trabalho no meu setor  são adequadas?",
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
    st.title("📈 Dashboard de Clima Organizacional")

    if st.session_state.get("df_unificado") is not None:
        df = st.session_state.df_unificado

        st.markdown("### 🔍 Filtros Gerais")
        df_filtrado = aplicar_filtros_topbar(df)

        st.markdown("---")
        st.subheader("📊 Dados Filtrados")
        st.dataframe(df_filtrado, use_container_width=True, height=500)

        st.markdown("---")
        st.subheader("📌 Análises e Indicadores")

        rating_col = "e)   De um modo geral qual a nota (0 a 10) atribuiria a sua experiência na empresa?"

        # Adicionando toggle para alternar entre contagem e porcentagem
        mostrar_porcentagem = st.toggle('Mostrar dados em porcentagem (%)', value=True)

        with st.expander("🔹 Análise por Categoria (Dimensão)", expanded=True):
            selected_dimensao = st.selectbox("Categoria de Análise", ["Todas"] + list(dimensoes.keys()))
            if selected_dimensao != "Todas":
                colunas = [c for c in df_filtrado.columns if any(pergunta in c for pergunta in dimensoes[selected_dimensao])]
                for coluna in colunas:
                    grafico_distribuicao_por_questao(df_filtrado, coluna, porcentagem=mostrar_porcentagem)

        with st.expander("🔹 Visão Geral por Base"):
            if rating_col in df_filtrado.columns:
                grafico_pizza_respostas(df_filtrado, porcentagem=mostrar_porcentagem)
                grafico_respostas_por_base(df_filtrado, porcentagem=mostrar_porcentagem)
                grafico_nota_media_por_base(df_filtrado, rating_col)
                grafico_boxplot_notas(df_filtrado, rating_col)
                


# 🔒 [Seção Ocultada do Front-End]
# Esta parte do código permite comparar resultados por questão específica.
# Está comentada temporariamente — pode ser reativada se necessário no futuro.

        # with st.expander("🔹 Comparação por Fator Específico"):
#     prefixos = ['a)', 'b)', 'c)', 'd)', 'e)']
#     fator_options = [
#         col for col in df_filtrado.columns 
#         if any(col.startswith(prefix) for prefix in prefixos)
#     ]
#     if fator_options:
#         selected_fator = st.selectbox(
#             "Selecione a Questão para Comparação:", 
#             options=fator_options
#         )
#         grafico_respostas_por_fator(
#             df_filtrado, 
#             selected_fator, 
#             porcentagem=mostrar_porcentagem
#         )

    else:
        st.warning("Nenhum dado unificado disponível. Por favor, faça o upload dos arquivos na seção 'Upload & Unificação'.")