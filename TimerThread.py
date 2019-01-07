import threading
import time

class TimerThread(threading.Thread):
	"""
	Represents a timer that calls a function with provided arguments every n seconds
	"""
	def __init__(self, timeout, callback, args, unpack=True):
		"""
		:timeout: the timeout intervall in which the callback function will be called
		:callback: the function that will be called
		:args: a list of arguments the callback function will be called with
		:unpack: unpack the argument list when calling the function or leaving it as a list
		         a list is preferred when the function alters the arguments and this should be
				 preserved. The list is mutable and passed by reference in this case
		"""
		threading.Thread.__init__(self)
		self.timeout = timeout
		self.callback = callback
		self.callback_args = args
		self.unpack = unpack
		self.terminate_event = threading.Event()
		
	def run(self):
		"""
		Calls the callback function every timeout-seconds 
		with provided arguments while no terminate event is called
		"""
		while not self.terminate_event.wait(self.timeout):
			if self.unpack:
				self.callback(*self.callback_args)
			else:
				self.callback(self.callback_args)
			# self.callback(*self.callback_args if self.unpack else self.callback_args) # ternary operator doesn't work here..

	def terminate(self):
		"""
		Terminate all execution of this threaded timer
		"""
		self.terminate_event.set()