from row64tools.AxisOptions import AxisOptions
from row64tools.GridOptions import GridOptions
from row64tools.FontOptions import FontOptions

class ScatterPlotFormat:
	
	GridlineX = GridOptions() # GridOptions classes
	GridlineY = GridOptions() # GridOptions classes
	AxisX = AxisOptions() # AxisOptions
	AxisY = AxisOptions() # AxisOptions
	DataLabelPos = 3 # int32 - 0 = none, 1 = right, 2 = left, 3 = top, 4 = bottom
	PrimarySep = 1 # int32 - 0 = none, 1 = comma, 2 = semicolon, 3 = period, 4 = newline, 5 = space
	SecondarySep = 1 # int32
	LabelTypes = [0, 0, 0] # int32vec - [primary, secondary1, secondary2] where 0 = none, 1 = label, 2 = x value, 3 = y value
	Reverse = False # bool - reverses primary & secondary order
	PrimaryFont = FontOptions() # FontOptions class
	SecondaryFont = FontOptions() # FontOptions class
	FontAlignment = [0.5, 0.6] # floatvec - [x alignment, y alignment]
	LabelShift = 0 # float - LabelShift in content space

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
