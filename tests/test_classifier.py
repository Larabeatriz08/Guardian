import pytest

from backend import classifier


@pytest.fixture
def com_ia(monkeypatch):
    monkeypatch.setenv("GUARDIAN_AI", "on")


# ---------- interpretar a resposta da IA ----------
def test_interpretar_json_valido():
    r = classifier.interpretar('{"categoria": "adulto", "confianca": 0.93}')
    assert r == ("adulto", 0.93)


def test_interpretar_json_com_texto_em_volta():
    r = classifier.interpretar('Claro! {"categoria": "drogas", "confianca": 0.8} ok')
    assert r == ("drogas", 0.8)


def test_interpretar_seguro_vira_none():
    assert classifier.interpretar('{"categoria": "seguro", "confianca": 0.99}') == (None, 0.0)


def test_interpretar_categoria_inventada():
    assert classifier.interpretar('{"categoria": "hacker", "confianca": 1}') == (None, 0.0)


def test_interpretar_lixo_nao_quebra():
    assert classifier.interpretar("blablabla") == (None, 0.0)
    assert classifier.interpretar("") == (None, 0.0)


def test_confianca_e_limitada_entre_0_e_1():
    assert classifier.interpretar('{"categoria": "adulto", "confianca": 7}')[1] == 1.0


# ---------- classify ----------
def test_ia_desligada_nao_chama_o_modelo(monkeypatch):
    chamadas = []
    monkeypatch.setattr(classifier, "_chamar", lambda *a: chamadas.append(1))
    assert classifier.classify("https://novo.com", "t", "texto") == (None, 0.0)
    assert chamadas == []


def test_classifica_com_modelo_falso(com_ia, monkeypatch):
    monkeypatch.setattr(
        classifier, "_chamar",
        lambda *a: '{"categoria": "violencia", "confianca": 0.9}',
    )
    r = classifier.classify("https://novo.com/a", "t", "texto qualquer")
    assert r == ("violencia", 0.9)


def test_cache_evita_segunda_chamada(com_ia, monkeypatch):
    chamadas = []

    def falso(*a):
        chamadas.append(1)
        return '{"categoria": "adulto", "confianca": 0.9}'

    monkeypatch.setattr(classifier, "_chamar", falso)
    classifier.classify("https://novo.com/a?q=1", "t", "texto")
    classifier.classify("https://novo.com/a?q=2", "t", "texto")
    assert len(chamadas) == 1


def test_falha_da_ia_nao_quebra(com_ia, monkeypatch):
    def falha(*a):
        raise OSError("ollama desligado")

    monkeypatch.setattr(classifier, "_chamar", falha)
    assert classifier.classify("https://novo.com", "t", "texto") == (None, 0.0)


def test_dominio_seguro_nao_chama_a_ia(com_ia, monkeypatch):
    chamadas = []
    monkeypatch.setattr(classifier, "_chamar", lambda *a: chamadas.append(1))
    classifier.classify("https://pt.wikipedia.org/x", "t", "texto")
    assert chamadas == []


def test_texto_e_cortado_e_so_o_dominio_vai(com_ia, monkeypatch):
    vistos = []

    def falso(dominio, titulo, trecho):
        vistos.append((dominio, trecho))
        return '{"categoria": "seguro", "confianca": 1}'

    monkeypatch.setattr(classifier, "_chamar", falso)
    classifier.classify("https://novo.com/p?busca=segredo", "t", "a" * 5000)
    dominio, trecho = vistos[0]
    assert dominio == "novo.com"
    assert len(trecho) == classifier.MAX_CHARS

def test_cache_de_videos_diferentes_do_youtube_nao_se_mistura(com_ia, monkeypatch):
    chamadas = []

    def falso(*a):
        chamadas.append(1)
        return '{"categoria": "seguro", "confianca": 1}'

    monkeypatch.setattr(classifier, "_chamar", falso)
    classifier.classify("https://www.youtube.com/watch?v=AAA", "t", "texto")
    classifier.classify("https://www.youtube.com/watch?v=BBB", "t", "texto")
    assert len(chamadas) == 2
