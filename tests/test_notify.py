from backend import notify


def test_sem_topico_nao_envia(monkeypatch):
    chamadas = []
    monkeypatch.setattr(notify.urllib.request, "urlopen",
                        lambda *a, **k: chamadas.append(1))
    notify.enviar("adulto", "block", "https://x.com")
    assert chamadas == []


def test_envia_so_o_dominio(monkeypatch):
    chamadas = []
    monkeypatch.setattr(notify, "NTFY_TOPIC", "topico-teste")
    monkeypatch.setattr(notify.urllib.request, "urlopen",
                        lambda req, timeout=None: chamadas.append(req))
    notify.enviar("drogas", "alert", "https://site.com/pagina?q=segredo")
    assert len(chamadas) == 1
    corpo = chamadas[0].data.decode("utf-8")
    assert "site.com" in corpo
    assert "segredo" not in corpo


def test_cooldown_evita_repeticao(monkeypatch):
    chamadas = []
    monkeypatch.setattr(notify, "NTFY_TOPIC", "topico-teste")
    monkeypatch.setattr(notify.urllib.request, "urlopen",
                        lambda req, timeout=None: chamadas.append(req))
    notify.enviar("adulto", "block", "https://x.com/a")
    notify.enviar("adulto", "block", "https://x.com/b")
    assert len(chamadas) == 1


def test_falha_de_rede_nao_quebra(monkeypatch):
    monkeypatch.setattr(notify, "NTFY_TOPIC", "topico-teste")

    def falha(*a, **k):
        raise OSError("sem internet")

    monkeypatch.setattr(notify.urllib.request, "urlopen", falha)
    notify.enviar("adulto", "block", "https://x.com")  # nao pode levantar erro