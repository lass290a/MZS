import socket
from sys import exit
from time import sleep
from random import randint

class NetworkClient:
	def __init__(self, timeout, success_callback, failed_callback):
		self.success_callback = success_callback
		self.failed_callback = failed_callback
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(timeout)

	def establishConnection(self, ip_address, port_nr):
		try:
			self.sock.connect((ip_address, port_nr))
			self.success_callback()
		except Exception as errormsg:
			self.failed_callback(errormsg)

	def sendData(self, strdata):
		try:
			self.sock.send(str(strdata).encode())
			response = self.sock.recv(1024).decode()
			return str(response)
		except socket.timeout as errormsg:
			self.failed_callback(errormsg)


def conn_success():
	print('CONNECTION SUCCESSFUL')

def conn_error(msg):
	print(f'CONNECTION ERROR: {msg}')
	exit()


if __name__ == "__main__":
	server = NetworkClient(10, conn_success, conn_error)
	server.establishConnection("localhost", 4422)
	while 1:

		resp = server.sendData(str({'position':(randint(0,10),randint(0,10)), 'rotation':randint(0,10)}))
		print(resp)
		sleep(2)