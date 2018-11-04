import multiplayer
import arcade
from gameobjects import *
import threading
from datetime import datetime

#serverAddress = ('localhost', 4422); user = ('AlexBMJ', '4312')
#serverAddress = ('80.198.253.146', 4422); user = ('meatface', '1234')
serverAddress = ('localhost', 4422); user = ('meatface', '1234')

versionText = 'Zython pre-beta (arcade)'
screenWidth, screenHeight = 1600, 900

class Game(arcade.Window):
	def focus(self, object):
		if 'stop_focus' in dir(object):
			object.stop_focus()
		self.focused = object
		if 'start_focus' in dir(object):
			object.start_focus()
		for trigger in ['on_mouse_motion', 'on_mouse_press', 'on_mouse_release', 'on_key_press', 'on_key_release']:
			if trigger in dir(self.focused):
				self.focusedTriggers.append(trigger)

	def __init__(self, width, height):
		super().__init__(width, height)
		arcade.set_background_color(arcade.color.BLACK)
		self.world = World()
		self.world.screenWidth, self.world.screenHeight = screenWidth, screenHeight
		self.focused = None
		self.focusedTriggers = []
		self.focus(self.world)

	def on_mouse_motion(self, x, y, dx, dy):
		if 'on_mouse_motion' in self.focusedTriggers:
			self.focused.on_mouse_motion(x, y, dx, dy)

	def on_mouse_press(self, x, y, button, modifiers):
		if 'on_mouse_press' in self.focusedTriggers:
			self.focused.on_mouse_press(x, y, button, modifiers)

	def on_mouse_release(self, x, y, button, modifiers):
		if 'on_mouse_release' in self.focusedTriggers:
			self.focused.on_mouse_release(x, y, button, modifiers)

	def on_key_press(self, key, modifiers):
		if 'on_key_press' in self.focusedTriggers:
			self.focused.on_key_press(key, modifiers)

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
			for obj in object.children:
				render(obj)
		render(self.world)

game = Game(screenWidth, screenHeight)
mousePos = ()

def connectionSuccess():
	#game.world.noteText.setText('Connected to '+serverAddress[0]+' on port '+str(serverAddress[1]), (0, 0, 0))
	print('connected to server')
	global connecting
	connecting = False
	player = game.world.player
	recv = eval(server.sendData(str({'start_connection':{'username':user[0], 'password':user[1]}})))
	player.x, player.y = recv['start_connection']['position']
	def sendData():
		timer = datetime.now()
		recv = eval(server.sendData(str({'player_data':{'position':(round(player.x, 2), round(player.y, 2)) , 'angle':round(player.angle, 2), 'targetFired': player.weapon1.targetFired}})))
		#print(recv)
		oldPuppetList = sorted([puppet.username for puppet in game.world.find("Puppet")])
		newPuppetList = sorted(recv['player_data'].keys())
		disconnectedList = list(set(oldPuppetList)-set(newPuppetList))
		joinedList = list(set(newPuppetList)-set(oldPuppetList))
		
		for puppet in game.world.find('Puppet'):
			if puppet in disconnectedList:
				puppet.delete()
		for puppet in game.world.find('Puppet'):
			puppet.x, puppet.y = recv['player_data'][puppet.username]['position']
			puppet.angle = recv['player_data'][puppet.username]['angle']
			puppet.weapon1.rightarm.angle = recv['player_data'][puppet.username]['angle']
			puppet.weapon1.leftarm.angle = recv['player_data'][puppet.username]['angle']
			puppet.weapon1.targetFired = recv['player_data'][puppet.username]['targetFired']
		for puppet in joinedList:
			game.world.create(Puppet, {'username': puppet, **recv['player_data'][puppet]})
			game.world.children[-1].weapon1.rightarm.angle = recv['player_data'][puppet]['angle']
			game.world.children[-1].weapon1.leftarm.angle = recv['player_data'][puppet]['angle']
			game.world.children[-1].weapon1.targetFired = recv['player_data'][puppet]['targetFired']
			sleep(1/65-(datetime.now()-timer).seconds+(datetime.now()-timer).microseconds/1000000)

	threading.Thread(target=sendData).start()

def connectionFailed(a):
	print('Failed!', a)
	global connecting
	connecting = False

connecting = True
server = multiplayer.NetworkClient(1, connectionSuccess, connectionFailed)
server.establishConnection(*serverAddress)

arcade.run()
