import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to Flask server')

@sio.on('metric_update')
def on_metric(data):
    print('Received metric:', data)

sio.connect('http://127.0.0.1:5000')
time.sleep(10)
sio.disconnect()
