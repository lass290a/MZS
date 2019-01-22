import arcade
import engine as engine
from random import choice, uniform
from math import cos, sin

screen_width, screen_height = 980, 520

class Game(engine.Game):
	def __init__(self):
		super().__init__(
			sprites_folder_path="Sprites",
			width=screen_width,
			height=screen_height,
			background_color=(0, 0, 0),)
		self.average_frames = []

	def update(self, delta_time):
		self.average_frames.append(1/delta_time)
		if self.frame % 23 == 0:
			world.create(Ball, sprite_filename="ball1", layer="main", width=50, height=50, x=(self.frame*10)%screen_width, y=300, gravity_x=0.5, gravity_y=0.5, change_y=10, change_x=(self.frame*737)%31, elasticity=0.8)
		if self.frame >= 1500:
			print(sum(self.average_frames)/len(self.average_frames))
			arcade.window_commands.close_window()

	def on_close(self):
		arcade.window_commands.close_window()

	def on_mouse_motion(self, x, y, dx, dy):
		self.a = engine.pos_to_ang(x-screen_width/2, y-screen_height/2)
		print(self.a)

	def on_mouse_press(self, x, y, button, modifiers):
		pass

	def on_mouse_release(self, x, y, button, modifiers):
		pass

	def on_key_press(self, key, modifiers):
		pass

	def on_key_release(self, key, modifiers):
		pass

class Ball(engine.Sprite):
	def __init__(self, parent, sprite_filename, layer, width=50, height=50, x=0, y=0, change_x=0, change_y=0, gravity_x=0, gravity_y=-1, elasticity=0.9):
		super().__init__(parent=parent,
			sprite_filename=sprite_filename,
			layer=layer,
			width=width,
			height=height,
			relative_rotation=True,)
		self.x = x
		self.y = y
		self.gravity_x = gravity_x
		self.gravity_y = gravity_y
		self.change_x = change_x
		self.change_y = change_y
		self.elasticity = elasticity

	def update(self):

		self.gravity_x = cos(self.origin.a)/2
		self.gravity_y = sin(self.origin.a)/2

		self.change_x += self.gravity_x
		self.change_y += self.gravity_y
		self.x += self.change_x
		self.y += self.change_y
		
		if self.y + self.change_y < 0:
			self.change_y *= -self.elasticity
			self.change_x *= 1-(1-self.elasticity)/5
			self.y = -(self.y-self.change_y)
		
		if self.y + self.change_y > screen_height:
			self.change_y *= -self.elasticity
			self.change_x *= 1-(1-self.elasticity)/5
			self.y = 2*screen_height-(self.y-self.change_y)
		
		if self.x + self.change_x < 0:
			self.change_x *= -self.elasticity
			self.change_y *= 1-(1-self.elasticity)/5
			self.x = -(self.x-self.change_x)
		
		if self.x + self.change_x > screen_width:
			self.change_x *= -self.elasticity
			self.change_y *= 1-(1-self.elasticity)/5
			self.x = 2*screen_width-(self.x-self.change_x)

class Orbit(engine.Sprite):
	def __init__(self, parent):
		super().__init__(parent=parent,
			sprite_filename="ball3.png",
			layer="main",
			width=50,
			height=50)
		self.orbit_angle = 0
		self.orbit_speed = 0.1
		self.orbit_radius = 25

	def update(self):
		self.orbit_angle += self.orbit_speed
		self.x = cos(self.orbit_angle)*self.orbit_radius
		self.y = sin(self.orbit_angle)*self.orbit_radius

game = Game()
world = game.create(engine.Entity)
game.world = world

arcade.run()