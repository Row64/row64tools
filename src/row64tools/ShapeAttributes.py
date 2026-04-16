class ShapeAttributes:
	
	TimeSeriesAccum = False #  bool - attribute data from the previous time period is added to the current one, effectively doing a prefix sum to provide an "accumulation" effect
	AntiAliasing = True # bool - anti-aliasing in Studio
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)