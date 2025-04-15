from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import string

def limpar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto.strip()

def analisar_sentimento(texto):
    blob = TextBlob(texto)
    polaridade = blob.sentiment.polarity
    if polaridade > 0.1:
        return "Positivo"
    elif polaridade < -0.1:
        return "Negativo"
    else:
        return "Neutro"

def clusterizar_comentarios(lista_textos, n_clusters=3):
    vectorizer = TfidfVectorizer(stop_words='portuguese')
    X = vectorizer.fit_transform(lista_textos)
    modelo = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    modelo.fit(X)
    return modelo.labels_
