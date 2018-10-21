from multiplayer import ThreadedServer

server_data = {'players':{
	'Player1':{
		'name':'AlexBMJ',
		'position':(0,0),
		'rotation':90
		}
}}

clients = {'192.168.0.10:43234':'Player1'}

test_json = {'192.168.0.10:43234':{'position':(3,4), 'rotation':180}}


def event_handler(json_events):
	ipaddress = list(json_events.keys())[0]
	if ipaddress in clients:
		player_ref = str(clients[list(json_events.keys())[0]])
	else:
		clients[str(list(json_events.keys())[0])] = f'Player{len(clients)+1}'
		player_ref = str(clients[list(json_events.keys())[0]])
		server_data['players'][player_ref] = {'name':'Steve', 'position':(0,0), 'rotation':90}
		print('user created!')
	for event in json_events[ipaddress]:
		server_data['players'][player_ref][event] = json_events[ipaddress][event]
	return str(server_data)


ThreadedServer('',4422, event_handler).listen()