class Object:
	def __init__(self, sprite='nosprite', x=0, y=0, angle=0, parent=None, relativePos=False, relativeAngle=False):
		self.x=x
		self.y=y
		self.angle=angle
		self.parent=parent
		self.relativePos=relativePos
		self.relativeAngle=relativeAngle
		self.type=self.__class__.__name__
		self.realX=0
		self.realY=0
		self.realAngle=0
		self.subObjects=[]
		self.pos=[]
		self.realPos=[]

	def create(self, object, input={}):
		self.subObjects.append(object(parent=self, **input))
		return self.subObjects[-1]

	def delete(self, string=''):
		if string=='':
			string=str(self.parent)

		for obj in self.subObjects:
			obj.delete(string)
		
		if self.parent!=None:
			for index, obj in enumerate(self.parent.subObjects):
				if obj==self:
					self.parent.subObjects.pop(index)
					if self.parent.subObjects!=[] and str(self.parent)!=string:
						self.parent.subObjects[0].delete(string)

	def find(self, type):
		objecttype=[]
		for object in self.subObjects:
			if object.type==type:
				objecttype.append(object)
		return objecttype

	def render(self):
		parent=None
		if isinstance(self.relativePos, Object):
			parent=self.relativePos
		else:
			parent=self.parent
		if (self.relativePos==True or isinstance(self.relativePos, Object)) and self.parent!=None:
			self.realX=parent.realX + cos(radians(-parent.realAngle))*self.x + cos(radians(-parent.realAngle+90))*self.y
			self.realY=parent.realY + sin(radians(-parent.realAngle))*self.x + sin(radians(-parent.realAngle+90))*self.y
		else:
			self.realX=self.x
			self.realY=self.y
		if isinstance(self.relativeAngle, Object):
			parent=self.relativeAngle
		else:
			parent=self.parent
		if self.relativeAngle==True or isinstance(self.relativeAngle, Object):
			self.realAngle=parent.realAngle+self.angle
		elif self.relativeAngle==False:
			self.realAngle=self.angle
		self.pos=[self.x, self.y]
		self.realPos=[self.realX, self.realY]
		return rot_center(self.sprite, self.realAngle), (self.realX-self.spriteSize/2, self.realY-self.spriteSize/2)		

class Widget:
	def __init__(self, sprite='nosprite', angle=0, spriteSize=(10, 10), x=0, y=0, parent=None, relativePos=False):
		self.x=x
		self.y=y
		self.angle = angle
		self.parent=parent
		self.relativePos=relativePos
		self.type=self.__class__.__name__
		self.spriteSize=spriteSize
		if sprite != None:
			self.sprite=pygame.transform.scale(sprites[sprite], spriteSize)
		self.sprite = self.sprite.convert_alpha()
		self.realX=0
		self.realY=0
		self.subObjects=[]
		self.pos=[]
		self.realPos=[]

	def create(self, object, input={}):
		self.subObjects.append(object(parent=self, **input))
		return self.subObjects[-1]

	def delete(self, string=''):
		if string=='':
			string=str(self.parent)

		for obj in self.subObjects:
			obj.delete(string)
		
		if self.parent!=None:
			for index, obj in enumerate(self.parent.subObjects):
				if obj==self:
					self.parent.subObjects.pop(index)
					if self.parent.subObjects!=[] and str(self.parent)!=string:
						self.parent.subObjects[0].delete(string)

	def find(self, type):
		objecttype=[]
		for object in self.subObjects:
			if object.type==type:
				objecttype.append(object)
		return objecttype

	def render(self):
		parent=None
		if isinstance(self.relativePos, Widget):
			parent=self.relativePos
		else:
			parent=self.parent
		if (self.relativePos==True or isinstance(self.relativePos, Widget)) and self.parent!=None:
			self.realX=parent.realX + cos(radians(-parent.realAngle))*self.x + cos(radians(-parent.realAngle+90))*self.y
			self.realY=parent.realY + sin(radians(-parent.realAngle))*self.x + sin(radians(-parent.realAngle+90))*self.y
		else:
			self.realX=self.x
			self.realY=self.y
		self.realAngle=self.angle
		self.pos=[self.x, self.y]
		self.realPos=[self.realX, self.realY]
		return rot_center(self.sprite, self.realAngle), (self.realX-self.spriteSize[0]/2, self.realY-self.spriteSize[1]/2)		

