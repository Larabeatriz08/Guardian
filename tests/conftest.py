import pytest

from backend import notify


@pytest.fixture(autouse=True)
def sem_notificacao_real(monkeypatch):
    monkeypatch.setattr(notify, "NTFY_TOPIC", "")
    monkeypatch.setattr(notify, "_ultimo", {})