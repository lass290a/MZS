import multiplayer
import arcade
from gameobjects import *
import threading
from datetime import datetime
from time import sleep

local_file = open('localip.txt','r').read().split('\n')
mapworld = eval(open('map1.world', 'r').read())

user = (local_file[0], 'placeholder')
print(user)
serverAddress = (local_file[1],int(local_file[2]))
print(serverAddress)

versionText = 'Zython pre-beta (arcade)'
screenWidth, screenHeight = 1280, 720

class Game(arcade.Window):
	def focus(self, object, x=0, y=0, button=0, modifiers=0):
		if 'stop_focus' in dir(self.focused):
			self.focused.stop_focus()
		self.focused = object
		self.focusedTriggers = []
		for trigger in ['on_mouse_motion', 'on_mouse_press', 'on_mouse_release', 'on_key_press', 'on_key_release', 'start_focus', 'stop_focus']:
			if trigger in dir(self.focused):
				self.focusedTriggers.append(trigger)
		if 'start_focus' in dir(object):
			object.start_focus()
		if 'on_mouse_press' in dir(object):
			object.on_mouse_press(x, y, button, modifiers)

	def __init__(self, width, height, full_screen=False):
		super().__init__(width, height, fullscreen=full_screen)
		arcade.set_background_color(arcade.color.ASH_GREY)
		self.parent = None
		self.world = World(self)
		self.world.chunks = self.world.create(ChunkContainer)
		self.world.screenWidth, self.world.screenHeight = width, height
		self.overlay = Overlay(self)
		self.world.player = self.world.create(Player, x=0, y=0)
		self.focused = None
		self.focusedTriggers = []
		self.respawn = False
		
		self.overlay.debugWindow = self.overlay.create(Window, windowTitle='Debug Menu', width=260, height=140, X=25, Y=self.overlay.game.world.screenHeight-25, minimizable=True, closable=False)
		self.overlay.debugWindow.windowBody.text = self.overlay.debugWindow.windowBody.create(Text, string='', X=10, Y=-10, size=10)
		self.overlay.debugWindow.windowBody.text.connectedText = ''
		self.overlay.debugWindow.windowBody.input = self.overlay.debugWindow.windowBody.create(Entry, X=10, Y=-80, width=120, height=25)
		
		self.focus(self.world)
		self.set_update_rate(1/60)

	def on_mouse_motion(self, x, y, dx, dy):
		if 'on_mouse_motion' in self.focusedTriggers:
			self.focused.on_mouse_motion(x, y, dx, dy)

	def on_mouse_press(self, x, y, button, modifiers):
		self.tempFocus = self.world
		def is_pressed(object):
			in_x = x > object.center_x and x < object.center_x+object.width
			in_y = y < object.center_y and y > object.center_y-object.height
			has_triggers = [i for i in ['on_mouse_motion', 'on_mouse_press', 'on_mouse_release', 'on_key_press', 'on_key_release', 'start_focus', 'stop_focus'] if i in dir(object)]!=[]
			if in_x and in_y and has_triggers:
				self.tempFocus = object
			for obj in object.children:
				is_pressed(obj)
		is_pressed(self.overlay)
		if self.focused != self.tempFocus:
			self.focus(self.tempFocus, x, y, button, modifiers)
		elif 'on_mouse_press' in self.focusedTriggers:
			self.focused.on_mouse_press(x, y, button, modifiers)

	def on_mouse_release(self, x, y, button, modifiers):
		if 'on_mouse_release' in self.focusedTriggers:
			self.focused.on_mouse_release(x, y, button, modifiers)

	def on_key_press(self, key, modifiers):
		if key == 65307:
			global online
			online = False
			arcade.window_commands.close_window()
		if 'on_key_press' in self.focusedTriggers:
			self.focused.on_key_press(key, modifiers)

	def on_close(self):
		global online
		online = False
		arcade.window_commands.close_window()

	def on_key_release(self, key, modifiers):
		if 'on_key_release' in self.focusedTriggers:
			self.focused.on_key_release(key, modifiers)

	def on_draw(self):
		arcade.start_render()
		def render(object):
			if 'run' in dir(object):
				object.run()
			if 'render' in dir(object):
				object.render()
				#Display Sprite center
				#arcade.draw_text('+', object.center_x-6, object.center_y+3, (0, 0, 0), 18, anchor_y='center')
			for obj in object.children:
				render(obj)

		self.world.X, self.world.Y=-self.world.player.X + screenWidth/2, -self.world.player.Y + screenHeight/2
		self.overlay.debugWindow.windowBody.text.string = (
			'Position: ('+str(round(self.world.player.X, 2))+', '+str(round(self.world.player.Y, 2))+')\n'+
			'Angle: '+str(round(self.world.player.Angle%360))+' Degrees\n'+
			'Server status: '+self.overlay.debugWindow.windowBody.text.connectedText+'\n'+
			'Health: '+str(player.health))
		render(self.world)
		render(self.overlay)
		PlayerMechanics()
		chunksys.update()

