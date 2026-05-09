from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from rq import Queue
from train import run_training_job
import redis
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000"])

r = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379)

conn = psycopg2.connect(
	dbname='mlplatform',
	user='mluser',
	password='mlpassword',
	host=os.environ.get('DB_HOST', 'localhost')
)
conn.autocommit = True
cursor = conn.cursor()

@app.route('/metric', methods=['POST'])
def receive_metric():
	data = request.get_json()
	experiment_id = data['experiment_id']
	epoch = data['epoch']
	loss = data['loss']
	accuracy = data['accuracy']

	cursor.execute(
		"INSERT INTO metrics (experiment_id, epoch, loss, accuracy) VALUES (%s, %s, %s, %s)",
		(experiment_id, epoch, loss, accuracy)
	)

	socketio.emit('metric_update', data)

	return jsonify({'status': 'ok'})

@app.route('/experiment', methods=['POST'])
def create_experiment():
	data = request.get_json()
	experiment_id = data['experiment_id']
	name = data['name']
	hyperparameters = data['hyperparameters']

	cursor.execute(
		"INSERT INTO experiments (id, name, hyperparameters) VALUES (%s, %s, %s)",
		(experiment_id, name, psycopg2.extras.Json(hyperparameters))
	)

	return jsonify({'status': 'ok', 'experiment_id': experiment_id})

@app.route('/inference', methods=['POST'])
def receive_inference():
	data = request.get_json()
	socketio.emit('inference_update', data)
	return jsonify({'status': 'ok'})

q = Queue(connection=r)

@app.route('/job', methods=['POST'])
def submit_job():
	data = request.get_json()
	job = q.enqueue(run_training_job,
		data['experiment_id'],
		data['epochs'],
		data['learning_rate'],
		data.get('batch_size', 64),
		job_timeout=3600
	)
	return jsonify({'status': 'queued', 'job_id': job.id})

@app.route('/imu', methods=['POST'])
def receive_imu():
	data = request.get_json()
	socketio.emit('imu_update', data)
	return jsonify({'status': 'ok'})

if __name__ == '__main__': socketio.run(app, port=5050, host='0.0.0.0', allow_unsafe_werkzeug=True)
