from row64tools.MarkerOptions import MarkerOptions
from row64tools.LineOptions import LineOptions
from row64tools.FillOptions import FillOptions
import copy

class LinePlotData:
	
	Name = "" # Name of the series
	Values = "" # Cell reference of the values in the series (list or cell reference like Excel)
	Labels = ""  # Lables on the series (list or cell reference like Excel)
	Marker = MarkerOptions() # MarkerOptions class
	HasLine = True
	Line = LineOptions() # LineOptions class
	FillType = 0 # int32 - 0=None, 1=Solid Fill, 2=Gradient
	Fill = [] # vector of FillOptions for future multi-color gradients
	DR_Marker = MarkerOptions() # MarkerOptions - Dynamic Reveal Racing Marker
	
	def __init__(self):
		self.Line.Size = 1.5
		self.Line.Color = 0x3178FA
		baseFill = FillOptions()
		self.Fill=[]
		self.Fill.append( copy.deepcopy(baseFill) )
		self.Line = LineOptions()
		self.Marker.Shape = 0
		self.DR_Marker.Shape = 0
		
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)