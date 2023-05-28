import gc
import board
from Maix import I2S
from machine import Timer
from speech_recognizer import asr

board.register(20,board.FPIOA.I2S0_IN_D0)
board.register(18,board.FPIOA.I2S0_SCLK)
board.register(19,board.FPIOA.I2S0_WS)
rx  = I2S(I2S.DEVICE_0)
rx.channel_config(rx.CHANNEL_0, rx.RECEIVER, align_mode=I2S.STANDARD_MODE)
rx.set_sample_rate(16000)

try:
	gc.collect()
	tim.stop()
	asr.__del__()
	del asr
	del tim
except Exception:
    pass

	
class ASR(asr):

	asr_vocab = ["lv", "shi", "yang", "chun", "yan", "jing", "da", "kuai", "wen", "zhang", "de", "di", "se", "si", "yue", "lin", "luan", "geng", "xian", "huo", "xiu", "mei", "yi", "ang", "ran", "ta", "jin", "ping", "yao", "bu", "li", "liang", "zai", "yong", "dao", "shang", "xia", "fan", "teng", "dong", "she", "xing", "zhuang", "ru", "hai", "tun", "zhi", "tou", "you", "ling", "pao", "hao", "le", "zha", "zen", "me", "zheng", "cai", "ya", "shu", "tuo", "qu", "fu", "guang", "bang", "zi", "chong", "shui", "cuan", "ke", "shei", "wan", "hou", "zhao", "jian", "zuo", "cu", "hei", "yu", "ce", "ming", "dui", "cheng", "men", "wo", "bei", "dai", "zhe", "hu", "jiao", "pang", "ji", "lao", "nong", "kang", "yuan", "chao", "hui", "xiang", "bing", "qi", "chang", "nian", "jia", "tu", "bi", "pin", "xi", "zou", "chu", "cun", "wang", "na", "ge", "an", "ning", "tian", "xiao", "zhong", "shen", "nan", "er", "ri", "zhu", "xin", "wai", "luo", "gang", "qing", "xun", "te", "cong", "gan", "lai", "he", "dan", "wei", "die", "kai", "ci", "gu", "neng", "ba", "bao", "xue", "shuai", "dou", "cao", "mao", "bo", "zhou", "lie", "qie", "ju", "chuan", "guo", "lan", "ni", "tang", "ban", "su", "quan", "huan", "ying", "a", "min", "meng", "wu", "tai", "hua", "xie", "pai", "huang", "gua", "jiang", "pian", "ma", "jie", "wa", "san", "ka", "zong", "nv", "gao", "ye", "biao", "bie", "zui", "ren", "jun", "duo", "ze", "tan", "mu", "gui", "qiu", "bai", "sang", "jiu", "yin", "huai", "rang", "zan", "shuo", "sha", "ben", "yun", "la", "cuo", "hang", "ha", "tuan", "gong", "shan", "ai", "kou", "zhen", "qiong", "ding", "dang", "que", "weng", "qian", "feng", "jue", "zhuan", "ceng", "zu", "bian", "nei", "sheng", "chan", "zao", "fang", "qin", "e", "lian", "fa", "lu", "sun", "xu", "deng", "guan", "shou", "mo", "zhan", "po", "pi", "gun", "shuang", "qiang", "kao", "hong", "kan", "dian", "kong", "pei", "tong", "ting", "zang", "kuang", "reng", "ti", "pan", "heng", "chi", "lun", "kun", "han", "lei", "zuan", "man", "sen", "duan", "leng", "sui", "gai", "ga", "fou", "kuo", "ou", "suo", "sou", "nu", "du", "mian", "chou", "hen", "kua", "shao", "rou", "xuan", "can", "sai", "dun", "niao", "chui", "chen", "hun", "peng", "fen", "cang", "gen", "shua", "chuo", "shun", "cha", "gou", "mai", "liu", "diao", "tao", "niu", "mi", "chai", "long", "guai", "xiong", "mou", "rong", "ku", "song", "che", "sao", "piao", "pu", "tui", "lang", "chuang", "keng", "liao", "miao", "zhui", "nai", "lou", "bin", "juan", "zhua", "run", "zeng", "ao", "re", "pa", "qun", "lia", "cou", "tie", "zhai", "kuan", "kui", "cui", "mie", "fei", "tiao", "nuo", "gei", "ca", "zhun", "nie", "mang", "zhuo", "pen", "zun", "niang", "suan", "nao", "ruan", "qiao", "fo", "rui", "rao", "ruo", "zei", "en", "za", "diu", "nve", "sa", "nin", "shai", "nen", "ken", "chuai", "shuan", "beng", "ne", "lve", "qia", "jiong", "pie", "seng", "nuan", "nang", "miu", "pou", "cen", "dia", "o", "zhuai", "yo", "dei", "n", "ei", "nou", "bia", "eng", "den", "_"]

	def get_asr_list(string='xiao-ai-fas-tong-xue'):
		return [__class__.asr_vocab.index(t) for t in string.split('-') if t in __class__.asr_vocab]

	def get_asr_string(listobj=[117, 214, 257, 144]):
		return '-'.join([__class__.asr_vocab[t] for t in listobj if t < len(__class__.asr_vocab)])

	def config(self, sets):
		self.set([(sets[key], __class__.get_asr_list(key)) for key in sets])

	def recognize(self):
		res = self.result()
		if res != None:
			return [__class__.get_asr_string(res[0][1]),res[0][0]]
		return None

def on_timer(timer):
	timer.callback_arg().state()

def ASR_init(shift=0):

	#default: shift=0:MixNo  MIXHO  shift=1:MixPY
	asr = ASR(0x500000, I2S.DEVICE_0, 3, shift) 
	tim = Timer(Timer.TIMER0, Timer.CHANNEL2, mode=Timer.MODE_PERIODIC, period=64, callback=on_timer, arg=asr)
	tim.start()
	return asr
