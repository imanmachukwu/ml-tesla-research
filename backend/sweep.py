import requests
import itertools
import time

learning_rates = [0.0001, 0.001, 0.01]
batch_sizes = [32, 64, 128]

run_id = int(time.time())

combinations = list(itertools.product(learning_rates, batch_sizes))

print(f'Submitting {len(combinations)} jobs')

for i, (lr, bs) in enumerate(combinations):
    experiment_id = f'sweep_{run_id}_{i:03d}'

    requests.post('http://127.0.0.1:5050/experiment', json={
        'experiment_id': experiment_id,
        'name': f'Sweep lr={lr} bs={bs}',
        'hyperparameters': {
            'learning_rate': lr,
            'batch_size': bs,
            'epochs': 5
        }
    })

    requests.post('http://127.0.0.1:5050/job', json={
        'experiment_id': experiment_id,
        'epochs': 5,
        'learning_rate': lr,
        'batch_size': bs
    })

    print(f'Submitted {experiment_id}: lr={lr}, bs={bs}')

print('All jobs queued.')
