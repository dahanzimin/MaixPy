import time
import ustruct

class ASR3320:
 
    ASR_RESULT_ADDR = 100
    #识别结果存放处，通过不断读取此地址的值判断是否识别到语音，不同的值对应不同的语音

    ASR_WORDS_ERASE_ADDR = 101
    #擦除所有词条

    ASR_MODE_ADDR = 102
    #识别模式设置，值范围1~3
    #1：循环识别模式。状态灯常亮（默认模式）    
    #2：口令模式，以第一个词条为口令。状态灯常灭，当识别到口令词时常亮，等待识别到新的语音,并且读取识别结果后即灭掉
    #3：按键模式，按下开始识别，不按不识别。支持掉电保存。状态灯随按键按下而亮起，不按不亮

    ASR_ADD_WORDS_ADDR = 160
    #词条添加的地址，支持掉电保存

    def __init__(self, i2c, address=0x79):
        self.address = address
        self.i2c = i2c
       
    def getResult(self):     
		value = self.i2c.readfrom_mem(self.address,self.ASR_RESULT_ADDR,1)[0]
		if value==0:
			data=0
		else:	
			data = int(value)-48
		#print(data)
		return data
    '''
    * 添加词条函数，
    * idNum：词条对应的识别号，1~255随意设置。识别到该号码对应的词条语音时，
    *        会将识别号存放到ASR_RESULT_ADDR处，等待主机读取，读取后清0
    * words：要识别汉字词条的拼音，汉字之间用空格隔开
    * 
    * 执行该函数，词条是自动往后排队添加的。   
    '''
    def addWords(self, idNum, words):
		buf=str(idNum)+' '+str(words)
		self.i2c.writeto_mem(self.address, self.ASR_ADD_WORDS_ADDR, buf)
		time.sleep(0.05)
        
    def eraseWords(self):
        self.i2c.writeto_mem(self.address, self.ASR_WORDS_ERASE_ADDR, 0)
        time.sleep(0.1)

    
    def setMode(self, mode): 
        self.i2c.writeto_mem(self.address, self.ASR_MODE_ADDR, mode)

        