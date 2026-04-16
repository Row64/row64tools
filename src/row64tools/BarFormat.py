from row64tools.AxisOptions import AxisOptions
from row64tools.GridOptions import GridOptions
from row64tools.FontOptions import FontOptions

class BarFormat:
	
	AxisX = AxisOptions() # AxisOptions class
	AxisY = AxisOptions() # AxisOptions class
	GridlineY = GridOptions() # GridOptions class - vertical axis grid lines
	ShowLabels = False # value labels
	LabelFont = FontOptions() # FontOptions
	LabelShift = 0 # float - pos as a percentage relative to top of bar
	Rounding = 0 # float
	BottomRound = False # bool
	ChartPadX = [0, 0] # floatvec - [left padding, right padding]
	AutoFit = True # bool
	BarSize = .25 # float
	StackedBar = False # bool
	HorizontalBar = False # bool
	BarOrder =  0 # int32 - 0 None, 1 Small to large, 2 Large to small
	ReorderSpeed = 0.5 # float - transition time in seconds
	
	# Depreciated
	LineToBarGap = 0 # float
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)