import arcade
from random import randint, uniform, getrandbits
from math import sin, cos, radians, degrees, atan
import glob, os

sprites={os.path.basename(os.path.splitext(filetype)[0]):filetype for filetype in glob.iglob(os.path.dirname(os.path.abspath(__file__))+'/**/*.png', recursive=True)}

def posToAng(x, y):
	return 180+(atan((y)/(x))*57.2957795+180*((x) < 0))

class Object(arcade.Sprite):
	def __init__(self, sprite='nosprite', size=0.1, width=0, height=0, parent=None, anchor=False, X=0, Y=0, Angle=0, relPosition=False, relAngle=False):
		super().__init__(sprites[sprite], size)
		self.children, self.parent = [], parent
		if width: self.width = width
		if height: self.height = height
		if anchor: self.offsetX, self.offsetY = self.width/2, -self.height/2
		else: self.offsetX, self.offsetY = 0, 0
		self.relPosition, self.relAngle = relPosition, relAngle
		self.X, self.Y, self.Angle = X, Y, Angle

		if self.parent != None:
			self.game = self.parent
			while self.game.parent != None:
				self.game = self.game.parent

		def renderRelAngleTrue():
			self.angle = self.parent.angle + self.Angle
		def renderRelAngleFalse():
			self.angle = self.Angle
		self.renderAngle = [renderRelAngleFalse, renderRelAngleTrue][relAngle]
		
		def renderRelPositionTrue():
			self.center_x=self.parent.center_x+cos(radians(self.parent.angle))*self.X+cos(radians(self.parent.angle+90))*self.Y
			self.center_y=self.parent.center_y+sin(radians(self.parent.angle))*self.X+sin(radians(self.parent.angle+90))*self.Y
		def renderRelPositionFalse():
			self.center_x=self.X
			self.center_y=self.Y
		self.renderPosition = [renderRelPositionFalse, renderRelPositionTrue][relPosition]

	def create(self, object, **parameters):
		self.children.append(object(**parameters, parent=self))
		return self.children[-1]

	def find(self, type):
		objecttype=[]
		for object in self.children:
			if object.__class__.__name__==type:
				objecttype.append(object)
		return objecttype

	def delete(self, string=''):
		if string=='':
			string=str(self.parent)
		for obj in self.children:
			obj.delete(string)
		if self.parent!=None:
			for index, obj in enumerate(self.parent.children):
				if obj==self:
					self.parent.children.pop(index)
					if self.parent.children!=[] and str(self.parent)!=string:
						self.parent.children[0].delete(string)

	def deleteChildren(self):
		while self.children != []:
			self.children[0].delete()

	def render(self):
		self.renderAngle()
		self.renderPosition()
		self.center_x+=self.offsetX
		self.center_y+=self.offsetY
		self.draw()
		self.center_x-=self.offsetX
		self.center_y-=self.offsetY

