import pygame, glob, os
from math import sqrt, cos, sin, radians, degrees, atan
from random import uniform, getrandbits
import socketclient
import threading
from time import sleep

#serverAdress = ('localhost', 4422)
serverAdress = ('80.198.253.146', 4422)
user = ('meatface', '1234')
versionText = 'Zython pre-beta'
displayWidth, displayHeight = 1400, 700

pygame.init()
pygame.font.init()
consolasFont=pygame.font.SysFont('Consolas', 14)
gameDisplay=pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption('Open-world')
clock=pygame.time.Clock()
running=True
heldKeys=[]
pressedKeys=[]
sprites={os.path.basename(os.path.splitext(filetype)[0]):pygame.image.load(filetype)
	for filetype in glob.iglob(os.path.dirname(os.path.abspath(__file__))+'/**/*.png', recursive=True)}
layers=[[] for x in range(15)]

def rot_center(image, angle):
	orig_rect=image.get_rect()
	rotImage=pygame.transform.rotate(image, angle)
	rotRect=orig_rect.copy()
	rotRect.center=rotImage.get_rect().center
	rotImage=rotImage.subsurface(rotRect).copy()
	return rotImage

def posToAng(x, y):
	return 180+(-atan((y)/(x))*57.2957795+180*((x) < 0))

class Object:
	def __init__(self, sprite='nosprite', spriteSize=1, layer=5, x=0, y=0, angle=0, parent=None, relativePos=False, relativeAngle=False):
		self.x=x
		self.y=y
		self.angle=angle
		self.parent=parent
		self.relativePos=relativePos
		self.relativeAngle=relativeAngle
		self.type=self.__class__.__name__
		self.layer=layer
		self.spriteSize=spriteSize
		if sprite != None:
			self.sprite=pygame.transform.scale(sprites[sprite], (spriteSize, spriteSize))
		layers[layer].append(self)
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
		
		for idx0, layer in enumerate(layers):
			for idx1, obj in enumerate(layer):
				if obj==self:
					del layers[idx0][idx1]
		
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

class World(Object):
	def __init__(self):
		super().__init__(
			layer=0,
			sprite='cross',
			spriteSize=10)
		self.player=self.create(Player, {'x':0, 'y':0})
		self.noteText=self.create(Text, {'x':5, 'y':displayHeight-14, 'text':'', 'color':(0, 0, 0)})
		self.versionText=self.create(Text, {'x':5, 'y':5, 'text':versionText, 'color':(0, 0, 0)})

	def run(self):
		try:
			self.x, self.y=-self.player.x + displayWidth/2, -self.player.y + displayHeight/2
		except:
			pass

class Player(Object):
	def __init__(self, x, y, parent):
		super().__init__(
			sprite='body',
			spriteSize=70,
			layer=5,
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
		self.head = self.create(Head)
		self.weapon1 = self.create(Weapon1)

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
			layer=5,
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
			layer=6,
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
			layer=7,
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
			layer=8,
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
			layer=8,
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
			layer=14,
			x=x,
			y=y,
			parent=parent)
		self.text = text
		self.sprite = consolasFont.render(text, False, color)
	def setText(self, text, color):
		self.sprite = consolasFont.render(text, False, color)

world=World()

def conn_success():
	print('Connection success...')
	world.noteText.setText('Connected to '+serverAdress[0]+' on port '+str(serverAdress[1]), (0, 0, 0))
	global connecting
	connecting = False
	player = world.player
	recv = eval(server.sendData(str({'start_connection':{'username':user[0], 'password':user[1]}})))
	print(recv)
	world.player.x, world.player.y = recv['start_connection']['position']
	print("yeet")
	def sendData():
		while running:
			print(str({'player_data':{'position':(player.x, player.y) , 'angle':player.angle}}))
			recv = eval(server.sendData(str({'player_data':{'position':(player.x, player.y) , 'angle':player.angle}})))
			print(recv)
			oldPuppetList = [puppet.username for puppet in world.find("Puppet")]
			newPuppetList = recv['player_data'].keys()
			disconnectedList = list(set(oldPuppetList)-set(newPuppetList))
			joinedList = list(set(newPuppetList)-set(oldPuppetList))
			print('yeet')
			for puppet in world.find('Puppet'):
				if puppet in disconnectedList:
					puppet.delete()
			for puppet in world.find('Puppet'):
				puppet.x, puppet.y = recv['player_data'][puppet.username]['position']
				puppet.angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.rightarm.angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.leftarm.angle = recv['player_data'][puppet.username]['angle']
			for puppet in joinedList:
				world.create(Puppet, recv['player_data']['player_data'][puppet])
				world.subObjects[-1].weapon1.rightarm.angle = recv['player_data'][puppet]['angle']
				world.subObjects[-1].weapon1.leftarm.angle = recv['player_data'][puppet]['angle']

	threading.Thread(target=sendData).start()

def conn_error(a):
	print('Connection error:', a)
	world.noteText.setText('Failed to connect', (0, 0, 0))
	global connecting
	connecting = False

gameDisplay.fill((0, 0, 0))
gameDisplay.blit(consolasFont.render('Connecting...', False, (255, 255, 255)), (displayWidth/2, displayHeight/2))
pygame.display.update()
clock.tick(60)
connecting = True
server = socketclient.NetworkClient(2, conn_success, conn_error)
server.establishConnection(*serverAdress)

while connecting:
	sleep(0.05)

while running:
	mousePos=pygame.mouse.get_pos()
	pressedKeys=[]
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			running=False
		if event.type==pygame.KEYDOWN:
			pressedKeys.append(chr(event.key))
			heldKeys.append(chr(event.key))
		if event.type==pygame.KEYUP:
			del heldKeys[heldKeys.index(chr(event.key))]
		if event.type==pygame.MOUSEBUTTONDOWN:
			try:
				world.player.weapon1.fire()
			except:
				pass
	if '' in heldKeys:
		running=False
	if 'r' in heldKeys:
		try:
			world.player.weapon1.delete()
		except:
			pass
	if 'e' in pressedKeys:
		try:
			world.player.create(Weapon1)
		except:
			pass
	gameDisplay.fill((255, 255, 255))
	for layer in layers:
		for obj in layer:
			if 'run' in dir(obj):
				obj.run()
			gameDisplay.blit(*obj.render())
			#Debug
			#gameDisplay.blit(pygame.transform.scale(sprites['cross'], (12, 12)), (obj.realX-6, obj.realY-6))
			#gameDisplay.blit(consolasFont.render('''+obj.type+' '+('@'+obj.parent.type if obj.parent!=None else ''), False, (0, 0, 0)), (obj.realX+10, obj.realY+20))
	pygame.display.update()
	clock.tick(60)
sleep(0.5)
pygame.quit()
