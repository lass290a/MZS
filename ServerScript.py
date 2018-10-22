from multiplayer import ThreadedServer

server_data = {'player_data':{

}}

{'192.168.0.1:8888':{'start_connection':{'username':'meatface','password':'1234'}}}

address_id = {}


def server_started():
	print('Server is running!')

def event_handler(raw_json):
	#print(raw_json)
	address = str(list(raw_json.keys())[0])
	event_data = raw_json[address]

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
		if str(user) != str(player_ref):
			send_data['player_data'][user] = server_data['player_data'][user]
			print(send_data)
	return str(send_data)


ThreadedServer('',4422, event_handler, server_started).listen()