import engine
import arcade
import multiplayer
import threading
from time import sleep

class Game(engine.Game):
	def __init__(self, screen_res=(1280,720), fullscreen=False):
		super().__init__(
			sprites_folder_path="Sprites",
			width=screen_res[0],
			height=screen_res[1],
			layers=['gnd', 'gtop', 'main', 'top'],
			background_color=(50, 50, 50),
			fullscreen=fullscreen)
		self.screen_res=screen_res

		self.world = self.create(engine.Entity, relative_rotation=True)
		self.world.player = self.world.create(Player, x=0, y=0)
		self.camera_target = self.world.player


	def event_close(self):
		try:
			server.fail('Game Closed')
		except:
			exit()

	def event_update(self, delta_time):
		self.world.x, self.world.y = (self.screen_res[0]//2)-(self.camera_target.x*1), (self.screen_res[1]//2)-(self.camera_target.y*1)
		#self.world.rotation += delta_time*10

class Player(engine.Sprite):
	def __init__(self, x, y, parent):
		super().__init__(parent=parent,
			sprite='body',
			layer='main',
			x=0,
			y=0,
			width=75,
			height=75,
			align=[0, 0])
		self.vectorx=0
		self.vectory=0
		self.pointx=0
		self.pointy=0
		self.deaccel=1.3
		self.accel=1.5
		self.point_pos = (0, 0)
		self.weapon1 = self.create(Weapon1, targetFired=0)
		self.head = self.create(Head)
		self.health = 100
		self.username = 'Placeholder'

	def event_update(self):
		if 'a' in engine.held_keys:
			self.vectorx-=self.accel
		if 'd' in engine.held_keys:
			self.vectorx+=self.accel
		if 's' in engine.held_keys:
			self.vectory-=self.accel
		if 'w' in engine.held_keys:
			self.vectory+=self.accel

		self.vectorx /= self.deaccel
		self.vectory /= self.deaccel

		self.x += round(self.vectorx, 5)
		self.y += round(self.vectory, 5)

		self.point_pos=[[self.center_x, self.center_y][i] - (engine.mouse.x, engine.mouse.y)[i] for i in range(2)]
		try:self.rotation = engine.pos_to_ang(self.point_pos[0], self.point_pos[1])
		except ZeroDivisionError:
			pass

class Puppet(engine.Sprite):
	def __init__(self, parent, username='', x=0, y=0, rotation=0, targetFired=0):
		super().__init__(
			sprite='body',
			layer='main',
			width=75,
			height=75,
			align=[0, 0],
			x=x,
			y=y,
			rotation=rotation,
			parent=parent,
			relative_rotation=True,
			relative_position=True)
		self.weapon1 = self.create(Weapon1, targetFired=targetFired)
		self.head = self.create(Head)
		self.username = username

class Weapon1(engine.Entity):
	def __init__(self, targetFired, parent):
		super().__init__(
			parent=parent,
			relative_position=True,
			relative_rotation=True)

		self.leftarm = self.create(Weapon1Arm, side='armright')
		self.rightarm = self.create(Weapon1Arm, side='armleft')
		self.weaponClk=0
		self.targetFired=targetFired
		self.fired=targetFired

	def fire(self):
		if self.parent.__class__.__name__ != 'Puppet':
			self.targetFired += 1
		self.weaponClk = not self.weaponClk
		self.children[self.weaponClk].fire()

	def event_update(self):
		if self.parent.__class__.__name__ == 'Puppet':
			if self.fired < self.targetFired:
				self.fired+=1
				self.fire()

class Weapon1Arm(engine.Sprite):
	def __init__(self, side, parent):
		self.side=[-1, 1][side=='armright']
		super().__init__(parent=parent,
			sprite=side,
			layer='main',
			width=200,
			height=200,
			relative_position=True,
			relative_rotation=False,
			x=0,
			y=30*self.side)
		self.shootRotation=0
		self.tempRotation=0

	def fire(self):
		self.shootRotation+=uniform(15, 25)*[-1, 1][bool(getrandbits(1))]
		self.create(Muzzleflash)

	def event_update(self):
		self.shootRotation /= 1.2
		if self.parent.parent.__class__.__name__ == 'Player':
			self.point_pos=[[self.center_x, self.center_y][i] - (engine.mouse.x, engine.mouse.y)[i] for i in range(2)]
			try:self.rotation = engine.pos_to_ang(self.point_pos[0], self.point_pos[1])
			except ZeroDivisionError:
				pass
		else:
			self.rotation = self.tempRotation + self.shootRotation


class Box(engine.Sprite):
	def __init__(self, parent):
		super().__init__(parent=parent,
			sprite="box",
			layer='main',
			width=200,
			height=200,
			relative_position=True,
			relative_rotation=False,
			x=0,
			y=0,
			align=[-1, -1])

class Head(engine.Sprite):
	def __init__(self, parent):
		super().__init__(
			parent=parent,
			sprite='head',
			width=80,
			height=80,
			layer='main',
			relative_position=True,
			relative_rotation=True)

class Muzzleflash(engine.Sprite):
	def __init__(self, parent):
		super().__init__(
			sprite='flash',
			width=70,
			height=70,
			parent=parent,
			layer='main',
			x=parent.center_x+cos(radians(parent.rotation))*85+cos(radians(parent.rotation+90))*-10*parent.side,
			y=parent.center_y+sin(radians(parent.rotation))*85+sin(radians(parent.rotation+90))*-10*parent.side)
		self.rotation=self.parent.rotation
		self.destructTimer=0

	def event_update(self):
		self.destructTimer+=1
		if self.destructTimer==3:
			self.delete()

class Wall(engine.Sprite):
	def __init__(self, parent, x=0, y=0, rotation=0, texture='Wall_Wood_01'):
		super().__init__(
			sprite=texture,
			width=width,
			height=height,
			x=x,
			y=y,
			rotation=rotation,
			parent=parent,
			layer='gtop',
			relative_rotation=True,
			relative_position=True)

class Ground(engine.Sprite):
	def __init__(self, parent, texture, x, y, rotation=0, width=256, height=256):
		super().__init__(
			parent=parent,
			sprite=texture,
			x=x,
			y=y,
			rotation=rotation,
			width=width,
			height=height,
			layer='gnd',
			relative_rotation=True,
			relative_position=True)

class Car(engine.Sprite):
	def __init__(self, parent, x=0, y=0, rotation=0, width=50, height=50):
		super().__init__(
			sprite='Red_Car_01',
			width=width,
			height=height,
			x=x,
			y=y,
			rotation=rotation,
			parent=parent,
			layer='gtop',
			relative_rotation=True,
			relative_position=True) 

class Rock(engine.Sprite):
	def __init__(self, parent, x=0, y=0, rotation=0, width=50, height=50):
		super().__init__(
			sprite='stone',
			width=width,
			height=height,
			x=x,
			y=y,
			rotation=rotation,
			parent=parent,
			layer='gtop',
			relative_rotation=True,
			relative_position=True)

class ChunkContainer(engine.Entity):
	def __init__(self, parent, raw_map, x=0, y=0):
		super().__init__(
			parent=parent,
			x=x,
			y=y,
			relative_rotation=True,
			relative_position=True)
		self.map_name = raw_map['world_name']
		self.map = raw_map['world_data']
		self.current_player_chunk = None
		self.unload_range = 2
		self.chunk_cache = {}

		self.iter_chunk = iter([])

		#self.debug_obj = self.create(Ground, texture='Grass_01', x=0,y=0)
		print('Loading', self.map_name)

	def event_update(self):
		
		player_chunk = (int(player.x//256), int(player.y//256))
		start_chunk = (0, 0)
		try:
			for _ in range(15):
				chunk = self.iter_chunk.__next__()
				if chunk not in self.chunk_cache and chunk in self.map:
					cd = self.map[chunk]
					self.chunk_cache[chunk] = self.create(Ground, texture=cd['texture'], x=cd['x'], y=cd['y'])
					break
		except StopIteration:
			pass

		if self.current_player_chunk != player_chunk:

			# Chunk Creation
			start_chunk = tuple(c-engine.ceil((r/2)/256) for c,r in zip(player_chunk, game.screen_res))
			onscreen_chunks = [(row, column) for column in range(start_chunk[1], start_chunk[1]+engine.ceil((game.screen_res[1])/256)+2) for row in range(start_chunk[0], start_chunk[0]+engine.ceil((game.screen_res[0])/256)+2)]
			self.iter_chunk = iter(onscreen_chunks)
			
			# Chunk Deletion
			for chunk in list(self.chunk_cache):
				if chunk[0] < start_chunk[0]-self.unload_range or chunk[0] > start_chunk[0]+1+engine.ceil((game.screen_res[0])/256)+self.unload_range or chunk[1] < start_chunk[1]-self.unload_range or chunk[1] > start_chunk[1]+1+engine.ceil((game.screen_res[1])/256)+self.unload_range:
					self.chunk_cache[chunk].delete()
					del self.chunk_cache[chunk]
			
			total_chunks = len(self.find(lambda child, i:i, i=1))
			print(f'{total_chunks}')
			
			self.current_player_chunk = player_chunk

class Server(threading.Thread):
	def __init__(self):
		self.recv = eval(nc.sendData(str({'connection':{'username':player.username}})))
		self.online = True
		super().__init__(target=self.mainloop)
		if 'connection' in list(self.recv.keys()) and self.recv['connection'] == 'disconnect':
			self.fail('User is already online')
		player.x, player.y = self.recv['connection']['position']
		self.start()

	def post_request(self):
		delivery_content = {'player_data':{'position':(round(player.x, 2), round(player.y, 2)), 'angle':round(player.rotation, 2), 'targetFired': player.weapon1.targetFired}}
		if player.health <= 0:
			delivery_content['player_data']['dead'] = False
		self.recv = eval(nc.sendData(str(delivery_content)))

	def puppet_controller(self):
		oldPuppetList = sorted([puppet.username for puppet in game.world.find(obj_type='Puppet')])
		newPuppetList = sorted(self.recv['player_data'].keys())
		disconnectedList = list(set(oldPuppetList)-set(newPuppetList))
		joinedList = list(set(newPuppetList)-set(oldPuppetList))

		for puppet in disconnectedList:
			puppet.delete()

		for puppet in game.world.find(obj_type='Puppet'):
			puppet.x, puppet.y = self.recv['player_data'][puppet.username]['position']
			puppet.rotation = self.recv['player_data'][puppet.username]['angle']
			puppet.weapon1.rightarm.tempAngle = self.recv['player_data'][puppet.username]['angle']
			puppet.weapon1.leftarm.tempAngle = self.recv['player_data'][puppet.username]['angle']
			puppet.weapon1.targetFired = self.recv['player_data'][puppet.username]['targetFired']

		for puppet in joinedList:
			self.recv['player_data'][puppet]['x'],self.recv['player_data'][puppet]['y'] = self.recv['player_data'][puppet]['position']
			del self.recv['player_data'][puppet]['position']
			world.create(Puppet, username=puppet, **self.recv['player_data'][puppet])
			world.children[-1].weapon1.rightarm.tempAngle = self.recv['player_data'][puppet]['angle']
			world.children[-1].weapon1.leftarm.tempAngle = self.recv['player_data'][puppet]['angle']
			world.children[-1].weapon1.targetFired = self.recv['player_data'][puppet]['targetFired']

	def player_data(self):
		if player.health != self.recv['self_data']['health']:
			player.health = self.recv['self_data']['health']
		if 'position' in self.recv['self_data']:
			player.x, player.y = self.recv['self_data']['position']
		if 'dead' in self.recv['self_data']:
			player.dead = self.recv['self_data']['dead']

	def fail(self, e):
		print(e)
		self.online = False
		#exit()

	def mainloop(self):
		while self.online:
			self.post_request()
			self.puppet_controller()
			self.player_data()
		exit()

if __name__ == '__main__':
	game = Game(screen_res=(1280,720), fullscreen=False)
	player = game.world.player
	game.world.create(ChunkContainer, raw_map=eval(open('map1.world').read()))
	serverAddress = ('localhost', 4422)
	nc = multiplayer.NetworkClient(1, Server)
	try:
		server = nc.establishConnection(*serverAddress)
	except:
		pass
	game.start()