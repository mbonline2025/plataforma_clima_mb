import string

def limpar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto
