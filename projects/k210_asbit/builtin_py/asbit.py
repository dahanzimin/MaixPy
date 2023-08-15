"""
ASBIT -Onboard resources
"""
import board, time
from machine import UART

'''ESP32 RESET'''
def esp32_reset():
	board.pin(8, board.GPIO.OUT).value(0)
	time.sleep_ms(20)
	board.pin(8, board.GPIO.IN)

'''Video UART''' 
board.register(6,board.FPIOA.UART2_TX)
board.register(0,board.FPIOA.UART2_RX)
uart2 = UART(UART.UART2, 921600, timeout=1000, read_buf_len=4096)
_falg=True

def ob_stream(img, quality=80):
	global _falg 
	if _falg:
		board.register(6,board.FPIOA.UART2_TX)
		_falg=False
	img.compress(quality)
	uart2.write(img.to_bytes())

'''Data UART'''   
board.register(7,board.FPIOA.UART3_TX)
board.register(5,board.FPIOA.UART3_RX)
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

'''4RGB_WS2812'''    
from modules import ws2812
ob_rgb = ws2812(25, 4)
for i in range(0, 4, 1):
	ob_rgb.set_led(i,(0,0,0))
	ob_rgb.display()

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

key_a = Button(15)
key_b = Button(16)
