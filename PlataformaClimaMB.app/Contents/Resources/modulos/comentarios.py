import streamlit as st
import pandas as pd
import unicodedata
import re
from collections import Counter
from io import BytesIO
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import umap.umap_ as umap
import plotly.express as px
from textblob import TextBlob
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

# Stopwords em português ampliadas
STOPWORDS_PT = set(STOPWORDS).union({
    'que', 'com', 'para', 'não', 'mais', 'muito', 'mesmo', 'assim',
    'também', 'como', 'ainda', 'cada', 'ser', 'foi', 'isso', 'essa',
    'está', 'estao', 'estavam', 'já', 'a', 'e', 'i', 'o', 'u',
    'da', 'de', 'di', 'do', 'du', 'é', 'tem', 'pois', 'em', 'seu', 'sua', 'seus', 'suas',
    'empresa', 'setor', 'trabalho', 'colaborador', 'colaboradores',
    'gestor', 'gestora', 'área', 'pessoas', 'atividade', 'atividades',
    'bom', 'boa', 'sim', 'não', 'pode', 'poderia', 'há', 'tudo', 'nada',
    'todo', 'toda', 'todos', 'todas', 'mesma', 'mesmo', 'além', 'quando',
    'onde', 'qual', 'quais', 'porque', 'pra', 'fazer', 'feito', 'faz', 'fez'
})

@st.cache_data(show_spinner=False)
def ler_excel_seguro(uploaded_file):
    try:
        return pd.read_excel(uploaded_file, sheet_name=0, engine="openpyxl")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {uploaded_file.name}:")
        st.exception(e)
        return None

def normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.lower().strip()

def detectar_coluna_comentarios(df):
    keywords = ["coment"]
    comentarios_colunas = []
    for col in df.columns:
        nome_normalizado = normalizar(col)
        if any(keyword in nome_normalizado for keyword in keywords):
            comentarios_colunas.append(col)
    return comentarios_colunas

def analisar_sentimento(texto):
    blob = TextBlob(texto)
    polaridade = blob.sentiment.polarity
    if polaridade > 0.2:
        return ("Positivo", polaridade)
    elif polaridade < -0.2:
        return ("Negativo", polaridade)
    else:
        return ("Neutro", polaridade)

def extrair_palavras_chave(textos: List[str], n_words=10) -> Dict[str, List[Tuple[str, int]]]:
    palavras_chave = {}
    for texto in textos:
        palavras = re.findall(r'\b\w{4,}\b', texto.lower())
        palavras_filtradas = [p for p in palavras if p not in STOPWORDS_PT]
        contador = Counter(palavras_filtradas)
        palavras_chave[texto] = contador.most_common(n_words)
    return palavras_chave

def clusterizar_comentarios(lista_textos):
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = modelo.encode(lista_textos, show_progress_bar=True)
    clusterizador = DBSCAN(eps=0.35, min_samples=3, metric='cosine', n_jobs=-1)
    labels = clusterizador.fit_predict(embeddings)
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
    reduzido = reducer.fit_transform(embeddings)
    return labels, reduzido, embeddings

def gerar_wordcloud(textos):
    texto_completo = ' '.join(textos)
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=STOPWORDS_PT,
        max_words=50,
        collocations=False
    ).generate(texto_completo)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

def analisar_topicos_por_cluster(df):
    topicos = {}
    for cluster in df['Cluster'].unique():
        textos_cluster = df[df['Cluster'] == cluster]['comentario']
        palavras = ' '.join(textos_cluster).split()
        palavras_filtradas = [p for p in palavras if len(p) > 3 and p not in STOPWORDS_PT]
        contador = Counter(palavras_filtradas)
        topicos[cluster] = contador.most_common(5)
    return topicos

