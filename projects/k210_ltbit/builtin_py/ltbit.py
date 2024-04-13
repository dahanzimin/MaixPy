"""
LTBIT -Onboard resources
20240413-取消电机驱动及霍尔，增加总线舵机
"""
import board, time, math
from machine import I2C, UART

ob_i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)

'''ADC*5+舵机*8''' 
class EXT:
	def __init__(self, i2c_bus, addr=0x27):
		self._i2c = i2c_bus
		self._addr = addr
		if self._rreg(0x00)!= 0x27:
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
		"""Reset all registers to default state"""
		for reg in range(0x09, 0x19):
			self._wreg(reg,0x00)

	def adc_read(self, index):
		if not 0 <= index <= 3:
			raise ValueError("ADC port must be a number in the range: 0~3")	
		return self._rreg(0x01 + index * 2) << 2 | self._rreg(0x01 + index * 2 + 1)	>> 6

	def bat_read(self, ratio=14.5/1023):
		'''Read battery power'''
		vbat = self._rreg(0x19) << 2 | self._rreg(0x19 + 1) >> 6
		return round(vbat * ratio, 2)

	def pwm(self, index, value=None, duty=None):
		"""Servo*8 PWM duty cycle data register"""
		if duty is None and value is None:
			return self._rreg(0x09 + index * 2) << 8 | self._rreg(0x09 + index * 2 + 1)
		if duty is not None:
			value = int(min(max(duty, 0), 100) * 4095 / 100)
		self._wreg(0x09 + index * 2, value >> 8)
		self._wreg(0x09 + index * 2 + 1, value & 0xff)

	def servo180(self, index, angle=None):
		if not 0 <= index <= 7:
			raise ValueError("Servo port must be a number in the range: 0~7")
		if angle is None:
			return  round((self.pwm(index) - 102.375) * 180 / 409.5)
		else:
			angle = min(max(angle, 0), 180)
			self.pwm(index, round(102.375 + 409.5 / 180 * angle))

on_ext = EXT(ob_i2c)

'''Video UART''' 
board.register(23, board.FPIOA.UART2_RX)
board.register(24, board.FPIOA.UART2_TX)

uart2 = UART(UART.UART2, 921600, timeout=1000, read_buf_len=4096)
_falg=True

def ob_stream(img, quality=80):
	global _falg 
	if _falg:
		board.register(24, board.FPIOA.UART2_TX)
		_falg=False
	img.compress(quality)
	uart2.write(img.to_bytes())

'''Data UART'''   
board.register(28, board.FPIOA.UART3_RX)
board.register(29, board.FPIOA.UART3_TX)

uart3=UART(UART.UART3, 115200, timeout=1000, read_buf_len=4096)
_data=None

def ob_send(data, repeat=True):
	global _data   
	data_b = data
	if data_b != _data:
		uart3.write((str(data)+'\n'))
		if not repeat:
			_data = data_b
			
def ob_recv():
	data = uart3.readline()
	if data:
		data_str = data.strip()
		try:
			data_str=data_str.decode()
			return eval(data_str)
		except:
			return data_str

'''1-Button'''
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

key_boot = Button(0)
