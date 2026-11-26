import json
import sqlite3
import urllib.request
from xmlrpc import client

casos = [
    ("https://site-novo-exemplo.com/receitas", "Receitas",
     "Bolo de cenoura com cobertura de chocolate. Misture os ingredientes e leve ao forno por 40 minutos. " * 3),
    ("https://site-novo-exemplo.com/video", "Video",
     "Pagina com cenas de violencia extrema contra pessoas reais, sangue, tortura e mutilacao mostrados em detalhes, conteudo gore. " * 3),
]

for url, titulo, texto in casos:
    dados = json.dumps({"url": url, "title": titulo, "text": texto}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8765/event",
        data=dados,
        headers={"Content-Type": "application/json"},
    )
    print(titulo, "->", urllib.request.urlopen(req, timeout=120).read().decode())

    def test_visita_repetida_nao_duplica_registro(client):
    c, banco = client
    for _ in range(3):
        c.post("/event", json={"url": "https://bloqueado.com", "title": "x"})
    with sqlite3.connect(banco) as conn:
        assert conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1