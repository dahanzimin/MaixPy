#加载预置参数
try:
	from config_s import *		#加载舵机中位
except:
	raise ValueError("请先运行舵机标定配置...")
#引入模块
import board
import PA_SERVO
import PA_GAIT
import PA_IK
import PA_ATTITUDE
import PA_STABLIZE
import time
from math import sin,cos,pi,atan,tan,floor
from machine import PWM,Timer

#======警告======
alarm_pin =PWM(Timer(Timer.TIMER0, Timer.CHANNEL1, mode=Timer.MODE_PWM), freq=1000, duty=50, pin=board.pin_D[21])

alarm_flash_node=0
sound_freq1=0
sound_freq2=0
alarm_per=0
alarm_per_add=0
alarm_time_per=0

def alarm_run():
  global alarm_flash_node,alarm_per_add
  alarm_per_add=alarm_per_add+5
  if alarm_per_add>=alarm_time_per:
	alarm_per_add=0
	if alarm_flash_node==0:
	  alarm_pin.freq(sound_freq1+1)
	  alarm_flash_node=1
	else:
	  alarm_flash_node=0
	  alarm_pin.freq(sound_freq2+1)

def alarm(alarm_per,s_freq,s_freq2):
  global sound_freq1,sound_freq2,alarm_time_per
  sound_freq1=s_freq;sound_freq2=s_freq2
  if alarm_per==0:
	alarm_pin.freq(1)
	alarm_pin.duty(0)
	alarm_time_per=0
  else:
	alarm_time_per=alarm_per
	alarm_pin.duty(50)
	
def start_ring():
  alarm(10,100,100)
  time.sleep(0.15)
  alarm(10,300,300)
  time.sleep(0.15)
  alarm(10,400,400)
  time.sleep(0.15)
  alarm(10,600,600)
  time.sleep(0.15)
  alarm(10,800,800)
  time.sleep(0.15)
  alarm(0,0,0)
  time.sleep(1)
#======警告======

#=============一些中间或初始变量=============
t=0
init_x=0;init_y=-110
ges_x_1=0;ges_x_2=0;ges_x_3=0;ges_x_4=0
ges_y_1=init_y;ges_y_2=init_y;ges_y_3=init_y;ges_y_4=init_y
x1=0;x2=0;x3=0;x4=0;y1=0;y2=0;y3=0;y4=0;
PIT_S=0;ROL_S=0;X_S=0;PIT_goal=0;ROL_goal=0;X_goal=in_y
spd=0;spd_goal=0;L=0;R=0
R_H=abs(init_y);H_goal=110
init_case=0
key_stab=False;gait_mode=0
stop_run_node=0
speed_init=speed
acc_z=0
IK_ERROR=0;normal_node=0;error_node=0
pit_max_ang=25	 #设定俯仰轴最大限制角度
rol_max_ang=20	 #设定滚转轴最大限制角度
Kp_V=1		   #速度变化P环
act_tran_mov_kp=tran_mov_kp
def mechan_offset_corr(x):
  p1=0.006649
  p2=0.4414
  p3=5.53
  return p1*x*x+p2*x+p3

  
def servo_output(case,init,ham1,ham2,ham3,ham4,shank1,shank2,shank3,shank4):
  if case==0 and init==0:
	#腿1
	PA_SERVO.angle(1, init_1h+90-ham1)	# 腿1大腿
	PA_SERVO.angle(2, (init_1s-90)+mechan_offset_corr(shank1))	# 腿1小腿
	#腿2
	PA_SERVO.angle(3, init_2h-90+ham2)	# 腿2大腿
	PA_SERVO.angle(4, (init_2s+90)-mechan_offset_corr(shank2))	# 腿2小腿
	#腿3
	PA_SERVO.angle(5, init_3h-90+ham3)	# 腿3大腿
	PA_SERVO.angle(6, (init_3s+90)-mechan_offset_corr(shank3))	# 腿3小腿
	#腿4
	PA_SERVO.angle(7, init_4h+90-ham4)	# 腿4大腿
	PA_SERVO.angle(8, (init_4s-90)+mechan_offset_corr(shank4))	# 腿4小腿
  else:
	#腿1
	PA_SERVO.angle(1, init_1h)	# 腿1大腿
	PA_SERVO.angle(2, init_1s)	# 腿1小腿
	#腿2
	PA_SERVO.angle(3, init_2h)	# 腿2大腿
	PA_SERVO.angle(4, init_2s)	# 腿2小腿
	#腿3
	PA_SERVO.angle(5, init_3h)	# 腿3大腿
	PA_SERVO.angle(6, init_3s)	# 腿3小腿
	#腿4
	PA_SERVO.angle(7, init_4h)	# 腿4大腿
	PA_SERVO.angle(8, init_4s)	# 腿4小腿


