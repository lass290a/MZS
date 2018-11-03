import arcade
from gameobjects import *

screenWidth = 800
screenHeight = 600

class Game(arcade.Window):
	def __init__(self, width, height):
		super().__init__(width, height)
		arcade.set_background_color(arcade.color.BLACK)
		self.world = World()

	def on_draw(self):
		arcade.start_render()
		def render(object):
			object.render()
			if 'run' in dir(object):
				object.run()
			for obj in object.children:
				render(obj)
		render(self.world)

def main():
	game = Game(screenWidth, screenHeight)
	arcade.run()

if __name__ == "__main__":
	main()