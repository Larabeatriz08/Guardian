import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

from backend import classifier, db, rules
from backend.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    banco_teste = tmp_path / "teste.db"
    monkeypatch.setattr(db, "DB", banco_teste)
    monkeypatch.setattr(rules, "BLOCKLIST", {"bloqueado.com": "adulto"})
    arq = tmp_path / "k.json"
    arq.write_text(json.dumps({"drogas": ["maconha"]}), encoding="utf-8")
    monkeypatch.setattr(rules, "KEYWORDS", rules.load_keywords(arq))
    db.init()
    return TestClient(app), banco_teste


def test_health(client):
    c, _ = client
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_site_bloqueado(client):
    c, _ = client
    r = c.post("/event", json={"url": "https://www.bloqueado.com", "title": "x"})
    assert r.json() == {"action": "block", "category": "adulto"}


def test_site_permitido(client):
    c, _ = client
    r = c.post("/event", json={"url": "https://google.com", "title": "x"})
    assert r.json() == {"action": "allow", "category": None}


def test_palavra_chave_gera_alerta_sem_bloquear(client):
    c, _ = client
    r = c.post("/event", json={"url": "https://x.com", "title": "maconha"})
    assert r.json() == {"action": "alert", "category": "drogas"}


def test_evento_bloqueado_e_gravado_no_banco(client):
    c, banco = client
    c.post("/event", json={"url": "https://bloqueado.com", "title": "teste"})
    with sqlite3.connect(banco) as conn:
        linhas = conn.execute("SELECT url, category, action FROM events").fetchall()
    assert linhas == [("https://bloqueado.com", "adulto", "block")]


def test_payload_invalido_retorna_422(client):
    c, _ = client
    r = c.post("/event", json={"title": "sem url"})
    assert r.status_code == 422


# ---------- classificador com IA ----------
def test_ia_so_bloqueia_se_estiver_liberado(client, monkeypatch):
    monkeypatch.setattr(classifier, "PODE_BLOQUEAR", True)
    monkeypatch.setattr(classifier, "classify", lambda *a: ("adulto", 0.95))
    c, _ = client
    r = c.post("/event", json={"url": "https://novo.com", "title": "x", "text": "abc"})
    assert r.json() == {"action": "block", "category": "adulto"}


def test_ia_por_padrao_so_alerta(client, monkeypatch):
    monkeypatch.setattr(classifier, "PODE_BLOQUEAR", False)
    monkeypatch.setattr(classifier, "classify", lambda *a: ("adulto", 0.95))
    c, _ = client
    r = c.post("/event", json={"url": "https://novo.com", "title": "x", "text": "abc"})
    assert r.json() == {"action": "alert", "category": "adulto"}


def test_ia_com_pouca_confianca_so_alerta(client, monkeypatch):
    monkeypatch.setattr(classifier, "PODE_BLOQUEAR", True)
    monkeypatch.setattr(classifier, "classify", lambda *a: ("adulto", 0.5))
    c, _ = client
    r = c.post("/event", json={"url": "https://novo.com", "title": "x", "text": "abc"})
    assert r.json() == {"action": "alert", "category": "adulto"}


def test_sem_texto_a_ia_nao_e_consultada(client, monkeypatch):
    def nao_deve_chamar(*a):
        raise AssertionError("IA chamada sem texto")

    monkeypatch.setattr(classifier, "classify", nao_deve_chamar)
    c, _ = client
    r = c.post("/event", json={"url": "https://novo.com", "title": "x"})
    assert r.json() == {"action": "allow", "category": None}


def test_visita_liberada_sem_texto_nao_e_gravada(client):
    c, banco = client
    c.post("/event", json={"url": "https://novo.com", "title": "x"})
    with sqlite3.connect(banco) as conn:
        assert conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0