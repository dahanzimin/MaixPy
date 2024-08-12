"""
MixNO -Onboard resources
"""
import time
from Maix import *
from machine import I2C
#                                                          LED MS  MW  MD  RX TX EN SE  SW  SD  SS  KA  KB  
#K210pin 0  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17 18 19 20  21  22  23  24  25
pin_D = [4, 5,  9, 10, 11, 12, 13, 14, 15, 21, 22, 23, 24, 25, 18, 19, 20, 6, 7, 8, 32, 33, 34, 35, 17, 16]

#I2C Onboard
ob_i2c = I2C(I2C.I2C3, freq=400000, scl=30, sda=31)
i2c_scan = ob_i2c.scan()

#Version judgment
if 0x27 in i2c_scan:
	import bot_51
	_iobot = bot_51.BOT(ob_i2c)
	version = 1
elif (0x48 in i2c_scan) and (0x49 in  i2c_scan):
	import ads1x15
	_adc1 = ads1x15.ADS1015(ob_i2c, address=0x48, gain=0)
	_adc2 = ads1x15.ADS1015(ob_i2c, address=0x49, gain=0)
	version = 0
else:
	version = None

def register(pin=None, function=None):
	FPIOA().set_function(pin_D[pin], function)
	return 1

def pin(pin=None, function=None, *k):
	FPIOA().set_function(pin_D[pin], 24 + pin)
	return GPIO(pin, function, *k)

def bot_init(gpio, inout=False):
	if version:
		_iobot.io_init(gpio, inout)
	else:
		print("Warning: The old version does not have this feature!")

def adc_init(gain=0):
	#Fake functions used for older versions
	if version == 0:
		_adc1.gain = gain
		_adc2.gain = gain

def adc_read(channel):
	if version:
		return _iobot.adc_raw(channel)
	elif version == 0:
		return _adc1.read(channel1=channel)	if channel <=3 else _adc2.read(channel1=channel-4)
	else:
		raise ValueError("[MixNo] No ADC for this channel")
	
def adc_vread(channel):
	if version:
		return _iobot.adc_vol(channel)
	elif version == 0:
		return _adc1.raw_to_v(_adc1.read(channel1=channel))	if channel <=3 else _adc2.raw_to_v(_adc2.read(channel1=channel-4))
	else:
		raise ValueError("[MixNo] No ADC for this channel")

def bat_read():
	if version:
		return _iobot.bat_read()
	else:
		print("Warning: The old version does not have this feature!")

def pwm_write(channel, duty):
	if version:
		_iobot.pwm(channel, duty)
	else:
		print("Warning: The old version does not have this feature!")

def servo180(channel, angle):
	if version:
		_iobot.servo180(channel, angle)
	else:
		print("Warning: The old version does not have this feature!")

def lcd_led(en):
	if version:
		pin(20, GPIO.OUT).value(en)
	else:
		print("Warning: The old version does not have this feature!")

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
