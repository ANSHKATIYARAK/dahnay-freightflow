import pytest
from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)

def test_fintech___taxops_health():
    res = client.get('/api/v1/records/health')
    assert res.status_code == 200
    assert res.json()['domain'] == 'FinTech / TaxOps'

def test_create_record_boundary():
    payload = {'metric_value': 149.50, 'status': 'active'}
    res = client.post('/api/v1/records', json=payload)
    assert res.status_code == 201
