
import math

x=1
y=2
pix=3
rolNum=0

rad_to_angle = 57.29 #弧度转度
isRidOutlier = True  #是否剔除离异点

imgWidth = 320
imgHeight = 240
width = imgHeight/3

roiLen  = 10 #扫描区域宽度
roiL_count = int(imgHeight/roiLen) #扫描区域数量
roiH_count = int(imgWidth/roiLen) #扫描区域数量

roiL = [] #扫描区域
roiH = [] #扫描区域

#初始化扫描区域
for i in range(roiL_count):
    roiL.append( (0,roiLen*i,imgWidth-1,roiLen) )#(x，y，w，h)
for i in range(roiH_count):
    roiH.append( (roiLen*i,0,roiLen,imgHeight-1) )#(x，y，w，h)

class line(object):
    a=0
    b=0
    c=0
    err=0
    d_mean=0
    pix_mean=1000

lineL = line()
lineH = line()

class fitLine(object):
    x_angle = 0
    y_angle = 0
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    x = 0
    y = 0
    flag = 0

fitLine = fitLine()

def lineFit(Points,Line):

    #计算点的个数
    size = len(Points)

    #点太少，无法拟合
    if  size<5:
        return False

    #以下求得xy平均值
    x_mean = 0;
    y_mean = 0;

    for i in range(size):
        x_mean = x_mean + Points[i][x]
        y_mean = y_mean + Points[i][y]

    x_mean = x_mean / size
    y_mean = y_mean / size

    #拟合数据
    Dxx = 0
    Dxy = 0
    Dyy = 0

    for i in range(size):
        Dxx = Dxx + (Points[i][x] - x_mean) * (Points[i][x] - x_mean);
        Dxy = Dxy + (Points[i][x] - x_mean) * (Points[i][y] - y_mean);
        Dyy = Dyy + (Points[i][y] - y_mean) * (Points[i][y] - y_mean);

    lam = ( (Dxx + Dyy) - math.sqrt( (Dxx - Dyy) * (Dxx - Dyy) + 4 * Dxy * Dxy) ) / 2.0
    den = math.sqrt( Dxy * Dxy + (lam - Dxx) * (lam - Dxx) )

    #拟合失败
    if den == 0:
        return False

    #拟合结果
    Line.a = Dxy / den;
    Line.b = (lam - Dxx) / den;
    Line.c = - Line.a * x_mean - Line.b * y_mean;

    #求点线的平均距离
    Line.d_mean = 0
    sqrt_aabb = math.sqrt( Line.a*Line.a + Line.b*Line.b)

    for i in range(size):
        Line.d_mean = Line.d_mean + abs( (Line.a*Points[i][x] + Line.b*Points[i][y] + Line.c) / sqrt_aabb )

    Line.d_mean = Line.d_mean / size

    #求线的粗细
    Line.pix_mean = 0
    for i in range(size):
        Line.pix_mean = Line.pix_mean + Points[i][pix]

    Line.pix_mean = Line.pix_mean / size

    return True

max_d = roiLen*1.5

#虚线扫描
def scanLine(img,roi,thresholds):

    points = []
    for i in range(len(roi)):

        pix = 0
        point = []

        for blob in img.find_blobs([thresholds], roi=roi[i], pixels_threshold=50):

            if pix<blob.pixels():
                pix = blob.pixels()
                point = [i,blob.cx(),blob.cy(),blob.pixels()]

        if pix>0:

            points.append( point )

    i = 0 #计数清零
    validLast = False #上有效
    validNext = False #下有效

    #剔除离散点
    while i<len(points):

        validNext = False
        j = i + 1
        while j<len(points) and points[j][rolNum]-points[i][rolNum]<2:
            dx = points[i][x]-points[j][x]
            dy = points[i][y]-points[j][y]
            d = math.sqrt( dx*dx + dy*dy)
            if d<max_d:
                validNext = True
            j = j + 1

        validLast = False
        j = i - 1
        while j>=0 and j<len(points) and points[i][rolNum]-points[j][rolNum]<2:
            dx = points[i][x]-points[j][x]
            dy = points[i][y]-points[j][y]
            d = math.sqrt( dx*dx + dy*dy)
            if d<max_d:
                validLast = True
            j = j - 1

        if validNext or validLast:
            i = i + 1
        else:
            del points[i]

    groupBuf = []

    #剔除小集群点
    while len(points):

        i = 0
        group = [(points[0])]
        del points[0]

        while i<len(points):
            j = len(group) - 1
            get = False
            while j>=0:
                dx = points[i][x]-group[j][x]
                dy = points[i][y]-group[j][y]
                d = math.sqrt( dx*dx + dy*dy)
                if d<max_d:
                    group.append( (points[i]) )
                    del points[i]
                    get = True
                    break
                else:
                    j = j - 1

            if not get:
                i = i + 1

        if len(group)>=3:
            groupBuf = groupBuf + group;

    return groupBuf

