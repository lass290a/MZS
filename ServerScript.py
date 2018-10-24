from multiplayer import ThreadedServer

class Database:
	def __init__(self, username=None, parent=None):
		self.username = username
		self.parent = parent
		self.players = []
		self.player_data = {}

	def addPlayer(self, object, input={}):
		self.subObjects.append(object(parent=self, **input))
		return self.players[-1]

	def deletePlayer(self, object=None):
		if object == None:
			for obj in players




server_data = {'player_data':{}}

address_id = {}


def server_started():
	print('Server is running!')

def event_handler(raw_json):
	#print(raw_json)
	address = str(list(raw_json.keys())[0])
	event_data = raw_json[address]


	if 'connection' in list(event_data.keys()):
		if event_data['connection'] == 'disconnect':
			try:
				del address_id[address]
			except:
				pass
			return False

	if 'start_connection' in list(event_data.keys()):
		if event_data['start_connection']['username'] in [username[0] for username in list(address_id.values())]:
			for user in [password for password in list(address_id.values())]:
				if event_data['start_connection']['username'] == user[0]:
					if event_data['start_connection']['password'] == user[1]:
						player_ref = event_data['start_connection']['username']
						return str({'start_connection':server_data['player_data'][player_ref]})
					else:
						return str({'connection_denied':'wrong_password'})
		else:
			address_id[address] = (event_data['start_connection']['username'],event_data['start_connection']['password'])
			player_ref = event_data['start_connection']['username']
			server_data['player_data'][player_ref] = {'position':(0,0),'angle':90}
			print('User Created!')
			return str({'start_connection':server_data['player_data'][player_ref]})
	else:
		for user in address_id:
			if address == user:
				player_ref = address_id[user][0]

	for event in event_data['player_data']:
		server_data['player_data'][player_ref][event] = event_data['player_data'][event]

	send_data = {'player_data':{}}
	for user in server_data['player_data']:
		if user != player_ref and user in [username[0] for username in list(address_id.values())]:
			send_data['player_data'][user] = server_data['player_data'][user]
	return str(send_data)


ThreadedServer('',4422, event_handler, server_started).listen()