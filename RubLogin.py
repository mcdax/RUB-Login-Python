from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSystemTrayIcon
from PyQt5.QtCore import Qt, QEvent
import sys
import design
from LoginAgent import LoginAgent
from AESCipher import AESCipher
import pickle
import signal
from SystemTrayIcon import SystemTrayIcon

class RubLogin(QMainWindow):
		
	def __init__(self):
		""" Initialize ui. Connect ui elements to functions. Initialize LoginAgent """
		super(RubLogin, self).__init__()
		uic.loadUi('design.ui', self)
		self.pushButton_login.clicked.connect(self.login)
		self.pushButton_logout.clicked.connect(self.logout)
		self.checkBox_auto.clicked.connect(self.checkBoxAuto)
		self.checkBox_save.clicked.connect(self.checkBoxSave)
		self.checkBox_auto_onstartup.clicked.connect(self.checkBoxAutoOnStartup)
		self.loginAgent = LoginAgent(self.textArea_log, self.checkBox_fileLogging, self.statusBar)
		self.guiEnabled = True
		
		aes_key = "Jgj-4f;5$f-d.kg&ghkDe-Fg&kSgZ5pd"
		self.aesCipher = AESCipher(aes_key)
		
		if len(sys.argv) > 1:
			for x in sys.argv:
				if x == "-nogui":
					self.guiEnabled = False
					
		# TODO comment
		try:
			data_file = open("data.bin", "rb") 
			self.checkBox_fileLogging.setChecked(pickle.load(data_file))
			self.checkBox_auto.setChecked(pickle.load(data_file))
			self.checkBox_save.setChecked(pickle.load(data_file))
			self.checkBox_auto_onstartup.setChecked(pickle.load(data_file))
			if self.checkBox_save.isChecked():
				self.lineEdit_id.setText(self.aesCipher.decrypt(pickle.load(data_file), pickle.load(data_file)))
				self.lineEdit_pass.setText(self.aesCipher.decrypt(pickle.load(data_file), pickle.load(data_file)))
			elif not self.guiEnabled:
				data_file.close()
				self.cl_exit("No login data saved")
			data_file.close()
		except (FileNotFoundError, EOFError): 
			if not self.guiEnabled:
				self.cl_exit("No login data saved")
				
		if self.guiEnabled:
			# systemtray icon
			self.trayIcon = SystemTrayIcon(QtGui.QIcon("logo.png"), self)
			self.show()
		
		if self.checkBox_auto_onstartup.isChecked():
			self.checkBox_auto.setChecked(True)
			self.login()

	def cl_exit(self, msg):
		print(msg)
		sys.exit(0)
				
	def login(self):
		""" Initiate login: Collect information from ui elements and start the login agent """

		loginID = self.lineEdit_id.text()
		pwd = self.lineEdit_pass.text()

		if self.checkBox_auto.isChecked():
			res = self.loginAgent.autoLogin(loginID, pwd) # auto login
		else:
			res = self.loginAgent.login(loginID, pwd, None, False) # login
		
		self.statusBar().showMessage("Login succeeded" if res else "Login failed")
			
		data_file = open("data.bin", "wb")
			
		pickle.dump(self.checkBox_fileLogging.isChecked(), data_file)
		pickle.dump(self.checkBox_auto.isChecked(), data_file)
		if res and self.checkBox_save.isChecked():
			pickle.dump(self.checkBox_auto_onstartup.isChecked(), data_file)
			pickle.dump(self.checkBox_save.isChecked(), data_file)
			[enc_id, iv_id] = self.aesCipher.encrypt(loginID)
			[enc_pwd, iv_pwd] = self.aesCipher.encrypt(pwd)
			pickle.dump(enc_id, data_file)
			pickle.dump(iv_id, data_file)
			pickle.dump(enc_pwd, data_file)
			pickle.dump(iv_pwd, data_file)
		elif not res and self.checkBox_save.isChecked():
			pickle.dump(False, data_file) # uncheck checkBox_save on login fail
			
		data_file.close()
		
		return res


	def logout(self):
		""" Clean up and logout """
		self.loginAgent.logout()
		
		
	def closeEvent(self, event):
		""" Clean up for when program is exited """
		self.loginAgent.stopLoginDaemon()
		event.accept()

	def checkBoxAuto(self):
		""" If the checkbox is unchecked by user, cancel the running auto login """
		if not self.checkBox_auto.isChecked():
			self.loginAgent.stopLoginDaemon()
			
	def checkBoxAutoOnStartup(self):
		if self.checkBox_auto_onstartup.isChecked():
			self.checkBox_save.setChecked(True)
			
	def checkBoxSave(self):
		if not self.checkBox_save.isChecked():
			self.checkBox_auto_onstartup.setChecked(False)

	def keyPressEvent(self, event):
		"""
		handle key press events:
		ENTER - does the same as clicking the login button
	    """
		if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
			# TODO
			pass
	
	def changeEvent(self, event):
		print("ChangeEvent!")
		# check if loginAgent was already instantiated in this class and if the auto login is running
		if hasattr(self, "loginAgent") and self.loginAgent is not None and self.loginAgent.is_auto_login_running():
			if event.type() == QEvent.WindowStateChange:
			# detect the window minimized event
				if self.windowState() & Qt.WindowMinimized:
					# show system tray icon, display notification, hide main window
					self.trayIcon.show()
					self.trayIcon.showMessage(self.windowTitle(), "Auto login is running in the background", QtWidgets.QSystemTrayIcon.Information, 5000)
					self.hide()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
	window = RubLogin()
	window.setWindowIcon(QtGui.QIcon('logo.png'))
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	sys.exit(app.exec_())