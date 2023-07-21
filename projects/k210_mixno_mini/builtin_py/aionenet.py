import base64
import json
import random
from machine import UART
import urequests as request

def nic_init(account,password):	
	from network_no import wlan_connect
	wlan_connect(account,password)

class SimpleEncode():
	keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz~!@#$%^&*()_+-={}[]:;<,>.?/|"
	keyLength = len(keyStr)
	encryptionA = 17
	encryptionB = 8
	decodeA = 0
	preCountMax = 15
	postCount = 5
	randomChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop"
	randomCharLength = len(randomChar)
	#base64字符
	ALPHABET = "ABCDEFGHIJKLMN0123456789OPQRSTUVWXYZ+/abcdefghijklmnopqrstuvwxyz"
	STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"  # 标准的字符串索引

	#找到密钥
	for i in range(1,keyLength):
			if (encryptionA * i) % keyLength == 1:
				decodeA = i

	def base64Encode(self,sourceStr):
		encode = ""
		for ch in base64.b64encode(sourceStr.encode()).decode():
			if ch == '=':
				encode += '='
			else:
				for i in range(64):
					if ch == self.STANDARD[i]:
						encode += self.ALPHABET[i]
		return encode

	def encrpyt(self,sourceStr):
		srcLength = len(sourceStr)
		#先加入干扰字符的数量
		addCharCount = random.randint(1,self.preCountMax) if srcLength < self.preCountMax else 0
		#随机字符
		sb = str(addCharCount)+"|"
		for i in range(addCharCount):
			sb += self.randomChar[random.randint(0,self.randomCharLength-1)]

		sb += sourceStr
		#尾部固定增加x个字符
		for i in range(self.postCount):
			sb += self.randomChar[random.randint(0,self.randomCharLength-1)]

		#base64 加密
		base64Str = self.base64Encode(sb)

		destStr = ''
		for i in range(len(base64Str)):
			#找到字符所在位置
			position = self.keyStr.find(base64Str[i])

			#对字符进行转换
			y = (self.encryptionA * position + self.encryptionB) % self.keyLength

			#找到替换后的字符

			destStr += self.keyStr[y]

		return destStr

def token(account,password):
	url = 'http://ai.heclouds.com:9090/v1/user/oneNetLogin'
	headers = {
		'Content-Type': 'application/json',
	}
	simpleencode = SimpleEncode()
	data = {'account': account, 'password': simpleencode.encrpyt(password)}
	try:
		req = request.post(url, data=json.dumps(data), headers=headers)
		req = json.loads(req.text)
	except Exception as e:
		raise Exception("[MixNo]:Network request error",e)

	if "success" == req['message']:
		return req['data']['loginToken']
	else:
		raise RuntimeError(req['message'],req['stateCode']) 

def post_ai(img,urlx,Token):
	ur = 'http://183.230.40.32:9090/v1/aiApi/picture/MixPY'
	url=ur.replace("MixPY",urlx)
	headers ={
		'Content-Type':'application/json',
		'Login-Token':'Token'
		}	
		
	headers['Login-Token']=Token
	
	imge = img.compressed(quality=50)
	file =imge.to_bytes()
	str = base64.b64encode(file).decode()
	data = {'picture':[str]}
	req = request.post(url,data=json.dumps(data),headers=headers)
	return json.loads(req.text)
	#return eval(req.text)