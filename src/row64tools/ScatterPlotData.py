from row64tools.EquationOptions import EquationOptions
from row64tools.LineOptions import LineOptions
from row64tools.MarkerOptions import MarkerOptions
from row64tools.FillOptions import FillOptions
import copy

class ScatterPlotData:

	Name = "" # Name of the series
	Labels = "" # Lables on the series (list or cell reference like Excel)
	XValues = "" # Cell reference of the X values in the series 
	YValues = "" # Cell reference of the Y values in the series 
	ZValues = "" # NOT USED (reserved for future 3D Scatter Plot)
	EQOptions = EquationOptions() # EquationOptions class
	Marker = MarkerOptions() # MarkerOptions class
	HasLine = False # bool  
	Line = LineOptions() # LineOptions class
	FillType = 0 # int32 - 0=None, 1=Fill, 2=Gradient
	Fill = [] # vector of FillOptions classes { {}, {} }

	def __init__(self):
		self.EQOptions = EquationOptions()
		self.Marker = MarkerOptions()
		self.Line = LineOptions()
		baseFill = FillOptions()
		self.Fill=[]
		self.Fill.append( copy.deepcopy(baseFill) )

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)