import os, sys, time

sys.path.append('')
sys.path.append('.')

# chdir to "/sd" or "/flash"
devices = os.listdir("/")
if "sd" in devices:
	os.chdir("/sd")
	sys.path.append('/sd')
else:
	os.chdir("/flash")
sys.path.append('/flash')
del devices

print("[MixNo] init end") # for IDE
for i in range(200):
	time.sleep_ms(1) # wait for key interrupt(for maixpy ide)
del i

# check IDE mode
ide_mode_conf = "/flash/ide_mode.conf"
ide = True
try:
	f = open(ide_mode_conf)
	f.close()
	del f
except Exception:
	ide = False

if ide:
	os.remove(ide_mode_conf)
	from machine import UART
	import lcd
	lcd.init(color=lcd.PINK)
	repl = UART.repl_uart()
	repl.init(1500000, 8, None, 1, read_buf_len=2048, ide=True, from_ide=False)
	sys.exit()
del ide, ide_mode_conf


import board

if not ((0x48 in board.ob_i2c.scan()) and (0x49 in board.ob_i2c.scan())):
	raise Exception("Sorry, you are not using a MixNo board")	

if board.key_a.is_pressed():
	ls=os.listdir()
	del_paths = [name for name in ls if name.endswith('.py')]
	for a in del_paths:
		os.remove(a)
		print("[MixNo] delete --{}".format(a)) # for factory
	del ls
	del del_paths
	print("[MixNo] restore factory settings") # for factory
# detect boot.py

main_py = '''
import lcd,image,random,time

lcd.init(freq=15000000,color=0x0000)
image = image.Image()
list = [0,0,8]

print("Welcome to MixNo")
while True:
	color=random.randint(0, 0xFFFF)
	for i in range(0, 100, 1):
		list[0] = random.randint(0, 320)
		list[1] = random.randint(0, 240)
		list[2] = random.randint(1, 8)
		image = image.draw_circle(list,(random.randint(0, 0xFFFF)),1,1)
		image = image.draw_string(80,80,"MixNo",color,6,mono_space=0) 
		image = image.draw_string(200,220,"Mini_V2.0.5",0xFFFF,2,mono_space=0) 
		lcd.display(image)
		time.sleep_ms(50)
	image.clear()
	print("Factory reset test procedure")
	lcd.display(image)
'''

flash_ls = os.listdir()
if not "main.py" in flash_ls:
	f = open("main.py", "wb")
	f.write(main_py)
	f.close()
del main_py

banner = '''

Welcome to MixNo
Chuangwu Educational Science and Technology Jiangsu Co., Ltd. 
'''
print(banner)
del banner

