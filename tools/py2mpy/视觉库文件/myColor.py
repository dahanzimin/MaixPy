
size = 7
half_size = (int)(size/2)
rect = (160-half_size,120-half_size,size,size)
lab = [0,0,0,0,0,1]

def test(img,thresholds):
    img.binary([thresholds],invert=True)
    img.draw_string(5,0,str(thresholds),color=(0,255,0),scale=3,mono_space=False)

def sampling(img):

    hist = img.get_histogram(roi=rect)

    #寻找L最值

    i = 0
    while i>=0 and i<=100:
        if hist.l_bins()[i] >0.000001:
            lab[0] = i - 5
            if(lab[0])<0:
                lab[0] = 0
            break
        i = i + 1

    i = 100

    while i>=0 and i<=100:
        if hist.l_bins()[i] >0.000001:
            lab[1] = i + 5
            if(lab[1])>100:
                lab[1] = 100
            break
        i = i - 1

    #寻找A最值

    i = 0

    while i>=0 and i<=255:
        if hist.a_bins()[i] >0.000001:
            lab[2] = i-128-15
            if(lab[2])<-128:
                lab[2] = -128
            break
        i = i + 1

    i = 255

    while i>=0 and i<=255:
        if hist.a_bins()[i] >0.000001:
            lab[3] = i-128+15
            if(lab[3])>127:
                lab[3] = 127
            break
        i = i - 1

    #寻找B最值

    i = 0

    while i>=0 and i<=255:
        if hist.b_bins()[i] >0.000001:
            lab[4] = i-128-15
            if(lab[4])<-128:
                lab[4] = -128
            break
        i = i + 1

    i = 255

    while i>=0 and i<=255:
        if hist.b_bins()[i] >0.000001:
            lab[5] = i-128+15
            if(lab[5])>127:
                lab[5] = 127
            break
        i = i - 1

    img.draw_cross(160, 120, size = 10, color=(255,255,0))
    img.draw_rectangle(rect,color=(255,0,0))
    img.draw_string(5,0,str(lab),color=(0,255,0),scale=3,mono_space=False)

    return lab

class BlobResuit(object):
    number = 0
    area = 0
    width = 0
    height = 0


def find_blobs(img,thresholds,mode):

    maxPix = 0
    blobResuit = BlobResuit()

    if mode:

        img.binary([thresholds],invert=False)

    else:

        img.binary([thresholds],invert=True)

    for blob in img.find_blobs([(0,10,-5,5,-5,5)], pixels_threshold=10):

        blobResuit.number = blobResuit.number + 1
        blobResuit.area = blobResuit.area + blob.pixels()

        if maxPix < blob.pixels():

            maxPix = blob.pixels()
            blobResuit.width  = blob.w()
            blobResuit.height = blob.h()

        img.draw_rectangle(blob.x(), blob.y(),blob.w(), blob.h(), color=(0,255,0))

    img.draw_string(5,0,str(blobResuit.number),color=(255,0,0),scale=4,mono_space=False)

    return blobResuit
