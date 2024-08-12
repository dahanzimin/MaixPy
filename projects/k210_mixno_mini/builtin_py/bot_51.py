"""
MixNo -协处理器BOT51驱动
"""
from micropython import const

_BOT_ADDR		= const(0x27)
_BOT_ID			= const(0x00)
_BOT_IO			= const(0x01)
_BOT_ADC		= const(0x02)
_BOT_PWM		= const(0x12)
_BOT_BAT		= const(0x22)

'''(ADC+PWM)*8+BAT''' 
class BOT:
	def __init__(self, i2c_bus, addr=_BOT_ADDR):
		self._i2c = i2c_bus
		self._addr = addr
		if self._rreg(_BOT_ID)!= 0x27:
			print("Warning Cannot find a external module!")
		self.reset()

	def _wreg(self, reg, val):
		'''Write memory address'''
		try:
			self._i2c.writeto_mem(self._addr, reg, val.to_bytes(1, 'little'))
		except:
			return 0 

	def _rreg(self, reg, nbytes=1):
		'''Read memory address'''
		try:
			self._i2c.writeto(self._addr, reg.to_bytes(1, 'little'))
			return  self._i2c.readfrom(self._addr, nbytes)[0] if nbytes<=1 else self._i2c.readfrom(self._addr, nbytes)[0:nbytes]
		except:
			return 0

	def reset(self):
		for reg in range(_BOT_IO, _BOT_BAT):
			self._wreg(reg, 0x00)

	def io_init(self, index, output=False):
		if not 0 <= index <= 7:
			raise ValueError("IO port must be a number in the range: 0~7")	
		if output:
			self._wreg(_BOT_IO,  (1 << index) | self._rreg(_BOT_IO))
		else:
			self._wreg(_BOT_IO, ~(1 << index) & self._rreg(_BOT_IO))


	def adc_raw(self, index):
		if not 0 <= index <= 7:
			raise ValueError("ADC port must be a number in the range: 0~7")	
		return self._rreg(_BOT_ADC + index * 2) | self._rreg(_BOT_ADC + index * 2 + 1) << 8

	def adc_vol(self, index, ratio=5/1023):
		return round(self.adc_raw(index) * ratio, 2)

	def pwm(self, index, duty=None, value=None):
		if not 0 <= index <= 7:
			raise ValueError("PWM port must be a number in the range: 0~7")	
		if duty is None and value is None:
			return self._rreg(_BOT_PWM + index * 2) | self._rreg(_BOT_PWM + index * 2 + 1) << 8 
		if duty is not None:
			value = round(min(max(duty, 0), 100) * 4095 / 100)
		self._wreg(_BOT_PWM + index * 2, value & 0xff)
		self._wreg(_BOT_PWM + index * 2 + 1, value >> 8)

	def servo180(self, index, angle=None):
		if angle is None:
			return  round((self.pwm(index) - 102.375) * 180 / 409.5)
		else:
			angle = min(max(angle, 0), 180)
			self.pwm(index, value = round(102.375 + 409.5 / 180 * angle))

	def bat_read(self, ratio=14.5/1023):
		vbat = self._rreg(_BOT_BAT) | self._rreg(_BOT_BAT + 1) << 8
		return round(vbat * ratio, 2)