def height(goal):	 #高度调节函数
	global H_goal
	H_goal=goal

def gesture(PIT,ROL,X):
	global PIT_goal,ROL_goal,X_goal
	PIT_goal=PIT
	ROL_goal=ROL
	X_goal=X

def move(spd_,L_,R_):
	global spd_goal,L,R
	spd_goal=spd_;L=L_;R=R_
  
def stable(key):
	global key_stab,speed
	key_stab=key
	if key==True:
	  speed=speed_init+0.01	  #补偿开陀螺仪造成的速度突变
	else:
	  speed=speed_init	 #补偿开陀螺仪造成的速度突变
  
def servo_init(key):
	global init_case
	init_case=key
	
def gait(mode):	  #设置步态
	global gait_mode
	gait_mode=mode
 
def state(mode):   #设置状态
    global stop_run_node
    stop_run_node=mode 
    if mode==1:
        alarm(0,0,0)
        PA_SERVO.release()

def swing_curve_generate(t,Tf,xt,zh,x0,z0,xv0):
  #输入参数：当前时间；支撑相占空比；x方向目标位置，z方向抬腿高度，摆动相抬腿前腿速度
  # X Generator
  if t>=0 and t<Tf/4:
	xf=(-4*xv0/Tf)*t*t+xv0*t+x0
	
  if t>=Tf/4 and t<(3*Tf)/4:
	xf=((-4*Tf*xv0-16*xt+16*x0)*t*t*t)/(Tf*Tf*Tf)+((7*Tf*xv0+24*xt-24*x0)*t*t)/(Tf*Tf)+((-15*Tf*xv0-36*xt+36*x0)*t)/(4*Tf)+(9*Tf*xv0+16*xt)/(16)
	
  if t>(3*Tf)/4:
	xf=xt

  # Z Generator
  if t>=0 and t<Tf/2:
	zf=(16*z0-16*zh)*t*t*t/(Tf*Tf*Tf)+(12*zh-12*z0)*t*t/(Tf*Tf)+z0
  
  if t>=Tf/2:
	zf=(4*z0-4*zh)*t*t/(Tf*Tf)-(4*z0-4*zh)*t/(Tf)+z0
	  
  #Record touch down position
  x_past=xf
  t_past=t
  
  # # Avoid zf to go zero
  if zf<=0:
	zf=0
  #x,z position,x_axis stop point,t_stop point;depend on when the leg stop
  
  return xf,zf,x_past,t_past


def support_curve_generate(t,Tf,x_past,t_past,zf):
  # 当前时间；支撑相占空比；摆动相 x 最终位;t最终时间，支撑相 zf
  # Only X Generator
  average=x_past/(1-Tf)
  xf=x_past-average*(t-t_past)
  return xf,zf
  
def alarm_and_servo_control():
  global normal_node,error_node
  judge_num_node=0

  if IK_ERROR==1:
	judge_num_node=judge_num_node+1
  #IK_ERROR ALARM
  if IK_ERROR==1 and error_node==0:
	alarm(300,100,0)
	error_node=1
	normal_node=0
	print("逆解算错误，检查运动是否超限，为保护舵机，舵机电源已急停")
  if IK_ERROR==0 and normal_node==0:   #Focus on Clear to Zero
	alarm(0,0,0)
	error_node=0
	normal_node=1
  return judge_num_node
	  
