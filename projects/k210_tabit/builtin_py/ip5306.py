"""
IP5306
"""
import time
from micropython import const

IP5306_SYS_CTL0		= const(0x00)
IP5306_SYS_CTL1		= const(0x01)
IP5306_CHG_DIG_CTL0	= const(0x24)
IP5306_REG_READ0	= const(0x70)
IP5306_REG_READ1	= const(0x71)

class IP5306:
	def __init__(self, i2c_bus, address=0x75):
		self._device = i2c_bus
		self._address = address
		self.manage() 

	def _wreg(self, reg, val):
		'''Write memory address'''
		self._device.writeto_mem(self._address,reg,val.to_bytes(1, 'little'))

	def _rreg(self, reg,nbytes=1):
		'''Read memory address'''
		return  self._device.readfrom_mem(self._address, reg, nbytes)[0] if nbytes<=1 else self._device.readfrom_mem(self._address, reg, nbytes)[0:nbytes]

	def manage(self, boost=True, charge=True):
		'''Charging and boost management settings'''
		_falg = self._rreg(IP5306_SYS_CTL0)
		self._wreg(IP5306_SYS_CTL0,(boost<<5 |charge <<4 | 0xC9) & _falg)

	def charged(self):
		'''Judge whether charging'''
		return bool(self._rreg(IP5306_REG_READ0) >>3 & 0x01)

	def fully_charged(self):
		'''Judge whether it is fully charged'''
		return bool(self._rreg(IP5306_REG_READ1) >>3 & 0x01)

	def charge_current(self, current=None):
		'''Charging current acquisition and setting'''
		_ca = self._rreg(IP5306_CHG_DIG_CTL0)
		if current is None:
			return 0.05 + (_ca & 0x01)*0.1 + (_ca>>1 & 0x01)*0.2 + (_ca>>2 & 0x01)*0.4 + (_ca>>3 & 0x01)*0.8 + (_ca>>4 & 0x01)*1.6
		else:
			_a = int(current * 10)
			_b4 = _a //16
			_a = _a - 16 if _b4 else _a
			_b3 = _a //8
			_a = _a - 8 if _b3 else _a
			_b2 = _a //4
			_a = _a - 4 if _b2 else _a
			_b1 = _a //2
			_a = _a - 2 if _b1 else _a
			_b0 = _a //1
			self._wreg(IP5306_CHG_DIG_CTL0, (_ca & 0xE0) | _b4 << 4 | _b3 << 3 | _b2 << 2 | _b1 << 1 | _b0)
