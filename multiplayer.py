import socket
import threading
import sys

class ThreadedServer(object):
	def __init__(self, host, port, events):
		self.events = events
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))

	def listen(self): 
		self.sock.listen()
		while True:
			client, address = self.sock.accept()
			client.settimeout(5)
			threading.Thread(target = self.listenToClient,args = (client,address)).start()

	def listenToClient(self, client, address):
		size = 1024
		while True:
			try:
				data = eval(client.recv(size).decode())
				if data:
					json_req = {f'{address[0]}:{address[1]}':data}
					response = self.events(json_req)
					client.send(response.encode())
				else:
					raise error('Client disconnected')
			except:
				client.close()
				return False

if __name__ == "__main__":
	ThreadedServer('',4422, 0).listen()