def mainloop():
  global t
  global R_H
  global PIT_S,ROL_S,X_S,act_tran_mov_kp,PIT_goal,ROL_goal,spd
  global ges_x_1,ges_x_2,ges_x_3,ges_x_4
  global ges_y_1,ges_y_2,ges_y_3,ges_y_4
  global IK_ERROR
  #Servo ON/OFF CONTROL
  if not (alarm_and_servo_control()==0):
	#print("PA_SERVO.release",alarm_and_servo_control())
	PA_SERVO.release()

  #锁定(因为摇晃身体做动作)
  if stop_run_node==1:
	return 0
  #判断步态模式
  if gait_mode==0:
	act_tran_mov_kp=tran_mov_kp
	if t>=1:#一个完整的运动周期结束 trot
	  t=0
	elif L==0 and R==0:
	  t=0
	else:
	 t=t+speed
	P_=PA_GAIT.trot(t,spd*10,h,L,L,R,R)
  elif gait_mode==1:
	act_tran_mov_kp=tran_mov_kp/2	#Walk Gait Slow down X_S change
	P_=PA_GAIT.walk(t,spd*10,h,L,L,R,R)
	if t>=2.5:
	  t=0
	elif L==0 and R==0:
	  t=0
	else:
	  pass
		
  #速度调节器
  if spd>spd_goal:
	spd=spd-abs(spd-spd_goal)*Kp_V
  elif spd<spd_goal:
	spd=spd+abs(spd-spd_goal)*Kp_V
  #高度调节器
  if R_H>H_goal:
	R_H=R_H-abs(R_H-H_goal)*Kp_H
  elif R_H<H_goal:
	R_H=R_H+abs(R_H-H_goal)*Kp_H
  
  if key_stab!=True:	 #自稳时屏蔽
	if PIT_S>PIT_goal:	 #俯仰
	  PIT_S=PIT_S-abs(PIT_S-PIT_goal)*pit_Kp_G
	elif PIT_S<PIT_goal:
	  PIT_S=PIT_S+abs(PIT_S-PIT_goal)*pit_Kp_G

	if ROL_S>ROL_goal:	 #滚转
	  ROL_S=ROL_S-abs(ROL_S-ROL_goal)*rol_Kp_G
	elif ROL_S<ROL_goal:
	  ROL_S=ROL_S+abs(ROL_S-ROL_goal)*rol_Kp_G
  else:
	PIT_S=PIT_goal
	ROL_S=ROL_goal
	#X_S=X_goal

  if X_S>X_goal:   #X位置
	X_S=X_S-abs(X_S-X_goal)*act_tran_mov_kp
  elif X_S<X_goal:
	X_S=X_S+abs(X_S-X_goal)*act_tran_mov_kp

  #姿态角度限位  
  if PIT_S>=pit_max_ang:PIT_S=pit_max_ang
  if PIT_S<=-pit_max_ang:PIT_S=-pit_max_ang
  if ROL_S>=rol_max_ang:ROL_S=rol_max_ang
  if ROL_S<=-rol_max_ang:ROL_S=-rol_max_ang

  #TROT模态根据迈腿长度自动调节重心
  if gait_mode==0:
	if spd>=0 and (L+R)!=0:
	  P_G=PA_ATTITUDE.cal_ges(PIT_S,ROL_S,l,b,w,X_S+abs(spd)*trot_cg_f,R_H)
	elif spd<0 and (L+R)!=0:
	  P_G=PA_ATTITUDE.cal_ges(PIT_S,ROL_S,l,b,w,X_S-abs(spd)*trot_cg_b,R_H)
	elif (L+R)==0:	  #原地旋转
	  P_G=PA_ATTITUDE.cal_ges(PIT_S,ROL_S,l,b,w,X_S+abs(spd)*trot_cg_t,R_H)
  else:
	P_G=PA_ATTITUDE.cal_ges(PIT_S,ROL_S,l,b,w,X_S,R_H)
  ges_x_1=P_G[0];ges_x_2=P_G[1]; ges_x_3=P_G[2]; ges_x_4=P_G[3];ges_y_1=P_G[4];ges_y_2=P_G[5]; ges_y_3=P_G[6]; ges_y_4=P_G[7]
  #自稳调节器(只静态稳定)
  #
  if key_stab==True:
	if abs(0-spd)<=0.1 and L==0 and R==0:
	  PA_STABLIZE.stab()
	else:	#进入TROT模式
	  PIT_goal=0
	  ROL_goal=0
  #作动
  try:
	A_=PA_IK.ik(ma_case,l1,l2,P_[0]+ges_x_1,P_[1]+ges_x_2,P_[2]+ges_x_3,P_[3]+ges_x_4,P_[4]+ges_y_1,P_[5]+ges_y_2,P_[6]+ges_y_3,P_[7]+ges_y_4)
	servo_output(ma_case,init_case,A_[0],A_[1],A_[2],A_[3],A_[4],A_[5],A_[6],A_[7])
	IK_ERROR=0
  except:
	IK_ERROR=1
#print("Py-apple V7.2 通用控制器 by 灯哥 20210723 ESP32)")
#print("开源协议:Apache License 2.0")
#print("作者邮件:ream_d@yeah.net")
def loop(x):
	mainloop()
	alarm_run()
	
start_ring()
tim0 =Timer(Timer.TIMER2,Timer.CHANNEL0,mode=Timer.MODE_PERIODIC,period = 20, callback = loop)










