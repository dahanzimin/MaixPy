import board
import audio,video
from Maix import I2S
import gc

sample_rate=16000

def voice_en(en):
	voice_en=board.pin(20,board.GPIO.OUT)
	voice_en.value(en)

def spk_init(sample_rate=16000):
	voice_en(1)
	board.register(22,board.FPIOA.I2S0_OUT_D1)
	board.register(23,board.FPIOA.I2S0_SCLK)
	board.register(21,board.FPIOA.I2S0_WS)
	wav_dev = I2S(I2S.DEVICE_0)
	wav_dev.channel_config(I2S.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT ,cycles = I2S.SCLK_CYCLES_32, align_mode = I2S.RIGHT_JUSTIFYING_MODE)
	wav_dev.set_sample_rate(sample_rate)
	return wav_dev

def mic_init(sample_rate=16000):
	voice_en(0)
	board.register(16,board.FPIOA.I2S0_IN_D0)
	board.register(14,board.FPIOA.I2S0_SCLK)
	board.register(15,board.FPIOA.I2S0_WS)
	wav_dev = I2S(I2S.DEVICE_0)
	wav_dev.channel_config(wav_dev.CHANNEL_0, wav_dev.RECEIVER, align_mode=I2S.STANDARD_MODE)
	wav_dev.set_sample_rate(sample_rate)
	return wav_dev


def audio_play(path,num=80):
	try:
		I2S=spk_init()
		player = audio.Audio(path=path)
		player.volume(num)
		wav_info=player.play_process(I2S)
		I2S.set_sample_rate(wav_info[1])
		while True:
			ret = player.play()
			if ret == None:
				print("[MixNo]:format error")
				break
			elif ret == 0:
				print("[MixNo]:play end")
				player.finish()
				break
		player.__deinit__()	
		del player
		del I2S	
		gc.collect()		
	except:
		raise NameError("[MixNo]:No audio file loaded ")
		
			
def audio_record(path,record_time):
	try:
		I2S=mic_init()
		recorder = audio.Audio(path=path, is_create=True, samplerate=sample_rate)
		queue = []
		frame_cnt = record_time*sample_rate//2048
		for i in range(frame_cnt):
			tmp = I2S.record(2048*2)
			if len(queue) > 0:
				ret = recorder.record(queue[0])
				queue.pop(0)
			I2S.wait_record()
			queue.append(tmp)
			print("record:{}s".format(round(((frame_cnt-i-1)/7.7) ,1)))
		recorder.finish()
		recorder.__deinit__()
		print("Audio record finish")
		del recorder
		del I2S
		gc.collect()
	except :
		raise NameError("[MixNo]:No audio file loaded ")		

def video_play(path,num=80):
	try:
		import lcd
		lcd.init()
		I2S=spk_init()
		vide = video.open(path)
		vide.volume(num)
		while True:
			ret = vide.play()
			if ret == None:
				print("[MixNo]:format error")
				break
			elif ret == 0:
				print("[MixNo]:play end")
				break
		vide.__del__()	
		del vide
		del I2S
		gc.collect()
	except:
		raise NameError("[[MixNo]:No video file loaded ")


def video_record(path,record_time):
	try:
		import sensor,lcd
		lcd.init()
		v = video.open(path, audio=False, record=True, interval=200000, quality=50)
		record_time=record_time*5
		for i in range(record_time):
			img = sensor.snapshot()
			lcd.display(img)
			v.record(img)
			print("record {}s".format((record_time-i-1)*0.2))
		v.record_finish()
		print("Video record finish")
		v.__del__()
		del v
		gc.collect()
	except :
		raise NameError("[MixNo]:Need to initialize camera")

