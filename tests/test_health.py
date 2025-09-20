"""
tests/test_health.py
Teste básico para endpoint de health.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
