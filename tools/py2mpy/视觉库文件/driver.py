#********** (C) COPYRIGHT 2018 Player Tech **********#

#OpenMv中文文档 https://docs.singtown.com/micropython/zh/latest/openmvcam/index.html
#OPENMV中文上手书籍 http://book.openmv.cc/

#本代码实现了：
#    1、点检测
#    2、线检测
#    3、二维码扫描
#    4、条形码扫描
#    5、AprilTag扫描

#开机默认是AprilTag扫描模式，可以通过串口设置成以上任何一种或者多种模式同时运行，
#但是同时运行的模式数量越多，计算输出的帧率就越低，所以尽量避免多模式同时运行。

import led_rgb
import board
from time import sleep,ticks_ms
from machine import UART

import lcd
lcd.init(freq=15000000,color=0x0000)
lcd.rotation(3)

import flyData
import myLine, myColor
from struct import pack, unpack
import sensor, image, math
from random import randint

CHECK_DOT    = 0x01
CHECK_LINE   = 0x02
CHECK_QR     = 0x04
CHECK_BAR    = 0x08
CHECK_TAG    = 0x10
SENSOR_FLIP  = 0x80

rad_to_angle = 57.29#弧度转度

REC_ERROR = 0xFFFFFFFE
REC_COMPLETE = 0xFFFFFFFF

class Ctrl(object):
    work_mode = CHECK_TAG    #工作模式.默认是AprilTag扫描，可以通过串口设置成其他模式
    check_show = 1           #开显示，在线调试时可以打开，脱机使用请关闭，可提高计算速度
    target_id = 0xFFFF       #默认目标标签号
    isSensorFlip = False     #默认是不翻转
    test_thresholds = [0,0]  #点检测阈值
    blob_thresholds = [0,0]  #点检测阈值
    line_thresholds = [0,0]  #线检测阈值
    photograph_mode = 0      #拍照模式

class Tag(object):
    id = 0
    x = 0
    y = 0
    z = 0
    angle = 0
    L = 0
    flag = 0

class Dot(object):
    x = 0
    y = 0
    w = 0
    h = 0
    pixels = 0
    num = 0
    ok = 0
    flag = 0
    rect = [0,0,0,0]

class Jpg(object):
    id = 0
    count = randint(0,255)
    countInit = False
    size = 0
    markLen = 0
    unitsLen = 0
    buff = 0
    lostMark = 0
    sendMark = 0
    updateMs = 0

class Rx(object):
    head = 0
    len = 0
    date = []
    cnt = 0
    state = 0
    buff = []
    fps = 0
    fpsCnt = 0

