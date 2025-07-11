import pytest
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_webhook_invalid_data(client):
    # Falta el campo From
    response = client.post('/webhook', data={'Body': 'Hola'})
    assert response.status_code == 400
    assert b'Datos inv' in response.data

def test_webhook_health(client):
    response = client.get('/webhook/health')
    assert response.status_code == 200
    assert b'status' in response.data 