import time
config_py = '''
init_1h=90
init_1s=90
init_2h=90
init_2s=90
init_3h=90
init_3s=90
init_4h=90
init_4s=90
l1=80           #大腿（杆1）长
l2=69           #小腿（杆2）长
l=142           #机器人长度
b=92.8          #机器人宽度
w=108           #机器人腿间距
speed=0.05      #步频
h=30            #抬腿高度
Kp_H=0.06       #高度调节P环
pit_Kp_G=0.04   #俯仰姿态P环
pit_Kd_G=0.6    #俯仰姿态D环
rol_Kp_G=0.04   #俯仰姿态P环
rol_Kd_G=0.35   #俯仰姿态D环
tran_mov_kp=0.1 #平移姿态P环
ma_case=0
trot_cg_f=4     #TROT前进重心调节P
trot_cg_b=4     #TROT后退重心调节P
trot_cg_t=2     #TROT转向重心调节P
in_y=17
'''
import os

flash_ls = os.listdir()
if not "config_s.py" in flash_ls:
	print("No profile found, add profile")
	f = open("config_s.py", "wb")
	f.write(config_py)
	f.close()
del config_py
time.sleep(1)


import padog

def spk_alarm():
	for i in range(3):
		padog.alarm(10,100,100)
		time.sleep(0.15)
		padog.alarm(10,300,300)
		time.sleep(0.15)
	padog.alarm(0,0,0)