if 'abstract objects':
	class World(Object):
		def __init__(self, parent):
			super().__init__(
				sprite='cross',
				size=1,
				X=0,
				Y=0,
				parent=parent)
			self.mousePos = (0, 0)
			self.heldKeys=[]

		def start_focus(self):
			pass

		def stop_focus(self):
			self.heldKeys = []

		def on_mouse_motion(self, x, y, dx, dy):
			self.mousePos = (x, y)

		def on_mouse_press(self, x, y, button, modifiers):
			if button == arcade.MOUSE_BUTTON_LEFT:
				if 'player' in dir(self):
					self.player.weapon1.fire()
			#if self.hand != None:
			#	self.create(self.hand.__class__, X=x, Y=y)

		def on_key_press(self, key, modifiers):
			if not chr(key) in self.heldKeys:
				self.heldKeys.append(chr(key))

		def on_key_release(self, key, modifiers):
			del self.heldKeys[self.heldKeys.index(chr(key))]

	class ChunkContainer(Object):
		def __init__(self, parent):
			super().__init__(
				X=0,
				Y=0,
				relPosition=True,
				parent=parent)

	class ChunkContainer(Object):
		def __init__(self, parent):
			super().__init__(
				X=0,
				Y=0,
				relPosition=True,
				parent=parent)

	class Chunk(Object):
		def __init__(self, parent, name, chunk_size, debug=False):
			super().__init__(
				X=eval(name)[0]*chunk_size,
				Y=eval(name)[1]*chunk_size,
				relPosition=True,
				parent=parent)
			if debug:
				self.create(DebugChunkLayer, name=name, chunk_size=chunk_size)

	class DebugChunkLayer(Object):
		def __init__(self, parent, name, chunk_size):
			super().__init__(X=0, Y=0, relPosition=True, parent=parent)
			self.create(DebugChunk, name=name, pos=(0,chunk_size), angle=0)
			self.create(DebugChunk, name=name, pos=(chunk_size,chunk_size), angle=270)
			self.create(DebugChunk, name=name, pos=(0,0), angle=90)
			self.create(DebugChunk, name=name, pos=(chunk_size,0), angle=180)

		def run(self):
			if self.parent.children.index(self) != len(self.parent.children):
				self.parent.children.append(self.parent.children.pop(self.parent.children.index(self)))

	class DebugChunk(Object):
		def __init__(self, parent, name, pos=(0,0), angle=270):
			super().__init__(
				sprite='chunk_debug',
				size=1,
				X=pos[0],
				Y=pos[1],
				Angle=angle,
				relPosition=True,
				parent=parent)
			self.create(Text, string='Chunk '+name, X=(12 if pos[0]==0 else -128), Y=(26 if pos[1]==0 else -11), size=12, relPosition=True)

if 'player objects':
	class Player(Object):
		def __init__(self, x, y, parent):
			super().__init__(
				sprite='body',
				size=0.33,
				X=x,
				Y=y,
				parent=parent,
				relPosition=True)
			self.vectorX=0
			self.vectorY=0
			self.pointX=0
			self.pointY=0
			self.deaccel=1.4
			self.accel=2
			self.pointPos = (0, 0)
			self.mousePos = (0, 0)
			self.weapon1 = self.create(Weapon1, targetFired=0)
			self.head = self.create(Head)
			self.health = 100
			self.health_check = 100
			self.dead = False			

		def run(self):
			if 'a' in self.parent.heldKeys:
				self.vectorX-=self.accel
			if 'd' in self.parent.heldKeys:
				self.vectorX+=self.accel
			if 's' in self.parent.heldKeys:
				self.vectorY-=self.accel
			if 'w' in self.parent.heldKeys:
				self.vectorY+=self.accel

			if self.health < self.health_check:
				self.game.overlay.create(Tint, width=self.game.world.screenWidth, height=self.game.world.screenHeight)
				self.health_check = self.health

			if self.health > self.health_check:
				self.game.overlay.create(Tint, width=self.game.world.screenWidth, height=self.game.world.screenHeight, texture='green_tint')
				self.health_check = self.health

			self.vectorX /=self.deaccel
			self.vectorY /=self.deaccel
			self.X+=self.vectorX
			self.Y+=self.vectorY
			self.pointPos=[[self.center_x, self.center_y][i] - self.parent.mousePos[i] for i in range(2)]
			try:self.Angle = posToAng(self.pointPos[0], self.pointPos[1])
			except ZeroDivisionError:
				pass

	class Puppet(Object):
		def __init__(self, parent, username='', X=0, Y=0, angle=0, targetFired=0):
			super().__init__(
				sprite='body',
				size=0.33,
				X=X,
				Y=Y,
				Angle=angle,
				parent=parent,
				relPosition=True)
			self.weapon1 = self.create(Weapon1, targetFired=targetFired)
			self.head = self.create(Head)
			self.username = username

	class Weapon1(Object):
		def __init__(self, targetFired, parent):
			super().__init__(
				parent=parent,
				Y=0,
				relPosition=True,
				relAngle=True)
			self.leftarm = self.create(Weapon1Arm, side='armright')
			self.rightarm = self.create(Weapon1Arm, side='armleft')
			self.weaponClk=0
			self.targetFired=targetFired
			self.fired=targetFired

		def fire(self):
			if self.parent.__class__.__name__ != 'Puppet':
				self.targetFired += 1
			self.weaponClk = not self.weaponClk
			self.children[self.weaponClk].fire()

		def run(self):
			if self.parent.__class__.__name__ == 'Puppet':
				if self.fired < self.targetFired:
					self.fired+=1
					self.fire()

	class Weapon1Arm(Object):
		def __init__(self, side, parent):
			self.side=[-1, 1][side=='armright']
			super().__init__(
				sprite=side,
				size=0.4,
				parent=parent,
				relPosition=True,
				X=0,
				Y=30*self.side)
			self.shootAngle=0
			self.tempAngle=0

		def fire(self):
			self.shootAngle+=uniform(15, 25)*[-1, 1][bool(getrandbits(1))]
			self.create(Muzzleflash)

		def run(self):
			self.shootAngle /= 1.2
			if self.parent.parent.__class__.__name__ == 'Player':
				self.pointPos=[[self.center_x, self.center_y][i] - self.parent.parent.parent.mousePos[i] for i in range(2)]
				try: self.Angle=posToAng(self.pointPos[0], self.pointPos[1])+self.shootAngle+self.side*3
				except ZeroDivisionError:
					pass
			else:
				self.Angle = self.tempAngle + self.shootAngle

	class Head(Object):
		def __init__(self, parent):
			super().__init__(
				parent=parent,
				sprite='head',
				size=0.4,
				relPosition=True,
				relAngle=True)

	class Muzzleflash(Object):
		def __init__(self, parent):
			super().__init__(
				sprite='flash',
				size=1.2,
				parent=parent,
				X=parent.center_x+cos(radians(parent.angle))*85+cos(radians(parent.angle+90))*-10*parent.side,
				Y=parent.center_y+sin(radians(parent.angle))*85+sin(radians(parent.angle+90))*-10*parent.side)
			self.Angle=self.parent.Angle
			self.destructTimer=0

		def run(self):
			self.destructTimer+=1
			if self.destructTimer==3:
				self.delete()