class init():

    #初始化
    def __init__(self,flyNum=1):

        #初始化镜头
        sensor.reset()
        sensor.set_framesize(sensor.QVGA)
        sensor.set_pixformat(sensor.RGB565)
        sensor.set_hmirror(True)
        sensor.set_vflip(True)
        #sensor.skip_frames(time = 100)

        board.register(1,board.FPIOA.UART1_TX)
        board.register(2,board.FPIOA.UART1_RX)
        self.uart = UART(UART.UART1, 500000, timeout=1000, read_buf_len=4096)

        self.led = led_rgb.init()

        self.tag  = Tag()
        self.dot  = Dot()
        self.jpg  = Jpg()
        self.ctrl = Ctrl()
        self.rx   = Rx()

        self.flyData = flyData.init(flyNum)
        self.type = "OpenMV"

    def getMs(self):

        return ticks_ms()
        
    def getSec(self):

        return ticks_ms()*0.001

    def write(self,buff):

        self.uart.write(buff)

    #读取串口缓存
    def uart_read_buf(self):

        size = self.uart.any()
        while size:
            self.Receive_Prepare(self.uart.readchar())
            size = size - 1

    #串口通信协议接收
    def Receive_Prepare(self,data):

        if self.rx.state==0:#header

            if data == 0xAA or data == 0xBB:
                self.rx.state = 1
                self.rx.head = data
            else:
                print("rxErr!")

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

    #串口数据解析
    def Receive_Anl(self):

        #和校验
        sum = 0
        sum = self.rx.head + self.rx.len
        for temp in self.rx.date:
            sum = sum + temp

        sum = (sum-self.rx.date[self.rx.len])%256 #求余

        if sum != self.rx.date[self.rx.len]: #和校验通
            return

        if self.rx.head == 0xBB:

            if self.rx.date[0]==0xF1:

                pack = unpack('<BH6b6b', bytearray(self.rx.date),1)#从第1字节开始解析，跳过fun

                self.ctrl.work_mode = pack[0]
                self.ctrl.target_id = pack[1]

                blobThresholds = [pack[2],pack[3],pack[4],pack[5],pack[6],pack[7]]
                lineThresholds = [pack[8],pack[9],pack[10],pack[11],pack[12],pack[13]]

                sumBlob = 0
                sumLine = 0

                for i in range(6):

                    sumBlob = sumBlob + blobThresholds[i]
                    sumLine = sumLine + lineThresholds[i]

                #色块阈值
                if sumBlob>0:

                    self.ctrl.blob_thresholds = blobThresholds

                elif len(self.ctrl.blob_thresholds)!=2:

                    self.ctrl.blob_thresholds = [0,0]

                #色线阈值
                if sumLine>0:

                    self.ctrl.line_thresholds = lineThresholds

                elif len(self.ctrl.line_thresholds)!=2:

                    self.ctrl.line_thresholds = [0,0]

                #翻转画面
                if self.ctrl.work_mode & SENSOR_FLIP:

                    if not self.ctrl.isSensorFlip:
                        sensor.set_hmirror(True)
                        sensor.set_vflip(True)
                        self.ctrl.isSensorFlip = True

                #返回ack数据
                self.uart.write( self.pack_ack_data() )

            elif self.rx.date[0]==0xF2:

                self.jpg.id = self.rx.date[1]#飞机编号
                self.ctrl.photograph_mode = self.rx.date[2]#拍照模式

            elif self.rx.date[0]==0x0A:#丢失重发

                pack = unpack('<BI', bytearray(self.rx.date),1)#从第1字节开始解析，跳过fun
                #self.jpg.id = pack[0]
                self.jpg.lostMark = pack[1]
                self.jpg.sendMark = self.jpg.lostMark
                self.jpg.startMs = self.getMs()

        elif self.rx.head == 0xAA:

            self.flyData.Receive_Anl(self.rx)

    def pyLink_pack(self,fun,buff):

        sum = 0

        pack_data = bytearray([0xAA,0x00,fun])#包头
        pack_data.extend(buff)#数据包
        pack_data[1] = len(pack_data)-2;#有效数据个数

        for temp in pack_data:
            sum = sum + temp

        pack_data.extend(pack('<B', sum%256))#和校验

        return pack_data

    #点检测数据打包
    def pack_dot_data(self):

        dot_x = int((160 - self.dot.x))
        dot_y = int((self.dot.y - 120))

        if len(self.ctrl.blob_thresholds)==6:
            return self.pyLink_pack(0xF2, pack('<B5h6b', self.dot.flag, self.dot.pixels, dot_x, dot_y, self.dot.w, self.dot.h, self.ctrl.blob_thresholds[0], self.ctrl.blob_thresholds[1], self.ctrl.blob_thresholds[2], self.ctrl.blob_thresholds[3], self.ctrl.blob_thresholds[4], self.ctrl.blob_thresholds[5]) )
        else:
            return self.pyLink_pack(0xF2, pack('<B5h6b', self.dot.flag, self.dot.pixels, dot_x, dot_y, self.dot.w, self.dot.h, 0,0,0,0,0,0) )

    #线检测数据打包
    def pack_line_data(self,line):

        line_x  = int((160 - int(line.x )))
        line_x0 = int((160 - int(line.x0)))
        line_x1 = int((160 - int(line.x1)))
        line_y  = int((int(line.y ) - 120))
        line_y0 = int((int(line.y0) - 120))
        line_y1 = int((int(line.y1) - 120))

        return self.pyLink_pack(0xF3,pack('<B8h',line.flag,line_x,line_y,int(line.x_angle),int(line.y_angle),line_x0,line_x1,line_y0,line_y1))

    #AprilTags数据打包
    def pack_apriltags_data(self):

        return self.pyLink_pack(0xF6,pack('<BH4hBH', self.tag.flag, self.tag.id, self.tag.x, self.tag.y, self.tag.z, self.tag.angle))

    #ACK数据打包
    def pack_ack_data(self):

        return self.pyLink_pack(0xF1, pack('<B', self.ctrl.work_mode) )

    #点检测函数
    def check_dot(self,img):

        #清零标志位
        self.dot.ok = 0
        self.dot.pixels = 0

        for blob in img.find_blobs([self.ctrl.blob_thresholds], pixels_threshold=100):
            if self.dot.pixels<blob.pixels():#寻找最大的黑点
                self.dot.pixels=blob.pixels()
                self.dot.x = blob.cx()
                self.dot.y = blob.cy()
                self.dot.w = blob.w()
                self.dot.h = blob.h()
                self.dot.rect = blob.rect()
                self.dot.ok= 1

        #判断标志位
        self.dot.flag = self.dot.ok

        #发送数据
        self.uart.write(self.pack_dot_data())

        #可视化显示
        if self.ctrl.check_show:
            img.draw_cross(self.dot.x, self.dot.y, color=127, size = 10)
            img.draw_circle(self.dot.x, self.dot.y, 5, color = 127)
            img.draw_rectangle(self.dot.rect)

    def send_mark(self,i):

        self.jpg.unitsLen = 26
        remain = self.jpg.size - i*26
        if self.jpg.unitsLen > remain:
            self.jpg.unitsLen = remain
        data = bytearray(pack('<H',i))
        for j in range(self.jpg.unitsLen):
            data.append(self.jpg.buff[i*26+j])
        self.uart.write(self.pyLink_pack(0x0B,data))

    def send_jpg(self,img):

        #压缩图片
        self.jpg.buff = bytearray(img.compressed(60))
        #self.jpg.buff = img.compressed(60).bytearray()
        self.jpg.size = len(self.jpg.buff)

        if self.jpg.countInit:
            self.jpg.count = self.jpg.count + 1
        else:
            self.jpg.count = int(self.getSec() * 1000) % 256;#创建随机数
            self.jpg.countInit = True

        self.jpg.markLen = int(self.jpg.size/26)
        if (self.jpg.size-self.jpg.markLen*26):
            self.jpg.markLen = self.jpg.markLen + 1
        self.jpg.lostMark = REC_ERROR;
        self.jpg.sendMark = 0

        #计时开始
        self.jpg.startMs = self.getMs()

        #发送图片大小等信息
        while self.jpg.lostMark==REC_ERROR:
            if(self.getMs()-self.jpg.startMs)>1000:
                self.jpg.buff = bytearray()#清空数据
                return#超时退出
            self.uart_read_buf()#读取数据
            self.uart.write(self.pyLink_pack(0x0A,pack('<BHL',self.jpg.id,self.jpg.count,self.jpg.size)))
            sleep(0.002)

        #发送图片数据
        while self.jpg.lostMark!=REC_COMPLETE:
            if(self.getMs()-self.jpg.startMs)>5000:
                self.jpg.buff = bytearray()#清空数据
                return#超时退出
            self.uart_read_buf()#读取数据
            self.send_mark(self.jpg.sendMark)#发送数据
            self.jpg.sendMark = self.jpg.sendMark + 1
            if self.jpg.sendMark>=self.jpg.markLen:
                self.jpg.sendMark = self.jpg.lostMark
            sleep(0.002)

        #清空数据
        self.jpg.buff = bytearray()
        
    def snapshot(self):
        
        return sensor.snapshot()
        
    def display(self,img):
        
        lcd.display(img)

    def run(self,time=-1):

        startMs = self.getMs()

        #主循环
        while(True):
            
            img = sensor.snapshot()

            #拍照回传
            if self.ctrl.photograph_mode:

                self.led.on(2)

                if self.ctrl.photograph_mode == 2:#颜色采样

                    self.ctrl.test_thresholds = myColor.sampling(img)

                elif self.ctrl.photograph_mode == 3:#颜色识别

                    if len(self.ctrl.test_thresholds)==6:
                        myColor.test(img,self.ctrl.test_thresholds)#色块阈值参数测试
                    else:
                        myColor.test(img.to_grayscale(),self.ctrl.test_thresholds)#灰度阈值参数测试

                elif self.ctrl.photograph_mode == 4 or self.ctrl.photograph_mode == 5:#色块测量

                    mode = self.ctrl.photograph_mode-4 #测量模式0、1

                    if len(self.ctrl.test_thresholds)==6:
                        blobResuit = myColor.find_blobs(img,self.ctrl.test_thresholds,mode)#色块阈值
                    else:
                        blobResuit = myColor.find_blobs(img.to_grayscale(),self.ctrl.test_thresholds,mode)#灰度阈值

                    self.uart.write( self.pyLink_pack(0xF7,pack('<BL2H',blobResuit.number,blobResuit.area,blobResuit.width,blobResuit.height)))#发送消息数据


                self.ctrl.photograph_mode = 0
                self.send_jpg(img) #回传图片

                self.led.off(2)

                continue

            #扫描二维码
            if (self.ctrl.work_mode & CHECK_QR):
                self.led.off(2)
                for code in img.find_qrcodes():
                    string = code.payload()
                    if len(string)>28:
                        self.uart.write( self.pyLink_pack(0xF4,"Too Long!") )#发送数据
                    else:
                        self.uart.write( self.pyLink_pack(0xF4,string) )#发送数据
                    self.led.on(2)#扫描成功后灯光提示

            #扫描条形码
            if (self.ctrl.work_mode & CHECK_BAR):
                self.led.off(1)
                for code in img.find_barcodes():
                    string = code.payload()
                    if len(string)>28:
                        self.uart.write( self.pyLink_pack(0xF5,"Too Long!") )#发送数据
                    else:
                        self.uart.write( self.pyLink_pack(0xF5,string) )#发送数据
                    self.led.on(1)#扫描成功后灯光提示

            #色块检测
            if self.ctrl.work_mode&CHECK_DOT and len(self.ctrl.blob_thresholds)==6:

                self.check_dot(img)#色块检测
                self.ctrl.test_thresholds = self.ctrl.blob_thresholds

                if self.dot.flag:
                    self.led.toggle(1)
                else:
                    self.led.off(1)

            #色线检测
            if self.ctrl.work_mode&CHECK_LINE and len(self.ctrl.line_thresholds)==6:

                line = myLine.check_dotLine(img,self.ctrl.line_thresholds,self.ctrl.check_show)
                self.uart.write(self.pack_line_data(line))#发送数据
                if line.flag:
                    self.led.toggle(2)
                else:
                    self.led.off(2)

            #转灰度图像
            img.to_grayscale()

            #计算最优灰度阈值（如果希望使用自定义阈值，请把该函数注释掉）
            gray_thresholds = (int)(img.get_statistics().mean()*0.4)

            if len(self.ctrl.test_thresholds)==2:

                self.ctrl.test_thresholds = [0,gray_thresholds]

            if len(self.ctrl.blob_thresholds)==2:

                self.ctrl.blob_thresholds = [0,gray_thresholds]

                #黑块检测
                if (self.ctrl.work_mode & CHECK_DOT):

                    self.check_dot(img)#黑块检测
                    self.ctrl.test_thresholds = self.ctrl.blob_thresholds

                    if self.dot.flag:
                        self.led.toggle(1)
                    else:
                        self.led.off(1)

            if len(self.ctrl.line_thresholds)==2:

                self.ctrl.line_thresholds = [0,gray_thresholds]

                #黑线检测
                if (self.ctrl.work_mode & CHECK_LINE):

                    line = myLine.check_dotLine(img,self.ctrl.line_thresholds,self.ctrl.check_show)
                    self.uart.write(self.pack_line_data(line))#发送数据
                    if line.flag:
                        self.led.toggle(2)
                    else:
                        self.led.off(2)

            #图像二值化（仅在线调试时使用，实际上机运行时请把该函数注释掉，可以提高计算速度）
            #img.binary([[0,gray_thresholds]],invert=True)

            #扫描AprilTags
            if (self.ctrl.work_mode & CHECK_TAG):

                img = img.resize(160, 120)
                #img.scale(x_scale=0.5,y_scale=0.5)#缩放至160x120
                self.led.off(1)
                self.led.off(2)
                self.tag.flag = 0
                self.tag.L = 1000
                
                for apriltag in img.find_apriltags(families=image.TAG36H11|image.TAG36H10):
                    
                    #判断错误数位，避免误检测
                    if apriltag.hamming()>0:
                        continue

                    #可视化显示
                    if self.ctrl.check_show:
                        img.draw_rectangle(apriltag.rect(), color = 127)
                        img.draw_cross(apriltag.cx(), apriltag.cy(), color = 127)
                        print_args = (apriltag.id(), (180 * apriltag.rotation()) / math.pi)
                        print("Tag ID %d, rotation %f (degrees)" % print_args)

                    #计算位置
                    if self.ctrl.target_id!=0xFFFF:#追踪目标标签模式

                        if (apriltag.id()==self.ctrl.target_id):
                            self.tag.id = apriltag.id()
                            self.tag.x  = (80 - apriltag.cx())*2
                            self.tag.y  = (apriltag.cy() - 60)*2
                            self.tag.z  = int(-apriltag.z_translation()*100)
                            self.tag.angle = int((180 * apriltag.rotation()) / math.pi)
                            self.led.on(1)
                            self.led.on(2)
                            self.tag.flag = 1
                    else:
                        x_temp = (80 - apriltag.cx())*2
                        y_temp = (apriltag.cy() - 60)*2
                        L_temp = math.sqrt(x_temp*x_temp+y_temp*y_temp)
                        if(L_temp<self.tag.L):#筛选最靠中心位置的标签
                            self.tag.L  = L_temp
                            self.tag.id = apriltag.id()
                            self.tag.x  = x_temp
                            self.tag.y  = y_temp
                            self.tag.z  = int(-apriltag.z_translation()*100)
                            self.tag.angle = int((180 * apriltag.rotation()) / math.pi)
                        self.led.on(1)
                        self.led.on(2)
                        self.tag.flag = 1

                #发送数据
                self.uart.write(self.pack_apriltags_data())

            #接收串口数据
            self.uart_read_buf()

            #LED灯闪烁
            self.led.toggle(0)
            
            img = img.resize(242, 182)
            lcd.display(img.invert())
            
            if time>=0:
                runTime = (self.getMs() - startMs)*0.001;
                if runTime>=time:
                    break;

if __name__ == '__main__':

    mvCtrl = init()
    mvCtrl.run()

#********** (C) COPYRIGHT 2023/07/06 Player Tech **********#
