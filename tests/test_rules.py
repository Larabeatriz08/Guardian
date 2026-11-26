import json

import pytest

from backend import rules


@pytest.fixture(autouse=True)
def listas_falsas(tmp_path, monkeypatch):
    monkeypatch.setattr(rules, "BLOCKLIST", {"bloqueado.com": "adulto"})
    arq = tmp_path / "k.json"
    arq.write_text(
        json.dumps({"adulto": ["porn*", "sexo explicito"], "drogas": ["maconha"]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(rules, "KEYWORDS", rules.load_keywords(arq))


# ---------- dominios ----------
def test_dominio_exato_e_bloqueado():
    assert rules.check_domain("https://bloqueado.com") == ("adulto", 1.0)


def test_subdominio_e_bloqueado():
    assert rules.check_domain("https://www.bloqueado.com/pagina")[0] == "adulto"


def test_subdominio_profundo_e_bloqueado():
    assert rules.check_domain("https://a.b.bloqueado.com")[0] == "adulto"


def test_maiusculas_sao_ignoradas():
    assert rules.check_domain("HTTPS://WWW.BLOQUEADO.COM")[0] == "adulto"


def test_dominio_permitido():
    assert rules.check_domain("https://google.com") == (None, 0.0)


def test_dominio_parecido_nao_e_bloqueado():
    assert rules.check_domain("https://naobloqueado.com")[0] is None


def test_truque_de_dominio_dentro_de_outro():
    assert rules.check_domain("https://bloqueado.com.evil.org")[0] is None


def test_url_vazia_ou_invalida_nao_quebra():
    assert rules.check_domain("")[0] is None
    assert rules.check_domain("isso-nao-e-url")[0] is None


# ---------- palavras-chave ----------
def test_palavra_no_titulo():
    assert rules.check_keywords("https://x.com", "Video de MACONHA") == ("drogas", 0.6)


def test_prefixo_com_asterisco():
    assert rules.check_keywords("https://pornsite.com")[0] == "adulto"


def test_acento_e_ignorado():
    assert rules.check_keywords("https://x.com", "Sexo explícito")[0] == "adulto"


def test_palavra_inteira_nao_casa_pedaco():
    assert rules.check_keywords("https://x.com", "maconhal")[0] is None


def test_texto_normal_passa():
    assert rules.check_keywords("https://wikipedia.org", "Historia do Brasil")[0] is None


# ---------- decisao ----------
def test_dominio_tem_prioridade():
    assert rules.check("https://bloqueado.com", "maconha")[0] == "adulto"


def test_politica():
    assert rules.decide(None) == "allow"
    assert rules.decide("adulto") == "block"
    assert rules.decide("drogas") == "alert"
    assert rules.decide("palavroes") == "log"
    assert rules.decide("categoria-inventada") == "alert"