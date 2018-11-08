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

	def render(self):
		self.renderAngle()
		self.renderPosition()
		self.center_x+=self.offsetX
		self.center_y+=self.offsetY
		self.draw()
		self.center_x-=self.offsetX
		self.center_y-=self.offsetY

if 'world objects':
	class World(Object):
		def __init__(self, parent):
			super().__init__(
				sprite='TestWorld01',
				size=2,
				X=0,
				Y=0,
				parent=parent)
			self.player = self.create(Player, x=0, y=0)
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
				self.player.weapon1.fire()

		def on_key_press(self, key, modifiers):
			self.heldKeys.append(chr(key))

		def on_key_release(self, key, modifiers):
			del self.heldKeys[self.heldKeys.index(chr(key))]

		def run(self):
			global screenWidth, screenHeight
			self.X, self.Y=-self.player.X + self.screenWidth/2, -self.player.Y + self.screenHeight/2

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

		def run(self):
			if 'a' in self.parent.heldKeys:
				self.vectorX-=self.accel
			if 'd' in self.parent.heldKeys:
				self.vectorX+=self.accel
			if 's' in self.parent.heldKeys:
				self.vectorY-=self.accel
			if 'w' in self.parent.heldKeys:
				self.vectorY+=self.accel
			
			self.vectorX /=self.deaccel
			self.vectorY /=self.deaccel
			self.X+=self.vectorX
			self.Y+=self.vectorY
			self.pointPos=[[self.center_x, self.center_y][i] - self.parent.mousePos[i] for i in range(2)]
			try:self.Angle = posToAng(self.pointPos[0], self.pointPos[1])
			except ZeroDivisionError:
				pass

	class Puppet(Object):
		def __init__(self, username, position, angle, targetFired, parent):
			super().__init__(
				sprite='body',
				size=0.33,
				X=position[0],
				Y=position[1],
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
				self.angle = self.Angle + self.shootAngle

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

if 'overlay objects':
	class Overlay(Object):
		def __init__(self, parent):
			super().__init__(parent=parent)

			self.debugWindow = self.create(Window, windowTitle='Debug Menu', width=260, height=120, X=25, Y=self.game.world.screenHeight-25)
			self.debugWindow.windowBody.text = self.debugWindow.windowBody.create(Text, string='', X=8, Y=-8, size=10)
			self.debugWindow.windowBody.text.connectedText = ''
			self.debugWindow.windowBody.input = self.debugWindow.windowBody.create(Entry, X=8, Y=-60, width=120, height=25)
		
		def run(self):
			self.debugWindow.windowBody.text.string = ('Position:  ('+str(round(self.game.world.player.X, 2))+', '+str(round(self.game.world.player.Y, 2))+')\n'+
					'Angle: '+str(round(self.game.world.player.Angle%360))+' Degrees\nServer status: '+self.game.overlay.debugWindow.windowBody.text.connectedText)

	class Text(Object):
		def __init__(self, string, X, Y, size, parent, color=(255, 255, 255), font_name='Bahnschrift', relPosition=True, anchor_x="left", anchor_y="top"):
			super().__init__(
				parent=parent,
				X=X,
				Y=Y,
				relPosition=relPosition)
			self.string = string
			self.color = color
			self.size = size
			self.font_name = font_name
			self.anchor_x = anchor_x
			self.anchor_y = anchor_y
			def render():
				self.center_x=self.parent.center_x+self.X
				self.center_y=self.parent.center_y+self.Y
				arcade.draw_text(self.string, self.center_x, self.center_y, self.color, self.size, anchor_x=anchor_x, anchor_y=anchor_y, font_name=self.font_name)
			self.render = render

	class Window(Object):
		def __init__(self, parent, windowTitle, width, height, X, Y):
			super().__init__(
				sprite='windowtop',
				size=2,
				parent=parent,
				X=X,
				Y=Y,
				width=width,
				height=25,
				anchor=True)
			self.dragging=False
			self.dragOffsetX = 0
			self.dragOffsetY = 0
			self.windowBody = self.create(WindowBody, width=width, height=height)
			self.windowTitle = self.create(Text, string=windowTitle, X=6, Y=-6, size=12)

		def start_focus(self):
			print(self.center_x, self.center_y, self.windowBody.center_x, self.windowBody.center_y)

		def on_mouse_motion(self, x, y, dx, dy):
			if self.dragging == True:
				self.X = x+self.dragOffsetX
				self.Y = y+self.dragOffsetY

		def on_mouse_press(self, x, y, button, modifiers):
			self.dragging = True
			self.dragOffsetX = self.X-x
			self.dragOffsetY = self.Y-y

		def on_mouse_release(self, x, y, button, modifiers):
			if self.dragging == True:
				self.dragging = False

	class WindowBody(Object):
		def __init__(self, width, height, parent):
			super().__init__(
				sprite='windowbody',
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
		def __init__(self, X, Y, width, height, parent):
			super().__init__(
				parent=parent,
				X=X,
				Y=Y,
				relPosition=True,
				anchor=True,
				sprite='entry',
				width=width,
				height=height)
			self.height = height
			self.width = width
			self.inputText = self.create(Text, string='', X=height*0.5*(1-0.5), Y=-height/2, size=height*0.5, anchor_x="left", anchor_y="center", color=(255, 255, 255), relPosition=True, font_name='Consolas')
			self.cursorPosition = 0
			self.cursorMaxPosition = 0

		def start_focus(self):
			self.cursorText = self.create(Text, string='', X=self.height*0.5*(1-0.5)-4, Y=-self.height/2, size=self.height*0.5, anchor_x="left", anchor_y="center", color=(255, 255, 255), relPosition=True, font_name='Consolas')
			self.cursorText.string = ' '*self.cursorPosition+'|'
			
		def stop_focus(self):
			self.cursorText.delete()

		def on_key_press(self, key, modifiers):
			#print(key, modifiers)
			if key in [65509, 65289, 65513, 65507, 65514, 65383, 65508, 65361, 65364, 65362, 65363, 65505, 65367, 65366, 65293, 65365, 65360, 65288]:
				if key == 65288 and self.cursorPosition > 0:
					self.inputText.string = self.inputText.string[:self.cursorPosition-1]+self.inputText.string[self.cursorPosition:]
					self.cursorMaxPosition -= 1
					self.cursorPosition -= 1
					self.cursorText.string = ' '*self.cursorPosition+'|'
				if key == 65293:
					self.inputText.string = ''
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
			print(self.cursorPosition, self.cursorMaxPosition)