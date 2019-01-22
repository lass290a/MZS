import arcade
from math import cos, sin, radians, atan
from inspect import getmro
import glob, os
from pyglet import gl

def pos_to_ang(x, y):
	return 180+(atan((y)/(x))*57.2957795+180*((x) < 0))

class Entity:
	def __init__(self, parent, x=0, y=0, rotation=0, relative_position=True, relative_rotation=False):
		self.x = x
		self.y = y
		self.rotation = rotation
		self.relative_position = relative_position
		self.relative_rotation = relative_rotation
		self.parent = parent
		self.children = []
		if self.parent == None:
			self.origin = self
		else:
			self.origin = self.parent.origin
		if Sprite not in getmro(self.__class__):
			self.center_x = 0
			self.center_y = 0
			self.angle = 0

	def create(self, Object, **kwargs):
		obj = Object(parent=self, **kwargs)
		self.children.append(obj)
		try:
			self.origin.sprite_list.insert(obj)
		except AttributeError:
			pass
		return obj

	def delete(self):
		if self.parent != None:
			for obj in self.children:
				obj.delete()
			self.parent.children.remove(self)
			if Sprite in getmro(self.__class__):
				self.origin.sprite_list.remove(self)
				self.kill()

	def determine_orientation(self):
		if self.relative_position and self.parent != self.origin:
			self.center_x = self.parent.center_x+(cos(radians(self.parent.rotation))*self.x*self.origin.render_scale+cos(radians(self.parent.rotation+90))*self.y*self.origin.render_scale)
			self.center_y = self.parent.center_y+(sin(radians(self.parent.rotation))*self.x*self.origin.render_scale+sin(radians(self.parent.rotation+90))*self.y*self.origin.render_scale)
		else:
			self.center_x = self.x
			self.center_y = self.y
		if self.relative_rotation and self.parent != self.origin:
			self.angle = self.parent.angle + self.rotation
		else:
			self.angle = self.rotation

class Sprite(Entity, arcade.Sprite):
	def __init__(self, sprite_filename, layer, width, height, **kwargs):
		arcade.Sprite.__init__(self, kwargs["parent"].origin.sprites[sprite_filename])
		Entity.__init__(self, **kwargs)
		self.sprite_filename = sprite_filename
		self.width = width
		self.height = height
		self.layer = layer

		def find_overlap_parent(obj):
			if Sprite in getmro(obj.__class__):
				if obj.layer == self.layer:
					return obj
				else:
					return None
			elif obj.parent != None:
				find_overlap_parent(obj.parent)
			else:
				return None
		
		self.overlap_parent = find_overlap_parent(self.parent)

class SpriteList(arcade.SpriteList):
	def __init__(self, layers):
		super().__init__(use_spatial_hash=False)
		self.layerIndicies = {layer:0 for layer in layers}

	def insert(self, obj):
		if obj.overlap_parent != None:
			self.sprite_list.insert(self.sprite_list.index(obj.overlap_parent)+1, obj)
		else:
			self.sprite_list.insert(self.layerIndicies[obj.layer], obj)
		for layer in list(self.layerIndicies.keys())[list(self.layerIndicies.keys()).index(obj.layer):]:
			self.layerIndicies[layer] += 1

	def remove(self, obj):
		self.sprite_list.remove(obj)
		for layer in list(self.layerIndicies.keys())[list(self.layerIndicies.keys()).index(obj.layer):]:
			self.layerIndicies[layer] -= 1
	
	"""def replace(self, target, new_object):
		obj_idx = None
		for index, obj in enumerate(self.sprite_list):
			if obj == target:
				obj_idx = index
		if obj_idx == None:
			raise Exception(f'unable to find object "{target}" in sprite list')
		
		self.sprite_list.pop(obj_idx)
		self.sprite_list.insert((obj_idx), object)"""

class Game(Entity, arcade.Window):
	def __init__(self, width, height, sprites_folder_path, layers=['gnd', 'gtop', 'main', 'top'], update_rate=1/60, render_scale=1, background_color=(0, 0, 0)):
		Entity.__init__(self, parent=None)
		arcade.Window.__init__(self, width, height)
		self.sprites = {os.path.basename(os.path.splitext(filetype)[0]):filetype for filetype in glob.iglob(sprites_folder_path+'/**/*.png', recursive=True)}
		self.sprite_list = SpriteList(layers=layers)
		self.update_rate = update_rate
		self.set_update_rate(update_rate)
		self.width = width
		self.height = height
		self.render_scale = render_scale
		self.background_color = background_color
		self.frame = 0
		
	def on_draw(self):
		self.frame += 1
		
		def search_and_update(origin):
			try:
				origin.update()
			except AttributeError:
				pass
			origin.determine_orientation()
			for obj in origin.children:
				search_and_update(obj)

		for obj in self.children:
				search_and_update(obj)

		arcade.start_render()
		self.sprite_list.draw()
		gl.glFlush()