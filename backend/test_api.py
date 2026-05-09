import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_experiment(client):
    response = client.post('/experiment',
        data=json.dumps({
            'experiment_id': 'test_001',
            'name': 'Test experiment',
            'hyperparameters': {'learning_rate': 0.001}
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'

def test_create_metric(client):
    response = client.post('/metric',
        data=json.dumps({
            'experiment_id': 'test_001',
            'epoch': 1,
            'loss': 0.85,
            'accuracy': 0.62
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
