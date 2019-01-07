import urllib
import urllib.request  as urllib2
from TimerThread import TimerThread 
from datetime import datetime
import threading
from bs4 import BeautifulSoup
import socket

CONNECTION_CHECK_SERVERS = ["www.google.com", "www.microsoft.com", "www.youporn.com"]
CONNECTION_CHECK_INTERVALL = 5
LOGIN_URL = 'https://login.rz.ruhr-uni-bochum.de/cgi-bin/laklogin'
LOGIN_FORM_URL = 'https://login.rz.ruhr-uni-bochum.de/cgi-bin/start'
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0' }
LOGFILE = 'login.log'


class LoginAgent():
	def __init__(self, logField , checkBox_FileLogging, statusbar):
		"""
		Initiate a new login agent. Save the required urls and other information in variables
		"""
		self.checkBox_FileLogging = checkBox_FileLogging
		self.logField = logField
		self.statusbar = statusbar
		self.statusbarAnimThread = None
		self.autoLoginThread = None
		self.autoLoginRunning = False


	def getIP(self):
		"""
		Sends a request to the loginFormUrl and parses the result to retrieve the users IP address
		"""
		try:
			response = urllib2.urlopen(LOGIN_FORM_URL)
		except urllib.error.URLError:
			return None
			
		soup = BeautifulSoup(response.read(), 'html.parser')
		return soup.find(attrs={"name": "ipaddr"})['value']


	def autoLogin(self, loginID, password):
		print('autoLogin()')
		self.stopLoginDaemon()
		if self.login(loginID, password, None, True):
			self.autoLoginThread = TimerThread(CONNECTION_CHECK_INTERVALL, self.loginDaemon, [loginID, password, None, True])
			self.autoLoginThread.start()
			self.statusbarAnimThread = TimerThread(.45, self.statusbarAnim, ["Auto login running", "."], False)
			self.statusbarAnimThread.start()
			self.autoLoginRunning = True
			return True
		return False
				

	def loginDaemon(self, loginID, password, ipaddr = None, auto = True):
		print('loginDaemon()')
		if not self.is_connected():
			self.login(loginID, password, ipaddr, auto)
		

	def stopLoginDaemon(self):
		print('stopLoginDaemon()')
		if self.autoLoginThread is not None:
			self.autoLoginThread.terminate()
		if self.statusbarAnimThread is not None:
			self.statusbarAnimThread.terminate()
		if self.statusbar is not None:
			self.statusbar().clearMessage()
		self.autoLoginRunning = False

	def login(self, loginID, password, ipaddr = None, auto = False):
		"""
		Login the user with ID and password 
		This function sends a request to the login page and displays the result of the response in ui element(s)
		If logging is enabled, the results are written to a log file
		"""		
		if not auto:
			self.stopLoginDaemon()

		if ipaddr is None:
			ipaddr = self.getIP()
			if ipaddr is None: # self.getIP() returns None if there is no access to the login page
				self.log("Connection issue occurred\n\n")
				#self.cancelTimers() TODO simply remove if no problems occur. Old
				self.statusbar().showMessage("Connection issue occurred")
				return False
		
		values = { 'code' : '1', 'loginid' : loginID, 'password' : password, 'ipaddr' : ipaddr, 'action' : 'Login' }
		page_response = self.urlrequest(values, HEADER)
		
		msg = ''
		if b"Authentisierung gelungen" in page_response:
			msg = "[{0}] Login succeeded - IP: {1}\n\n".format(str(datetime.now()), ipaddr)
			self.log(msg)
			return True
		else:
			soup = BeautifulSoup(page_response, 'html.parser')
			error_msg = [text.get_text() for text in soup.find_all("big") if ('Authentisierung fehlgeschlagen' in text.get_text())][0] # error_msg: First string that contains 'Authentisierung fehlgeschlagen'
			error_msg = [emsg for emsg in error_msg.split('\n') if emsg and not emsg[0].isdigit()]
			msg = "[{0}] Issue occurred:\n{1}\n\n".format(str(datetime.now()), "\n".join(str(emsg) for emsg in error_msg)) # error_msg.split('\n')[0]: The error message ends with a line break
			self.log(msg)
			#self.cancelTimers() TODO simply remove if no problems occur. Old
			return False



	def logout(self, ipaddr = None):
		"""
		Logout the user with his IP
		This function sends a request to the login page and displays the result of the response in ui element(s)
		The request only uses the users IP address. ID and password are not required
		If logging is enabled, the results are written to a log file
	    """
		self.stopLoginDaemon()
			
		if ipaddr is None:
			ipaddr = self.getIP()
		values = { 'code' : '1', 'ipaddr' : ipaddr, 'action' : 'Logout' }
		page_response = self.urlrequest(values, HEADER)
		fileLogging = self.checkBox_FileLogging.isChecked()

		msg = ''
		if b"Logout erfolgreich" in page_response:
			msg = "[{0}] Logout succeeded - IP: {1}\n".format(str(datetime.now()), ipaddr)
			self.log(msg)
			return True
		else:
			soup = BeautifulSoup(page_response, 'html.parser')
			error_msg = "[{0}] Logout failed - IP: {1}\n".format(str(datetime.now()), ipaddr)
			msg = "[{0}] Issue occurred:\n{1}\n\n".format(str(datetime.now()), error_msg)
			self.log(msg)
			return False

	
	def urlrequest(self, values, header):
		""" 
		URL request for given values and headers. Return response 
		"""
		data = urllib.parse.urlencode(values).encode('utf-8')
		req = urllib2.Request(LOGIN_URL, data, HEADER)
		return urllib2.urlopen(req).read()


	def log(self, msg):
		"""
		Log a non-empty message 
		"""
		self.logField.insertPlainText(msg)
		print(msg)
		if self.checkBox_FileLogging.isChecked():
			f = open(LOGFILE, 'a')
			if msg: f.write(msg)
			f.close


	def statusbarAnim(self, msg):
		"""
		Three dot animation for statusbar when auto login is running
		:msg: the message to be shown in a list (intended to be used in combination with a threaded timer)
		      the message to be displayed is accessed through msg[0]
			  the animation character is accessed through msg[1]
		"""
		msg[0] = msg[0] + msg[1] if msg[0].count(msg[1]) < 3 else msg[0].replace(msg[1], '')
		self.statusbar().showMessage(msg[0])

		
	def is_connected(self, serverindex = 0):
		try:
			# see if we can resolve the host name -- tells us if there is
			# a DNS listening
			host = socket.gethostbyname(CONNECTION_CHECK_SERVERS[serverindex])
			# connect to the host -- tells us if the host is actually
			# reachable
			s = socket.create_connection((host, 80), 2)
			return True
		except:
			if serverindex is len(CONNECTION_CHECK_SERVERS)-1:
				return False
			else:
				return self.is_connected(serverindex+1)
				
	def is_auto_login_running(self):
		return self.autoLoginRunning