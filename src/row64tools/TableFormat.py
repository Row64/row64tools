class TableFormat:
	
	def __init__(self):
		self.HeaderHeight = 26.0 # float - Height of Dataframe Header
		self.ApplyFormat = False # boolean - is TableFormat applied to dataframe
		self.BkgdColor = 0xE7E7E7 # int - Background color of Dataframe Header
		self.TxtColor = 0x000000 # int - Text color of Dataframe Header
		self.Bold = True # boolean - bold text in Dataframe Header
		self.Italic = False # boolean - italic text in Dataframe Header
		self.Underline = False # boolean - underline text in Dataframe Header
		self.LMRAlign = 1 # int - Text alignment in Dataframe Header, 0 Left, 1 Middle, 2 Right aligned
		self.ShowHeadBorder = True # boolean - Show border in Dataframe Header
		self.ShowDataframeBorder = False # boolean - Show border around entire Dataframe
		self.BorderColor = 0x000000 # int - border color of Dataframe Header
		self.BorderThickness = 1.0 # float - border thickness of Dataframe Header

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
		
	def log(self):
		print(" HeaderHeight:",self.HeaderHeight)
		print(" ApplyFormat:",self.ApplyFormat)
		print(" BkgdColor:","{:06x}".format(self.BkgdColor))
		print(" TxtColor:","{:06x}".format(self.TxtColor))
		print(" Bold:",self.Bold)
		print(" Italic:",self.Italic)
		print(" Underline:",self.Underline)
		print(" LMRAlign:",self.LMRAlign)
		print(" ShowHeadBorder:",self.ShowHeadBorder)
		print(" ShowDataframeBorder:",self.ShowDataframeBorder)
		print(" BorderColor:",self.BorderColor)
		print(" BorderThickness:",self.BorderThickness)

		