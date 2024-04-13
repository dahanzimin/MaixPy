import board
from modules import ws2812

class init():
    
    def __init__(self):
        
        
        self.rgb = [0,0,0]
        self.ledPin=ws2812(board.pin_D[23],4)
        self.display()
        
    def on(self,index):
        
        self.rgb[index] = 10
        self.display()

    def off(self,index):
        
        self.rgb[index] = 0
        self.display()

    def toggle(self,index):
        
        if self.rgb[index]:
            self.rgb[index] = 0
        else:
            self.rgb[index] = 10
            
        self.display()
        
    def display(self):
        
        self.ledPin.set_led(0,(self.rgb[0],self.rgb[1],self.rgb[2]))
        self.ledPin.set_led(1,(0,0,0))
        self.ledPin.set_led(2,(0,0,0))
        self.ledPin.set_led(3,(0,0,0))
        self.ledPin.display()
    