class Game(Object):
	def __init__(self):
		super().__init__()
		self.world = self.create(World)
		#self.overlay = self.create(Overlay)

class Overlay(Object):
	def __init__(self, parent):
		super().__init__(
			parent=parent)
		self.create(Window)

class Players(Object):
	def __init__(self, parent):
		super().__init__(
			parent=parent,
			relativePos=True)
		self.player=self.create(Player, {'x':0, 'y':0})

class MapObjects(Object):
	def __init__(self, parent):
		super().__init__(
			parent=parent,
			relativePos=True
			)

class World(Object):
	def __init__(self, parent):
		super().__init__(
			sprite='cross',
			spriteSize=19,
			parent=parent)
		self.mapobjects=self.create(MapObjects)
		self.players=self.create(Players)
		#self.noteText=self.create(Text, {'x':5, 'y':displayHeight-14, 'text':'', 'color':(0, 0, 0)})
		#self.versionText=self.create(Text, {'x':5, 'y':5, 'text':versionText, 'color':(0, 0, 0)})

	def run(self):
		try:
			self.x, self.y=-self.players.player.x + displayWidth/2, -self.players.player.y + displayHeight/2
		except:
			pass

class Chunk(Object):
	def __init__(self, x, y, tex, parent):
		super().__init__(
			sprite=tex,
			spriteSize=512,
			x=x,
			y=y,
			parent=parent,
			relativePos=True)

class Window(Widget):
	def __init__(self, parent):
		super().__init__(
			sprite='background',
			spriteSize=(120,100),
			x=500,
			y=500,
			parent=parent)

class Player(Object):
	def __init__(self, x, y, parent):
		super().__init__(
			sprite='body',
			spriteSize=70,
			x=x,
			y=y,
			parent=parent,
			relativePos=True)
		self.vectorX=0
		self.vectorY=0
		self.pointX=0
		self.pointY=0
		self.deaccel=1.4
		self.accel=2
		#self.pointDeaccel=2
		#self.pointAccel=3
		self.states={}
		self.pointPos = (0, 0)
		self.weapon1 = self.create(Weapon1)
		self.head = self.create(Head)

	def run(self):
		if 'a' in heldKeys:
			self.vectorX -=self.accel
		if 'd' in heldKeys:
			self.vectorX+=self.accel
		if 'w' in heldKeys:
			self.vectorY -=self.accel
		if 's' in heldKeys:
			self.vectorY+=self.accel
		self.vectorX /=self.deaccel
		self.vectorY /=self.deaccel
		self.x+=self.vectorX
		self.y+=self.vectorY
		self.pointPos=[[self.realX, self.realY][i] - mousePos[i] for i in range(2)]
		try:self.angle = posToAng(self.pointPos[0], self.pointPos[1])
		except ZeroDivisionError:
			pass

class Puppet(Object):
	def __init__(self, username, position, angle, parent):
		super().__init__(
			sprite='body',
			spriteSize=70,
			x=position[0],
			y=position[1],
			angle=angle,
			parent=parent,
			relativePos=True)
		self.states={}
		self.head = self.create(Head)
		self.weapon1 = self.create(Weapon1)
		self.username = username

