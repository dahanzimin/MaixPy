
import driver
from math import sqrt
from struct import pack, unpack
from random import randint

class order(object):
    takeOff=0
    flyMode=1
    xySpeed=2
    zSpeed=3
    followLine=4
    moveCtrl=5
    moveSearchDot=6
    moveSearchTag=7
    moveSearchBlob=8
    goTo=9
    rotation=10
    flyHigh=11
    flipCtrl=12
    ledCtrl=13
    mvMode=14
    magnetCtrl=15
    servoCtrl=16
    roleCtrl=17
    lockDir=18
    shootCtrl=19
    switchCtrl=20
    moveFollowTag=21
    photographMode=22
    goToTag=23
    move=24
    serServoCtrl=25
    robotArmCtrl=26
    robotArmRecord=27
    robotArmFree=28
    robotArmCover=29
    setLocation=30
    setTagDistance=31
    setCenterOffset=32
    cameraDeg=33
    showStr=34
    showCtrl=35
    irSend=36
    fmaInit=0xFD
    flyCtrl=0xFE
    nullCmd=0xFF

class fly():

    #初始化
    def __init__(self):

        self.maxNum = 10 #最多支持maxNum台飞机
        self.isDelay = True
        self.horSpeed = 100
        self.verSpeed = 100
        self.count = randint(0,255)

        self.port = driver.init(self.maxNum)
        self.timerStart = self.getTicks_sec()
        self.timeSec = [self.getTicks_sec() for _ in range(self.maxNum)]

        try:
            from myVoice import textToSpeed
            self.voice = textToSpeed() #语音播报

        except Exception as e:
            self.voice = False

    def getTicks_sec(self):

        return self.port.getSec()

    def getTimer(self):

        return self.getTicks_sec() - self.timerStart

    def clearTimer(self):

        self.timerStart = self.getTicks_sec()

    #显示文字
    def showText(self,id,string):

        nowTime = self.getTicks_sec()
        dT = (nowTime-self.timeSec[id])
        self.timeSec[id] = nowTime

        if self.port.type == "OpenMV":

            if dT>=0.1:
                print("---"+ ("%.1f" % dT) +"s")
            print(string)

        else:

            if dT>=0.1:
                print( '\33[1;34m' +"---"+ ("%.1f" % dT) +"s"  + '\33[0m')
            print( '\33[1;30m' + string + '\33[0m')

    def pyLink_pack(self,fun,buff):

        sum = 0

        pack_data = bytearray([0xBB,0x00,fun])#包头
        pack_data.extend(buff)#数据包
        pack_data[1] = len(pack_data)-2;#有效数据个数

        for temp in pack_data:
            sum = sum + temp

        pack_data.extend(pack('<B', sum%256))#和校验

        return pack_data

    #发送指令数据包
    def sendOrderPack(self,id,cmd,pack):

        self.count = self.count + 1
        buff = bytearray([id,cmd,self.count%256])
        buff = buff + pack
        dLen = 13 - len(buff)
        if(dLen>0):
            buff.extend(bytearray(dLen))

        self.port.write(self.pyLink_pack(0xF3,buff+buff+bytearray([100,0])))

    #发送指令数据包
    def sendOrder(self,id,cmd,fmt,*args):

        self.sendOrderPack(id,cmd,pack(fmt,*args))

    #延时(重要部分)
    def sleep(self,sec):
        self.port.run(sec)

    #设置自动延时
    def setAutoDelay(self,auto):
        self.isDelay = auto

    #语音播报
    def tts(self,string,wait=True):
        if self.voice:
            self.voice.speak(string,wait)
        else:
            print("语音播报："+string)

    #自动延时
    def moveDelay(self,id):

        if self.isDelay:
            self.sleep(1)
            dis = 100
            while dis>10:
                self.sleep(0.1)
                dx = self.port.flyData.flySensor[id].locErr[0]
                dy = self.port.flyData.flySensor[id].locErr[1]
                dz = self.port.flyData.flySensor[id].locErr[2]
                dis = sqrt(dx*dx+dy*dy+dz*dz)
            self.sleep(1)
        else:
            self.sleep(0.05)

    #自动延时
    def autoDelay(self,sec):

        if self.isDelay:
            self.sleep(sec)
        else:
            self.sleep(0.05)

    '''以下是发送部分'''

    # __号起飞__厘米
    def takeOff(self,id,high):

        high = int(high+0.5)#四舍五入取整
        self.sendOrder(id,order.takeOff,'<h2B2h',high,50,0,0,0)
        self.showText(id,"takeOff("+str(id)+","+str(high)+")")
        self.autoDelay(3+high/100)

    # __号__(0降落1刹车2悬停3急停4校准)
    def flyCtrl(self,id,mode):

        self.sendOrder(id,order.flyCtrl,'<B',mode)
        self.showText(id,"flyCtrl("+str(id)+","+str(mode)+")")
        self.autoDelay(3)

    # __号切换为__模式(0光流定位1标签定位2自主巡线)
    def flyMode(self,id,mode):

        self.sendOrder(id,order.flyMode,'<B',mode)
        self.showText(id,"flyMode("+str(id)+","+str(mode)+")")
        self.autoDelay(0.1)

    # __号水平速度__厘米/秒
    def xySpeed(self,id,speed):

        speed = int(speed+0.5)
        self.horSpeed = speed
        self.sendOrder(id,order.xySpeed,'<h',speed)
        self.showText(id,"xySpeed("+str(id)+","+str(speed)+")")
        self.autoDelay(0.1)

    # __号垂直速度__厘米/秒
    def zSpeed(self,id,speed):

        speed = int(speed+0.5)
        self.verSpeed = speed
        self.sendOrder(id,order.zSpeed,'<h',speed)
        self.showText(id,"zSpeed("+str(id)+","+str(speed)+")")
        self.autoDelay(0.1)

    # __号从__位置移动(__,__,__)
    def move(self,id,mode,loc):

        loc[0] = int(loc[0]+0.5)
        loc[1] = int(loc[1]+0.5)
        loc[2] = int(loc[2]+0.5)
        self.sendOrder(id,order.move,'<B3h',mode,int(loc[0]),int(loc[1]),int(loc[2]))
        self.showText(id,"move("+str(id)+","+str(mode)+",["+str(loc[0])+","+str(loc[1])+","+str(loc[2])+"])")
        self.moveDelay(id)

    # __号向__飞__厘米
    def moveCtrl(self,id,dir,distance):

        if dir>6:
            distance = int(distance*0.7071+0.5)
        else:
            distance = int(distance+0.5)
        self.sendOrder(id,order.moveCtrl,'<Bh',dir,distance)
        self.showText(id,"moveCtrl("+str(id)+","+str(dir)+","+str(distance)+")")
        self.moveDelay(id)

    # __号向__飞__厘米，寻找黑色色块
    def moveSearchDot(self,id,dir,distance):

        if dir>6:
            distance = int(distance*0.7071+0.5)
        else:
            distance = int(distance+0.5)
        self.sendOrder(id,order.moveSearchDot,'<Bh',dir,distance)
        self.showText(id,"moveSearchDot("+str(id)+","+str(dir)+","+str(distance)+")")
        self.moveDelay(id)

    # __号向__飞__厘米，寻找色块__
    def moveSearchBlob(self,id,dir,distance,blob):

        if dir>6:
            distance = int(distance*0.7071+0.5)
        else:
            distance = int(distance+0.5)
        self.sendOrder(id,order.moveSearchBlob,'<Bh6b',dir,distance,blob[0],blob[1],blob[2],blob[3],blob[4],blob[5])
        self.showText(id,"moveSearchDot("+str(id)+","+str(dir)+","+str(distance)+",["+str(blob[0])+","+str(blob[1])+","+str(blob[2])+","+str(blob[3])+","+str(blob[4])+","+str(blob[5])+"])")
        self.moveDelay(id)

    # __号向__飞__厘米，寻找__号标签
    def moveSearchTag(self,id,dir,distance,tagID):

        if dir>6:
            distance = int(distance*0.7071+0.5)
        else:
            distance = int(distance+0.5)
        self.sendOrder(id,order.moveSearchTag,'<Bhh',dir,distance,tagID)
        self.showText(id,"moveSearchTag("+str(id)+","+str(dir)+","+str(distance)+","+str(tagID)+")")
        self.moveDelay(id)

    # __号向__飞__厘米，跟随__号标签
    def moveFollowTag(self,id,dir,distance,tagID):

        if dir>6:
            distance = int(distance*0.7071+0.5)
        else:
            distance = int(distance+0.5)
        self.sendOrder(id,order.moveFollowTag,'<Bhh',dir,distance,tagID)
        self.showText(id,"moveFollowTag("+str(id)+","+str(dir)+","+str(distance)+","+str(tagID)+")")
        self.moveDelay(id)

    # __号直达(__,__,__)
    def goTo(self,id,loc):

        loc[0] = int(loc[0]+0.5)
        loc[1] = int(loc[1]+0.5)
        loc[2] = int(loc[2]+0.5)
        self.sendOrder(id,order.goTo,'<3h',loc[0],loc[1],loc[2])
        self.showText(id,"goTo("+str(id)+",["+str(loc[0])+","+str(loc[1])+","+str(loc[2])+"])")
        self.moveDelay(id)

    # __号直达__号标签
    def goToTag(self,id,tagID,high):

        high = int(high+0.5)
        self.sendOrder(id,order.goToTag,'<2h',tagID,high)
        self.showText(id,"goToTag("+str(id)+","+str(tagID)+","+str(high)+")")
        self.moveDelay(id)

    # __号旋转__度
    def rotation(self,id,angle):

        angle = int(angle+0.5)
        self.sendOrder(id,order.rotation,'<h',angle)
        self.showText(id,"rotation("+str(id)+","+str(angle)+")")
        self.autoDelay(1+abs(angle)/20)

    # __号高度__厘米
    def flyHigh(self,id,high):

        high = int(high+0.5)
        self.sendOrder(id,order.flyHigh,'<h',high)
        self.showText(id,"flyHigh("+str(id)+","+str(high)+")")
        self.moveDelay(id)

    # __号向__翻滚__圈
    def flipCtrl(self,id,dir,cir):

        self.sendOrder(id,order.flipCtrl,'<2B',dir,cir)
        self.showText(id,"flipCtrl("+str(id)+","+str(dir)+","+str(cir)+")")
        self.autoDelay(2)

    # __号灯光(__,__)
    def ledCtrl(self,id,mode,color):

        color[0] = int(color[0]+0.5)
        color[1] = int(color[1]+0.5)
        color[2] = int(color[2]+0.5)
        self.sendOrder(id,order.ledCtrl,'<4B',mode,color[0],color[1],color[2])
        self.showText(id,"ledCtrl("+str(id)+","+str(mode)+",["+str(color[0])+","+str(color[1])+","+str(color[2])+"])")
        self.autoDelay(0.1)

    # __号关闭灯光
    def closeLed(self,id):

        self.sendOrder(id,order.ledCtrl,'<4B',0,0,0,0)
        self.showText(id,str(id)+"号关闭灯光")
        self.autoDelay(0.1)

    # __号检测__
    def mvCheckMode(self,id,mode):

        self.sendOrder(id,order.mvMode,'<B6bh',mode,0,0,0,0,0,0,0)
        self.showText(id,"mvCheckMode("+str(id)+","+str(mode)+")")
        self.autoDelay(0.1)

    # __号检测__号标签
    def mvCheckTag(self,id,tagID):

        self.sendOrder(id,order.mvMode,'<B6bh',6,0,0,0,0,0,0,tagID)
        self.showText(id,"mvCheckTag("+str(id)+","+str(tagID)+")")
        self.autoDelay(0.1)

    # __号检测色块(__,__,__,__,__,__,)
    def mvCheckBlob(self,id,type,blob):

        self.sendOrder(id,order.mvMode,'<B6bh',type,blob[0],blob[1],blob[2],blob[3],blob[4],blob[5],0)
        self.showText(id,"mvCheckBlob("+str(id)+",["+str(blob[0])+","+str(blob[1])+","+str(blob[2])+","+str(blob[3])+","+str(blob[4])+","+str(blob[5])+"])")
        self.autoDelay(0.1)

    # __号__发射激光
    def shootCtrl(self,id,mode):

        self.sendOrder(id,order.shootCtrl,'<B',mode)
        self.showText(id,"shootCtrl("+str(id)+","+str(mode)+")")
        self.autoDelay(0.1)

    # __号__电磁铁
    def magnetCtrl(self,id,mode):

        self.sendOrder(id,order.magnetCtrl,'<B',mode)
        self.showText(id,"magnetCtrl("+str(id)+","+str(mode)+")")
        self.autoDelay(0.1)

    # __号舵机__度
    def servoCtrl(self,id,angle):

        angle = int(angle+0.5)
        self.sendOrder(id,order.servoCtrl,'<B',angle)
        self.showText(id,"servoCtrl("+str(id)+","+str(angle)+")")
        self.autoDelay(1)

    # __号__机头方向
    def lockDir(self,id,mode):

        self.sendOrder(id,order.lockDir,'<B',mode)
        self.showText(id,"lockDir("+str(id)+","+str(mode)+")")
        self.autoDelay(0.1)

    # __号发送__
    def roleCtrl(self,id,string):

        strBuf = string.encode("utf-8")
        strLen = len(strBuf)

        if strLen<11:
            self.sendOrderPack(id,order.roleCtrl,strBuf)
            self.showText(id,"roleCtrl("+str(id)+",\""+string+"\")")
            self.autoDelay(0.1)
        else:
            self.showText(id,"发送失败：字符超过10字节")

    # __号设置当前位置为__,__
    def setCenterOffset(self,id,offset):

        self.sendOrder(id,order.setCenterOffset,'<2h',offset[0],offset[1])
        self.showText(id,"setCenterOffset("+str(id)+",["+str(offset[0])+","+str(offset[1])+"])")
        self.autoDelay(0.1)

    # __号设置当前位置为__,__
    def setLocation(self,id,loc):

        self.sendOrder(id,order.setLocation,'<2h',loc[0],loc[1])
        self.showText(id,"setLocation("+str(id)+",["+str(loc[0])+","+str(loc[1])+"])")
        self.autoDelay(0.1)

    # __号设置标签间距为__厘米
    def setTagDistance(self,id,distance):

        self.sendOrder(id,order.setTagDistance,'<h',distance)
        self.showText(id,"setTagDistance("+str(id)+","+str(distance)+")")
        self.autoDelay(0.1)

    # __镜头__度
    def cameraDeg(self,id,deg):

        self.sendOrder(id,order.cameraDeg,'<h',deg)
        self.showText(id,"cameraDeg("+str(id)+","+str(deg)+")")
        self.autoDelay(1)

    # __号__回传
    def photographMode(self,id,mode):

        self.port.flyData.photo.id = id
        self.port.flyData.photo.isOk = False
        self.sendOrder(id,order.photographMode,'<B',mode)
        self.showText(id,"photographMode("+str(id)+","+str(mode)+")")
        self.autoDelay(0.1)

    # __号红外发送
    def irSend(self,id,mode,data):

        self.sendOrder(id,order.irSend,'<5B',mode,data[0],data[1],data[2],data[3])
        self.showText(id,"irSend("+str(id)+","+str(mode)+",["+hex(data[0])+","+hex(data[1])+","+hex(data[2])+","+hex(data[3])+"])")
        self.autoDelay(0.1)

    #显示字符串
    def showStr(self,id,x,y,string,scal):

        buf = pack('<3B',x,y,scal)
        strBuf = string.encode("utf-8")
        strLen = len(strBuf)

        if strLen<=7:
            self.sendOrderPack(id,order.showStr,buf+strBuf)
            self.showText(id,"showStr("+str(id)+","+str(x)+","+str(y)+",\""+string+"\","+str(scal)+")")
            self.autoDelay(0.1)
        else:
            self.showText(id,"显示失败：字符超过7字节")

    #显示控制
    def showCtrl(self,id,mode):

        self.sendOrder(id,order.showCtrl,'<B',mode)
        self.showText(id,"showCtrl("+str(id)+","+str(mode)+")")
        self.autoDelay(0.1)


    '''以下是回传部分'''

    #图片回传
    def photoOk(self):

        if self.port.type == "MindPlus":
            return True
        else:
            return self.port.flyData.photo.isOk

    #按键回传
    def getKeyPress(self,id):

        return True if (self.port.flyData.keyPressId==id) else False

    #检测到__
    def isMvCheck(self,id,mode):

        return self.port.flyData.flySensor[id].mv.flag&(1<<mode)!=0

    #检测到__边有线
    def isMvCheckLine(self,id,dir):

        return self.port.flyData.flySensor[id].mv.flag&(1<<dir)!=0

    #__障碍物的距离
    def getObsDistance(self,id,dir):

        return round(self.port.flyData.flySensor[id].obs_dist[dir],1)#保留1位小数

    #__
    def getFlySensor(self,id,type):

        if type == "tagID":
            return self.port.flyData.flySensor[id].mv.tagId
        elif type == "qrCode":
            return self.port.flyData.flySensor[id].qrCode
        elif type == "brCode":
            return self.port.flyData.flySensor[id].brCode
        elif type == "rol":
            return round(self.port.flyData.flySensor[id].imu[0],1)#保留1位小数
        elif type == "pit":
            return round(self.port.flyData.flySensor[id].imu[1],1)#保留1位小数
        elif type == "yaw":
            return round(self.port.flyData.flySensor[id].imu[2],1)#保留1位小数
        elif type == "loc_x":
            return round(self.port.flyData.flySensor[id].loc[0],1)#保留1位小数
        elif type == "loc_y":
            return round(self.port.flyData.flySensor[id].loc[1],1)#保留1位小数
        elif type == "loc_z":
            return round(self.port.flyData.flySensor[id].loc[2],1)#保留1位小数
        elif type == "err_x":
            return round(self.port.flyData.flySensor[id].locErr[0],1)#保留1位小数
        elif type == "err_y":
            return round(self.port.flyData.flySensor[id].locErr[1],1)#保留1位小数
        elif type == "err_z":
            return round(self.port.flyData.flySensor[id].locErr[2],1)#保留1位小数
        elif type == "vol":
            return round(self.port.flyData.flySensor[id].vol,2)#保留2位小数

    #__
    def getBlobResult(self,id,type):

        if type == "s":
            return self.port.flyData.flySensor[id].mv.blob_s
        elif type == "w":
            return self.port.flyData.flySensor[id].mv.blob_w
        elif type == "h":
            return self.port.flyData.flySensor[id].mv.blob_h
        elif type == "n":
            return self.port.flyData.flySensor[id].mv.blob_n

    #消息__
    def getRoleNews(self,id,type):

        if type=="details":
            return self.port.flyData.flySensor[id].news
        elif type=="id":
            return self.port.flyData.flySensor[id].newsCount

    #清除消息
    def clearRoleNews(self,id):

        self.port.flyData.flySensor[id].news = ""

    '''以下是互联模块部分'''

        # __号__开关
    def switchCtrl(self,id,mode):

        self.sendOrder(id,order.switchCtrl,'<B',mode)
        self.showText(id,"switchCtrl("+str(id)+","+str(mode)+")")
        self.autoDelay(0.1)

     # __号电子秤读数
    def getScaleWeight(self,id):

        return self.port.flyData.flySensor[id].scale_weight

     # __号电子秤读数
    def getShootResult(self,id,type):

        if type=="number":
            return self.port.flyData.flySensor[id].laserTarget_count
        elif type=="result":
            return self.port.flyData.flySensor[id].laserTarget_result
        elif type=="x":
            return self.port.flyData.flySensor[id].laserTarget_x
        elif type=="y":
            return self.port.flyData.flySensor[id].laserTarget_y

    '''以下是机械臂部分'''

    # __号总线舵机__,__,__
    def serServoCtrl(self,id,index,value,time):

        self.sendOrder(id,order.serServoCtrl,'<B2h',index,value,time)
        self.showText(id,"serServoCtrl("+str(id)+","+str(index)+","+str(value)+","+str(time)+")")
        self.autoDelay(time*0.001)

    # __号机械臂执行动作__,时间__秒
    def robotArmCtrl(self,id,index,time):

        self.sendOrder(id,order.robotArmCtrl,'<Bh',index,time)
        self.showText(id,"robotArmCtrl("+str(id)+","+str(index)+","+str(time)+")")
        self.autoDelay(time*0.001)

    # __号机械臂记录动作__
    def robotArmCover(self,id,index):

        self.sendOrder(id,order.robotArmCover,'<B',index)
        self.showText(id,"robotArmCover("+str(id)+","+str(index)+")")
        self.autoDelay(0.1)

    # __号机械臂清空动作
    def robotArmRecord(self,id,mode):

        self.sendOrder(id,order.robotArmRecord,'<B',mode)
        self.showText(id,"robotArmRecord("+str(id)+","+str(mode)+")")
        self.autoDelay(0.1)
        
    '''以下是拍照和LCD显示部分'''
    
    def snapshot(self):
        
        return self.port.snapshot()
        
    def display(self,img):
        
        self.port.display(img.invert())

