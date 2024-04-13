
import board
from time import sleep
from machine import UART

import _thread
from struct import pack, unpack
from random import randint

def pyLink_pack(fun,buff):

    pack_data = bytearray([0xBB,0x00,fun])#包头
    pack_data.extend(buff)#数据包
    pack_data[1] = len(pack_data)-2;#有效数据个数

    sum = 0
    for temp in pack_data:
        sum = sum + temp

    pack_data.extend(pack('<B', sum%256))#和校验

    return pack_data

def getDirNum(dir):
    dirNum = 0
    if dir=="前":
        dirNum = 1
    elif dir=="后":
        dirNum = 2
    elif dir=="左":
        dirNum = 3
    elif dir=="右":
        dirNum = 4
    elif dir=="上":
        dirNum = 5
    elif dir=="下":
        dirNum = 6
    if dir=="左上":
        dirNum = 7
    elif dir=="右上":
        dirNum = 8
    elif dir=="左下":
        dirNum = 9
    elif dir=="右下":
        dirNum = 10
    return dirNum

#传感器数据结构体
class sensor(object):
    id = 0
    vol = 0
    ssi = 0
    state = 0
    mv_flag = 0
    mv_tagId = 0
    obs_dist = [0,0,0,0]
    imu = [0,0,0]
    loc = [0,0,0]
    locErr = [0,0,0]
    ai_id = 0
    
    laserTarget_count = 0
    laserTarget_result = 0
    laserTarget_x = 0 
    laserTarget_y = 0 
    scale_weight = 0 
    
    newsCount = 0
    newsLen = 0
    news = ""

#协议接收结构体
class receive(object):
    head = 0
    len = 0
    date = []
    cnt = 0
    state = 0
    fps = 0
    fpsCnt = 0

