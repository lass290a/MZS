import arcade
from gameobjects import *
from datetime import datetime

local_file = open('localip.txt','r').read().split('\n')

versionText = 'Zython pre-beta (arcade)'
screenWidth, screenHeight = 1000, 600
spawnableObjects = [Puppet, ]

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
		self.world.screenWidth, self.world.screenHeight = screenWidth, screenHeight
		self.overlay = Overlay(self)
		self.focused = None
		self.focusedTriggers = []
		self.overlay.toolsMenu = self.overlay.create(Window,
			windowTitle='Tools',
			width=260,
			height=120,
			X=25,
			Y=self.overlay.game.world.screenHeight-25,
			closable=False)
		pnt = self.overlay.toolsMenu.windowBody
		pnt.selectTool = 
		self.overlay.toolsMenu.windowBody.optionsMenu = self.overlay.toolsMenu.windowBody.create(Window,
			windowTitle='Options',
			width=pnt.width,
			height=120,
			Y=-pnt.height,
			movable=False,
			closable=False,
			relPosition=True)
		"""self.overlay.toolsMenu.windowBody.noObject = self.overlay.toolsMenu.windowBody.create(Button, string='None', width=130, height=25, X=6, Y=-6)
		def setHandToNone(x, y, button, modifiers):
			if self.world.hand != None:
				self.world.hand.delete()
			self.world.hand = None
		self.overlay.toolsMenu.windowBody.noObject.on_mouse_press = setHandToNone"""
		"""for index, Class in enumerate([Puppet, Puppet]):
			self.overlay.toolsMenu.windowBody.create(ObjectButton, hand=Class, width=130, X=6, Y=-6-(1+index)*30)"""
		self.world.hand = None
		self.focus(self.world)
		self.set_update_rate(1/60)

	def on_mouse_motion(self, x, y, dx, dy):
		if 'on_mouse_motion' in self.focusedTriggers:
			self.focused.on_mouse_motion(x, y, dx, dy)
		if self.world.hand != None:
			self.world.hand.X, self.world.hand.Y = x, y

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
		def render(object, origin=False):
			if 'run' in dir(object):
				object.run()
			if 'render' in dir(object):
				object.render()
				#Display Sprite center
				if origin: arcade.draw_text('+', object.center_x-6, object.center_y+3, (0, 0, 0), 18, anchor_y='center')

			for obj in object.children:
				render(obj, origin=origin)

		render(self.world, origin=True)
		render(self.overlay)

game = Game(screenWidth, screenHeight, False)
mousePos = ()

arcade.run()
