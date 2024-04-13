import board
from machine import PWM
from machine import Timer


leg1_b=PWM(Timer(Timer.TIMER2,Timer.CHANNEL3, mode=Timer.MODE_PWM), freq=50, duty=0, pin=board.pin_D[8])
leg1_s=PWM(Timer(Timer.TIMER1,Timer.CHANNEL3, mode=Timer.MODE_PWM), freq=50, duty=0, pin=board.pin_D[12])

leg2_b=PWM(Timer(Timer.TIMER0,Timer.CHANNEL3, mode=Timer.MODE_PWM), freq=50, duty=0, pin=board.pin_D[4])
leg2_s=PWM(Timer(Timer.TIMER2,Timer.CHANNEL2, mode=Timer.MODE_PWM), freq=50, duty=0, pin=board.pin_D[0])

leg3_b=PWM(Timer(Timer.TIMER1,Timer.CHANNEL2, mode=Timer.MODE_PWM), freq=50, duty=0, pin=board.pin_D[5])
leg3_s=PWM(Timer(Timer.TIMER0,Timer.CHANNEL2, mode=Timer.MODE_PWM), freq=50, duty=0, pin=board.pin_D[6])

leg4_b=PWM(Timer(Timer.TIMER2,Timer.CHANNEL1, mode=Timer.MODE_PWM), freq=50, duty=0, pin=board.pin_D[7])
leg4_s=PWM(Timer(Timer.TIMER1,Timer.CHANNEL1, mode=Timer.MODE_PWM), freq=50, duty=0, pin=board.pin_D[1])


def angle(pin_num,degrees):            #设置舵机角度
	if pin_num==1:
		leg1_b.duty(degrees/18.0+2.5)
	elif pin_num==2:
		leg1_s.duty(degrees/18.0+2.5)
	elif pin_num==3:
		leg2_b.duty(degrees/18.0+2.5)
	elif pin_num==4:
		leg2_s.duty(degrees/18.0+2.5)		
	elif pin_num==5:
		leg3_b.duty(degrees/18.0+2.5)
	elif pin_num==6:
		leg3_s.duty(degrees/18.0+2.5)			
	elif pin_num==7:
		leg4_b.duty(degrees/18.0+2.5)
	elif pin_num==8:
		leg4_s.duty(degrees/18.0+2.5)
		
def release():
	leg1_b.duty(0)
	leg1_s.duty(0)
	leg2_b.duty(0)
	leg2_s.duty(0)
	leg3_b.duty(0)
	leg3_s.duty(0)
	leg4_b.duty(0)
	leg4_s.duty(0)








