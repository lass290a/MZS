import arcade
from math import cos, sin, radians, atan
from inspect import getmro
import glob, os
from pyglet import gl
from time import sleep

class Mouse:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.click = 0
		self.modifier = 0

def pos_to_ang(x, y):
	try:
		angle = (180+(atan((y)/(x))*57.2957795+180*((x) < 0)))
	except ZeroDivisionError:
		angle = -90
	return angle

class Entity:
	def __init__(self, parent, x=0, y=0, rotation=0, relative_position=True, relative_rotation=False):
		self.x = x
		self.y = y
		self.rotation = rotation
		self.relative_position = relative_position
		self.relative_rotation = relative_rotation
		self.parent = parent
		self.children = []
		self.angle = 0
		self.exists = True
		if self.parent == None:
			self.origin = self
		else:
			self.origin = self.parent.origin
		if Sprite not in getmro(self.__class__):
			self.center_x = 0
			self.center_y = 0
			self.rotation = 0

	def create(self, Object, **kwargs):
		obj = Object(parent=self, **kwargs)
		self.children.append(obj)
		return obj

	def find(self, condition=lambda x:x, **kwargs):
		return [child for child in self.children if condition(child, **kwargs)]

	def delete(self):
		if self.parent != None:
			for obj in self.children:
				obj.delete()
			self.parent.children.remove(self)
			if Sprite in getmro(self.__class__):
				self.origin.sprite_list.remove(self)
				self.kill()
			self.exists = False

	def determine_orientation(self):

		if self.relative_position and self.parent != self.origin:
			self.center_x = self.parent.center_x+(cos(radians(self.parent.angle))*self.x*self.origin.render_scale+cos(radians(self.parent.angle+90))*self.y*self.origin.render_scale)
			self.center_y = self.parent.center_y+(sin(radians(self.parent.angle))*self.x*self.origin.render_scale+sin(radians(self.parent.angle+90))*self.y*self.origin.render_scale)
		else:
			self.center_x = self.x
			self.center_y = self.y

		if Sprite in getmro(self.__class__):			
			x = self.width*self.align[0]*0.5
			y = self.height*self.align[1]*0.5
			self.center_x += x
			self.center_y += y

		if self.relative_rotation and self.parent != self.origin:
			self.angle = self.parent.angle + self.rotation
		else:
			self.angle = self.rotation



class Sprite(Entity, arcade.Sprite):
	def __init__(self, sprite, layer, width, height, align=[0, 0], **kwargs):
		arcade.Sprite.__init__(self, kwargs["parent"].origin.sprites[sprite])
		Entity.__init__(self, **kwargs)
		self.sprite = sprite
		self.width = width
		self.height = height
		self.layer = layer
		self.align = align

		def find_overlap_parent(obj):
			if Sprite in getmro(obj.__class__):
				if obj.layer == self.layer:
					return obj
				else:
					return None
			elif obj.parent != None:
				return find_overlap_parent(obj.parent)
			else:
				return None
		
		self.overlap_parent = find_overlap_parent(self.parent)
		self.origin.sprite_list.insert(self)

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
		
	def update(self, delta_time):
		if "event_update" in dir(self): self.event_update(delta_time)

	def on_close(self):
		if "event_close" in dir(self): self.event_close()
		arcade.window_commands.close_window()

	def on_mouse_motion(self, x, y, dx, dy):
		if "event_mouse_motion" in dir(self): self.event_mouse_motion(x, y, dx, dy)
		mouse.x = x
		mouse.y = y
		mouse.dx = dx
		mouse.dy = dy

	def on_mouse_press(self, x, y, button, modifiers):
		mouse.x = x
		mouse.y = y
		mouse.button = button
		mouse.modifiers = modifiers
		if "event_mouse_press" in dir(self): self.event_mouse_press(x, y, button, modifiers)

	def on_mouse_release(self, x, y, button, modifiers):
		if "event_mouse_release" in dir(self): self.event_mouse_release(x, y, button, modifiers)

	def on_key_press(self, key, modifiers):
		if not key_codes[key] in held_keys:
			held_keys.append(key_codes[key])
		if "event_key_press" in dir(self): self.event_key_press(key, modifiers)

	def on_key_release(self, key, modifiers):
		del held_keys[held_keys.index(key_codes[key])]
		if "event_key_release" in dir(self): self.event_key_release(key, modifiers)


	def start(self):
		arcade.run()

	def on_draw(self):
		self.frame += 1
		def search_and_update(origin):
			try:
				origin.event_update()
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