#虚线检测
def check_dotLine(img,thresholds,show=False):

    fitLine.flag = 0

    #检测竖线
    pointL = scanLine(img,roiL,thresholds)

    if lineFit(pointL,lineL) and lineL.a!=0: #直线拟合成功

        #判断标志位
        for i in range(len(pointL)):
            if pointL[i][y]<width:
                fitLine.flag = fitLine.flag | 0x01 #up_ok
            elif pointL[i][y]>(imgHeight-width):
                fitLine.flag = fitLine.flag | 0x02 #down_ok

        #计算位置
        if fitLine.flag&0x01 or fitLine.flag&0x02:

            fitLine.x0 = (-lineL.c - lineL.b*0)/lineL.a
            fitLine.x1 = (-lineL.c - lineL.b*(imgHeight-1))/lineL.a
            fitLine.x = (fitLine.x0+fitLine.x1)/2
            fitLine.x_angle = -math.atan(lineL.b/lineL.a) * rad_to_angle

        lineL.err = 0

    else :
        lineL.err = lineL.err + 1
        if lineL.err > 2:
            lineL.a = 0
            lineL.b = 0
            lineL.c = 0
            lineL.pix_mean = 1000
            lineL.err = 0

    #检测横线
    pointH = scanLine(img,roiH,thresholds)

    #删除与竖线重合的点
    if fitLine.flag&0x01 or fitLine.flag&0x02: #up_ok or down_ok

        sqrt_aabb = math.sqrt( lineL.a*lineL.a + lineL.b*lineL.b)
        if sqrt_aabb!=0:
            i = 0
            while i<len(pointH):
                d = abs( (lineL.a*pointH[i][x] + lineL.b*pointH[i][y] + lineL.c) / sqrt_aabb )
                if d<(roiLen*2):
                    pointH.pop(i)
                else:
                    i = i + 1

    if lineFit(pointH,lineH) and lineH.b!=0: #直线拟合成功

        #判断标志位
        for i in range(len(pointH)):
            if pointH[i][x]<width:
                fitLine.flag = fitLine.flag | 0x04 #left_ok
            elif pointH[i][x]>(imgWidth-width):
                fitLine.flag = fitLine.flag | 0x08 #rigt_ok

        #计算位置
        if fitLine.flag&0x04 or fitLine.flag&0x08:

            fitLine.y0 = (-lineH.c - lineH.a*0)/lineH.b
            fitLine.y1 = (-lineH.c - lineH.a*(imgWidth-1))/lineH.b
            fitLine.y = (fitLine.y0+fitLine.y1)/2
            fitLine.y_angle = math.atan(lineH.a/lineH.b) * rad_to_angle

        lineH.err = 0

    else :
        lineH.err = lineH.err + 1
        if lineH.err > 2:
            lineH.a = 0
            lineH.b = 0
            lineH.c = 0
            lineH.pix_mean = 1000
            lineH.err = 0

    #显示
    if show:
        img.draw_line(int(fitLine.x0), 0, int(fitLine.x1), imgHeight-1, color = (255, 0, 0), thickness = 1)

        for i in range(len(pointL)):
            img.draw_cross(pointL[i][x],pointL[i][y])

        img.draw_line(0, int(fitLine.y0), imgWidth-1, int(fitLine.y1), color = (255, 0, 0), thickness = 1)

        for i in range(len(pointH)):
            img.draw_circle(pointH[i][x],pointH[i][y],5)

    return fitLine
