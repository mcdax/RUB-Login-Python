import base64
import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class AESCipher(object):

	def __init__(self, key): 
		self.key = str.encode(key)
		self.bs = 32

	def encrypt(self, raw):
		backend = default_backend()
		iv = os.urandom(16)
		cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
		encryptor = cipher.encryptor()
		ct = encryptor.update(str.encode(self._pad(raw))) + encryptor.finalize()
		return [ct, iv]

	def decrypt(self, enc, iv):
		backend = default_backend()
		cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
		decryptor = cipher.decryptor()
		plain = decryptor.update(enc) + decryptor.finalize()
		return self._unpad(plain).decode("utf-8")

	def _pad(self, s):
		return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

	@staticmethod
	def _unpad(s):
		return s[:-ord(s[len(s)-1:])]