import engine
import arcade

class Game(engine.Game):
	def __init__(self, screen_res=(1280,720)):
		super().__init__(
			sprites_folder_path="Sprites",
			width=screen_res[0],
			height=screen_res[1],
			background_color=(50, 50, 50))
		self.screen_res=screen_res
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

	def on_key_press(self, key, modifiers):
		if not chr(key) in self.heldKeys:
			self.heldKeys.append(chr(key))

	def on_key_release(self, key, modifiers):
		del self.heldKeys[self.heldKeys.index(chr(key))]

class Player(engine.Sprite):
	def __init__(self, x, y, parent):
		super().__init__(parent=parent,
			sprite='body',
			layer='main',
			x=game.screen_res[0]/2,
			y=game.screen_res[1]/2,
			width=75,
			height=75)
		self.vectorx=0
		self.vectory=0
		self.pointx=0
		self.pointy=0
		self.deaccel=1.2
		self.accel=0.5
		self.pointPos = (0, 0)
		self.mousePos = (0, 0)
		self.weapon1 = self.create(Weapon1, targetFired=0)
		self.head = self.create(Head)
		self.health = 100

	def update(self):
		print([self.x, self.y])

		if 'a' in game.heldKeys:
			self.vectorx-=self.accel
		if 'd' in game.heldKeys:
			self.vectorx+=self.accel
		if 's' in game.heldKeys:
			self.vectory-=self.accel
		if 'w' in game.heldKeys:
			self.vectory+=self.accel

		self.vectorx /= self.deaccel
		self.vectory /= self.deaccel

		self.x += round(self.vectorx, 5)
		self.y += round(self.vectory, 5)

		self.pointPos=[[self.center_x, self.center_y][i] - game.mousePos[i] for i in range(2)]
		try:self.rotation = engine.pos_to_ang(self.pointPos[0], self.pointPos[1])
		except ZeroDivisionError:
			pass

class Puppet(engine.Sprite):
	def __init__(self, parent, username='', x=0, y=0, angle=0, targetFired=0):
		super().__init__(
			sprite='body',
			size=0.33,
			x=x,
			y=y,
			Angle=angle,
			parent=parent,
			relPosition=True)
		self.weapon1 = self.create(Weapon1, targetFired=targetFired)
		self.head = self.create(Head)
		self.username = username

class Weapon1(engine.Entity):
	def __init__(self, targetFired, parent):
		super().__init__(
			parent=parent,
			relative_position=True,
			relative_rotation=True)

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

	def update(self):
		if self.parent.__class__.__name__ == 'Puppet':
			if self.fired < self.targetFired:
				self.fired+=1
				self.fire()

class Weapon1Arm(engine.Sprite):
	def __init__(self, side, parent):
		self.side=[-1, 1][side=='armright']
		super().__init__(parent=parent,
			sprite=side,
			layer='main',
			width=200,
			height=200,
			relative_position=True,
			relative_rotation=True,
			x=0,
			y=30*self.side)
		self.shootRotation=0
		self.tempRotation=0

	def fire(self):
		self.shootRotation+=uniform(15, 25)*[-1, 1][bool(getrandbits(1))]
		self.create(Muzzleflash)

	def update(self):
		self.shootRotation /= 1.2
		if self.parent.parent.__class__.__name__ == 'Player':
			self.pointPos=[[self.center_x, self.center_y][i] - self.parent.parent.mousePos[i] for i in range(2)]
			try: self.rotation=engine.pos_to_ang(self.pointPos[0], self.pointPos[1])+self.shootRotation+self.side*3
			except ZeroDivisionError:
				pass
		else:
			self.rotation = self.tempRotation + self.shootRotation

class Head(engine.Sprite):
	def __init__(self, parent):
		super().__init__(
			parent=parent,
			sprite='head',
			width=80,
			height=80,
			layer='main',
			relative_position=True,
			relative_rotation=True)

class Muzzleflash(engine.Sprite):
	def __init__(self, parent):
		super().__init__(
			sprite='flash',
			width=70,
			height=70,
			parent=parent,
			layer='main',
			x=parent.center_x+cos(radians(parent.rotation))*85+cos(radians(parent.rotation+90))*-10*parent.side,
			y=parent.center_y+sin(radians(parent.rotation))*85+sin(radians(parent.rotation+90))*-10*parent.side)
		self.rotation=self.parent.rotation
		self.destructTimer=0

	def update(self):
		self.destructTimer+=1
		if self.destructTimer==3:
			self.delete()

class Wall(engine.Sprite):
	def __init__(self, parent, x=0, y=0, rotation=0, texture='Wall_Wood_01'):
		super().__init__(
			sprite=texture,
			width=width,
			height=height,
			x=x,
			y=y,
			rotation=rotation,
			parent=parent,
			layer='gtop',
			relative_rotation=True,
			relative_position=True)

class Ground(engine.Sprite):
	def __init__(self, parent, x=0, y=0, rotation=0, width=50, texture='Grass_01'):
		super().__init__(
			sprite=texture,
			width=256,
			height=256,
			x=x,
			y=y,
			rotation=rotation,
			parent=parent,
			layer='gnd',
			relative_rotation=True,
			relative_position=True)

class Car(engine.Sprite):
	def __init__(self, parent, x=0, y=0, rotation=0, width=50, height=50):
		super().__init__(
			sprite='Red_Car_01',
			width=width,
			height=height,
			x=x,
			y=y,
			rotation=rotation,
			parent=parent,
			layer='gtop',
			relative_rotation=True,
			relative_position=True) 

class Rock(engine.Sprite):
	def __init__(self, parent, x=0, y=0, rotation=0, width=50, height=50):
		super().__init__(
			sprite='stone',
			width=width,
			height=height,
			x=x,
			y=y,
			rotation=rotation,
			parent=parent,
			layer='gtop',
			relative_rotation=True,
			relative_position=True)


game = Game(screen_res=(1280,720))
game.world = game.create(engine.Entity)
game.world.player = game.world.create(Player, x=0, y=0)
game.world.ground = game.world.create(Ground, x=512, y=512)


arcade.run()