import engine
import arcade

class Game(engine.Game):
	def __init__(self, width, height):
		super().__init__(
			sprites_folder_path="Sprites",
			width=width,
			height=height,
			background_color=(50, 50, 50))
		self.held_keys = []

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse_x = x
		self.mouse_y = y

	def on_mouse_press(self, x, y, button, modifiers):
		pass

	def on_key_press(self, key, modifiers):
		inp = engine.key_codes[key]
		if inp not in self.held_keys:
			self.held_keys.append(engine.key_codes[key])

	def on_key_release(self, key, modifiers):
		try:
			self.held_keys.remove(engine.key_codes[key])
		except ValueError:
			pass

	def update(self, delta_time):
		print(self.held_keys)		

class Player(engine.Sprite):
	def __init__(self, parent, x, y):
		super().__init__(parent=parent,
			sprite='body',
			width=100,
			height=100,
			layer="main",
			x=x,
			y=y)
		self.deacceleration = 1.35
		self.acceleration = 2.5
		self.vector_x = 0
		self.vector_y = 0
		self.create(Arm, sprite="armleft")

	def update(self):
		self.rotation = engine.pos_to_ang(self.x-self.origin.mouse_x, self.y-self.origin.mouse_y)
		if "d" in self.origin.held_keys:
			self.vector_x += self.acceleration
		if "a" in self.origin.held_keys:
			self.vector_x -= self.acceleration
		if "w" in self.origin.held_keys:
			self.vector_y += self.acceleration
		if "s" in self.origin.held_keys:
			self.vector_y -= self.acceleration
		self.vector_x /= self.deacceleration
		self.vector_y /= self.deacceleration
		self.x += self.vector_x
		self.y += self.vector_y

class Arm(engine.Sprite):
	def __init__(self, parent, sprite):
		super().__init__(parent=parent,
			sprite=sprite,
			layer="main",
			width=100,
			height=30)



game = Game(1280, 720)
game.world = game.create(engine.Entity)
world = game.world

world.create(Player, x=game.width/2, y=game.height/2)

arcade.run()