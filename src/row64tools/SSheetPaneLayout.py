from row64tools.FontOptions import FontOptions
from row64tools.LineOptions import LineOptions

class SSheetPaneLayout:

	Fit = 1 # uint8_t -  0 = no fit, 1 = fit to pane, 2 = stretch to pane
	Zoom = 1  # float - Zoom magnification scale
	
	ShowLines = True # bool
	OuterLines = LineOptions()
	InnerLines = LineOptions() 

	def __init__(self):
		self.OuterLines.Color =	0xD5D5D5
		self.InnerLines.Color =	0xE5E5E5

	def __getitem__(self, key):
		return getattr(self, key) 
	def __setitem__(self, key, value):
		setattr(self, key, value)


