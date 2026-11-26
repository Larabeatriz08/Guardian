import os
import time
import urllib.request
from urllib.parse import urlparse

NTFY_SERVER = os.getenv("GUARDIAN_NTFY_SERVER", "https://ntfy.sh")
NTFY_TOPIC = os.getenv("GUARDIAN_NTFY_TOPIC", "")
COOLDOWN = 300  # segundos: nao repete o mesmo aviso (mesmo site + categoria)

ROTULO = {"block": "BLOQUEADO", "alert": "ALERTA", "log": "Registro"}
_ultimo = {}


def enviar(categoria, action, url):
    """Manda o aviso ao celular. Nunca derruba o servidor se falhar."""
    if not NTFY_TOPIC:
        return
    dominio = urlparse(url).hostname or "desconhecido"
    chave = (dominio, categoria)
    agora = time.time()
    if agora - _ultimo.get(chave, 0) < COOLDOWN:
        return
    _ultimo[chave] = agora

    texto = f"{ROTULO.get(action, action)}: {categoria} em {dominio}"
    req = urllib.request.Request(
        f"{NTFY_SERVER}/{NTFY_TOPIC}",
        data=texto.encode("utf-8"),
        headers={
            "Title": "Guardian",
            "Priority": "high" if action == "block" else "default",
            "Tags": "warning",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception as err:
        print("Guardian: falha ao enviar aviso:", err)