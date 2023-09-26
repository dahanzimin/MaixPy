from Maix import *
                                                         
#k210pin 0   1  2  3  4  5   6   7   8   9   10  11  12  13  14  15  16  17  18  19  20  21  22  23 24 25  26  27  28 29
pin_D = [16, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 30, 31, 32, 33, 34, 35, 0, 1, 23, 24, 25, 2, 3]

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