# ML research

I built an ML platform with real-time training visualization, distributed job queueing and edge inference on a Raspberry Pi to mirror and learn from the infrastructure behind Tesla Autopilot research.


## Demo
[![ML research platform demo](https://cdn.loom.com/sessions/thumbnails/bbd4d9dfebd84249b64aa3b144fe6d29-ad7e588d755b3cbc-full-play.gif)](https://www.loom.com/share/bbd4d9dfebd84249b64aa3b144fe6d29)

## What it does
- Trains a neural net on my computer using PyTorch with hyperparameters tracked through a REST API and saved in a PostgreSQL db
- Distributes training jobs using Redis Queue with worker processes
- Streams live training metrics to a Nextjs dashboard using websockets. Loss and accuracy metrics for each epoch are sent
- Deploys a trained model to a Raspberry Pi 5 for edge inference on a real camera input
- Reports telemetry data, IMU sensor data and inference latency back to the dashboard in realtime
  

## Stack
For the frontend (dashboard UI), NextJS and Typescript was used. Typescript’s type checking was essential to ensure there was no type mismatch across the ui. Recharts is the charting library. Redux toolkit and socketio-client were also used.

In the backend, I had Flask running the core with multiple API endpoints defined. Flask-SocketIO for the websocket. Python to write all the scripts and PostgreSQL to store data. I implemented foreign key integrity and JSONB hyperparameters to store abstract but queryable data. Redis and RQ were used too.

For the ml itself, PyTorch is the go-to. The platform currently has uses the CNN architecture to improve model accuracy. Torchvision was used. For the infra, docker is used to house the backend with each service running its own container. Hardware includes a Raspberry Pi 5, Pi Camera 3 and MPU-6050 sensor as the major components.


## Setup
### Backend:
```
cd backend
docker compose up --build
```
### Frontend:
```
cd frontend
npm install
npm run dev
```
### Pi inference:
```
# SSH into the pi
cd inference
python3 infer.py
python3 imu.py
```

Submitting a training job involves running a curl command with the hyperparameters you want, or using a script to conduct a hyperparameter sweep.


## Example curl commands
### Create the experiments
```
curl -X POST http://127.0.0.1:5050/experiment -H "Content-Type: application/json" -d '{"experiment_id": "depth_001", "name": "1 epoch", "hyperparameters": {"learning_rate": 0.001, "batch_size": 64, "epochs": 1}}'

curl -X POST http://127.0.0.1:5050/experiment -H "Content-Type: application/json" -d '{"experiment_id": "depth_002", "name": "3 epochs", "hyperparameters": {"learning_rate": 0.001, "batch_size": 64, "epochs": 3}}'

curl -X POST http://127.0.0.1:5050/experiment -H "Content-Type: application/json" -d '{"experiment_id": "depth_003", "name": "5 epochs", "hyperparameters": {"learning_rate": 0.001, "batch_size": 64, "epochs": 5}}'

curl -X POST http://127.0.0.1:5050/experiment -H "Content-Type: application/json" -d '{"experiment_id": "depth_004", "name": "8 epochs", "hyperparameters": {"learning_rate": 0.001, "batch_size": 64, "epochs": 8}}'

curl -X POST http://127.0.0.1:5050/experiment -H "Content-Type: application/json" -d '{"experiment_id": "depth_005", "name": "10 epochs", "hyperparameters": {"learning_rate": 0.001, "batch_size": 64, "epochs": 10}}'
```
### Create the jobs
```
curl -X POST http://127.0.0.1:5050/job -H "Content-Type: application/json" -d '{"experiment_id": "depth_001", "epochs": 1, "learning_rate": 0.001, "batch_size": 64}'

curl -X POST http://127.0.0.1:5050/job -H "Content-Type: application/json" -d '{"experiment_id": "depth_002", "epochs": 3, "learning_rate": 0.001, "batch_size": 64}'

curl -X POST http://127.0.0.1:5050/job -H "Content-Type: application/json" -d '{"experiment_id": "depth_003", "epochs": 5, "learning_rate": 0.001, "batch_size": 64}'

curl -X POST http://127.0.0.1:5050/job -H "Content-Type: application/json" -d '{"experiment_id": "depth_004", "epochs": 8, "learning_rate": 0.001, "batch_size": 64}'

curl -X POST http://127.0.0.1:5050/job -H "Content-Type: application/json" -d '{"experiment_id": "depth_005", "epochs": 10, "learning_rate": 0.001, "batch_size": 64}'
```

This trains multiple models concurrently or sequentially depending on the amount of workers you have running in the docker container. To run more than one worker, add `--scale worker={how many you want here}` to the Docker compose up command when starting the backend. Open `http://localhost:3000/dashboard` to watch training live.
