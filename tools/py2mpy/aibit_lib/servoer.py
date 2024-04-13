import board
from machine import PWM

class Servo:
    def __init__(self, timer,pin):
        self._pwm = PWM(timer, freq=50, duty=2.5, pin=board.pin_D[pin])
        self._angle = None

    def set_angle(self,angle):
        self._angle=angle
        self._pwm.duty(self._angle/18.0+2.5)
    
    def read_angle(self):
        return self._angle
 