from row64tools.LineOptions import LineOptions
from row64tools.EquationOptions import EquationOptions
from row64tools.MarkerOptions import MarkerOptions
from row64tools.FillOptions import FillOptions
import copy

class TrellisData:
	
	Name = "" # series name
	Labels  = "" # string - x Axis Values
	XValues = "" # string
	YValues = "" # string - Y Axis Values
	ZValues = "" # string
	IValues = "" # string - grid index or row category values
	JValues = "" # string - grid col values
    
	EQOptions = None # EquationOptions() - equation options (scatter, bubble)
	ColorMode = 0 # int - color mode (bar)
	Color = [] # vector<int> - color theme (bar, bubble)
	Marker = None # MarkerOptions() -  marker options (scatter, line, bubble)

    # Line and Fill options (scatter, line)
	HasLine = True # bool
	Line =  LineOptions()
	FillType = 0 # int32 - 0=None, 1=Fill, 2=Gradient
	Fill = [] # vector of fill FillOptions()
	
	def __init__(self):
		self.Line = LineOptions()
		baseFill = FillOptions()
		self.Fill=[]
		self.Fill.append( copy.deepcopy(baseFill) )

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)