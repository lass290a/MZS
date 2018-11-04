import arcade
from gameobjects import *

screenWidth = 800
screenHeight = 600
mousePos = ()

class Game(arcade.Window):
	def __init__(self, width, height):
		super().__init__(width, height)
		arcade.set_background_color(arcade.color.WHITE)
		self.world = World()
	
	def on_mouse_motion(self, x, y, dx, dy):
		print(x, y)
	
	def on_draw(self):
		arcade.start_render()
		def render(object):
			object.render()
			if 'run' in dir(object):
				object.run()
			for obj in object.children:
				render(obj)
		render(self.world)

game = Game(screenWidth, screenHeight)
arcade.run()
