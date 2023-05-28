"""
TABIT -Onboard resources
"""
import board, time
from machine import I2C

ob_i2c = I2C(I2C.I2C0, freq=400000, scl=31, sda=32)

'''ACC-Sensor'''
try :
	import mxc6655xa
	ob_acc = mxc6655xa.MXC6655XA(ob_i2c)     
except Exception as e:
	print("Warning: Failed to communicate with ACC or",e)

'''ALS_PS-Sensor'''
try :
	import ltr553als
	ob_als = ltr553als.LTR_553ALS(ob_i2c)     
except Exception as e:
	print("Warning: Failed to communicate with ALS+PS or",e)

'''PMU-Sensor'''
try :
	import ip5306
	ob_pmu = ip5306.IP5306(ob_i2c)     
except Exception as e:
	print("Warning: Failed to communicate with PMU or",e)

'''4RGB_WS2812'''    
from modules import ws2812
ob_rgb = ws2812(17, 4)
for i in range(0, 4, 1):
	ob_rgb.set_led(i,(0,0,0))
	ob_rgb.display()

'''Network'''
try :
	from network import ESP32_SPI
	board.register(15,board.FPIOA.GPIOHS15)#cs
	board.register(22,board.FPIOA.GPIOHS22)#rst
	board.register(21,board.FPIOA.GPIOHS21)#rdy
	board.register(30,board.FPIOA.SPI1_D0)#mosi
	board.register(28,board.FPIOA.SPI1_D1)#miso
	board.register(29,board.FPIOA.SPI1_SCLK)#sclk
	try:
		wifi = ESP32_SPI(cs=board.FPIOA.GPIOHS15, rst=board.FPIOA.GPIOHS22, rdy=board.FPIOA.GPIOHS21, spi=1)
	except:
		wifi = ESP32_SPI(cs=board.FPIOA.GPIOHS15, rst=board.FPIOA.GPIOHS22, rdy=board.FPIOA.GPIOHS21, spi=1)
except Exception as e:
	print("Warning: Failed to communicate with ESP32 or",e)

'''1,5KEY_Sensor'''
class KEYSensor:
	_kadc=((-50, 100), (100, 350), (350, 600), (600, 850), (850, 1100))
	def __init__(self, pin):
		self.boot = board.pin(pin, board.GPIO.IN)

	def _value(self):
		values = []
		for _ in range(20):
			time.sleep_us(50)
			values.append(wifi.adc()[0])
		return sum(sorted(values)[5:15])//10

	def pressed(self, nkey):
		if not self.boot.value():
			return self._kadc[nkey][0] < self._value() < self._kadc[nkey][1]

	def irp_func(self, nkey):
		if self._on_handle:
			for nkey in self._kadc:
				if nkey[0] < self._value() < nkey[1]:
					self._on_handle(self._kadc.index(nkey))    

	def irq(self, handler, irq_cb):
		self._on_handle = irq_cb
		if irq_cb:
			self.boot.irq(self.irp_func, handler, board.GPIO.WAKEUP_NOT_SUPPORT, 7)

ob_key=KEYSensor(16)

'''Battery'''
def vbattery():
	return round(wifi.adc()[6]*6.6/4095, 2)

'''ADC'''
def adc_read(num):
	_index=(5, 4, 2, 1, 3, 7)
	return wifi.adc()[_index[num]]
