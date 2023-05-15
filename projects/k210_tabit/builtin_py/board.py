from Maix import *

#                                                           
#k210pin 0   1   2   3  4  5  6  7   8   9  10   11  12  13  14 
pin_D = [11, 10, 12, 0, 1, 2, 3, 13, 14, 15, 21, 22, 23, 24, 25]

def register(pin = None,function = None):
	FPIOA().set_function(pin,function)
	return True

def pin(pin = None,function = None, *k):
	FPIOA().set_function(pin,24+pin)
	pins=GPIO(pin, function, *k)
	return pins
	
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