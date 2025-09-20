"""
tests/test_auth.py
Testes básicos para endpoints de auth (integração leve).
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root():
    # apenas smoke test de rota /docs
    r = client.get("/docs")
    assert r.status_code in (200, 307)
