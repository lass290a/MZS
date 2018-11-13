import multiplayer
import arcade
from gameobjects import *
import threading
from datetime import datetime
from time import sleep

local_file = open('localip.txt','r').read().split('\n')

user = (local_file[0], 'placeholder')
serverAddress = (local_file[1],int(local_file[2]))
print(serverAddress)

versionText = 'Zython pre-beta (arcade)'
screenWidth, screenHeight = 1000, 600

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
		self.world.player = self.world.create(Player, x=0, y=0)
		self.world.screenWidth, self.world.screenHeight = screenWidth, screenHeight
		self.overlay = Overlay(self)
		self.focused = None
		self.focusedTriggers = []
		self.focus(self.world)
		self.overlay.debugWindow = self.overlay.create(Window, windowTitle='Debug Menu', width=260, height=120, X=25, Y=self.world.screenHeight-25)
		self.overlay.debugWindow.windowBody.text = self.overlay.debugWindow.windowBody.create(Text, string='', X=8, Y=-8, size=10)
		self.overlay.debugWindow.windowBody.text.connectedText = ''
		self.overlay.debugWindow.windowBody.input = self.overlay.debugWindow.windowBody.create(Entry, X=8, Y=-60, width=120, height=25)

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
		self.overlay.debugWindow.windowBody.text.string = ('Position:  ('+str(round(self.world.player.X, 2))+', '+str(round(self.world.player.Y, 2))+')\n'+
			'Angle: '+str(round(self.world.player.Angle%360))+' Degrees\nServer status: '+self.overlay.debugWindow.windowBody.text.connectedText)
		render(self.world)
		render(self.overlay)

game = Game(screenWidth, screenHeight, False)
mousePos = ()

def connectionSuccess():
	game.overlay.debugWindow.windowBody.text.connectedText = serverAddress[0]+':'+str(serverAddress[1])
	player = game.world.player
	recv = eval(server.sendData(str({'connection':{'username':user[0], 'password':user[1]}})))
	if 'connection' in list(recv.keys()) and recv['connection'] == 'disconnect':
		connectionFailed('User is already online')
		return
	player.X, player.Y = recv['connection']['position']
	def sendData():
		while online:
			timer = datetime.now()
			recv = eval(server.sendData(str({'player_data':{'position':(round(player.X, 2), round(player.Y, 2)) , 'angle':round(player.Angle, 2), 'targetFired': player.weapon1.targetFired}})))
			
			# Puppet animations
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
				puppet.weapon1.rightarm.tempAngle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.leftarm.tempAngle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.targetFired = recv['player_data'][puppet.username]['targetFired']
			for puppet in joinedList:
				game.world.create(Puppet, username=puppet, **recv['player_data'][puppet])
				game.world.children[-1].weapon1.rightarm.tempAngle = recv['player_data'][puppet]['angle']
				game.world.children[-1].weapon1.leftarm.tempAngle = recv['player_data'][puppet]['angle']
				game.world.children[-1].weapon1.targetFired = recv['player_data'][puppet]['targetFired']
				sleep(1/65-(datetime.now()-timer).seconds+(datetime.now()-timer).microseconds/1000000)
			player.health = recv['self_data']['health']

	global online
	online = True
	threading.Thread(target=sendData).start()

def connectionFailed(a):
	print(a)
	game.overlay.debugWindow.windowBody.text.connectedText = 'Not connected'

server = multiplayer.NetworkClient(1, connectionSuccess, connectionFailed)
server.establishConnection(*serverAddress)

arcade.run()
