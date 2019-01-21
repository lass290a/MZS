import arcade

sprites={os.path.basename(os.path.splitext(filetype)[0]):filetype for filetype in glob.iglob(os.path.dirname(os.path.abspath(__file__))+'/**/*.png', recursive=True)}

class SpriteBuffer(arcade.SpriteList):
	def __init__(self):
		super().__init__(*layers)
		self.layer_dict = {}
        
	def newlayer(self, layer_name):
		self.layer_dict[layer_name] = []

	def insert(self, object, layer_name, index=None):
		if index:
			self.layer_dict[layer_name].insert(index, object)
		else:
			self.layer_dict[layer_name].append(object)
		self.sprite_list = [obj for sublist in self.layer_dict.values() for obj in sublist]

	def remove(self, obj):
		#self.layer_dict[obj.layer].remove(obj)
		#self.sprite_list.remove(obj)
		obj.kill()


class Entity(arcade.Sprite):
	def __init__(self, sprite=None, image_scale=0.1, size=1, parent=None, X=0, Y=0, Angle=0, relPosition=False, relAngle=False, layer=None):
		if sprite:
            super().__init__(sprites[sprite], image_scale)
		self.children, self.parent = [], parent
		self.relPosition, self.relAngle = relPosition, relAngle
		self.X, self.Y, self.Angle = X, Y, Angle

		self.layer = layer

		def renderRelAngleTrue():
			self.angle = self.parent.angle + self.Angle
		def renderRelAngleFalse():
			self.angle = self.Angle
		self.renderAngle = [renderRelAngleFalse, renderRelAngleTrue][relAngle]

		def renderRelPositionTrue():
			self.center_x=(self.parent.center_x+cos(radians(self.parent.angle))*self.X+cos(radians(self.parent.angle+90))*self.Y)+self.offsetX
			self.center_y=(self.parent.center_y+sin(radians(self.parent.angle))*self.X+sin(radians(self.parent.angle+90))*self.Y)+self.offsetY
		def renderRelPositionFalse():
			self.center_x=self.X+self.offsetX
			self.center_y=self.Y+self.offsetY
		self.renderPosition = [renderRelPositionFalse, renderRelPositionTrue][relPosition]

		self.game.buffer.insert(self, self.layer)

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
					self.game.buffer.remove(self)
					self.parent.children.pop(index)
					if self.parent.children!=[] and str(self.parent)!=string:
						self.parent.children[0].delete(string)

	def deleteChildren(self):
		while self.children != []:
			self.children[0].delete()

	def update(self):
		self.renderAngle()
		self.renderPosition()

class Empty(Entity):
    def __init__(self):
        super().__init__(
            X=0,
            Y=0,
            size=1,
        )
