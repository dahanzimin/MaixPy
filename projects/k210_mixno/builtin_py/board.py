from Maix import *
                                                         
#k210pin 0   1   2   3  4  5  6  7   8   9  10   11  12  13  14  15  16  17  18  19  20  21 22 23 24 25  26  27  28  29  30
pin_D = [11, 10, 12, 0, 1, 2, 3, 13, 14, 15, 21, 22, 23, 24, 25, 30, 16, 17, 18, 19, 20, 9, 8, 7, 6, 33, 34, 35, 26, 27, 28]

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