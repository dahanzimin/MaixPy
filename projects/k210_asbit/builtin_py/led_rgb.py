from asbit import *

class init():
    
    def __init__(self):
        
        self.rgb = [0,0,0]
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
        
        ob_rgb.set_led(0,(self.rgb[0],self.rgb[1],self.rgb[2]))
        ob_rgb.set_led(1,(0,0,0))
        ob_rgb.set_led(2,(0,0,0))
        ob_rgb.set_led(3,(0,0,0))
        ob_rgb.display()
        
    