#PAC9685 for 8Servos & 4Motor 
import math
import ustruct
import time
import board
from machine import I2C

class PCA9685:
	def __init__(self, i2c, address=0x40):
		self.i2c = i2c
		self.address = address
		self.reset()
		time.sleep(0.5)

	def _write(self, address, value):
		try:
			self.i2c.writeto_mem(self.address, address, bytearray([value]))
		except:
			return 0 

	def _read(self, address):
		try:
			return self.i2c.readfrom_mem(self.address, address, 1)[0]
		except:
			return 0

	def reset(self):
		self._write(0x00, 0x00) # Mode1

	def freq(self, freq=None):
		if freq is None:
			return int(25000000.0 / 4096 / (self._read(0xfe) - 0.5))
		prescale = int(25000000.0 / 4096.0 / freq + 0.5)
		old_mode = self._read(0x00) # Mode 1
		self._write(0x00, (old_mode & 0x7F) | 0x10) # Mode 1, sleep
		self._write(0xfe, prescale) # Prescale
		self._write(0x00, old_mode) # Mode 1
		time.sleep(0.005)
		self._write(0x00, old_mode | 0xa1) # Mode 1, autoincrement on

	def pwm(self, index, on=None, off=None):
		if on is None or off is None:
			data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * index, 4)
			return ustruct.unpack('<HH', data)
		data = ustruct.pack('<HH', on, off)
		try:
			self.i2c.writeto_mem(self.address, 0x06 + 4 * index,  data)
		except:
			return 0

	def duty(self, index, value=None, invert=False):
		if value is None:
			pwm = self.pwm(index)
			if pwm == (0, 4096):
				value = 0
			elif pwm == (4096, 0):
				value = 4095
			value = pwm[1]
			if invert:
				value = 4095 - value
			return value
		if not 0 <= value <= 4095:
			raise ValueError("Out of range")
		if invert:
			value = 4095 - value
		if value == 0:
			self.pwm(index, 0, 4096)
		elif value == 4095:
			self.pwm(index, 4096, 0)
		else:
			self.pwm(index, 0, value)

class MOTOR(PCA9685):
	def __init__(self, i2c, address=0x55, freq=50):
		super().__init__(i2c, address)
		self.freq(freq)
		self.release()

	def release(self):
		for i in range(8,16,1):
			self.duty(i, 0)

	def servo(self, index, degrees=0):
		if 1<=index <=8:
			duty = 102 + 410 * degrees / 180
			duty = min(512, max(102, int(duty)))
			self.duty(index-1, duty)
		else:
			raise ValueError("Servo port selection 1~8")

	def motor(self, index, speed):
		if 1<=index <=4:
			speed = min(max(speed, -100), 100)
			duty = int(4095*speed/100)
			if speed==0:
				self.duty(8+(index-1)*2, 0)
				self.duty(9+(index-1)*2, 0)
			if speed<0:
				self.duty(8+(index-1)*2, -duty)
				self.duty(9+(index-1)*2, 0)
			if speed>0:
				self.duty(8+(index-1)*2, 0)
				self.duty(9+(index-1)*2, duty)
		else:
			raise ValueError("Motor port selection 1~4")

class MOTOR_NEW:
	def __init__(self, i2c_bus, addr=0x25):
		self._i2c = i2c_bus
		self._addr = addr
		self.reset()

	def _wreg(self, reg, val):
		try:
			self._i2c.writeto_mem(self._addr, reg, val.to_bytes(1, 'little'))
		except:
			return 0 

	def _rreg(self, reg, nbytes=1):
		try:
			self._i2c.writeto(self._addr, reg.to_bytes(1, 'little'))
			return  self._i2c.readfrom(self._addr, nbytes)[0] if nbytes<=1 else self._i2c.readfrom(self._addr, nbytes)[0:nbytes]
		except:
			return 0

	def reset(self):
		for reg in range(0x01, 0x01 + 24):
			self._wreg(reg,0x00)

	def m_pwm(self, index, duty=None):
		if not 0 <= duty <= 255:
			raise ValueError("Duty must be a number in the range: 0~255")
		self._wreg(0x01 + index, duty)

	def s_pwm(self, index, duty=None):
			if not 0 <= duty <= 4095:
				raise ValueError("Duty must be a number in the range: 0~4095")
			self._wreg(0x09 + index * 2, duty >> 8)
			self._wreg(0x09 + index * 2 + 1, duty & 0xff)

	def motor(self, index, speed):
		if  1 <= index <= 4:
			speed = min(max(speed, -100), 100)
			if speed > 0:
				self.m_pwm((4-index) * 2, speed * 255 // 100)
				self.m_pwm((4-index) * 2 + 1, 0)
			elif speed < 0:
				self.m_pwm((4-index) * 2, 0)
				self.m_pwm((4-index) * 2 + 1, -(speed * 255 // 100))
			else:
				self.m_pwm((4-index) * 2, 0)
				self.m_pwm((4-index) * 2 + 1, 0)
		else:
			raise ValueError("Motor port selection 1~4")

	def servo(self, index, angle=None):
		if 1 <= index <= 8:
			angle = min(max(angle, 0), 180)
			self.s_pwm(index-1, round(102.375 + 409.5 / 180 * angle))
		else:
			raise ValueError("Servo port selection 1~8")

i2c = I2C(I2C.I2C0, freq=100000, scl=30, sda=31)
i2c_scan = i2c.scan()

if not i2c_scan:
	i2c = I2C(I2C.I2C0, freq=100000, scl=31, sda=32)
	i2c_scan = i2c.scan()	

#print('i2c_scan: ',i2c_scan)
if 0x40 in i2c_scan:
	motors = MOTOR(i2c,address=0x40)
if 0x25 in i2c_scan:
	motors = MOTOR_NEW(i2c)
