class SingleMarker:

	W = -1 # int32 - Width 
	H = -1 # int32 - Height
	# Marker offsets OX, OY - allows setting a center for a marker that's not the middle of the sprite, good for trees & pins
	OX = 0
	OY = 0
	SheetID = 0 # Sprite sheet to be stored on
	ID = "" # unique ID of marker, typically the path where it is genrated from
	Bytes = None # Flat bytes of image, needs to be 8-bit RGBA
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)