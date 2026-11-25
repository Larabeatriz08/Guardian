import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "guardiao.db"


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