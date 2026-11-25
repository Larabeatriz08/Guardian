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
    category, conf = rules.check_domain(e.url)
    action = "block" if category else "allow"
    db.log(e.url, e.title, category or "none", action, conf)
    return {"action": action, "category": category}