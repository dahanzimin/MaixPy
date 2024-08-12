import time

head=b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00'
link=b'\x07\x13\x00\x00\x00\x00\x00\x1B'
readflash=b'\x03\x16\x00\x1A'
readmould=b'\x03\x1D\x00\x21'
readindex=b'\x04\x1F\x00\x00\x24'
readindex1=b'\x04\x1F\x01\x00\x25'
cmd_search=b'\x03\x01\x00\x05'
cmd_upload=b'\x03\x0A\x00\x0E'
cmd_gen1=b'\x04\x02\x01\x00\x08'
cmd_gen2=b'\x04\x02\x02\x00\x09'
cmd_reg=b'\x03\x05\x00\x09'
cmd_save=b'\x06\x06\x01\x00'	#+存储地址+两字节校验(0xE+存储地址)
cmd_dis=b'\x08\x04\x01\x00\x00\x01\x2C\x00\x3B'

class AS608:
	def __init__(self,uart):
		self.uart = uart
		self.sendcmd(link)
		self.sendcmd(readflash)
		self.sendcmd(readmould)
		self.sendcmd(readindex)
		self.sendcmd(readindex1)
		time.sleep_ms(500)
		
	def	sendcmd(self,cmd):
		self.uart.write(head)
		self.uart.write(cmd)

	def	searchfig(self):
		hc=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.uart.read()
		self.sendcmd(cmd_search)
		while not self.uart.any():
			pass
		hc=self.uart.read()
		#print(hc,"---",hc[11])
		while hc[11]!=0xa:
			self.uart.read()
			self.sendcmd(cmd_search)
			while not self.uart.any():
				pass
			hc=self.uart.read()
			#print(hc,"***",hc[11])
			self.sendcmd(cmd_upload)
			time.sleep_ms(10)
			
			
	def	savefig(self,addr):
		print('编号{}：请按手指'.format(addr))
		self.searchfig()
		self.sendcmd(cmd_gen1)
		print('编号{}：请再按手指'.format(addr))
		self.searchfig()
		self.sendcmd(cmd_gen2)
		self.sendcmd(cmd_reg)
		add=cmd_save+bytearray([addr,0,addr+0xe])
		self.sendcmd(add)
		print('编号{}：指纹录入成功'.format(addr))
		
	def	disfig(self):
		print('请按手指')
		self.searchfig()
		print('识别中...')
		self.uart.read()
		time.sleep_ms(20)
		self.sendcmd(cmd_gen1)
		self.sendcmd(cmd_dis)
		time.sleep_ms(10)
		while not self.uart.any():
			pass
		hc=self.uart.read()
		#hc=self.uart.read()
		time.sleep_ms(10)
		if hc[9]==9:
			return 0
		else :
			return hc[11]