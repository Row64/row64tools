class FontOptions:
	
	Font = 0 # int32 - font type
	Size = 20 # float - font size
	Color = 0x000000 # int32 - font color
	Bold = False 
	Italic = False
	Underline = False
	Alpha = 1.0 # float - transparency of the title font
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)