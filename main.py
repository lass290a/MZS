import pygame, glob, os
from math import sqrt, cos, sin, radians, degrees, atan
from random import uniform, getrandbits
import multiplayer
import threading
from time import sleep
from datetime import datetime

#serverAddress = ('localhost', 4422); user = ('AlexBMJ', '4312')
serverAddress = ('80.198.253.146', 4422); user = ('meatface', '1234')

versionText = 'Zython pre-beta'
displayWidth, displayHeight = 1100, 500

pygame.init()
pygame.font.init()
consolasFont=pygame.font.SysFont('Consolas', 14)
gameDisplay=pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption(versionText)
clock=pygame.time.Clock()
running=True
heldKeys=[]
pressedKeys=[]
sprites={os.path.basename(os.path.splitext(filetype)[0]):pygame.image.load(filetype)
	for filetype in glob.iglob(os.path.dirname(os.path.abspath(__file__))+'/**/*.png', recursive=True)}

def rot_center(image, angle):
	orig_rect=image.get_rect()
	rotImage=pygame.transform.rotate(image, angle)
	rotRect=orig_rect.copy()
	rotRect.center=rotImage.get_rect().center
	rotImage=rotImage.subsurface(rotRect).copy()
	return rotImage

def posToAng(x, y):
	return 180+(-atan((y)/(x))*57.2957795+180*((x) < 0))

#####################
# CHUNK RENDER TEST #

class ChunkRender:
	def __init__(self, map_data):
		self.map = map_data

	def getChunks(self, player_pos):
		chunk_coord = tuple([round(coord/512) for coord in player_pos])
		try:
			new_chunk = str(tuple([co*512 for co in chunk_coord])).replace(' ','') + ':' + self.map[str(chunk_coord).replace(' ','')]
			return new_chunk
		except KeyError:
			return False



#####################

class Object:
	def __init__(self, sprite='nosprite', spriteSize=1, x=0, y=0, angle=0, parent=None, relativePos=False, relativeAngle=False):
		self.x=x
		self.y=y
		self.angle=angle
		self.parent=parent
		self.relativePos=relativePos
		self.relativeAngle=relativeAngle
		self.type=self.__class__.__name__
		self.spriteSize=spriteSize
		if sprite != None:
			self.sprite=pygame.transform.scale(sprites[sprite], (spriteSize, spriteSize))
			self.sprite = self.sprite.convert_alpha()
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
		self.weapon1 = self.create(Weapon1, {'targetFired': 0})
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
	def __init__(self, username, position, angle, targetFired, parent):
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
		self.weapon1 = self.create(Weapon1, {'targetFired': targetFired})
		self.username = username

