from Maix import *
                                                         
#k210pin 0   1  2   3   4   5  6  7  8  9  10  11  12  13  14  15  16  17  18  19  20  21
pin_D = [0, 9, 10, 33, 34,  1, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 25]

def register(pin = None,function = None):
	FPIOA().set_function(pin_D[pin],function)

def pin(pin = None,function = None, *k):
	FPIOA().set_function(pin_D[pin],24+pin)
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