class FillOptions:
	
	Color = 0x000000 # font color
	Alpha = 1.0 # float - transparency
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)