"""
LTBIT -Onboard resources
"""
import board, time
from machine import I2C, UART

ob_i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)

'''Motor*4*2 + Servo*8''' 
class MOTOR:
	def __init__(self, i2c_bus, addr=0x25):
		self._i2c = i2c_bus
		self._addr = addr
		if self._rreg(0x00)!= 0x25:
			raise AttributeError("Cannot find a Motor")
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
		for reg in range(0x01, 0x01 + 24):
			self._wreg(reg,0x00)

	def m_pwm(self, index, duty=None):
		"""Motor*4*2 PWM duty cycle data register"""
		if duty is None:
			return self._rreg(0x01 + index)
		else:
			if not 0 <= duty <= 255:
				raise ValueError("Duty must be a number in the range: 0~255")
			self._wreg(0x01 + index, duty)

	def s_pwm(self, index, duty=None):
		"""Servo*8 PWM duty cycle data register"""
		if duty is None:
			return self._rreg(0x09 + index * 2) << 8 | self._rreg(0x09 + index * 2 + 1)
		else:
			if not 0 <= duty <= 4095:
				raise ValueError("Duty must be a number in the range: 0~4095")
			self._wreg(0x09 + index * 2, duty >> 8)
			self._wreg(0x09 + index * 2 + 1, duty & 0xff)

	def motor(self, index, speed=None, brake=False):
		if not 0 <= index <= 3:
			raise ValueError("Motor port must be a number in the range: 0~3")
		if speed is None:
			return round(self.m_pwm(index*2)*100/255 - self.m_pwm(index*2+1)*100/255)
		else:
			speed = min(max(speed, -100), 100)
			if speed > 0:
				self.m_pwm(index * 2, speed * 255 // 100)
				self.m_pwm(index * 2 + 1, 0)
			elif speed < 0:
				self.m_pwm(index * 2, 0)
				self.m_pwm(index * 2 + 1, -(speed * 255 // 100))
			else:
				if brake:
					self.m_pwm(index * 2, 255)
					self.m_pwm(index * 2 + 1, 255)
				else:
					self.m_pwm(index * 2, 0)
					self.m_pwm(index * 2 + 1, 0)

	def servo180(self, index, angle=None):
		if not 0 <= index <= 7:
			raise ValueError("Motor port must be a number in the range: 0~7")
		if angle is None:
			return  round((self.s_pwm(index) - 102.375) * 180 / 409.5)
		else:
			angle = min(max(angle, 0), 180)
			self.s_pwm(index,round(102.375 + 409.5 / 180 * angle))

on_motor = MOTOR(ob_i2c)

'''Video UART''' 
board.register(23, board.FPIOA.UART2_TX)
board.register(24, board.FPIOA.UART2_RX)
uart2 = UART(UART.UART2, 921600, timeout=1000, read_buf_len=4096)
_falg=True

def ob_stream(img, quality=80):
	global _falg 
	if _falg:
		board.register(23, board.FPIOA.UART2_TX)
		_falg=False
	img.compress(quality)
	uart2.write(img.to_bytes())

'''Data UART'''   
board.register(28, board.FPIOA.UART3_TX)
board.register(29, board.FPIOA.UART3_RX)
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
		self._pin = board.pin(pio, board.GPIO.IN)
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
