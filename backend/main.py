from fastapi import FastAPI
from pydantic import BaseModel

from backend import db, rules

app = FastAPI(title="Guardian")
db.init()


class TabEvent(BaseModel):
    url: str
    title: str = ""
    active: bool = True  # False = aba em segundo plano


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/event")
def event(e: TabEvent):
    categoria, conf = rules.check(e.url, e.title)
    action = rules.decide(categoria)
    db.log(e.url, e.title, categoria or "none", action, conf)
    return {"action": action, "category": categoria}