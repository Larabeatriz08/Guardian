import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "guardian.db"


def init():
    with sqlite3.connect(DB) as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS events(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, url TEXT, title TEXT,
                category TEXT, action TEXT, confidence REAL)"""
        )


def log(url, title, category, action, confidence):
    with sqlite3.connect(DB) as c:
        c.execute(
            "INSERT INTO events(ts,url,title,category,action,confidence) VALUES(?,?,?,?,?,?)",
            (datetime.now().isoformat(), url, title, category, action, confidence),
        )


def recente(url, action, segundos=300):
    """True se a mesma URL com a mesma acao ja foi gravada nos ultimos segundos."""
    with sqlite3.connect(DB) as c:
        linha = c.execute(
            "SELECT ts FROM events WHERE url=? AND action=? ORDER BY id DESC LIMIT 1",
            (url, action),
        ).fetchone()
    if not linha:
        return False
    return datetime.now() - datetime.fromisoformat(linha[0]) < timedelta(seconds=segundos)