class ChunkSystem:
	def __init__(self, map_data, chunk_size=1024):
		self.map = map_data
		self.chunk_size = chunk_size
		self.current_player_chunk = ''
		self.rendered_chunks = {}

	def update(self):
		player_chunk = str((int(player.X//self.chunk_size), int(player.Y//self.chunk_size))).replace(' ','')
		if self.current_player_chunk != player_chunk:
			surrounding_chunk_names = [str(tuple([p+s for p,s in zip(eval(player_chunk),surpos)])).replace(' ','') for surpos in [(-1,1),(0,1),(1,1),(-1,0),(0,0),(1,0),(-1,-1),(0,-1),(1,-1)]]
			
			for chunk_name in surrounding_chunk_names:
				if chunk_name in self.map and chunk_name not in self.rendered_chunks:
					self.rendered_chunks[chunk_name] = game.world.chunks.create(Chunk, name=chunk_name, chunk_size=self.chunk_size)
					for obj in self.map[chunk_name]:
						self.rendered_chunks[chunk_name].create(**obj)

			for chunk in list(self.rendered_chunks):
				if chunk not in surrounding_chunk_names:
					self.rendered_chunks[chunk].delete()
					del self.rendered_chunks[chunk]

			self.current_player_chunk = player_chunk

def PlayerMechanics():

	def Respawn():
		game.respawn = True

	if player.health <= 0 and not player.dead:
		game.overlay.deathmsg = game.overlay.create(Window, windowTitle='', width=game.world.screenWidth//2, height=game.world.screenHeight//2, X=(game.world.screenWidth//2)//2, Y=(game.world.screenHeight//2)*1.5, minimizable=False, closable=False)
		game.overlay.deathmsg.text = game.overlay.deathmsg.create(Text, string='YOU\nDIED', X=(game.world.screenWidth//2)//2, Y=(game.world.screenHeight//10)*-1, size=game.world.screenHeight//10, color=(200,40,40), anchor_x='center', anchor_y='top', align='center')
		game.overlay.deathmsg.button = game.overlay.deathmsg.create(Button, string='RESPAWN', width=(game.world.screenWidth//8), height=(game.world.screenHeight//20), X=((game.world.screenWidth//2)//2)-(game.world.screenWidth//8)//2, Y=(game.world.screenHeight//2.5)*-1, function=Respawn)
		player.dead = True


game = Game(screenWidth, screenHeight, False)
player = game.world.player
mousePos = ()

def connectionSuccess():
	game.overlay.debugWindow.windowBody.text.connectedText = serverAddress[0]+':'+str(serverAddress[1])
	recv = eval(server.sendData(str({'connection':{'username':user[0], 'password':user[1]}})))
	if 'connection' in list(recv.keys()) and recv['connection'] == 'disconnect':
		connectionFailed('User is already online')
		return
	player.X, player.Y = recv['connection']['position']
	def sendData():
		while online:
			timer = datetime.now()
			delivery_content = {'player_data':{'position':(round(player.X, 2), round(player.Y, 2)) , 'angle':round(player.Angle, 2), 'targetFired': player.weapon1.targetFired}}
			if game.respawn == True and player.health<=0:
				delivery_content['player_data']['dead'] = False
				game.respawn = False
			recv = eval(server.sendData(str(delivery_content)))

			# Puppet animations
			oldPuppetList = sorted([puppet.username for puppet in game.world.find("Puppet")])
			newPuppetList = sorted(recv['player_data'].keys())
			disconnectedList = list(set(oldPuppetList)-set(newPuppetList))
			joinedList = list(set(newPuppetList)-set(oldPuppetList))
			for puppet in game.world.find('Puppet'):
				if puppet.username in disconnectedList:
					puppet.delete()
			for puppet in game.world.find('Puppet'):
				puppet.X, puppet.Y = recv['player_data'][puppet.username]['position']
				puppet.Angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.rightarm.tempAngle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.leftarm.tempAngle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.targetFired = recv['player_data'][puppet.username]['targetFired']
			for puppet in joinedList:
				recv['player_data'][puppet]['X'],recv['player_data'][puppet]['Y'] = recv['player_data'][puppet]['position']
				del recv['player_data'][puppet]['position']
				game.world.create(Puppet, username=puppet, **recv['player_data'][puppet])
				game.world.children[-1].weapon1.rightarm.tempAngle = recv['player_data'][puppet]['angle']
				game.world.children[-1].weapon1.leftarm.tempAngle = recv['player_data'][puppet]['angle']
				game.world.children[-1].weapon1.targetFired = recv['player_data'][puppet]['targetFired']
			#sleep(1/60-(datetime.now()-timer).seconds+(datetime.now()-timer).microseconds/1000000)
			#print(recv)
			if player.health != recv['self_data']['health']:
				player.health = recv['self_data']['health']
			if 'position' in recv['self_data']:
				player.X, player.Y = recv['self_data']['position']
			if 'dead' in recv['self_data']:
				player.dead = recv['self_data']['dead']
				if not player.dead:
					game.overlay.deathmsg.delete()
					game.focus(game.world)

	global online
	online = True
	threading.Thread(target=sendData).start()

def connectionFailed(a):
	print(a)
	game.overlay.debugWindow.windowBody.text.connectedText = 'Not connected'

server = multiplayer.NetworkClient(1, connectionSuccess, connectionFailed)
server.establishConnection(*serverAddress)
chunksys = ChunkSystem(mapworld)
arcade.run()