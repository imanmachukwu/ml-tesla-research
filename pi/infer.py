import torch
import torch.nn as nn
import requests
import time
from PIL import ImageOps
from picamera2 import Picamera2
from PIL import Image
import io

MODEL_PATH = '/home/raspberrypi/cnn_002.pt'
FLASK_URL = 'http://192.168.1.158:5050/inference'

model = nn.Sequential(
    nn.Conv2d(1, 32, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(32, 64, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(64 * 7 * 7, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

picam = Picamera2()
picam.configure(picam.create_still_configuration(main={"size": (640, 480)}))
picam.start()
time.sleep(2)

while True:
	buffer = io.BytesIO()
	picam.capture_file(buffer, format='jpeg')
	buffer.seek(0)

	image = Image.open(buffer).convert('L').resize((28, 28))
	image = ImageOps.invert(image)
	tensor = torch.tensor(list(image.getdata()), dtype=torch.float32).view(1, 1, 28, 28)
	tensor = (tensor / 255.0 - 0.1307) / 0.3081

	start = time.time()
	with torch.no_grad():
		output = model(tensor)
		prediction = torch.argmax(output, dim=1).item()
	latency_ms = (time.time() - start) * 1000

	cpu_temp = float(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1000

	requests.post(FLASK_URL, json={
		'prediction': prediction,
		'latency_ms': round(latency_ms, 2),
		'cpu_temp': round(cpu_temp, 1)
	})

	print(f'Predicted: {prediction} | Latency: {latency_ms: .2f}ms | Temp: {cpu_temp}°C')
	time.sleep(2)