def servo_config():
	print("请打开串口监视器，进行对舵机标定(输入调整误差值，使外壳中线对准)")
	padog.servo_init(1)	 #舵机进去标定状态

	init_1h=None
	while not (init_1h=="ok"):
	
		init_1h=input("腿1_大腿-标定:")
		spk_alarm()
		try:
			if -20< int(init_1h) < 20:
				padog.init_1h=padog.init_1h+int(init_1h)
			else:
				print("请输入正确数值范围(-20~20)\n")
		except:
			if init_1h=='ok':
				print("进入下一项--------- \n")
			else:
				print("请输入正确数(如'1','-1')或完成'ok'")
				
	

	init_1s=None
	while not (init_1s=="ok"):
		
		init_1s=input("腿1_小腿-标定:")
		spk_alarm()
		try:
			if -20 < int(init_1s) < 20:
				padog.init_1s=padog.init_1s+int(init_1s)
			else:
				print("请输入正确数值范围(-20~20)\n")
		except:
			if init_1s=='ok':
				print("进入下一项--------- \n")
			else:
				print("请输入正确数(如'1','-1')或完成'ok'")		

	init_2h=None
	while not (init_2h=="ok"):
		
		init_2h=input("腿2_大腿-标定:")
		spk_alarm()
		try:
			if -20 < int(init_2h) < 20:
				padog.init_2h=padog.init_2h+int(init_2h)
			else:
				print("请输入正确数值范围(-20~20)\n")
		except:
			if init_2h=='ok':
				print("进入下一项--------- \n")
			else:
				print("请输入正确数(如'1','-1')或完成'ok'")

	init_2s=None
	while not (init_2s=="ok"):
		
		init_2s=input("腿2_小腿-标定:")
		spk_alarm()
		try:
			if -20 < int(init_2s) < 20:
				padog.init_2s=padog.init_2s+int(init_2s)
			else:
				print("请输入正确数值范围(-20~20)\n")				
		except:
			if init_2s=='ok':
				print("进入下一项--------- \n")
			else:
				print("请输入正确数(如'1','-1')或完成'ok'")	   

	init_3h=None
	while not (init_3h=="ok"):
		
		init_3h=input("腿3_大腿-标定:")
		spk_alarm()
		try:
			if -20 < int(init_3h) < 20:
				padog.init_3h=padog.init_3h+int(init_3h)
			else:
				print("请输入正确数值范围(-20~20)\n")				 
		except:
			if init_3h=='ok':
				print("进入下一项--------- \n")
			else:
				print("请输入正确数(如'1','-1')或完成'ok'")
				
	init_3s=None
	while not (init_3s=="ok"):
		
		init_3s=input("腿3_小腿-标定:")
		spk_alarm()
		try:
			if -20 < int(init_3s) < 20:
				padog.init_3s=padog.init_3s+int(init_3s)
			else:
				print("请输入正确数值范围(-20~20)\n")				  
		except:
			if init_3s=='ok':
				print("进入下一项--------- \n")
			else:
				print("请输入正确数(如'1','-1')或完成'ok'")
		
	init_4h=None
	while not (init_4h=="ok"):
		
		init_4h=input("腿4_大腿-标定:")
		spk_alarm()
		try:
			if -20 < int(init_4h) < 20:
				padog.init_4h=padog.init_4h+int(init_4h)
			else:
				print("请输入正确数值范围(-20~20)\n")				  
		except:
			if init_4h=='ok':
				print("进入下一项--------- \n")
			else:
				print("请输入正确数(如'1','-1')或完成'ok'")

	init_4s=None
	while not (init_4s=="ok"):
		
		init_4s=input("腿4_小腿-标定:")
		spk_alarm()
		try:
			if -20 < int(init_4s) < 20:
				padog.init_4s=padog.init_4s+int(init_4s)
			else:
				print("请输入正确数值范围(-20~20)\n")				  
		except:
			if init_4s=='ok':
				print("进入下一项--------- \n")
			else:
				print("请输入正确数(如'1','-1')或完成'ok'")
				
				
	print("舵机校准完成 ,请注意即将进入重心校准(输入'k'打开踏步，'g'关闭踏步) \n")	
	time.sleep(1)	
	padog.servo_init(0)
	time.sleep(2)	
	padog.gesture(0,0,padog.in_y)
	
	init_Yst=None
	while not (init_Yst=="ok"):
		
		init_Yst=input("重心-后前平移:")
		spk_alarm()
		try:
			if init_Yst=="k":
				padog.move(0,1,1)
			if init_Yst=="g":
				padog.move(0,0,0)
			if -40 < int(init_Yst) < 40:
				padog.X_goal=int(init_Yst)
			else:
				print("请输入正确数值范围(-40~40)\n")				  
				
		except:
			if init_Yst=='ok':
				print("将保存校准数据 \n")
			else:
				print("请输入正确数(如'1','-1')或完成'ok'")	
				
	padog.move(0,0,0)			
	time.sleep(1)
	
	s_f = open("config_s.py", "w+")
	#保存中位
	s_f.write("init_1h="+str(padog.init_1h)+"\n")
	s_f.write("init_1s="+str(padog.init_1s)+"\n")
	s_f.write("init_2h="+str(padog.init_2h)+"\n")
	s_f.write("init_2s="+str(padog.init_2s)+"\n")
	s_f.write("init_3h="+str(padog.init_3h)+"\n")
	s_f.write("init_3s="+str(padog.init_3s)+"\n")
	s_f.write("init_4h="+str(padog.init_4h)+"\n")
	s_f.write("init_4s="+str(padog.init_4s)+"\n")
	#保存机械、步态参数
	s_f.write("l1="+str(padog.l1)+"\n")
	s_f.write("l2="+str(padog.l2)+"\n")
	s_f.write("l="+str(padog.l)+"\n")
	s_f.write("b="+str(padog.b)+"\n")
	s_f.write("w="+str(padog.w)+"\n")
	s_f.write("speed="+str(padog.speed)+"\n")
	s_f.write("h="+str(padog.h)+"\n")
	s_f.write("Kp_H="+str(padog.Kp_H)+"\n")
	s_f.write("pit_Kp_G="+str(padog.pit_Kp_G)+"\n")
	s_f.write("pit_Kd_G="+str(padog.pit_Kd_G)+"\n")
	s_f.write("rol_Kp_G="+str(padog.rol_Kp_G)+"\n")
	s_f.write("rol_Kd_G="+str(padog.rol_Kd_G)+"\n")
	s_f.write("tran_mov_kp="+str(padog.tran_mov_kp)+"\n")
	s_f.write("ma_case="+str(padog.ma_case)+"\n")
	s_f.write("trot_cg_f="+str(padog.trot_cg_f)+"\n")
	s_f.write("trot_cg_b="+str(padog.trot_cg_b)+"\n")
	s_f.write("trot_cg_t="+str(padog.trot_cg_t)+"\n")
	#保存重心平移量
	s_f.write("in_y="+str(padog.X_goal)+"\n")
	s_f.close() 
	
	padog.start_ring() 
	print("保存成功，数据校准OK \n")
	