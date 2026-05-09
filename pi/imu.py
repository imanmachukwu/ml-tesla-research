import smbus2
import requests
import time

bus = smbus2.SMBus(1)
MPU_ADDR = 0x68
FLASK_URL = 'http://192.168.1.158:5050/imu'

bus.write_byte_data(MPU_ADDR, 0x6B, 0)

def read_word(reg):
	high = bus.read_byte_data(MPU_ADDR, reg)
	low = bus.read_byte_data(MPU_ADDR, reg + 1)
	value = (high << 8) | low
	if value > 32767:
		value -= 65536
	return value

while True:
	accel_x = read_word(0x3B) / 16384.0
	accel_y = read_word(0x3D) / 16384.0
	accel_z = read_word(0x3F) / 16384.0
	gyro_x = read_word(0x43) / 131.0
	gyro_y = read_word(0x45) / 131.0
	gyro_z = read_word(0x47) / 131.0

	print(f'Sending: x={accel_x:.3f}, y={accel_y:.3f}, z={accel_z:.3f}')

	requests.post(FLASK_URL, json={
		'accel_x': round(accel_x, 3),
		'accel_y': round(accel_y, 3),
		'accel_z': round(accel_z, 3),
		'gyro_x': round(gyro_x, 2),
		'gyro_y': round(gyro_y, 2),
		'gyro_z': round(gyro_z, 2)
	})

	time.sleep(1)
