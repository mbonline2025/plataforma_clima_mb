import streamlit as st
import pandas as pd
import unicodedata
import re
from io import BytesIO
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import umap.umap_ as umap
import numpy as np
from collections import Counter
import plotly.express as px
from textblob import TextBlob

# Função segura para ler arquivos Excel
@st.cache_data(show_spinner=False)
def ler_excel_seguro(uploaded_file):
    try:
        return pd.read_excel(uploaded_file, sheet_name=0, engine="openpyxl")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {uploaded_file.name}:")
        st.exception(e)
        return None

# Função para normalizar string (remove acentos e converte para caixa baixa)
def normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.lower().strip()

# Função para detectar automaticamente a coluna de comentários,
# incluindo o padrão "espaco reservado para comentarios sobre o item"
def detectar_coluna_comentarios(df):
    keywords = [
        "coment", 
        "espaco reservado para coment", 
        "espaco reservado para comentarios sobre o item", 
        "observ", 
        "sugest", 
        "respost"
    ]
    comentarios_colunas = []
    ignoradas = []
    for col in df.columns:
        nome_normalizado = normalizar(col)
        if any(keyword in nome_normalizado for keyword in keywords):
            comentarios_colunas.append(col)
        else:
            ignoradas.append(col)
    if comentarios_colunas:
        st.info(f"🧠 Colunas de comentário detectadas: {comentarios_colunas}")
    if ignoradas:
        st.caption(f"🔍 Colunas ignoradas: {ignoradas}")
    return comentarios_colunas

# Função de análise de sentimento usando TextBlob
def analisar_sentimento(texto):
    blob = TextBlob(texto)
    polaridade = blob.sentiment.polarity
    if polaridade > 0.1:
        return "Positivo"
    elif polaridade < -0.1:
        return "Negativo"
    else:
        return "Neutro"

# Função para agrupamento semântico dos comentários
def clusterizar_comentarios(lista_textos):
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = modelo.encode(lista_textos, show_progress_bar=True)
    clusterizador = DBSCAN(eps=0.4, min_samples=2, metric='cosine')
    labels = clusterizador.fit_predict(embeddings)
    reducer = umap.UMAP(n_neighbors=10, min_dist=0.3, metric='cosine')
    reduzido = reducer.fit_transform(embeddings)
    return labels, reduzido

# Função para processamento e unificação dos arquivos
@st.cache_data(show_spinner=False)
def processar_arquivos(uploaded_files):
    dfs = []
    for uploaded_file in uploaded_files:
        df = ler_excel_seguro(uploaded_file)
        if df is None:
            continue

        padrao = r'PESQUISA DE CLIMA (.*?)\s*-\s*2025'
        match = re.search(padrao, uploaded_file.name)
        base = match.group(1).strip() if match else "Desconhecido"
        df["BASE"] = base

        colunas_comentario = detectar_coluna_comentarios(df)
        if colunas_comentario:
            comentarios = []
            for col in colunas_comentario:
                # Converte cada valor para string, removendo espaços extras
                valores = df[col].astype(str).str.strip()
                for valor in valores:
                    # Descarta valores vazios ou "nan"
                    if valor and valor.lower() != "nan":
                        # Divide o conteúdo da célula em linhas separadas e adiciona cada linha não vazia como comentário individual
                        linhas = [linha.strip() for linha in valor.splitlines() if linha.strip() != ""]
                        comentarios += linhas
            if comentarios:
                df_com = pd.DataFrame({"BASE": base, "COMENTARIO": comentarios})
                dfs.append(df_com)
                st.success(f"✅ {len(comentarios)} comentários detectados na base '{base}'.")
            else:
                st.warning(f"⚠️ A base '{base}' possui colunas de comentário, mas não há valores preenchidos.")
        else:
            st.warning(f"❌ A base '{base}' não possui nenhuma coluna de comentários detectável.")

    if dfs:
        df_unificado = pd.concat(dfs, ignore_index=True).drop_duplicates()
        return df_unificado
    else:
        return None

# Página principal que integra o upload e as análises com IA semântica
def show():
    st.header("Upload e Análise de Comentários com IA Semântica")

    if st.session_state.get("df_unificado") is not None:
        df_unificado = st.session_state.df_unificado
    else:
        uploaded_files = st.file_uploader("📤 Selecione os arquivos Excel", type=["xlsx"], accept_multiple_files=True)
        if uploaded_files:
            df_unificado = processar_arquivos(uploaded_files)
            if df_unificado is not None:
                st.session_state.df_unificado = df_unificado
            else:
                st.error("❌ Nenhum dado unificado foi processado.")
                return
        else:
            st.warning("Faça upload dos arquivos na aba de Upload e Unificação.")
            return

    st.success("✔️ Dados unificados carregados!")
    st.dataframe(df_unificado.head(10))

    # Permite baixar o Excel unificado
    towrite = BytesIO()
    df_unificado.to_excel(towrite, index=False)
    towrite.seek(0)
    st.download_button("📥 Baixar Excel Unificado", towrite, "unificado.xlsx", 
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader("🔎 Análise de IA por Base")
    base_sel = st.selectbox("Selecione a base:", df_unificado["BASE"].unique())

    if "COMENTARIO" not in df_unificado.columns:
        st.warning("Nenhuma coluna de comentários foi identificada no dataframe unificado.")
        return

    comentarios = df_unificado[df_unificado["BASE"] == base_sel]["COMENTARIO"].dropna().astype(str)
    if not comentarios.empty:
        textos = comentarios.tolist()
        df_sent = pd.DataFrame({"comentario": textos})
        df_sent["Sentimento"] = df_sent["comentario"].apply(analisar_sentimento)
        st.plotly_chart(px.histogram(df_sent, x="Sentimento", title="Distribuição de Sentimentos"))

        st.subheader("🧠 Agrupamento por Similaridade de Sentido")
        with st.spinner("Processando IA semântica..."):
            labels, coords = clusterizar_comentarios(textos)
            df_sent["Cluster"] = labels
            df_sent["x"] = coords[:, 0]
            df_sent["y"] = coords[:, 1]

        st.plotly_chart(px.scatter(
            df_sent,
            x="x",
            y="y",
            color=df_sent["Cluster"].astype(str),
            hover_data=["comentario"],
            title="Mapa Semântico dos Comentários"
        ))

        st.subheader("📌 Comentários por Grupo")
        for cluster_id in sorted(df_sent["Cluster"].unique()):
            st.markdown(f"### {'Comentários Únicos' if cluster_id == -1 else f'Grupo {cluster_id}'}")
            for linha in df_sent[df_sent["Cluster"] == cluster_id]["comentario"].head(5):
                st.markdown(f"- {linha}")
    else:
        st.info("Não há comentários válidos nesta base para análise.")

if __name__ == "__main__":
    show()