def show():
    st.title("📊 Análise de Comentários com IA Semântica")
    st.markdown("""
    <style>
    .big-font { font-size:18px !important; }
    .cluster-box { border-left: 5px solid #4CAF50; padding: 10px; margin: 10px 0; }
    .negative-cluster { border-left-color: #f44336 !important; }
    .positive-cluster { border-left-color: #4CAF50 !important; }
    </style>
    """, unsafe_allow_html=True)

    with st.expander("📤 Carregar Dados", expanded=True):
        if st.session_state.get("df_unificado") is None:
            uploaded_files = st.file_uploader("Selecione os arquivos Excel", type=["xlsx"], accept_multiple_files=True)
            if uploaded_files:
                dfs = []
                for uploaded_file in uploaded_files:
                    df_temp = ler_excel_seguro(uploaded_file)
                    if df_temp is None:
                        continue
                    match = re.search(r'PESQUISA DE CLIMA (.*?)\s*-\s*2025', uploaded_file.name)
                    base = match.group(1).strip() if match else "Desconhecido"
                    df_temp["BASE"] = base
                    dfs.append(df_temp)
                if dfs:
                    df = pd.concat(dfs, ignore_index=True).drop_duplicates()
                    st.session_state.df_unificado = df
                else:
                    st.warning("Nenhum dado carregado corretamente.")
                    return
            else:
                st.info("Por favor, carregue arquivos na seção Upload ou aqui mesmo.")
                return
        else:
            df = st.session_state.df_unificado.copy()

    col1, col2 = st.columns(2)
    with col1:
        base_sel = st.selectbox("Selecione a base:", df["BASE"].unique(), key='base_select')
    with col2:
        col_comentarios = detectar_coluna_comentarios(df)
        coluna_sel = st.selectbox("Coluna de Comentário:", col_comentarios if col_comentarios else [None], key='coluna_select')

    if not coluna_sel:
        st.warning("Nenhuma coluna de comentários foi detectada.")
        return

    comentarios = df[df["BASE"] == base_sel][coluna_sel].dropna().astype(str)
    if comentarios.empty:
        st.info("Nenhum comentário preenchido nesta base.")
        return

    df_sent = pd.DataFrame({"comentario": comentarios})
    df_sent[["Sentimento", "Pontuacao"]] = df_sent["comentario"].apply(lambda x: pd.Series(analisar_sentimento(x)))

    tab1, tab2, tab3 = st.tabs(["📈 Visão Geral", "🧩 Análise por Grupo", "📤 Exportar Relatório"])

    with tab1:
        st.subheader("📊 Visão Geral dos Comentários")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Comentários", len(df_sent))
        col2.metric("Comentários Positivos", f"{len(df_sent[df_sent['Sentimento'] == 'Positivo'])} ({len(df_sent[df_sent['Sentimento'] == 'Positivo'])/len(df_sent):.1%})")
        col3.metric("Comentários Negativos", f"{len(df_sent[df_sent['Sentimento'] == 'Negativo'])} ({len(df_sent[df_sent['Sentimento'] == 'Negativo'])/len(df_sent):.1%})")
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.plotly_chart(px.pie(df_sent, names='Sentimento', title='Distribuição de Sentimentos',
                                   color='Sentimento',
                                   color_discrete_map={'Positivo': '#4CAF50', 'Negativo': '#f44336', 'Neutro': '#FFC107'}))
        with fig_col2:
            st.pyplot(gerar_wordcloud(df_sent['comentario']))

    with tab2:
        st.subheader("🧠 Análise Semântica Avançada")
        with st.spinner("Processando agrupamentos semânticos e tópicos..."):
            labels, coords, embeddings = clusterizar_comentarios(df_sent["comentario"].tolist())
            df_sent["Cluster"] = labels
            df_sent["x"] = coords[:, 0]
            df_sent["y"] = coords[:, 1]
            topicos_por_cluster = analisar_topicos_por_cluster(df_sent)
        st.plotly_chart(px.scatter(df_sent, x="x", y="y", color=df_sent["Cluster"].astype(str),
                                   hover_data=["comentario", "Sentimento"],
                                   title="<b>Mapa Semântico dos Comentários</b><br>Pontos próximos = Temas similares",
                                   width=1000, height=600), use_container_width=True)
        for cluster_id in sorted(df_sent["Cluster"].unique()):
            cluster_data = df_sent[df_sent["Cluster"] == cluster_id]
            nome_cluster = "Comentários Únicos" if cluster_id == -1 else f"Grupo {cluster_id}"
            sentimento_pred = cluster_data["Sentimento"].mode()[0]
            cluster_class = ""
            if sentimento_pred == "Positivo":
                cluster_class = "positive-cluster"
            elif sentimento_pred == "Negativo":
                cluster_class = "negative-cluster"
            with st.container():
                st.markdown(f"""
                <div class="cluster-box {cluster_class}">
                    <h3>{nome_cluster} • {len(cluster_data)} comentários • {sentimento_pred}</h3>
                    <p class="big-font"><b>Tópicos principais:</b> {', '.join([t[0] for t in topicos_por_cluster.get(cluster_id, [])])}</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander(f"📌 Ver exemplos do {nome_cluster.lower()}"):
                    for i, linha in enumerate(cluster_data["comentario"].head(5)):
                        sentimento = cluster_data.iloc[i]["Sentimento"]
                        emoji = "😊" if sentimento == "Positivo" else "😞" if sentimento == "Negativo" else "😐"
                        st.markdown(f"{emoji} {linha}")
                    st.markdown(f"**Distribuição de sentimentos no grupo:**")
                    sent_counts = cluster_data['Sentimento'].value_counts()
                    st.bar_chart(sent_counts)

    with tab3:
        st.subheader("📤 Exportar Relatório Completo")
        report = f"""
        # Relatório de Análise de Comentários - {base_sel}
        ## Dados Gerais
        - Total de comentários analisados: {len(df_sent)}
        - Período de referência: 2025
        - Tema analisado: {coluna_sel}
        
        ## Distribuição de Sentimentos
        - Positivos: {len(df_sent[df_sent['Sentimento'] == 'Positivo'])} ({len(df_sent[df_sent['Sentimento'] == 'Positivo'])/len(df_sent):.1%})
        - Neutros: {len(df_sent[df_sent['Sentimento'] == 'Neutro'])} ({len(df_sent[df_sent['Sentimento'] == 'Neutro'])/len(df_sent):.1%})
        - Negativos: {len(df_sent[df_sent['Sentimento'] == 'Negativo'])} ({len(df_sent[df_sent['Sentimento'] == 'Negativo'])/len(df_sent):.1%})
        
        ## Principais Insights
        """
        for cluster_id in sorted(df_sent["Cluster"].unique()):
            cluster_data = df_sent[df_sent["Cluster"] == cluster_id]
            nome_cluster = "Comentários Únicos" if cluster_id == -1 else f"Grupo {cluster_id}"
            report += f"""
            ### {nome_cluster} ({len(cluster_data)} comentários)
            **Tópicos principais:** {', '.join([t[0] for t in topicos_por_cluster.get(cluster_id, [])])}
            **Sentimento predominante:** {cluster_data["Sentimento"].mode()[0]}
            
            **Exemplos representativos:**
            """
            for linha in cluster_data["comentario"].head(3):
                report += f"- {linha}\n"
            report += "\n"
        st.download_button(
            label="📥 Baixar Relatório Completo",
            data=report,
            file_name=f"relatorio_comentarios_{base_sel}.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    show()
