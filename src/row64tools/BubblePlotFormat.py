from row64tools.AxisOptions import AxisOptions
from row64tools.GridOptions import GridOptions
from row64tools.FontOptions import FontOptions

class BubblePlotFormat:
	
	GridlineX = GridOptions() # GridOptions class
	GridlineY = GridOptions() # GridOptions class
	AxisX = AxisOptions() # AxisOptions class
	AxisY = AxisOptions() # AxisOptions class
	DataLabelPos = 5 # int32 - 0 = none, 1 = right, 2 = left, 3 = top, 4 = bottom, 5 = center 
	PrimarySep  = 1 # int32 - 0 = none, 1 = comma, 2 = semicolon, 3 = period, 4 = newline, 5 = space 
	SecondarySep = 1 # int32 
	LabelTypes = [0, 0, 0] # int32vec - [primary, secondary1, secondary2]  where 0 = none, 1 = label, 2 = x value, 3 = y value, 4 = z value
	Reverse = False # bool
	PrimaryFont = FontOptions() # FontOptions class
	SecondaryFont = FontOptions() # FontOptions class 
	FontAlignment = [0.5, 0.6] # floatvec - [x alignment, y alignment]
	LabelShift = 0 # float - LabelShift in content space
	MinChipSize = 0 # float - Minimum bubble size (this is a % of the max bubble size, which is given by Details.Legend.Size)
	
	def __init__(self):
		self.GridlineX = GridOptions()
		self.GridlineY = GridOptions()
		self.AxisX = AxisOptions()
		self.AxisY = AxisOptions()
		self.PrimaryFont = FontOptions()
		self.SecondaryFont = FontOptions()

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