class Weapon1(Object):
	def __init__(self, parent):
		super().__init__(
			parent=parent,
			y=-60)
		self.leftarm = self.create(Weapon1Arm, {'side':'armleft'})
		self.rightarm = self.create(Weapon1Arm, {'side':'armright'})
		self.weaponClk=0
		self.fired=False

	def fire(self):
		self.weaponClk=not self.weaponClk
		self.fired=True
		self.subObjects[self.weaponClk].fire()

class Weapon1Arm(Object):
	def __init__(self, side, parent):
		self.side=[-1, 1][side=='armleft']
		super().__init__(
			sprite=side,
			spriteSize=180,
			parent=parent,
			relativePos=parent.parent,
			x=0,
			y=30*self.side,
			relativeAngle=None,)
		self.shootAngle=0

	def fire(self):
		self.shootAngle+=uniform(15, 25)*[-1, 1][bool(getrandbits(1))]
		self.create(Muzzleflash)

	def run(self):
		self.shootAngle /=1.2
		if self.parent.parent.type == 'Player':
			self.pointPos=[[self.realX, self.realY][i] - mousePos[i] for i in range(2)]
			try:self.angle=posToAng(self.pointPos[0], self.pointPos[1])+self.shootAngle+self.side*-3
			except ZeroDivisionError:
				pass
			self.realAngle = self.angle
		else:
			self.realAngle = self.angle + self.shootAngle

class Head(Object):
	def __init__(self, parent):
		super().__init__(
			sprite='head',
			spriteSize=80,
			parent=parent,
			relativePos=True)

	def run(self):
		self.angle=self.parent.angle

class Muzzleflash(Object):
	def __init__(self, parent):
		super().__init__(
			sprite='flash',
			spriteSize=80,
			parent=parent,
			relativePos=True,
			x=80,
			y=-10*parent.side)
		self.angle=self.parent.angle
		self.destructTimer=0

	def run(self):
		self.destructTimer+=1
		if self.destructTimer==3:
			self.delete()

class Text(Object):
	def __init__(self, x, y, text, color, parent):
		super().__init__(
			x=x,
			y=y,
			parent=parent)
		self.text = text
		self.sprite = consolasFont.render(text, False, color)
	def setText(self, text, color):
		self.sprite = consolasFont.render(text, False, color)

game=Game()

def conn_success():
	#game.world.noteText.setText('Connected to '+serverAdress[0]+' on port '+str(serverAdress[1]), (0, 0, 0))
	global connecting
	connecting = False
	player = game.world.players.player
	recv = eval(server.sendData(str({'start_connection':{'username':user[0], 'password':user[1]}})))
	player.x, player.y = recv['start_connection']['position']
	def sendData():
		while running:
			recv = eval(server.sendData(str({'player_data':{'position':(player.x, player.y) , 'angle':player.angle}})))
			oldPuppetList = sorted([puppet.username for puppet in game.world.players.find("Puppet")])
			newPuppetList = sorted(recv['player_data'].keys())
			disconnectedList = list(set(oldPuppetList)-set(newPuppetList))
			joinedList = list(set(newPuppetList)-set(oldPuppetList))
			#print(recv['player_data'], joinedList, disconnectedList)
			for puppet in game.world.players.find('Puppet'):
				if puppet in disconnectedList:
					puppet.delete()
			for puppet in game.world.players.find('Puppet'):
				puppet.x, puppet.y = recv['player_data'][puppet.username]['position']
				puppet.angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.rightarm.angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.leftarm.angle = recv['player_data'][puppet.username]['angle']
			for puppet in joinedList:
				game.world.players.create(Puppet, {'username': puppet, **recv['player_data'][puppet]})
				game.world.players.subObjects[-1].weapon1.rightarm.angle = recv['player_data'][puppet]['angle']
				game.world.players.subObjects[-1].weapon1.leftarm.angle = recv['player_data'][puppet]['angle']

	threading.Thread(target=sendData).start()

def conn_error(a):
	print('Failed!', a)
	#game.world.noteText.setText('Failed to connect', (0, 0, 0))
	global connecting
	connecting = False