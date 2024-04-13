'''Bus servo '''
import time

class ZPxxx:
    def __init__(self, uart, baudrate=115200):
        self._uart = uart
        self._limit = 270
        self._uart.init(baudrate=baudrate)

    def _comm(self, num=0, wdat='', get=False, timeout=100):
        self._uart.write("#{:03d}{}!".format(num,wdat))
        time.sleep_ms(5)
        if get:
            t_star=time.ticks_ms()
            while not self._uart.any():
                if time.ticks_diff(time.ticks_ms(), t_star) >timeout:
                    return False 
            buf = self._uart.readline()
            try:
                buf = buf.decode()
                if buf[0] == "#" and buf[-1] == "!":
                    return buf[1:-1]
            except:
                return None 

    def angle(self, num, angle=None, times=0):
        if angle is None:
            angle = self._comm(num, 'PRAD', True)
            if angle:
                return max(-1, round((int(angle[4:]) -500) * self._limit / 2000)) if angle[4:].isdigit() else None
        else:
            angle = max(0, min(self._limit, angle))
            angle = round(angle * 2000 / self._limit + 500)
            times = round(times * 1000)
            self._comm(num, "P{:04d}T{:04d}".format(angle, times))

    def motor(self, num, speed=None, circle=0):
        speed = max(-100, min(100, speed))
        speed = round((speed + 100) * 2000 / 200 + 500)
        self._comm(num, "P{:04d}T{:04d}".format(speed, circle))

    def name(self, num, new=None):
        if new is None:
            num = self._comm(num, 'PID', True)
            if num:
                return int(num[:3]) if num[:3].isdigit() else None
        else:
            self._comm(num, "PID{:03d}".format(new))

    def torque(self, num, force=True):
        self._comm(num, "PULR") if force else self._comm(num, "PULK")

    def info(self, num):
        dat = self._comm(num, 'PRTV', True)
        if dat:
            print('---------',dat)
            return int(dat[4:6]) if dat[4:6].isdigit() else None, int(dat[7:]) if dat[7:].isdigit() else None

    def mode(self, num, mode=0, dire=0):
        self._comm(num, 'PMOD{}'.format(mode * 2 + dire + 1))
        if mode==0:
            self._limit = 270
        if mode==1:
            self._limit = 180
        time.sleep_ms(100)

    def operate(self, num, cmd):
        self._comm(num, cmd)
