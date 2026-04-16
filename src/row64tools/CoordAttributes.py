class CoordAttributes:
	
	'''Mode:
		0 = bubble_varying - circles - varying size & color
		1 = bubble_uniform - circles same size & color
		2 = sprite_varying - image sprites of varying size
		3 = sprite_uniform - image sprites of same size'''
	Mode = 0 # int32
	Radius = 32.0 # float - in screen pixels
	Alpha = 0.8 # float - 0 to 1, 0 = transparent 1 = Opaque
	SpriteColor = 0x287BE9 # int32 - Coord color
	BubbleRingColor = 0xFFFFFF # int32 - Coord ring color
	BubbleRingSize = 0.1 # float - fraction of the radius
	BubbleColorPalette = [ 0x1B617B, 0x2085A0, 0x46B1D3, 0xAFDEED ] # int32_vector - One of the "Basic" themes
	SpritePath = "" # string - path to the sprite relative to the .dash companion folder
	
	# Helper data, not in .dash format
	ModeTypes = {
		"bubble_varying":0, # bubble gradient (varying size & color)
		"bubble_uniform":1, # bubble uniform (same size & color)
		"sprite_varying":2, # image sprites (varying size)
		"sprite_uniform":3  # image sprites (same size)
	}

	# Data found in markers.img (bytestream for packed image lookup)
	IDList = [] # string_vector - List of IDs for images (typically path to image)
	ImgList = [] # string_vector - List of IDs for images (typically path to image)
	ImgData = [] # buffer_vector - meta-data for UVs and bin packing
	
	def set_mode(self, inModeStr):
		if inModeStr in self.ModeTypes:self.Mode = int(self.ModeTypes[inModeStr])
		else:
			print("SetModeType: INVALID Mode:",inModeStr)
			return False


	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)