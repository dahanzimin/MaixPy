from machine import PWM
from machine import Timer
import board

M1A=PWM(Timer(Timer.TIMER0,Timer.CHANNEL3, mode=Timer.MODE_PWM),freq=1000,duty=0, pin=board.pin_D[2])
M1B=PWM(Timer(Timer.TIMER2,Timer.CHANNEL2, mode=Timer.MODE_PWM),freq=1000,duty=0, pin=board.pin_D[12])
M2A=PWM(Timer(Timer.TIMER1,Timer.CHANNEL2, mode=Timer.MODE_PWM),freq=1000,duty=0, pin=board.pin_D[8])
M2B=PWM(Timer(Timer.TIMER0,Timer.CHANNEL2, mode=Timer.MODE_PWM),freq=1000,duty=0, pin=board.pin_D[1])

def moto1_init():
	global M1A
	global M1B
	Tim1 = Timer(Timer.TIMER0,Timer.CHANNEL2, mode=Timer.MODE_PWM)
	Tim2 = Timer(Timer.TIMER2,Timer.CHANNEL2, mode=Timer.MODE_PWM)
	M1A = PWM(Tim1,freq=1000,duty=0, pin=board.pin_D[2])
	M1B= PWM(Tim2,freq=1000,duty=0, pin=board.pin_D[12])

def moto2_init():
	global M2A
	global M2B
	Tim3 = Timer(Timer.TIMER1,Timer.CHANNEL2, mode=Timer.MODE_PWM)
	Tim4 = Timer(Timer.TIMER0,Timer.CHANNEL2, mode=Timer.MODE_PWM)
	M2A = PWM(Tim3,freq=1000,duty=0, pin=board.pin_D[8])
	M2B= PWM(Tim4,freq=1000,duty=0, pin=board.pin_D[1])
	
def moto1_run(speed=0):
	global M1A
	global M1B
	if speed == 0:
		M1A.duty(0)
		M1B.duty(0)
	if speed > 0:
		M1A.duty(speed)
		M1B.duty(0)					
	if speed < 0:
		M1A.duty(0)
		M1B.duty(-(speed))			
		
def moto2_run(speed=0):
	global M2A
	global M2B
	if speed == 0:
		M2A.duty(0)
		M2B.duty(0)
	if speed > 0:
		M2A.duty(speed)
		M2B.duty(0)					
	if speed < 0:
		M2A.duty(0)
		M2B.duty(-(speed))
		