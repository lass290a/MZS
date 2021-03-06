import socket
import threading

class ThreadedServer:
	def __init__(self, host, port, events, callback):
		self.callback = callback
		self.events = events
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))

	def listen(self):
		self.sock.listen()
		self.callback()
		while True:
			client, address = self.sock.accept()
			client.settimeout(1)
			threading.Thread(target = self.listenToClient,args = (client,address)).start()

	def listenToClient(self, client, address):
		size = 1024
		while True:
			try:
				rawdata = client.recv(size).decode()
				if rawdata.startswith('{') and rawdata.endswith('}') and ';' not in rawdata:
					data = eval(rawdata)
				else:
					#print('Invalid Data Format')
					self.events({f'{address[0]}:{address[1]}':{'connection':'disconnect'}})
					client.close()
					return False
				if data:
					json_req = {f'{address[0]}:{address[1]}':data}
					response = self.events(json_req)
					client.send(response.encode())
				else:
					raise error('Client disconnected')
			except Exception as e:
				print(e)
				self.events({f'{address[0]}:{address[1]}':{'connection':'disconnect'}})
				client.close()
				return False

class NetworkClient:
	def __init__(self, timeout, callback):
		self.callback = callback
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(timeout)
		self.cb_instance = None

	def establishConnection(self, ip_address, port_nr):
		try:
			self.sock.connect((ip_address, port_nr))
			self.cb_instance = self.callback()
			return self.cb_instance
		except Exception as errormsg:
			if self.cb_instance == None:
				raise ConnectionRefusedError('host is unreachable')
			else:
				self.cb_instance.fail(errormsg)

	def sendData(self, strdata):
		try:
			self.sock.send(str(strdata).encode())
			response = self.sock.recv(1024).decode()
			return str(response)
		except socket.timeout as errormsg:
			self.cb_instance.fail(errormsg)