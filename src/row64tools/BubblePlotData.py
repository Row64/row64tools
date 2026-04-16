from row64tools.EquationOptions import EquationOptions
from row64tools.MarkerOptions import MarkerOptions

class BubblePlotData:
	
	Name = "" # Name of the series
	Labels = "" # Lables on the series (list or cell reference like Excel)
	XValues = "" # Cell reference of the X values in the series 
	YValues = "" # Cell reference of the Y values in the series 
	ZValues = "" # Cell reference of the Z values in the series (bubble size & color)
	EQOptions = EquationOptions() # EquationOptions class
	Marker = MarkerOptions() # MarkerOptions class
	ColorTheme  = [0x215ea7, 0x0099cb, 0x00d6b2, 0x00ff2b] # int32vec - 4 Color theme for the series
	
	def __init__(self):
		self.EQOptions = EquationOptions()
		self.Marker = MarkerOptions()
		self.Marker.Shape = 1
		self.Marker.Size = 5
		self.Marker.Alpha = .7

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)