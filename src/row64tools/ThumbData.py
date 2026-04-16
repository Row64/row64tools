class ThumbData:

	I = -1 # int32 - Sprite sheet index
	X = -1 # int32 - X Location of sprite within sprite sheet
	Y = -1 # int32 - Y Location of sprite within sprite sheet
	W = -1 # int32 - Width Dimension of sprite
	H = -1 # int32 - Height Dimension of sprite
	OX = -1 # int32 - Thumb center offset X
	OY = -1 # int32 - Thumb center offset Y
	ID = "" # string - Unique ID base on image name
	RID = 0 # int32 - Rectangle ID in SingleMarkers
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)