if 'static world objects':
	class Wall(Object):
		def __init__(self, parent, X=0, Y=0, angle=0, texture='Wall_Wood_01'):
			super().__init__(
				sprite=texture,
				size=1,
				X=X,
				Y=Y,
				Angle=angle,
				parent=parent,
				relPosition=True)

	class Ground(Object):
		def __init__(self, parent, X=0, Y=0, angle=0, texture='Grass_01'):
			super().__init__(
				sprite=texture,
				size=1,
				X=X,
				Y=Y,
				Angle=angle,
				parent=parent,
				relPosition=True)
			
	class Car(Object):
		def __init__(self, parent, X=0, Y=0, angle=0):
			super().__init__(
				sprite='Red_Car_01',
				size=1,
				X=X,
				Y=Y,
				Angle=angle,
				parent=parent,
				relPosition=True) 

	class Rock(Object):
		def __init__(self, parent, X=0, Y=0, angle=0):
			super().__init__(
				sprite='stone',
				size=0.1,
				X=X,
				Y=Y,
				Angle=angle,
				parent=parent,
				relPosition=True) 

if 'overlay objects':

	class Overlay(Object):
		def __init__(self, parent):
			super().__init__(parent=parent)

	class Tint(Object):
		def __init__(self, parent, width, height, texture='red_tint', alive_time=0.5, fade_speed=0.01):
			super().__init__(
				sprite=texture,
				size=1,
				width=width,
				height=height,
				X=0,
				Y=height,
				anchor=True,
				parent=parent)
			self.alive_time = alive_time
			self.fade_speed = fade_speed

		def run(self):
			if self.alive_time <= 0:
				self.delete()
			else:
				self.alpha = self.alive_time
				self.alive_time -= self.fade_speed

	class Button(Object):
		def __init__(self, parent, X, Y, string, width, height, function):
			super().__init__(parent=parent,
				sprite='widget_entry',
				size=1,
				width=width,
				height=height,
				anchor=True,
				X=X,
				Y=Y,
				relPosition=True)
			self.text = self.create(Text, string=string, X=width/2-0.5*len(string)*(height*0.5*(6/7)), Y=-6, size=height*0.5, anchor_x="left", anchor_y="top", relPosition=True)
			self.function_callback = function

		def on_mouse_press(self, x, y, button, modifiers):
			self.function_callback()

	class SliderDrag(Object):
		def __init__(self, parent):
			super().__init__(parent=parent,
				sprite='slider',
				relPosition=True,
				X=-9,
				Y=16-parent.height/2,
				width=18,
				height=32,
				anchor=True,)
			self.dragging = False
			self.dragOffsetX = 0

		def on_mouse_motion(self, x, y, dx, dy):
			if self.dragging == True:
				if self.parent.step != 0:
					s = self.parent.width/((self.parent.maximum-self.parent.minimum)/self.parent.step)
					self.X = round((self.dragOffsetX+x+9)/s)*s-9
				else:
					self.X = x+self.dragOffsetX
				if self.X < -9:
					self.X = -9
				elif self.X > self.parent.width-9:
					self.X = self.parent.width-9
				self.parent.input.set(str(round(self.parent.minimum+((self.X+9)/self.parent.width)*(self.parent.maximum-self.parent.minimum),8)))
				self.parent.changed_callback(self.parent.get())

		def on_mouse_press(self, x, y, button, modifiers):
			self.dragging = True
			self.dragOffsetX = self.X-x
			
		def on_mouse_release(self, x, y, button, modifiers):
			if self.dragging == True:
				self.dragging = False
				self.parent.finished_callback(self.parent.get())

	class Slider(Object):
		def __init__(self, parent, X, Y, sliderWidth, entryWidth, minimum, maximum, step=0, start=0, changed_callback=lambda x:x, finished_callback=lambda x:x, disableLimit=True, roundFunction=lambda value, step: round(float(value)/step)*step):
			super().__init__(parent=parent,
				sprite='slider_body',
				size=1,
				width=sliderWidth,
				height=10,
				X=X+entryWidth+10,
				Y=Y,
				relPosition=True,
				anchor=True)
			self.sliderWidth = sliderWidth
			self.step = step
			self.maximum = maximum
			self.minimum = minimum
			self.start = start
			self.finished_callback = finished_callback
			self.changed_callback = changed_callback
			
			def inputChanged():
				try:
					float(self.input.get())
					self.sliderdrag.X = (min(self.maximum, max(self.minimum, (roundFunction if self.step != 0 else lambda value, step: value)(float(self.input.get()), self.step))) - self.minimum)/(self.maximum-self.minimum)*self.sliderWidth-9
				except:
					pass
				self.changed_callback(self.get())
			
			def entry_stop_focus_callback():
				try:
					self.input.set(str(min(self.maximum, max(self.minimum, round((roundFunction if self.step != 0 else lambda value, step: value)(float(self.input.get()), self.step), 3)))))
				except ValueError:
					self.sliderdrag.X = (self.start - self.minimum)/(self.maximum-self.minimum)*self.sliderWidth-9
					self.input.set(str(self.start))
				self.finished_callback(self.get())

			self.input = self.create(Entry, X=-(entryWidth+15), Y=-5+12.5, width=entryWidth, height=25, callback=inputChanged, stop_focus_callback=entry_stop_focus_callback)
			self.sliderdrag = self.create(SliderDrag)

			try:
				self.input.set(str(min(self.maximum, max(self.minimum, (roundFunction if self.step != 0 else lambda value, step: value)(float(self.start), self.step)))))
			except ValueError:
				pass

		def on_mouse_press(self, x, y, button, modifiers):
			pass#self.sliderdrag.on_mouse_press(self.sliderdrag.center_x, self.sliderdrag.center_y, 1, 0)

		def get(self):
			return float(self.input.get())

		def reset(self):
			self.sliderdrag.X = (self.start - self.minimum)/(self.maximum-self.minimum)*self.sliderWidth-9
			self.input.set(str(self.start))

		def set(self, value):
			try:
				self.input.set(str(min(self.maximum, max(self.minimum, (roundFunction if self.step != 0 else lambda value, step: value)(float(value), self.step)))))
			except ValueError:
				pass

	class ObjectButton(Object):
		def __init__(self, parent, X, Y, width, hand):
			super().__init__(parent=parent,
				sprite='widget_entry',
				size=1,
				width=width,
				height=25,
				anchor=True,
				X=X,
				Y=Y,
				relPosition=True)
			self.hand = hand
			self.text = self.create(Text, string=self.hand.__name__, X=width/2-0.5*len(self.hand.__name__)*10.7, Y=-6, size=12.5, anchor_x="left", anchor_y="top", relPosition=True)

		def on_mouse_press(self, x, y, button, modifiers):
			if self.game.world.hand != None:
				self.game.world.hand.delete()
			self.game.world.hand = self.game.world.create(self.hand, X=x, Y=y)
			self.game.world.hand.relPosition = False

	class Text(Object):
		def __init__(self, string, X, Y, size, parent, color=(255, 255, 255), font_name='Bahnschrift', relPosition=True, anchor_x="left", anchor_y="top", align='left'):
			super().__init__(
				parent=parent,
				X=X,
				Y=Y,
				relPosition=relPosition)
			self.string = string
			self.color = color
			self.size = size
			self.font_name = font_name
			self.align = align
			self.anchor_x = anchor_x
			self.anchor_y = anchor_y
			def render():
				self.center_x=self.parent.center_x+self.X
				self.center_y=self.parent.center_y+self.Y
				arcade.draw_text(self.string, self.center_x, self.center_y, self.color, self.size, align=align, anchor_x=anchor_x, anchor_y=anchor_y, font_name=self.font_name)
			self.render = render

	class WindowCloseButton(Object):
		def __init__(self, X, Y, parent):
			super().__init__(
				sprite='window_close',
				size=0.5,
				parent=parent,
				X=X,
				Y=Y,
				anchor=True,
				relPosition=True)

		def on_mouse_press(self, x, y, button, modifiers):
			self.parent.delete()

	class WindowMinimizeButton(Object):
		def __init__(self, X, Y, parent):
			super().__init__(
				sprite='window_minimize',
				size=0.5,
				parent=parent,
				X=X,
				Y=Y,
				anchor=True,
				relPosition=True)

		def on_mouse_press(self, x, y, button, modifiers):
			self.parent.windowBody.X -= 321000
			self.X -= 321000
			self.parent.minimizeUndoButton.X += 321000

	class WindowMinimizeUndoButton(Object):
		def __init__(self, X, Y, parent):
			super().__init__(
				sprite='window_minimize_undo',
				size=0.5,
				parent=parent,
				X=X,
				Y=Y,
				anchor=True,
				relPosition=True)

		def on_mouse_press(self, x, y, button, modifiers):
			self.parent.windowBody.X += 321000
			self.parent.minimizeButton.X += 321000
			self.X -= 321000

	class Window(Object):
		def __init__(self, parent, windowTitle, width, height, X=0, Y=0, movable=True, closable=True, minimizable=True, relPosition=False):
			super().__init__(
				sprite='window_top',
				size=2,
				parent=parent,
				X=X,
				Y=Y,
				width=width,
				height=25,
				anchor=True,
				relPosition=relPosition)
			self.movable = movable
			self.dragging=False
			self.dragOffsetX = 0
			self.dragOffsetY = 0
			self.windowBody = self.create(WindowBody, width=width, height=height)
			self.windowTitle = self.create(Text, string=windowTitle, X=6, Y=-5, size=12)
			if closable:
				self.windowCloseButton = self.create(WindowCloseButton, X=self.width-(16+4), Y=-5)
				if minimizable:
					self.minimizeButton = self.create(WindowMinimizeButton, X=self.width-(32+8), Y=-5)
					self.minimizeUndoButton = self.create(WindowMinimizeUndoButton, X=self.width-(32+8)-321000, Y=-5)
			elif minimizable:
				self.minimizeButton = self.create(WindowMinimizeButton, X=self.width-(16+6), Y=-5)
				self.minimizeUndoButton = self.create(WindowMinimizeUndoButton, X=self.width-(16+6)-321000, Y=-5)

		def start_focus(self):
			pass

		def on_mouse_motion(self, x, y, dx, dy):
			if self.dragging == True:
				self.X = x+self.dragOffsetX
				self.Y = y+self.dragOffsetY

		def on_mouse_press(self, x, y, button, modifiers):
			if self.movable:
				self.dragging = True
				self.dragOffsetX = self.X-x
				self.dragOffsetY = self.Y-y

		def on_mouse_release(self, x, y, button, modifiers):
			if self.dragging == True:
				self.dragging = False

	class WindowBody(Object):
		def __init__(self, width, height, parent):
			super().__init__(
				sprite='window_body',
				size=2,
				parent=parent,
				X=0,
				Y=-25,
				relPosition=True,
				width=width,
				height=height,
				anchor=True)

		def start_focus(self):
			pass

	class Entry(Object):
		def __init__(self, X, Y, width, height, parent, callback=None, stop_focus_callback=None):
			super().__init__(
				parent=parent,
				X=X,
				Y=Y,
				relPosition=True,
				anchor=True,
				sprite='widget_entry',
				width=width,
				height=height)
			self.height = height
			self.width = width
			self.inputText = self.create(Text, string='', X=height*0.5*(1-0.5), Y=-height/2, size=height*0.5, anchor_x="left", anchor_y="center", color=(255, 255, 255), relPosition=True, font_name='Consolas')
			self.cursorPosition = 0
			self.cursorMaxPosition = 0
			self.callback = callback
			self.stop_focus_callback = stop_focus_callback

		def set(self, a):
			self.inputText.string = a
			self.cursorPosition = len(a)
			self.cursorMaxPosition = len(a)

		def get(self):
			return self.inputText.string

		def start_focus(self):
			self.cursorText = self.create(Text, string='', X=self.height*0.5*(1-0.5)-4, Y=-self.height/2, size=self.height*0.5, anchor_x="left", anchor_y="center", color=(255, 255, 255), relPosition=True, font_name='Consolas')
			self.cursorText.string = ' '*self.cursorPosition+'|'
			
		def stop_focus(self):
			self.cursorText.delete()
			if self.stop_focus_callback != None:
				self.stop_focus_callback()
		
		def reset(self):
			self.inputText.string = ''
			self.cursorPosition = 0
			self.cursorMaxPosition = 0
			self.cursorText.string = ' '*self.cursorPosition+'|'
			self.game.focus(self.game.world)

		def on_key_press(self, key, modifiers):
			if key in [65509, 65289, 65513, 65507, 65514, 65383, 65508, 65361, 65364, 65362, 65363, 65505, 65367, 65366, 65293, 65365, 65360, 65288]:
				if key == 65288 and self.cursorPosition > 0:
					self.inputText.string = self.inputText.string[:self.cursorPosition-1]+self.inputText.string[self.cursorPosition:]
					self.cursorMaxPosition -= 1
					self.cursorPosition -= 1
					self.cursorText.string = ' '*self.cursorPosition+'|'
				if key == 65363 and self.cursorPosition < self.cursorMaxPosition:
					self.cursorPosition += 1
					self.cursorText.string = ' '*self.cursorPosition+'|'
				if key == 65361 and self.cursorPosition > 0:
					self.cursorPosition -= 1
					self.cursorText.string = ' '*self.cursorPosition+'|'
			else:
				try:
					self.cursorMaxPosition += 1
					self.cursorPosition += 1
					self.inputText.string = self.inputText.string[:self.cursorPosition]+(chr(key).upper() if modifiers else chr(key))+self.inputText.string[self.cursorPosition:]
					self.cursorText.string = ' '*self.cursorPosition+'|'
				except OverflowError:
					pass
			if self.callback != None:
				self.callback()
