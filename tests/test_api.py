import sqlite3

import pytest
from fastapi.testclient import TestClient

from backend import db, rules
from backend.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    banco_teste = tmp_path / "teste.db"
    monkeypatch.setattr(db, "DB", banco_teste)
    monkeypatch.setattr(rules, "BLOCKLIST", {"bloqueado.com"})
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
    assert r.status_code == 200
    assert r.json() == {"action": "block", "category": "blocklist"}


def test_site_permitido(client):
    c, _ = client
    r = c.post("/event", json={"url": "https://google.com", "title": "x"})
    assert r.json() == {"action": "allow", "category": None}


def test_evento_e_gravado_no_banco(client):
    c, banco = client
    c.post("/event", json={"url": "https://bloqueado.com", "title": "teste"})
    with sqlite3.connect(banco) as conn:
        linhas = conn.execute("SELECT url, category, action FROM events").fetchall()
    assert linhas == [("https://bloqueado.com", "blocklist", "block")]


def test_payload_invalido_retorna_422(client):
    c, _ = client
    r = c.post("/event", json={"title": "sem url"})
    assert r.status_code == 422