mouse = Mouse()
held_keys = []

key_codes = {65288: 'motion_backspace', 65289: 'tab', 65290: 'linefeed', 65291: 'clear', 65293: 'enter', 65299: 'pause', 65300: 'scrolllock', 65301: 'sysreq', 65307: 'escape', 65360: 'home', 65361: 'motion_left', 65362: 'motion_up', 65363: 'motion_right', 65364: 'motion_down', 65365: 'motion_previous_page', 65366: 'motion_next_page', 65367: 'end', 65368: 'begin', 65535: 'motion_delete', 65376: 'select', 65377: 'print', 65378: 'execute', 65379: 'insert', 65381: 'undo', 65382: 'redo', 65383: 'menu', 65384: 'find', 65385: 'cancel', 65386: 'help', 65387: 'break', 65406: 'scriptswitch', 1: 'motion_next_word', 2: 'motion_previous_word', 3: 'motion_beginning_of_line', 4: 'motion_end_of_line', 5: 'motion_beginning_of_file', 6: 'motion_end_of_file', 65407: 'numlock', 65408: 'num_space', 65417: 'num_tab', 65421: 'num_enter', 65425: 'num_f1', 65426: 'num_f2', 65427: 'num_f3', 65428: 'num_f4', 65429: 'num_home', 65430: 'num_left', 65431: 'num_up', 65432: 'num_right', 65433: 'num_down', 65434: 'num_page_up', 65435: 'num_page_down', 65436: 'num_end', 65437: 'num_begin', 65438: 'num_insert', 65439: 'num_delete', 65469: 'num_equal', 65450: 'num_multiply', 65451: 'num_add', 65452: 'num_separator', 65453: 'num_subtract', 65454: 'num_decimal', 65455: 'num_divide', 65456: 'num_0', 65457: 'num_1', 65458: 'num_2', 65459: 'num_3', 65460: 'num_4', 65461: 'num_5', 65462: 'num_6', 65463: 'num_7', 65464: 'num_8', 65465: 'num_9', 65470: 'f1', 65471: 'f2', 65472: 'f3', 65473: 'f4', 65474: 'f5', 65475: 'f6', 65476: 'f7', 65477: 'f8', 65478: 'f9', 65479: 'f10', 65480: 'f11', 65481: 'f12', 65482: 'f13', 65483: 'f14', 65484: 'f15', 65485: 'f16', 65505: 'lshift', 65506: 'rshift', 65507: 'lctrl', 65508: 'rctrl', 65509: 'capslock', 65511: 'lmeta', 65512: 'rmeta', 65513: 'lalt', 65514: 'ralt', 65515: 'lwindows', 65516: 'rwindows', 65517: 'lcommand', 65518: 'rcommand', 65488: 'loption', 65489: 'roption', 32: 'space', 33: 'exclamation', 34: 'doublequote', 35: 'pound', 36: 'dollar', 37: 'percent', 38: 'ampersand', 39: 'apostrophe', 40: 'parenleft', 41: 'parenright', 42: 'asterisk', 43: 'plus', 44: 'comma', 45: 'minus', 46: 'period', 47: 'slash', 48: 'key_0', 49: 'key_1', 50: 'key_2', 51: 'key_3', 52: 'key_4', 53: 'key_5', 54: 'key_6', 55: 'key_7', 56: 'key_8', 57: 'key_9', 58: 'colon', 59: 'semicolon', 60: 'less', 61: 'equal', 62: 'greater', 63: 'question', 64: 'at', 91: 'bracketleft', 92: 'backslash', 93: 'bracketright', 94: 'asciicircum', 95: 'underscore', 96: 'quoteleft', 97: 'a', 98: 'b', 99: 'c', 100: 'd', 101: 'e', 102: 'f', 103: 'g', 104: 'h', 105: 'i', 106: 'j', 107: 'k', 108: 'l', 109: 'm', 110: 'n', 111: 'o', 112: 'p', 113: 'q', 114: 'r', 115: 's', 116: 't', 117: 'u', 118: 'v', 119: 'w', 120: 'x', 121: 'y', 122: 'z', 123: 'braceleft', 124: 'bar', 125: 'braceright', 126: 'asciitilde'}

if __name__ == "__main__":
	print("stop opening the engine.py you retard")
