import arcade
from random import randint
from math import sin, cos, radians, degrees

class Object(arcade.Sprite):
	def __init__(self, sprite, size, parent=None, X=0, Y=0, Angle=0, relPosition=False, relAngle=False):
		super().__init__(sprite+'.png', size)
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

	def create(self, object, parameters={}):
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
		super().__init__(sprite='body', size=1)
		self.create(Player)

	def run(self):
		self.X += 1
		self.Y += 1
		self.Angle += 1

class Player(Object):
	def __init__(self, parent):
		super().__init__(sprite='body', size=0.7, Angle=90, X=100, parent=parent, relPosition=True, relAngle=True)