from multiplayer import ThreadedServer

server_data = {'players':{
}}

clients = {}

test_json = {}


def event_handler(json_events):
	ipaddress = str(list(json_events.keys())[0])
	if 'name' in list(json_events[ipaddress].keys()):
		if f"{ipaddress}:{json_events[ipaddress]['name']}" in clients:
			player_ref = str(clients[f"{ipaddress}:{json_events[ipaddress]['name']}"])
		else:
			clients[f"{ipaddress}:{json_events[ipaddress]['name']}"] = f'Player{len(clients)+1}'
			player_ref = str(clients[f"{ipaddress}:{json_events[ipaddress]['name']}"])
			server_data['players'][player_ref] = {'name':json_events[ipaddress]['name'], 'position':(0,0), 'rotation':90, 'fired':False}
			print('User Created!')
	for event in json_events[ipaddress]:
		server_data['players'][player_ref][event] = json_events[ipaddress][event]
	return str(server_data)


ThreadedServer('',4422, event_handler).listen()