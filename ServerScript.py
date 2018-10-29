from multiplayer import ThreadedServer

class Object:
	def __init__(self, username=None, type=None, parent=None, position=(0,0), angle=0, fired=0):
		self.username = username
		self.position = position
		self.angle = angle
		self.type = type
		self.fired = fired
		self.parent = parent
		self.subObjects=[]

	def create(self, object, input={}):
		self.subObjects.append(object(parent=self, **input))
		return self.subObjects[-1]

	def delete(self, string=''):
		if string=='':
			string=str(self.parent)

		for obj in self.subObjects:
			obj.delete(string)
		
		if self.parent!=None:
			for index, obj in enumerate(self.parent.subObjects):
				if obj==self:
					self.parent.subObjects.pop(index)
					if self.parent.subObjects!=[] and str(self.parent)!=string:
						self.parent.subObjects[0].delete(string)

	def find(self, username=None, type=None):
		if username == None and type == None:
			raise error('find() needs an input')
		elif username != None:
			for object in self.subObjects:
				if object.username==username:
					return object
			return False
		elif type != None:
			objecttype=[]
			for object in self.subObjects:
				if object.type==type:
					objecttype.append(object)
			return objecttype

class Database(Object):
	def __init__(self):
		super().__init__()
		pass

class Player(Object):
	def __init__(self, username, parent):
		super().__init__(
			username=username,
			type='Player',
			position=(0,0),
			angle=0,
			fired=0,
			parent=parent)

address_id = {}

database = Database()

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
		if event_data['start_connection']['username'] in list(address_id.values()):
			for user in list(address_id.values()):
				if event_data['start_connection']['username'] == user:
					player_ref = database.find(username=user)
					return str({'start_connection':{'position':player_ref.position}})
				else:
					return str({'connection_denied':'wrong_password'})
		else:
			address_id[address] = event_data['start_connection']['username']
			database.create(Player, {'username':event_data['start_connection']['username']})
			player_ref = database.find(username=event_data['start_connection']['username'])
			print('User Created!')
			return str({'start_connection':{'position':player_ref.position}})
	else:
		for user_ip in address_id:
			if address == user_ip:
				player_ref = database.find(username=address_id[user_ip])

	for event in event_data['player_data']:
		setattr(player_ref, event, event_data['player_data'][event])

	send_data = {'player_data':{}}
	for user in list(address_id.values()):
		if user != player_ref.username:
			temp_user = database.find(username=user)
			send_data['player_data'][user] = {'position':temp_user.position, 'angle':temp_user.angle, 'fired':temp_user.fired}
	return str(send_data)


ThreadedServer('',4422, event_handler, server_started).listen()