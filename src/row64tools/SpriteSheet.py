class SpriteSheet:
	
	W = -1 # int32 - Width 
	H = -1 # int32 - Height
	SheetID = 0 # Sprite sheet to be stored on
	ImgData = [] # List of ThumbData
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)