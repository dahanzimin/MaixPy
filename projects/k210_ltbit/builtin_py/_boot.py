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


# detect boot.py
import board

if not board.pin(0, board.GPIO.IN).value():
    time.sleep_ms(50)
    if not board.pin(0, board.GPIO.IN).value():
        ls=os.listdir()
        del_paths = [name for name in ls if name.endswith('.py')]
        for a in del_paths:
            os.remove(a)
            print("Delete --{}".format(a)) # for factory
        del ls
        del del_paths
        print("Restore factory settings") # for factory

main_py = '''
import lcd,image,random,time

lcd.init()
lcd.rotation(1)
image = image.Image()
print("Welcome to TABIT")
while True:
    for color in range(0, 0xFFFF):
        image = image.draw_string(45, 0, "Welcome", 0xFFFF, 2, mono_space=0) 
        image = image.draw_string(75, 80,"LTBIT", color, 6, mono_space=0) 
        image = image.draw_string(170, 220, "AOIT_V2.2", 0xFFFF, 2, mono_space=0) 
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
    del f
del main_py

banner = '''

Welcome to TABIT

'''
print(banner)
del banner
