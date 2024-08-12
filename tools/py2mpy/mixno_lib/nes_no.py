import nes,board

def joystick_init(cs_pin,clk_pin,mosi_pin,miso_pin,voll):	
	board.register(cs_pin, board.FPIOA.GPIOHS0)
	board.register(clk_pin, board.FPIOA.GPIOHS1)
	board.register(mosi_pin, board.FPIOA.GPIOHS2)
	board.register(miso_pin, board.FPIOA.GPIOHS3)
	nes.init(nes.JOYSTICK, cs=board.FPIOA.GPIOHS0, clk=board.FPIOA.GPIOHS1, mosi=board.FPIOA.GPIOHS2, miso=board.FPIOA.GPIOHS3,vol=voll)

def keyboard_init(voll):	
	nes.init(nes.KEYBOARD,vol=voll)

def run(path):
	nes.load(path)
	while True:
		nes.loop()