class fly():

    #初始化
    def __init__(self,speakEnable=False):

        self.speakEn = speakEnable

        if self.speakEn:
            try:
                import pyttsx3
                self.engine = pyttsx3.init() #初始化语音引擎
                self.engine.setProperty('rate', 200)   #设置语速
                self.engine.setProperty('volume',1.0)  #设置音量
                self.engine.setProperty('voice',self.engine.getProperty('voices')[0].id)   #设置第一个语音合成器
                
            except Exception as e:

                print("语音引擎加载失败：", e)
                self.speakEn = False

        self.maxNum = 10 #最多支持maxNum台飞机
        self.flySensor = []
        self.rx = receive()
        self.count = randint(0,255)

        for i in range(self.maxNum):
            self.flySensor.append(sensor()) 

        #串口初始化
        board.register(1,board.FPIOA.UART1_TX)
        board.register(2,board.FPIOA.UART1_RX)
        self.usart=UART(UART.UART1, 500000, timeout=1000, read_buf_len=4096)

        #运行数据接收线程
        _thread.start_new_thread(self.Receive_Thread, ())
        _thread.start_new_thread(self.Loop_1Hz_Thread, ())

    #语音播报
    def speak(self,string):
        print(string)
        if self.speakEn:
            self.engine.say(string)
            self.engine.runAndWait()
            self.engine.stop()

    #发送指令数据包
    def sendOrder(self,id,cmd,fmt,*args):

        self.count = self.count + 1
        buff = bytearray([id,cmd,self.count%256])
        buff = buff + pack(fmt,*args)
        dLen = 13 - len(buff)
        if(dLen>0):
            buff.extend(bytearray(dLen))

        self.usart.write(pyLink_pack(0xF3,buff+buff))

    #发送指令数据包
    def sendOrderPack(self,id,cmd,pack):

        self.count = self.count + 1
        buff = bytearray([id,cmd,self.count%256])
        buff = buff + pack
        dLen = 13 - len(buff)
        if(dLen>0):
            buff.extend(bytearray(dLen))

        self.usart.write(pyLink_pack(0xF3,buff+buff))

    #串口数据解析
    def Receive_Anl(self):

        #和校验
        sum = 0
        sum = self.rx.head + self.rx.len
        for temp in self.rx.date:
            sum = sum + temp

        sum = (sum-self.rx.date[self.rx.len])%256 #求余

        if sum != self.rx.date[self.rx.len]:
            return
        
        self.rx.fpsCnt = self.rx.fpsCnt + 1
        
        #和校验通过
        if self.rx.date[0]==0x01:

            pack = unpack('<3BHBH4B6h3bB', bytearray(self.rx.date)[1:self.rx.len]) #从第1字节开始解析
            
            id = pack[0]
            
            if id<self.maxNum:
            
                self.flySensor[id].id = pack[0]
                self.flySensor[id].vol = pack[1]*0.1
                self.flySensor[id].ssi = pack[2]
                self.flySensor[id].state = pack[3]
                self.flySensor[id].mv_flag = pack[4]
                self.flySensor[id].mv_tagId = pack[5]
                self.flySensor[id].obs_dist = [pack[6],pack[7],pack[8],pack[9]]
                self.flySensor[id].imu = [pack[10]*0.1,pack[11]*0.1,pack[12]*0.1]
                self.flySensor[id].loc = [pack[13],pack[14],pack[15]]
                self.flySensor[id].locErr = [pack[16],pack[17],pack[18]]
                self.flySensor[id].ai_id = pack[19]
                
        elif self.rx.date[0]==0x02:

            pack = unpack('<4B2h4Bf', bytearray(self.rx.date)[1:self.rx.len]) #从第1字节开始解析，跳过fun
            
            id = pack[0]
            
            if id<self.maxNum:
            
                self.flySensor[id].id = pack[0]
                self.flySensor[id].ssi = pack[1]
                self.flySensor[id].laserTarget_count = pack[2]
                self.flySensor[id].laserTarget_result = pack[3]
                self.flySensor[id].laserTarget_x = pack[4]
                self.flySensor[id].laserTarget_y = pack[5]
                self.flySensor[id].obs_dist = [pack[6],pack[7],pack[8],pack[9]]
                self.flySensor[id].scale_weight = pack[10]
                
        elif self.rx.date[0]==0xF6:

            pack = unpack('<3B', bytearray(self.rx.date)[1:4]) #从第1字节开始解析，跳过fun
            
            id = pack[0]
            if self.flySensor[id].newsCount == pack[1]:
                return;
            
            if id<self.maxNum:
            
                self.flySensor[id].id = pack[0]
                self.flySensor[id].newsCount = pack[1]
                self.flySensor[id].newsLen = pack[2]
                self.flySensor[id].news = bytearray(self.rx.date)[4:(4+pack[2])].decode("utf-8")
                print(str(id)+"号消息："+self.flySensor[id].news)

    #串口通信协议接收
    def Receive_Prepare(self,data):

        if self.rx.state==0:#header

            if data == 0xAA:
                self.rx.state = 1
                self.rx.head = data

        elif self.rx.state==1:#len

            if data>0 and data<30:
                self.rx.state = 2
                self.rx.len = data
                self.rx.cnt = 0
            else:
                self.rx.state = 0

        elif self.rx.state==2:#date[]

            self.rx.date.append(data)
            self.rx.cnt = self.rx.cnt + 1
            if self.rx.cnt>=self.rx.len:
                self.rx.state = 3

        elif self.rx.state==3:#sum

            self.rx.state = 0
            self.rx.date.append(data)
            self.Receive_Anl()#接收完毕处理数据
            self.rx.date=[]#清空缓冲区，准备下次接收数据

        else:
            self.rx.state = 0

    #数据接收线程
    def Receive_Thread(self):
        
        while True:

            temp = self.usart.read(self.usart.any())
            size = len(temp)

            for i in range(size):
                self.Receive_Prepare(temp[i])

            sleep(0.01)
        
    #统计接收帧率线程
    def Loop_1Hz_Thread(self):

        while True:

            self.rx.fps = self.rx.fpsCnt;
            self.rx.fpsCnt = 0
            sleep(1)

    '''以下是发送部分'''

    # __号起飞__厘米
    def takeOff(self,id,high):

        self.sendOrder(id,0,'<h2B2h',high,50,0,0,0)
        self.speak(str(id)+"号起飞"+str(high)+"厘米")

    # __号__(0降落1刹车2悬停3急停4校准)
    def flyCtrl(self,id,mode):

        modeNum = 0

        if mode=="降落":
            modeNum = 0
        elif mode=="刹车":
            modeNum = 1
        elif mode=="悬停":
            modeNum = 2
        elif mode=="急停":
            modeNum = 3
        elif mode=="校准":
            modeNum = 4

        self.sendOrder(id,0xFE,'<B',modeNum)
        self.speak(str(id)+"号"+mode)

    # __号切换为__模式(0光流定位1标签定位2自主巡线)
    def flyMode(self,id,mode):

        modeNnm = 0
        if mode=="光流定位":
            modeNnm = 0
        elif mode=="标签定位":
            modeNnm = 1
        elif mode=="自主巡线":
            modeNnm = 2

        self.sendOrder(id,1,'<B',modeNnm)
        self.speak(str(id)+"号切换为"+mode+"模式")

    # __号水平速度__厘米/秒
    def xySpeed(self,id,speed):

        self.sendOrder(id,2,'<h',speed)
        self.speak(str(id)+"号水平速度"+str(speed)+"厘米每秒")

    # __号垂直速度__厘米/秒
    def zSpeed(self,id,speed):

        self.sendOrder(id,3,'<h',speed)
        self.speak(str(id)+"号垂直速度"+str(speed)+"厘米每秒")

    # __号从__位置移动(__,__,__)
    def move(self,id,mode,distance):

        modeNnm = 1
        if mode=="当前":
            modeNnm = 0
        elif mode=="目标":
            modeNnm = 1
            
        self.sendOrder(id,29,'<B3h',modeNnm,distance[0],distance[1],distance[2])
        self.speak(str(id)+"号从"+mode+"位置移动"+"("+str(distance[0])+","+str(distance[1])+","+str(distance[2])+")")
        
    # __号向__飞__厘米
    def moveCtrl(self,id,dir,distance):

        dirNum = getDirNum(dir)
        if dirNum>6:
            distance = int(distance*0.7071)
        self.sendOrder(id,5,'<Bh',dirNum,distance)
        self.speak(str(id)+"号向"+dir+"飞"+str(distance)+"厘米")

    # __号向__飞__厘米，寻找黑色色块
    def moveSearchDot(self,id,dir,distance):

        dirNum = getDirNum(dir)
        if dirNum>6:
            distance = int(distance*0.7071)
        self.sendOrder(id,6,'<Bh',dirNum,distance)
        self.speak(str(id)+"号向"+dir+"飞"+str(distance)+"厘米,寻找黑色色块")

    # __号向__飞__厘米，寻找色块__
    def moveSearchBlob(self,id,dir,distance,blob):

        dirNum = getDirNum(dir)
        if dirNum>6:
            distance = int(distance*0.7071)
        self.sendOrder(id,8,'<Bh6b',dirNum,distance,blob[0],blob[1],blob[2],blob[3],blob[4],blob[5])
        self.speak(str(id)+"号向"+dir+"飞"+str(distance)+"厘米,寻找色块"+str(blob))

    # __号向__飞__厘米，寻找__号标签
    def moveSearchTag(self,id,dir,distance,tagID):

        dirNum = getDirNum(dir)
        if dirNum>6:
            distance = int(distance*0.7071)
        self.sendOrder(id,7,'<Bhh',dirNum,distance,tagID)
        self.speak(str(id)+"号向"+dir+"飞"+str(distance)+"厘米,寻找"+str(tagID)+"号标签")

    # __号向__飞__厘米，跟随__号标签
    def moveFollowTag(self,id,dir,distance,tagID):

        dirNum = getDirNum(dir)
        if dirNum>6:
            distance = int(distance*0.7071)
        self.sendOrder(id,26,'<Bhh',dirNum,distance,tagID)
        self.speak(str(id)+"号向"+dir+"飞"+str(distance)+"厘米,跟随"+str(tagID)+"号标签")

    # __号直达(__,__,__)
    def goTo(self,id,coordinate):

        self.sendOrder(id,9,'<3h',coordinate[0],coordinate[1],coordinate[2])
        self.speak(str(id)+"号直达("+str(coordinate[0])+"、"+str(coordinate[1])+"、"+str(coordinate[2])+")")

    # __号直达__号标签
    def goToTag(self,id,tagID,high):

        self.sendOrder(id,28,'<2h',tagID,high)
        self.speak(str(id)+"号直达"+str(tagID)+"号标签，高度"+str(high)+"厘米")

    # __号旋转__度
    def rotation(self,id,angle):

        self.sendOrder(id,10,'<h',angle)
        if angle<0:
            self.speak(str(id)+"号逆时针旋转"+str(-angle)+"度")
        else:
            self.speak(str(id)+"号顺时针旋转"+str(angle)+"度")

    # __号高度__厘米
    def flyHigh(self,id,high):

        self.sendOrder(id,11,'<h',high)
        self.speak(str(id)+"号高度"+str(high)+"厘米")

    # __号向__翻滚__圈
    def flipCtrl(self,id,dir,cir):
        
        dirNum = getDirNum(dir)
        if dirNum>0 and dirNum<5:
            self.sendOrder(id,12,'<2B',dirNum,cir)
            self.speak(str(id)+"号向"+dir+"翻滚"+str(cir)+"圈")
        else:
            self.speak("翻滚方向参数错误")

    # __号灯光(__,__)
    def ledCtrl(self,id,mode,rgb):

        modeNum = 0;

        if mode=="常亮":
            modeNum = 0
        elif mode=="呼吸灯":
            modeNum = 1
        elif mode=="七彩变幻":
            modeNum = 2

        self.sendOrder(id,13,'<4B',modeNum,rgb[0],rgb[1],rgb[2])
        self.speak(str(id)+"号灯光"+mode)

    # __号关闭灯光
    def closeLed(self,id):

        self.sendOrder(id,13,'<4B',0,0,0,0)
        self.speak(str(id)+"号关闭灯光")

    # __号检测__
    def mvCheckMode(self,id,mode):

        modeNum = 3
        if mode == "黑点":
            modeNum = 1
        elif mode == "黑线":
            modeNum = 2
        elif mode == "标签":
            modeNum = 3

        self.sendOrder(id,14,'<B6bh',modeNum,0,0,0,0,0,0,0)
        self.speak(str(id)+"号检测"+mode)

    # __号检测__号标签
    def mvCheckAprilTag(self,id,tagID):

        self.sendOrder(id,14,'<B6bh',7,0,0,0,0,0,0,tagID)
        self.speak(str(id)+"号检测"+str(tagID)+"号标签")

    # __号检测色块(__,__,__,__,__,__,)
    def mvCheckBlob(self,id,blob):

        self.sendOrder(id,14,'<B6bh',6,blob[0],blob[1],blob[2],blob[3],blob[4],blob[5],0)
        self.speak(str(id)+"号检测色块")

    # __号__回传
    def photographMode(self,id,mode):

        modeNum = 1
        if mode == "拍照":
            modeNum = 1
        elif mode == "颜色采样":
            modeNum = 2
        elif mode == "颜色识别":
            modeNum = 3

        self.sendOrder(id,27,'<B',modeNum)
        self.speak(str(id)+"号"+mode+"回传")

    # __号__发射激光
    def shootCtrl(self,id,mode):

        modeNum = 0
        if mode == "单次":
            modeNum = 0
        elif mode == "连续":
            modeNum = 1
        elif mode == "停止":
            modeNum = 2

        self.sendOrder(id,19,'<B',modeNum)
        self.speak(str(id)+"号"+mode+"发射激光")

    # __号__电磁铁
    def magnetCtrl(self,id,mode):

        modeNum = 0
        if mode == "关闭":
            modeNum = 0
        elif mode == "打开":
            modeNum = 1

        self.sendOrder(id,15,'<B',modeNum)
        self.speak(str(id)+"号"+mode+"电磁铁")

    # __号舵机__度
    def servoCtrl(self,id,angle):

        self.sendOrder(id,16,'<B',angle)
        self.speak(str(id)+"号舵机"+str(angle)+"度")

    # __号__机头方向
    def lockDir(self,id,mode):

        modeNum = 1
        if mode == "锁定":
            modeNum = 0
        elif mode == "解锁":
            modeNum = 1

        self.sendOrder(id,18,'<B',modeNum)
        self.speak(str(id)+"号"+mode+"机头方向")

    # __号发送__
    def roleCtrl(self,id,string):

        strBuf = string.encode("utf-8")
        strLen = len(strBuf)

        if strLen<11:
            self.sendOrderPack(id,17,strBuf)
            self.speak(str(id)+"号发送"+string)
        else:
            self.speak("字符超过10字节")

    '''以下是回传部分'''

    #检测到__
    def getMvCheak(self,id,mode):

        if mode=="黑点" or mode=="色块" :
            return self.flySensor[id].mv_flag&(1<<5)
        elif mode == "标签":
            return self.flySensor[id].mv_flag&(1<<4)

    #检测到__边有线
    def getMvCheakLine(self,id,dir):

        if dir == "前":
            return self.flySensor[id].mv_flag&(1<<0)
        elif dir == "后":
            return self.flySensor[id].mv_flag&(1<<1)
        elif dir == "左":
            return self.flySensor[id].mv_flag&(1<<2)
        elif dir == "右":
            return self.flySensor[id].mv_flag&(1<<3)

    #__障碍物的距离
    def getObsDistance(self,id,dir):

        if dir == "前":
            return self.flySensor[id].obs_dist[0]
        elif dir == "后":
            return self.flySensor[id].obs_dist[1]
        elif dir == "左":
            return self.flySensor[id].obs_dist[2]
        elif dir == "右":
            return self.flySensor[id].obs_dist[3]

    #__
    def getFlySensor(self,id,type):

        if type == "标签号":
            return self.flySensor[id].mv_tagId
        elif type == "横滚角":
            return self.flySensor[id].imu[0]
        elif type == "俯仰角":
            return self.flySensor[id].imu[1]
        elif type == "偏航角":
            return self.flySensor[id].imu[2]
        elif type == "横坐标":
            return self.flySensor[id].loc[0]
        elif type == "纵坐标":
            return self.flySensor[id].loc[1]
        elif type == "高度":
            return self.flySensor[id].loc[2]
        elif type == "横轴误差":
            return self.flySensor[id].locErr[0]
        elif type == "纵轴误差":
            return self.flySensor[id].locErr[1]
        elif type == "高度误差":
            return self.flySensor[id].locErr[2]
        elif type == "电压":
            return self.flySensor[id].vol

    #消息__
    def getRoleNews(self,id,type):

        if type=="内容":
            return self.flySensor[id].news
        elif type=="序号":
            return self.flySensor[id].newsCount


    #清除消息
    def clearRoleNews(self,id):

        self.flySensor[id].news = ""
