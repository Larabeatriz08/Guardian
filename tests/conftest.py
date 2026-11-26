import pytest

from backend import classifier, notify


@pytest.fixture(autouse=True)
def sem_efeitos_reais(monkeypatch):
    monkeypatch.setattr(notify, "NTFY_TOPIC", "")
    monkeypatch.setattr(notify, "_ultimo", {})
    monkeypatch.setenv("GUARDIAN_AI", "off")
    monkeypatch.setattr(classifier, "_cache", {})