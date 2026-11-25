from pathlib import Path
from urllib.parse import urlparse

BLOCKLIST_PATH = Path(__file__).resolve().parent / "blocklist.txt"


def load_blocklist(path=BLOCKLIST_PATH):
    with open(path, encoding="utf-8") as f:
        return {
            line.strip().lower()
            for line in f
            if line.strip() and not line.startswith("#")
        }


BLOCKLIST = load_blocklist()


def check_domain(url: str):
    """Testa o dominio e seus subdominios: a.b.site.com -> b.site.com -> site.com"""
    host = (urlparse(url).hostname or "").lower()
    parts = host.split(".")
    for i in range(len(parts) - 1):
        if ".".join(parts[i:]) in BLOCKLIST:
            return "blocklist", 1.0
    return None, 0.0