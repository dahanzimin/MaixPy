
def sendspeak(uart,data):
    eec=0
    buf=[0xfd,0x00,0x00,0x01,0x03]
    if not data is None:
        for char in data:
            buf.append(ord(char) >> 8)
            buf.append(ord(char) & 0xFF)
    buf[2]=(len(buf) -2) & 0xff
    buf[1]=(len(buf) -2) >> 8 & 0xff
    for i in range(len(buf)):
        eec^=int(buf[i])
    buf.append(eec)
    #print(buf)
    uart.write(bytes(buf))
