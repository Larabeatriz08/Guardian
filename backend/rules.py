import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
LISTS_DIR = BASE / "lists"
KEYWORDS_PATH = BASE / "keywords.json"

# O que fazer em cada categoria: "block", "alert" ou "log"
POLICY = {
    "adulto": "block",
    "violencia": "block",
    "drogas": "alert",
    "palavroes": "log",
}
DEFAULT_ACTION = "alert"  # categoria que nao esta na politica


def normalizar(texto):
    """minusculas, sem acento, quebrado em palavras"""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", texto)


def load_blocklists(folder=LISTS_DIR):
    """Le todos os .txt da pasta. O nome do arquivo (ate o 1o ponto) e a categoria."""
    dominios = {}
    for arq in sorted(folder.glob("*.txt")):
        categoria = arq.name.split(".")[0]
        with open(arq, encoding="utf-8") as f:
            for linha in f:
                d = linha.strip().lower()
                if d and not d.startswith("#"):
                    dominios[d] = categoria
    return dominios


def load_keywords(path=KEYWORDS_PATH):
    with open(path, encoding="utf-8") as f:
        bruto = json.load(f)
    saida = {}
    for categoria, termos in bruto.items():
        itens = []
        for t in termos:
            palavras = normalizar(t)
            if palavras:
                itens.append((" ".join(palavras), t.endswith("*")))
        saida[categoria] = itens
    return saida


BLOCKLIST = load_blocklists()
KEYWORDS = load_keywords()


def check_domain(url: str):
    """Testa o dominio e seus subdominios: a.b.site.com -> b.site.com -> site.com"""
    host = (urlparse(url).hostname or "").lower()
    parts = host.split(".")
    for i in range(len(parts) - 1):
        candidato = ".".join(parts[i:])
        if candidato in BLOCKLIST:
            return BLOCKLIST[candidato], 1.0
    return None, 0.0


def check_keywords(url: str, title: str = ""):
    p = urlparse(url)
    palavras = normalizar(f"{p.netloc} {p.path} {p.query} {title}")
    texto = " " + " ".join(palavras) + " "
    for categoria, itens in KEYWORDS.items():
        for frase, prefixo in itens:
            alvo = f" {frase}" if prefixo else f" {frase} "
            if alvo in texto:
                return categoria, 0.6
    return None, 0.0


def check(url: str, title: str = ""):
    categoria, conf = check_domain(url)
    if categoria:
        return categoria, conf
    return check_keywords(url, title)


def decide(categoria):
    if categoria is None:
        return "allow"
    return POLICY.get(categoria, DEFAULT_ACTION)