import os
import time
import requests

def run_training_job(experiment_id, epochs, learning_rate):
    for epoch in range(1, epochs + 1):
        time.sleep(1)
        loss = 1.0 / (epoch * learning_rate * 100)
        accuracy = 1 - loss
        requests.post(f'http://{os.environ.get("FLASK_HOST", "localhost")}:5050/metric', json={
            'experiment_id': experiment_id,
            'epoch': epoch,
            'loss': round(loss, 4),
            'accuracy': round(accuracy, 4)
        })
        print(f'Epoch {epoch}/{epochs} — loss: {loss:.4f}, accuracy: {accuracy:.4f}')
