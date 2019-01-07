import sys
from PyQt5 import QtGui, QtWidgets, QtCore


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
	"""
	A custom System Tray Icon with functionality
	"""
	def __init__(self, icon, parent = None):
		"""
		Initializes a custom QSystemTrayIcon with the given parameters
		:icon: the icon to be displayed in the SystemTray
		:parent: this objects parent
		"""
		QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
		# create a menu (opened on right click by default)
		self.menu = QtWidgets.QMenu(parent)
		self.setContextMenu(self.menu) 

		# on system tray event (some kind of click)
		self.activated.connect(self.on_tray_event)

		# open action
		openAction = self.menu.addAction("Open")
		openAction.triggered.connect(self.open)

        # # about action
		# aboutAction = self.menu.addAction("About")
		# aboutAction.triggered.connect(self.about)

        # quit action
		quitAction = self.menu.addAction("Quit")
		quitAction.triggered.connect(self.quit)

		
	def open(self):
		"""
		Opens the applications main window again
		"""
		self.parent().setWindowState(self.parent().windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
		self.parent().show()


	def about(self):
		"""
		Opens a message box with about information
		"""
		QtWidgets.QMessageBox.about(self.parent(), "About", "Created by\nPhilipp Smoluk &\nMaximilian Tosch\n( ͡° ͜ʖ ͡°)")


	def quit(self):
		"""
		Quits the application after a clean up. The clean up might not be necessary
		"""
		if self.parent().loginAgent is not None:
			self.parent().loginAgent.stopLoginDaemon()
		self.hide() # to make the tray icon immediately disappear
		sys.exit(0)


	def on_tray_event(self, reason):
		"""
		Called when an event on the system tray icon occurs
		"""
		# left mouse click
		if reason == QtWidgets.QSystemTrayIcon.Trigger:
			self.parent().setWindowState(self.parent().windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
			self.parent().show()