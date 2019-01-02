

class Compiler:
	def __init__(self):
		self.world = {}
		self.world_obj = None

	def compile(self, world_object):
		self.world_obj = world_object
		for obj in self.world_obj:
			pass
