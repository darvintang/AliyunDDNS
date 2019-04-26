import os, json, requests, time, signal

from xml.etree.ElementTree import fromstring
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest, DescribeDomainRecordsRequest, AddDomainRecordRequest


SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
CONFIG_FOLDER = os.path.join(SCRIPT_FOLDER, 'conf.d')
LOG_PATH = os.path.join(SCRIPT_FOLDER, 'execute.log')
LOG_PATH_BACK = os.path.join(SCRIPT_FOLDER, 'execute.log.back')
LOCK_PATH = os.path.join(SCRIPT_FOLDER, '.lock')
LOG_FILE_MAX_SIZE = 1024*1024	#在更新或添加解析记录前判断日志文件大小

class Client:
	
	def __init__(self, acckey, secret):
		self.clt = AcsClient(acckey, secret)
	
	def execute(self, newIp, rrKeyWord, domainName):
		
		self.newIp = newIp;
		self.rrKeyWord = rrKeyWord;
		self.domainName = domainName;
		
		self.recordId = ''
		self.oldIp = ''
		
		self.getDescribeDomainRecord()
		
		if self.recordId == '':
			self.addDomainRecord()
		else:
			if self.oldIp == self.newIp:
				self.writeLog('The DNS record already exists.')
			else:
				self.updateDomainRecord()

	def getDescribeDomainRecord(self):
		get = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
		get.set_DomainName(self.domainName)
		get.set_RRKeyWord(self.rrKeyWord)
		getResult = self.clt.do_action(get)
		
		xml = fromstring(getResult.decode())
		
		xmlOldIp = xml.find('DomainRecords/Record/Value')
		if xmlOldIp != None:
			self.oldIp = xmlOldIp.text
		
		xmlRecordId = xml.find('DomainRecords/Record/RecordId')
		if xmlRecordId != None:
			self.recordId = xmlRecordId.text

	def updateDomainRecord(self):
		update = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
		update.set_RR(self.rrKeyWord)
		update.set_RecordId(self.recordId)
		update.set_Type('A')
		update.set_Value(self.newIp)
		update.set_Line("default")
		updateResult = self.clt.do_action(update)
		
		xml = fromstring(updateResult.decode())
		if xml.find('Error') != None:
			message = xml.find('Error/Message').text
		else:
			message = 'The DNS record update success.'
		self.writeLog(message)
		

	def addDomainRecord(self):
		add = AddDomainRecordRequest.AddDomainRecordRequest()
		add.set_RR(self.rrKeyWord)
		add.set_Type('A')
		add.set_Value(self.newIp)
		add.set_Line("default")
		add.set_DomainName(self.domainName)
		addResult = self.clt.do_action(add)


		xml = fromstring(addResult.decode())
		if xml.find('Error') != None:
			message = xml.find('Error/Message').text
		else:
			message = 'The DNS record add success.'
		self.writeLog(message)

	def writeLog(self,message):
		if isinstance(message, bytes):
			message = message.decode()

		with open(LOG_PATH, "a+") as f:
			f.write(time.strftime('%Y/%m/%d %H:%M:%S %z ') + self.rrKeyWord + '.' + self.domainName + ' ==> ' + self.newIp +' ' + message)
			f.write("\n")
	
def getIP():
	r = requests.get("http://ipv4.icanhazip.com")
	return r.text.strip('\n')
	
def checkLock():
	if os.path.exists(LOCK_PATH):
		with open(LOCK_PATH, 'r') as f:
			pid = f.read()
		try:
			os.kill(int(pid), signal.SIGTERM)
		except OSError:
			pass
		os.remove(LOCK_PATH)
		checkLock()
	else:
		with open(LOCK_PATH, 'w')as f:
			f.write(str(os.getpid()))

def removeLock():
	os.remove(LOCK_PATH)

def startWithConfigPath(path):
	newIp = getIP()
	with open(path, 'r') as f:
		configs = json.load(f)
	for config in configs:
		client = Client(config['Key'],config['Secret'])
		domainsInfo = config['Domains']
		for domainInfo in domainsInfo:
			client.execute(newIp, domainInfo['RR'], domainInfo["Domain"])

checkLock()
if os.path.isfile(LOG_PATH):
	size = os.path.getsize(LOG_PATH)
	if size > LOG_FILE_MAX_SIZE:
		os.rename(LOG_PATH,LOG_PATH_BACK)

w = os.walk(CONFIG_FOLDER)

for a,b,c in w:
	for fn in c:
		if fn.endswith('.config'):
			configPath = os.path.join(a, fn)
			startWithConfigPath(configPath)
								
removeLock()
try:
	sys.exit(0)
except:
	print('Program is dead.')