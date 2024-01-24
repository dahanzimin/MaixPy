"""
AIBIT -Onboard resources
"""
import board, time
from machine import Timer,PWM

'''Version judgment'''
if board.pin(24, board.GPIO.IN, board.GPIO.PULL_UP):
	version = 1
else:
	version = 0

'''I2C'''
ob_i2c = board.ob_i2c

'''Light Sensor'''
def brightness():
	return board.adc_read(3)

'''3-RGB_WS2812'''    
from modules import ws2812
ob_rgb = ws2812(25, 3)
for i in range(0, 3, 1):
	ob_rgb.set_led(i,(0,0,0))
	ob_rgb.display()

'''1-LED''' 
ob_led = PWM(Timer(Timer.TIMER2, Timer.CHANNEL3, mode=Timer.MODE_PWM), freq=1000, duty=0, pin=24)

'''1-Buzzer''' 
ob_buzzer = PWM(Timer(Timer.TIMER1, Timer.CHANNEL3, mode=Timer.MODE_PWM), freq=1000, duty=0, pin=23)

def buzzer_pitch(fre=400000, vol=0):
	ob_buzzer.freq(fre)
	ob_buzzer.duty(vol/10)

def buzzer_stop():
	ob_buzzer.duty(0)

'''2-Button'''
class Button:
	def __init__(self, pio):
		self._pin = board.pin(pio, board.GPIO.IN, board.GPIO.PULL_UP)
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

key_a = Button(9)
key_b = Button(10)
key_c = Button(11)
