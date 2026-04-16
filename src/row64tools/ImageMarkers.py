class ImageMarkers:
	
	IDList = [] # string_vector - Unique name identifier for each thumbnail
	ImgList = [] # string_vector - Source path to the thumbnails to be packed
	ImgData = [] # ThumbData() List, buffer_vector - Sprite Sheet Packing Data
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)