"""
MixNO -Onboard resources
"""
import time
from Maix import *
from machine import I2C
#                                                          LED MS  MW  MD  RX TX EN SE  SW  SD  SS  KA  KB  
#k210pin 0  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17 18 19 20  21  22  23  24  25
pin_D = [4, 5,  9, 10, 11, 12, 13, 14, 15, 21, 22, 23, 24, 25, 18, 19, 20, 6, 7, 8, 32, 33, 34, 35, 17, 16]

adc1 = None
adc2 = None
ob_i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)

def register(pin = None,function = None):
	FPIOA().set_function(pin_D[pin],function)
	return 1

def pin(pin = None,function = None, *k):
	FPIOA().set_function(pin_D[pin],24+pin)
	pins=GPIO(pin, function, *k)
	return pins

def adc_init(gains=0):
	global adc1
	global adc2
	import ads1x15
	adc1=ads1x15.ADS1015(ob_i2c,address=0x48,gain=gains)
	adc2=ads1x15.ADS1015(ob_i2c,address=0x49,gain=gains)

def adc_read(channel):
	try:
		if channel <=3:
			return adc1.read(channel1=channel)	
		else:
			return adc2.read(channel1=channel-4)
	except Exception as e:
		raise ValueError("[MixNo] No ADC for this channel")	
	
def adc_vread(channel):
	try:
		if channel <=3:
			return adc1.raw_to_v(adc1.read(channel1=channel))	
		else:
			return adc2.raw_to_v(adc2.read(channel1=channel-4))
	except Exception as e:
		raise ValueError("[MixNo] No ADC for this channel")	

'''2-Button'''
class Button:
    def __init__(self, pio):
        self._pin = pin(pio, GPIO.IN, GPIO.PULL_UP)
        self._flag = True

    def is_pressed(self):
        return self._pin.value() == False

    def was_pressed(self):
        if self._pin.value() != self._flag:
            time.sleep(0.01)
            self._flag = self._pin.value()
            if self._flag:
                return False
            else:
                return True

    def irq(self, handler, trigger):
        self._pin.irq(handler, trigger, board.GPIO.WAKEUP_NOT_SUPPORT, 7)

key_a = Button(24)
key_b = Button(25)
	
def config(config):
	import json
	cfg = json.dumps(config)
	try:
		with open('config.json', "w") as f:
			f.write(cfg)
		print("[MixNo] Configuration modified successfully")
		import os
		os.remove("main.py")
	finally:	
		import machine
		machine.reset()
