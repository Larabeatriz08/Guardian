import pytest

from backend import rules


@pytest.fixture(autouse=True)
def blocklist_falsa(monkeypatch):
    monkeypatch.setattr(rules, "BLOCKLIST", {"bloqueado.com"})


def test_dominio_exato_e_bloqueado():
    assert rules.check_domain("https://bloqueado.com") == ("blocklist", 1.0)


def test_subdominio_e_bloqueado():
    assert rules.check_domain("https://www.bloqueado.com/pagina")[0] == "blocklist"


def test_subdominio_profundo_e_bloqueado():
    assert rules.check_domain("https://a.b.bloqueado.com")[0] == "blocklist"


def test_maiusculas_sao_ignoradas():
    assert rules.check_domain("HTTPS://WWW.BLOQUEADO.COM")[0] == "blocklist"


def test_dominio_permitido():
    assert rules.check_domain("https://google.com") == (None, 0.0)


def test_dominio_parecido_nao_e_bloqueado():
    # "naobloqueado.com" contem o texto, mas e outro dominio
    assert rules.check_domain("https://naobloqueado.com")[0] is None


def test_truque_de_dominio_dentro_de_outro():
    # o dominio real aqui e evil.org, nao bloqueado.com
    assert rules.check_domain("https://bloqueado.com.evil.org")[0] is None


def test_url_vazia_ou_invalida_nao_quebra():
    assert rules.check_domain("")[0] is None
    assert rules.check_domain("isso-nao-e-url")[0] is None