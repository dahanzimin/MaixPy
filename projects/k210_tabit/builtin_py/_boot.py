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

print("TABIT init end") # for IDE
for i in range(200):
    time.sleep_ms(1) # wait for key interrupt(for canmv ide)
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

if(board.pin(16,board.GPIO.IN).value()==0):
	ls=os.listdir()
	del_paths = [name for name in ls if name.endswith('.py')]
	for a in del_paths:
		os.remove(a)
		print("Delete --{}".format(a)) # for factory
	del ls
	del del_paths
	print("Restore factory settings") # for factory
# detect boot.py

#IP506 configuration
try:
    from machine import I2C
    ip_i2c = I2C(I2C.I2C0, freq=400000, scl=31, sda=32)
    ip_i2c.writeto_mem(0x75, 0x00, b'\x31')
    ip_i2c.writeto_mem(0x75, 0x24, b'\xc5')
except Exception as e:
    print('Warning: Power management configuration failed ', e)
    
main_py = '''
import lcd,image,random,time

lcd.init()
lcd.rotation(1)
image = image.Image()
print("Welcome to TABIT")
while True:
    for color in range(0, 0xFFFF):
        image = image.draw_string(75, 80,"TABIT", color, 6, mono_space=0) 
        image = image.draw_string(160, 220, "AOIT_V2.0", 0xFFFF, 2, mono_space=0) 
        lcd.display(image)
        time.sleep_ms(100)
    image.clear()
    print("Factory reset test procedure")
    lcd.display(image)
'''

flash_ls = os.listdir()
if not "main.py" in flash_ls:
    f = open("main.py", "wb")
    f.write(main_py)
    f.close()
    del f
del main_py

banner = '''

Welcome to TABIT

'''
print(banner)
del banner
