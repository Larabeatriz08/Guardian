from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

from backend import classifier, db, notify, rules

app = FastAPI(title="Guardian")
db.init()


class TabEvent(BaseModel):
    url: str
    title: str = ""
    text: str = ""       # trecho do texto da pagina (vazio na 1a fase)
    active: bool = True  # False = aba em segundo plano


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/event")
def event(e: TabEvent, background: BackgroundTasks):
    categoria, conf = rules.check(e.url, e.title)

    da_ia = False
    if categoria is None and e.text:
        categoria, conf = classifier.classify(e.url, e.title, e.text)
        da_ia = categoria is not None

    action = rules.decide(categoria)
    # a IA so bloqueia se estiver liberada E com confianca alta; senao, so avisa
    if da_ia and action == "block":
        if not classifier.PODE_BLOQUEAR or conf < classifier.MIN_CONF:
            action = "alert"

    # visita liberada e sem texto: nao polui o historico (a fase com texto registra)
    if action == "allow" and not e.text:
        return {"action": action, "category": categoria}

    db.log(e.url, e.title, categoria or "none", action, conf)
    if action != "allow":
        background.add_task(notify.enviar, categoria, action, e.url)
    return {"action": action, "category": categoria}