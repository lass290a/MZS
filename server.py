from numpy import arccos, array, dot, pi, cross
from numpy.linalg import det, norm
from math import sin, cos, tan, degrees, radians, sqrt

from multiplayer import ThreadedServer

class Object:
	def __init__(self, username=None, type=None, parent=None, position=(0,0), angle=0, targetFired=0, health=100):
		self.username = username
		self.position = position
		self.health = 100
		self.angle = angle
		self.type = type
		self.targetFired = targetFired
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

	def find(self, username=None, type=None, near=None):
		if username == None and type == None and near == None:
			raise error('find() needs an input')
		elif username != None:
			for object in self.subObjects:
				if object.username==username:
					return object
			return False

		elif near != None and type != None:
			objects=[]
			for object in self.subObjects:
				if object.type==type and norm(array(getattr(near['object_ref'],'position')) - array(object.position)) < near['radius']:
					objects.append(object)
			return objects

		elif near != None:
			objects=[]
			for object in self.subObjects:
				if norm(array(getattr(near['object_ref'],'position')) - array(object.position)) < near['radius']:
					objects.append(object)
			return objects


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
			health=100,
			targetFired=0,
			parent=parent)

def dist(A, B, P):
	""" segment line AB, point P, where each one is an array([x, y]) """
	if all(A == P) or all(B == P):
		return 0
	if arccos(dot((P - A) / norm(P - A), (B - A) / norm(B - A))) > pi / 2:
		return norm(P - A)
	if arccos(dot((P - B) / norm(P - B), (A - B) / norm(A - B))) > pi / 2:
		return norm(P - B)
	return round(norm(cross(A-B, A-P))/norm(B-A),3)

def hitReg(player_ref):
	bullet_travel = 1000
	player_hitbox = 70

	player_pos = player_ref.position
	player_angle = (player_ref.angle-450)*-1

	player_objs = database.find(type='Player')
	for target in player_objs:
		target_pos = target.position
		if norm(array(target_pos) - array(player_pos)).tolist() < bullet_travel and sin(radians(player_angle-90))*(player_pos[1]-target_pos[1]) >= cos(radians(player_angle-90))*(player_pos[0]-target_pos[0]) and target.username in list(address_id.values()) and target != player_ref:
			line_seg = (array(player_pos), array((player_pos[0]+bullet_travel*sin(radians(player_angle)), player_pos[1]+bullet_travel*cos(radians(player_angle)))))
			if dist(*line_seg, array(target_pos)) < player_hitbox:
				target.health -= 10

address_id = {}

database = Database()

def server_started():
	print('[Server Started]')

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
		if event == 'targetFired':
			while event_data['player_data'][event] > player_ref.targetFired:
				hitReg(player_ref)
				player_ref.targetFired += 1

		else:
			setattr(player_ref, event, event_data['player_data'][event])

	send_data = {'player_data':{}, 'self_data':{}}

	for user in list(address_id.values()):
		if user != player_ref.username:
			temp_user = database.find(username=user)
			send_data['player_data'][user] = {'position':temp_user.position, 'angle':temp_user.angle, 'targetFired':temp_user.targetFired}
		send_data['self_data']['health'] = player_ref.health
	return str(send_data)


ThreadedServer('',4422, event_handler, server_started).listen()