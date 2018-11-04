import multiplayer
import arcade
from gameobjects import *
import threading
from datetime import datetime
from time import sleep

local_file = open('localip.txt','r').read().split('\n')

user = (local_file[0], 'placeholder')
serverAddress = (local_file[1],int(local_file[2]))

versionText = 'Zython pre-beta (arcade)'
screenWidth, screenHeight = (1600//5)*4, (900//5)*4

class Game(arcade.Window):
	def focus(self, object, x=0, y=0, button=0, modifiers=0):
		if 'stop_focus' in dir(self.focused):
			self.focused.stop_focus()
		self.focused = object
		self.focusedTriggers = []
		for trigger in ['on_mouse_motion', 'on_mouse_press', 'on_mouse_release', 'on_key_press', 'on_key_release']:
			if trigger in dir(self.focused):
				self.focusedTriggers.append(trigger)
		if 'start_focus' in dir(object):
			object.start_focus()
		if 'on_mouse_press' in dir(object):
			object.on_mouse_press(x, y, button, modifiers)

	def __init__(self, width, height):
		super().__init__(width, height)
		arcade.set_background_color(arcade.color.ASH_GREY)
		self.world = World()
		self.overlay = Overlay()
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
		# scan for focused objects in 'overlay()'
		self.tempFocus = self.world
		def is_pressed(object):
			in_x = x > object.center_x-object.width/2 and x < object.center_x+object.width/2
			in_y = y > object.center_y-object.height/2 and y < object.center_y+object.height/2
			has_triggers = [i for i in ['on_mouse_motion', 'on_mouse_press', 'on_mouse_release', 'on_key_press', 'on_key_release'] if i in dir(object)]!=[]
			if in_x and in_y and has_triggers:
				self.tempFocus = object
			for obj in object.children:
				is_pressed(obj)
		is_pressed(self.overlay)
		if self.focused != self.tempFocus:
			self.focus(self.tempFocus, x, y, button, modifiers)

	def on_mouse_release(self, x, y, button, modifiers):
		if 'on_mouse_release' in self.focusedTriggers:
			self.focused.on_mouse_release(x, y, button, modifiers)

	def on_key_press(self, key, modifiers):
		if key == 65307:
			arcade.window_commands.close_window()
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
		render(self.overlay)
		'''arcade.draw_text(
			"Here's an incredible window, my dudes",
			self.world.mousePos[0],
			self.world.mousePos[1],
			arcade.color.BLACK,
			14,
			anchor_y='top',
			font_name='Franklin Gothic Medium Cond')'''

game = Game(screenWidth, screenHeight)
mousePos = ()

def connectionSuccess():
	print('connected to server')
	global connecting
	connecting = False
	player = game.world.player
	recv = eval(server.sendData(str({'start_connection':{'username':user[0], 'password':user[1]}})))
	player.x, player.y = recv['start_connection']['position']
	def sendData():
		while True:
			timer = datetime.now()
			recv = eval(server.sendData(str({'player_data':{'position':(round(player.X, 2), round(player.Y, 2)) , 'angle':round(player.Angle, 2), 'targetFired': player.weapon1.targetFired}})))
			print(recv, flush=True)
			oldPuppetList = sorted([puppet.username for puppet in game.world.find("Puppet")])
			newPuppetList = sorted(recv['player_data'].keys())
			disconnectedList = list(set(oldPuppetList)-set(newPuppetList))
			joinedList = list(set(newPuppetList)-set(oldPuppetList))
			for puppet in game.world.find('Puppet'):
				if puppet in disconnectedList:
					puppet.delete()
			for puppet in game.world.find('Puppet'):
				puppet.X, puppet.Y = recv['player_data'][puppet.username]['position']
				puppet.Angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.rightarm.Angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.leftarm.Angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.targetFired = recv['player_data'][puppet.username]['targetFired']
			for puppet in joinedList:
				game.world.create(Puppet, username=puppet, **recv['player_data'][puppet])
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
