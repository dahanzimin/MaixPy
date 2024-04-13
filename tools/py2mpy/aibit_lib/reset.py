import lcd,time,gc,machine


lcd.init(color=0x0000)
lcd.draw_string(88,100, "Welcome to TeaiLe!", lcd.YELLOW, lcd.BLACK)
lcd.draw_string(102,132, "loading .", lcd.YELLOW, lcd.BLACK)
time.sleep_ms(100)
lcd.draw_string(102,132, "loading ..", lcd.YELLOW, lcd.BLACK)
time.sleep_ms(100)
lcd.draw_string(102,132, "loading ...", lcd.YELLOW, lcd.BLACK)
time.sleep_ms(100)
lcd.draw_string(102,132, "loading ....", lcd.YELLOW, lcd.BLACK)
time.sleep_ms(100)
lcd.draw_string(102,132, "loading .....", lcd.YELLOW, lcd.BLACK)
time.sleep_ms(100)
lcd.draw_string(102,132, "loading ......", lcd.YELLOW, lcd.BLACK)
time.sleep_ms(100)
lcd.draw_string(102,132, "loading .......", lcd.YELLOW, lcd.BLACK)
time.sleep_ms(100)	
lcd.clear(0x0000)
gc.collect()
del time
del lcd
del gc
machine.reset()


