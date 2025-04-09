# visualizacoes.py atualizado para exibir dados em % e contagem

import pandas as pd
import plotly.express as px
import streamlit as st

def _formatar_porcentagem(df, group_cols, value_col=None):
    """Função auxiliar para calcular porcentagens"""
    if value_col:
        total = df.groupby(group_cols)[value_col].sum().reset_index()
        contagem = df.groupby(group_cols + [value_col]).size().reset_index(name='Contagem')
        merged = pd.merge(contagem, total, on=group_cols, suffixes=('', '_total'))
        merged['Porcentagem'] = (merged['Contagem'] / merged['Contagem_total']) * 100
        return merged
    else:
        contagem = df.groupby(group_cols).size().reset_index(name='Contagem')
        total = contagem['Contagem'].sum()
        contagem['Porcentagem'] = (contagem['Contagem'] / total) * 100
        return contagem

# Gráfico 1: Contagem/porcentagem de respostas por base
def grafico_respostas_por_base(df: pd.DataFrame, porcentagem: bool = True):
    dados = _formatar_porcentagem(df, ['BASE'])
    
    fig = px.bar(
        dados,
        x="BASE",
        y="Porcentagem" if porcentagem else "Contagem",
        title=f"Respostas por Base ({'%' if porcentagem else 'Contagem'})",
        color="BASE",
        text_auto='.1f' if porcentagem else True,
        color_discrete_sequence=px.colors.qualitative.Vivid,
        labels={'Porcentagem': 'Porcentagem (%)', 'Contagem': 'Número de Respostas'}
    )
    
    if porcentagem:
        fig.update_yaxes(title_text="Porcentagem (%)", range=[0, 100])
    else:
        fig.update_yaxes(title_text="Número de Respostas")
    
    st.plotly_chart(fig, use_container_width=True)

# Gráfico 2: Nota média geral por base (mantido original)
def grafico_nota_media_por_base(df: pd.DataFrame, coluna_nota: str):
    df[coluna_nota] = pd.to_numeric(df[coluna_nota], errors='coerce')
    media = df.groupby("BASE")[coluna_nota].mean().reset_index()
    media.columns = ["BASE", "Nota Média"]
    
    fig = px.line(
        media,
        x="BASE",
        y="Nota Média",
        title="Nota Média por Base",
        markers=True,
        text="Nota Média",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_traces(texttemplate='%{y:.2f}', textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

# Gráfico 3: Distribuição por questão de uma categoria específica
def grafico_distribuicao_por_questao(df: pd.DataFrame, coluna: str, porcentagem: bool = True):
    dados = _formatar_porcentagem(df, ['BASE', coluna])
    
    fig = px.bar(
        dados,
        x="BASE",
        y="Porcentagem" if porcentagem else "Contagem",
        color=coluna,
        barmode="group",
        title=f"Distribuição das Respostas - {coluna} ({'%' if porcentagem else 'Contagem'})",
        text_auto='.1f' if porcentagem else True,
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={'Porcentagem': 'Porcentagem (%)', 'Contagem': 'Número de Respostas'}
    )
    
    if porcentagem:
        fig.update_yaxes(title_text="Porcentagem (%)", range=[0, 100])
    else:
        fig.update_yaxes(title_text="Número de Respostas")
    
    st.plotly_chart(fig, use_container_width=True)

# Gráfico 4: Comparação das notas por base (Boxplot)
def grafico_boxplot_notas(df: pd.DataFrame, coluna_nota: str):
    df[coluna_nota] = pd.to_numeric(df[coluna_nota], errors='coerce')
    
    fig = px.box(
        df,
        x="BASE",
        y=coluna_nota,
        title="Distribuição de Notas por Base",
        color="BASE",
        points="all",
        color_discrete_sequence=px.colors.qualitative.Prism,
        hover_data=["BASE", coluna_nota]
    )
    fig.update_yaxes(title_text="Nota (0-10)", range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)

# Gráfico 5: Pizza com proporção de respostas por base
def grafico_pizza_respostas(df: pd.DataFrame, porcentagem: bool = True):
    dados = _formatar_porcentagem(df, ['BASE'])
    
    fig = px.pie(
        dados,
        names="BASE",
        values="Porcentagem" if porcentagem else "Contagem",
        title=f"Proporção de Respostas por Base ({'%' if porcentagem else 'Contagem'})",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Dark2,
        labels={'Porcentagem': 'Porcentagem (%)', 'Contagem': 'Número de Respostas'}
    )
    fig.update_traces(textinfo='percent+label' if porcentagem else 'value+label')
    st.plotly_chart(fig, use_container_width=True)

# Gráfico 6: Barras agrupadas por alternativa de uma pergunta específica
def grafico_respostas_por_fator(df: pd.DataFrame, coluna: str, porcentagem: bool = True):
    dados = _formatar_porcentagem(df, ['BASE', coluna])
    
    fig = px.bar(
        dados,
        x="BASE",
        y="Porcentagem" if porcentagem else "Contagem",
        color=coluna,
        barmode="group",
        title=f"Distribuição das Respostas para '{coluna}' por Base ({'%' if porcentagem else 'Contagem'})",
        text_auto='.1f' if porcentagem else True,
        color_discrete_sequence=px.colors.qualitative.Set3,
        labels={'Porcentagem': 'Porcentagem (%)', 'Contagem': 'Número de Respostas'}
    )
    
    if porcentagem:
        fig.update_yaxes(title_text="Porcentagem (%)", range=[0, 100])
    else:
        fig.update_yaxes(title_text="Número de Respostas")
    
    st.plotly_chart(fig, use_container_width=True)