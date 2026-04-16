class MarkerOptions:
	
	Shape = 1 # int32 - 0=None, 1=circle, 2=square, 3=triangle
	Size = 10.0 # float
	Alpha = 1.0 # float
	Color = -1 # int32
	HasFill = True # bool - marker is filled in

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)