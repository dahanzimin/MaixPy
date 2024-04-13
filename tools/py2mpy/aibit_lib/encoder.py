# 编码测速
import board
import time
import math

class ENCODER:
	def __init__(self, pin, scale_p=400, wheel_d=5):
		self._time = time.ticks_ms()
		self._pulse_turns=1/scale_p
		self._pulse_distance=self._pulse_turns*math.pi*wheel_d
		self._turns = 0
		self._distance = 0
		self._speed = 0
		_irq=board.pin(pin, board.GPIO.IN, board.GPIO.PULL_NONE)
		_irq.irq(self.irp_func,board.GPIO.IRQ_BOTH,board.GPIO.WAKEUP_NOT_SUPPORT, 7)

	def irp_func(self, event_source):
		self._turns += self._pulse_turns
		self._distance += self._pulse_distance
		self._speed += self._pulse_distance

	def turns(self,turns=None):
		if turns is None:
			return round(self._turns,2)
		else:
			self._turns=turns

	def distance(self,distance=None): #cm
		if distance is None:
			return round(self._distance,2)
		else:
			self._distance=distance

	def speed(self):    #cm/s
		ss_speed=self._speed/time.ticks_diff(time.ticks_ms(), self._time)*1000 if self._speed>0 else 0
		self._speed=0
		self._time = time.ticks_ms()
		return round(ss_speed, 2)