class Weapon1(Object):
	def __init__(self, targetFired, parent):
		super().__init__(
			parent=parent,
			y=-60)
		self.leftarm = self.create(Weapon1Arm, {'side':'armleft'})
		self.rightarm = self.create(Weapon1Arm, {'side':'armright'})
		self.weaponClk=0
		self.targetFired=targetFired
		self.fired=targetFired

	def fire(self):
		if self.parent.type != 'Puppet':
			self.targetFired += 1
		self.weaponClk = not self.weaponClk
		self.subObjects[self.weaponClk].fire()

	def run(self):
		if self.parent.type == 'Puppet':
			if self.fired < self.targetFired:
				self.fired+=1
				self.fire()

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
		self.shootAngle /= 1.2
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
	#game.world.noteText.setText('Connected to '+serverAddress[0]+' on port '+str(serverAddress[1]), (0, 0, 0))
	print('connected to server')
	global connecting
	connecting = False
	player = game.world.players.player
	recv = eval(server.sendData(str({'start_connection':{'username':user[0], 'password':user[1]}})))
	player.x, player.y = recv['start_connection']['position']
	def sendData():
		while running:
			timer = datetime.now()
			recv = eval(server.sendData(str({'player_data':{'position':(round(player.x, 2), round(player.y, 2)) , 'angle':round(player.angle, 2), 'targetFired': player.weapon1.targetFired}})))
			print(recv)
			oldPuppetList = sorted([puppet.username for puppet in game.world.players.find("Puppet")])
			newPuppetList = sorted(recv['player_data'].keys())
			disconnectedList = list(set(oldPuppetList)-set(newPuppetList))
			joinedList = list(set(newPuppetList)-set(oldPuppetList))
			print(player.weapon1.fired)
			#print(recv['player_data'], joinedList, disconnectedList)
			for puppet in game.world.players.find('Puppet'):
				if puppet in disconnectedList:
					puppet.delete()
			for puppet in game.world.players.find('Puppet'):
				puppet.x, puppet.y = recv['player_data'][puppet.username]['position']
				puppet.angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.rightarm.angle = recv['player_data'][puppet.username]['angle']
				puppet.weapon1.leftarm.angle = recv['player_data'][puppet.username]['angle']
				print(puppet.username, recv['player_data'][puppet.username]['targetFired'])
				puppet.weapon1.targetFired = recv['player_data'][puppet.username]['targetFired']
			for puppet in joinedList:
				game.world.players.create(Puppet, {'username': puppet, **recv['player_data'][puppet]})
				game.world.players.subObjects[-1].weapon1.rightarm.angle = recv['player_data'][puppet]['angle']
				game.world.players.subObjects[-1].weapon1.leftarm.angle = recv['player_data'][puppet]['angle']
				game.world.players.subObjects[-1].weapon1.targetFired = recv['player_data'][puppet]['targetFired']
				sleep(1/65-(datetime.now()-timer).seconds+(datetime.now()-timer).microseconds/1000000)


	threading.Thread(target=sendData).start()

def conn_error(a):
	print('Failed!', a)
	#game.world.noteText.setText('Failed to connect', (0, 0, 0))
	global connecting
	connecting = False

#gameDisplay.fill((0, 0, 0))
#gameDisplay.blit(consolasFont.render('Connecting...', False, (255, 255, 255)), (displayWidth/2, displayHeight/2))
#pygame.display.update()
#clock.tick(60)

connecting = True
server = multiplayer.NetworkClient(1, conn_success, conn_error)
server.establishConnection(*serverAddress)

#while connecting:
#	sleep(0.05)

loaded_chunks = []
test_map = {'(0,0)':'Asphalt_01','(1,0)':'Grass_01','(-1,0)':'Grass_01','(0,1)':'Grass_01','(0,-1)':'Grass_01','(-1,-1)':'Grass_01','(1,-1)':'Grass_01','(-1,1)':'Grass_01','(1,1)':'Grass_01'}
cr = ChunkRender(test_map)

def update_chunk():
	player_loc = (game.world.players.player.x, game.world.players.player.y)
	cd = cr.getChunks(player_loc)
	if cd:
		if cd.split(':')[0] not in loaded_chunks:
			loaded_chunks.append(cd.split(':')[0])

			game.world.mapobjects.create(Chunk, {'x':eval(cd.split(':')[0])[0],'y':eval(cd.split(':')[0])[1], 'tex':str(cd.split(':')[1])})
	#print(loaded_chunks)

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
			game.world.players.player.weapon1.fire()

	if '' in heldKeys:
		running=False
	update_chunk()
	gameDisplay.fill((255, 255, 255))
	def render(object):
		gameDisplay.blit(*object.render())
		if object.type == "Window":
			pygame.draw.rect(gameDisplay, (50, 50, 50, 125), [*[object.pos[i]-object.spriteSize[i]/2 for i in range(2)], *object.spriteSize], 2)
		#Debug
		gameDisplay.blit(pygame.transform.scale(sprites['cross'], (12, 12)), (object.realX-6, object.realY-6))
		#gameDisplay.blit(consolasFont.render(' '+object.type+' '+('@'+object.parent.type if object.parent!=None else ''), False, (0, 0, 0)), (object.realX+10, obj.realY+20))
		if 'run' in dir(object):
			object.run()
		for obj in object.subObjects:
			render(obj)
	render(game)
	pygame.display.update()
	clock.tick(60)
sleep(0.5)
pygame.quit()
