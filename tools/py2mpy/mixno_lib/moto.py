import board
from machine import PWM

class Motor:
	def __init__(self, timer, pina, pinb):
		self._pwm = PWM(timer, freq=1000, duty=0, pin=board.pin_D[pina])
		self._pin = board.pin(pinb, board.GPIO.OUT)
		self._speed = 0

	def run(self,speed=0):
		self._speed = max(min(speed,100),-100)
		if self._speed == 0:
			self._pwm.duty(0)
			self._pin.value(0)
		if self._speed > 0:
			self._pwm.duty(self._speed)
			self._pin.value(0)				
		if self._speed < 0:
			self._pwm.duty(100+self._speed)
			self._pin.value(1)	
	
	def speed(self):
		return self._speed
		
class Servo:
	def __init__(self, timer, pin):
		self._pwm = PWM(timer, freq=50, duty=2.5, pin=board.pin_D[pin])
		self._angle = None

	def set_angle(self,angle):
		self._angle = max(min(angle,180),0)
		self._pwm.duty(self._angle/18.0+2.5)
	
	def read_angle(self):
		return self._angle