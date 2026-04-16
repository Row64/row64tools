from row64tools.AxisOptions import AxisOptions
from row64tools.GridOptions import GridOptions
from row64tools.FontOptions import FontOptions

class LinePlotFormat:
	
	GridlineX = GridOptions() # GridOptions class
	GridlineY = GridOptions() # GridOptions class
	AxisX = AxisOptions() # AxisOptions - horizontal axis
	AxisY = AxisOptions() # AxisOptions - vertical axis
	DataLabelPos = 3 #  int32 - 0 = none, 1 = right, 2 = left, 3 = top, 4 = bottom
	PrimarySep = 1 # int32 - 0 = none, 1 = comma, 2 = semicolon, 3 = period, 4 = newline, 5 = space
	SecondarySep = 0 # int32
	LabelTypes = [0,0,0] # = int32vec { primary, secondary1, secondary2 } where 0 = none, 1 = label, 2 = value
	Reverse = False # reverses primary & secondary order
	PrimaryFont = FontOptions() # FontOptions class
	SecondaryFont = FontOptions() # FontOptions class
	FontAlignment = [0.5,0.6] # floatvec - [x alignment, y alignment]
	LabelShift = 0 # float - LabelShift in content space
	ChartPadX = [0, 0] # floatvec - [left padding, right padding]
	InterpolateNull = True # Smooth through NULL values
	# Dynamic Reveal Racing Text
	DR_DataLabelPos = 1 # int32 - 0 = none, 1 = right, 2 = left, 3 = top, 4 = bottom
	DR_PrimarySep = 4 # 0 = none, 1 = comma, 2 = semicolon, 3 = period, 4 = newline, 5 = space
	DR_SecondarySep = 1 # int32
	DR_LabelTypes = [0, 0, 0] # int32vec - { primary, secondary1, secondary2 } where 0 = none, 1 = series name, 1 = label, 3 = value
	DR_Reverse = False # reverses primary & secondary order
	DR_PrimaryFont = FontOptions() # FontOptions
	DR_SecondaryFont = FontOptions() # FontOptions
	DR_FontAlignment = [0.5, 0.6] # floatvec - x alignment, y alignment
	DR_LabelShift = 0 # float - LabelShift in content space

	def __init__(self):pass

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)