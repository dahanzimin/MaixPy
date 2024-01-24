from Maix import *
from machine import I2C
import ads1x15

#k210pin 0   1  2   3  4  5  6  7   8   9   10  11  12  13  14  15 16 17 18  19  20  21  22  23  24  25  26  27
pin_D = [11, 9, 10, 0, 1, 2, 3, 12, 13, 14, 15, 16, 17, 21, 22, 6, 7, 8, 18, 19, 20, 23, 24, 25, 32, 33, 34, 35]

ob_i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)
ob_adc = ads1x15.ADS1015(ob_i2c, address=0x48, gain=0)

def register(pin = None,function = None):
	FPIOA().set_function(pin_D[pin],function)

def pin(pin = None,function = None, *k):
	FPIOA().set_function(pin_D[pin],24+pin)
	pins=GPIO(pin, function, *k)
	return pins

def adc_init(gains=0):
	ob_adc.gain=gains

def adc_read(channel):
	try:
		return ob_adc.read(channel1=channel)
	except Exception as e:
		raise ValueError("[AIBIT] No ADC for this channel")	
	
def adc_vread(channel):
	try:
		return ob_adc.raw_to_v(ob_adc.read(channel1=channel))	
	except Exception as e:
		raise ValueError("[AIBIT] No ADC for this channel")	

def config(config):
	import json
	cfg = json.dumps(config)
	try:
		with open('config.json', "w") as f:
			f.write(cfg)
		print("Configuration modified successfully")
		import os
		os.remove("main.py")
	finally:	
		import machine
		machine.reset()
