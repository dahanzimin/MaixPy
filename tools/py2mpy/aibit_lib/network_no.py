import network,time,board
from machine import UART

wifi_en=board.pin(17,board.GPIO.OUT)
wifi_en.value(0)
board.register(16,board.FPIOA.UART2_TX)
board.register(15,board.FPIOA.UART2_RX)
uart = UART(UART.UART2, 115200, timeout=1000, read_buf_len=8192)

def at_cmd(cmd="AT\r\n", resp="OK\r\n", timeout=100):
	uart.write(cmd)
	time.sleep_ms(timeout)
	tmp = uart.read()
	if tmp and tmp.endswith(resp):
		return tmp
		
def wifi_reply(reply=5):
	for _ in range(reply):
		wifi_en.value(0)
		time.sleep_ms(50)
		wifi_en.value(1)
		time.sleep_ms(800) # at start > 500ms
		if at_cmd(timeout=200):
			return True
 
def wifi_init1():
	wifi_reply(5)
	at_cmd("AT+UART_CUR=921600,8,1,0,0\r\n")
	uart = UART(UART.UART2, 921600, timeout=1000, read_buf_len=10240) # important! baudrate too low or read_buf_len too small will loose data
	try:
		nic = network.ESP8285(uart)
		time.sleep_ms(500)
		#print(nic)
		return nic
	except Exception as e:
		raise Exception("[AIBIT]:WiFi init fail",e)

def wifi_init2():
	wifi_reply(5)
	try:
		nic = network.ESP8285(uart)
		time.sleep_ms(500)
		#print(nic)
		return nic
	except Exception as e:
		raise Exception("[AIBIT]:WiFi init fail",e)
	
def wifi_deal_ap_info(info):
	res = []
	for ap_str in info:
		ap_str = ap_str.split(",")
		info_one = []
		for node in ap_str:
			if node.startswith('"'):
				info_one.append(node[1:-1])
			else:
				info_one.append(int(node))
		res.append(info_one)
	return res

def scans(nic): 
	ap_info = nic.scan()
	ap_info = wifi_deal_ap_info(ap_info)
	ap_info.sort(key=lambda x:x[2], reverse=True)
	return ap_info

def do_connect(account, password, reply=5):
	print('connect', account, 'wifi ', end ="")
	for i in range(reply):
		try:
			print('.',end ="")
			nic=wifi_init1()
			nic.connect(account, password)
			if nic.isconnected():
				print(nic.ifconfig())
				return nic
		except Exception as e:
			err = e
	print('x')
	raise RuntimeError(err) 
