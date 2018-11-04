import arcade
from random import randint
from math import sin, cos, radians, degrees, atan
import glob, os

sprites={os.path.basename(os.path.splitext(filetype)[0]):filetype for filetype in glob.iglob(os.path.dirname(os.path.abspath(__file__))+'/**/*.png', recursive=True)}

def posToAng(x, y):
	return 180+(-atan((y)/(x))*57.2957795+180*((x) < 0))

class Object(arcade.Sprite):
	def __init__(self, sprite='nosprite', size=0.1, parent=None, X=0, Y=0, Angle=0, relPosition=False, relAngle=False):
		super().__init__(sprites[sprite], size)
		self.children, self.parent = [], parent
		self.relPosition, self.relAngle = relPosition, relAngle
		self.X, self.Y, self.Angle = X, Y, Angle

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
		self.draw()

class World(Object):
	def __init__(self):
		super().__init__(
			sprite='cross',
			size=0.7,
			X=400,
			Y=300,)
		self.create(Player, x=100, y=100)

class Player(Object):
	def __init__(self, x, y, parent):
		super().__init__(
			sprite='body',
			size=0.35,
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
		self.weapon1 = self.create(Weapon1, targetFired=0)
		self.head = self.create(Head)

	def run(self):
		"""
		if 'a' in heldKeys:
			self.vectorX -=self.accel
		if 'd' in heldKeys:
			self.vectorX+=self.accel
		if 'w' in heldKeys:
			self.vectorY -=self.accel
		if 's' in heldKeys:
			self.vectorY+=self.accel
		"""
		
		#self.vectorX+=self.accel
		#self.vectorY+=self.accel
		
		self.Angle += 1

		self.vectorX /=self.deaccel
		self.vectorY /=self.deaccel
		self.X+=self.vectorX
		self.Y+=self.vectorY
		self.pointPos=[[self.center_x, self.center_y][i] - [100, 100][i] for i in range(2)]
		try:self.Angle = posToAng(self.pointPos[0], self.pointPos[1])
		except ZeroDivisionError:
			pass

class Weapon1(Object):
	def __init__(self, targetFired, parent):
		super().__init__(
			parent=parent,
			Y=0,
			relPosition=True,
			relAngle=True)
		self.leftarm = self.create(Weapon1Arm, side='armleft')
		self.rightarm = self.create(Weapon1Arm, side='armright')
		self.weaponClk=0
		self.targetFired=targetFired
		self.fired=targetFired

	def fire(self):
		if self.parent.__class__.__name__ != 'Puppet':
			self.targetFired += 1
		self.weaponClk = not self.weaponClk
		self.subObjects[self.weaponClk].fire()

	def run(self):
		if self.parent.__class__.__name__ == 'Puppet':
			if self.fired < self.targetFired:
				self.fired+=1
				self.fire()

class Weapon1Arm(Object):
	def __init__(self, side, parent):
		self.side=[-1, 1][side=='armleft']
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
			self.pointPos=[[self.X, self.Y][i] - [100, 100][i] for i in range(2)]
			try:self.angle=posToAng(self.pointPos[0], self.pointPos[1])+self.shootAngle+self.side*-3
			except ZeroDivisionError:
				pass
			self.realAngle = self.angle
		else:
			self.realAngle = self.angle + self.shootAngle

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
			size=0.4,
			parent=parent,
			relPosition=True,
			X=80,
			Y=-10*parent.side)
		self.angle=self.parent.angle
		self.destructTimer=0

	def run(self):
		self.destructTimer+=1
		if self.destructTimer==3:
			self.delete()
