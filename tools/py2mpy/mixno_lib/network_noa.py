import network,time,board
from machine import UART

class wifi():

    uart = None
    nic = None

    def init():
        __class__.en =board.pin(19,board.GPIO.OUT)
        board.register(18,board.FPIOA.UART2_TX)
        board.register(17,board.FPIOA.UART2_RX)
        __class__.uart = UART(UART.UART2, 115200, timeout=1000, read_buf_len=8192)

    def enable(en):
        __class__.en.value(en)

    def _at_cmd(cmd="AT\r\n", resp="OK\r\n", timeout=20):
        __class__.uart.write(cmd) # "AT+GMR\r\n"
        time.sleep_ms(timeout)
        tmp = __class__.uart.read()
        if tmp and tmp.endswith(resp):
            return True
        return False

    def at_cmd(cmd="AT\r\n", timeout=20):
        __class__.uart.write(cmd) # "AT+GMR\r\n"
        time.sleep_ms(timeout)
        tmp = __class__.uart.read()
        return tmp

    def reset1(force=False, reply=3):
        if force == False and __class__.isconnected():
            return True
        __class__.init()
        for i in range(reply):
            #print('reset...')
            __class__.enable(False)
            time.sleep_ms(50)
            __class__.enable(True)
            time.sleep_ms(500) # at start > 500ms
            if __class__._at_cmd(timeout=500):
                break
        __class__._at_cmd()
        __class__._at_cmd('AT+UART_CUR=921600,8,1,0,0\r\n', "OK\r\n")
        __class__.uart = UART(UART.UART2, 921600, timeout=1000, read_buf_len=10240)
        try:
            __class__.nic = network.ESP8285(__class__.uart)
            time.sleep_ms(500) # wait at ready to connect
        except Exception as e:
            return False
        return True

    def reset2(force=False, reply=3):
        if force == False and __class__.isconnected():
            return True
        __class__.init()
        for i in range(reply):
            #print('reset...')
            __class__.enable(False)
            time.sleep_ms(50)
            __class__.enable(True)
            time.sleep_ms(500) # at start > 500ms
            if __class__._at_cmd(timeout=500):
                break
        try:
            __class__.nic = network.ESP8285(__class__.uart)
            time.sleep_ms(500) # wait at ready to connect
        except Exception as e:
            return False
        return True

    def connect(ssid="wifi_name", pasw="pass_word"):
        if __class__.nic != None:
            return __class__.nic.connect(ssid, pasw)

    def ifconfig(): # should check ip != 0.0.0.0
        if __class__.nic != None:
            return __class__.nic.ifconfig()

    def isconnected():
        if __class__.nic != None:
            return __class__.nic.isconnected()
        return False

    def scan():
        if __class__.nic != None:
            return __class__.nic.scan()
        return False


def wifi_init1():
    wifi.reset1()
    return wifi

def wifi_init2():
    wifi.reset2()
    return wifi

def wifi_deal_ap_info(info):
    res = []
    for ap_str in info:
        ap_str = ap_str.split(",")
        info_one = []
        for node in ap_str:
            if node.startswith('"'):
                info_one.append(node[1:-1])
            else:
                info_one.append(int(node))
        res.append(info_one)
    return res

def scans(nic,reply=5): 
    for i in range(reply):
        try:
            wifi.reset2()
            ap_info = wifi.scan()
            ap_info = wifi_deal_ap_info(ap_info)
            ap_info.sort(key=lambda x:x[2], reverse=True)
            return ap_info
        except Exception as e:
            pass

def wlan_connect(account,password,reply=5):
    if wifi.isconnected() != True:
        print('try connect wifi ',end ="")
        for i in range(reply):
            try:
                print('.',end ="")
                wifi.reset1()
                wifi.connect(account, password)
                if wifi.isconnected():
                    print('')
                    break
            except Exception as e:
                err = e
    if wifi.ifconfig() is None:
        raise RuntimeError(err) 
    print(wifi.ifconfig())
