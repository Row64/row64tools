from row64tools.LineOptions import LineOptions
from row64tools.FillOptions import FillOptions

class ChartLayout:
	
	RPadding = 10.0 # float - chart right padding
	LPadding = 10.0 # float - chart left padding
	TPadding = 10.0 # float - chart top padding
	BPadding = 10.0 # float - chart bottom padding
	Width = 1000.0 # float - default chart width, with be replaced by dashboard dimensions
	Height = 500.0 # float - default chart height, with be replaced by dashboard dimensions
	HasChartBorder = False
	ChartBorder = LineOptions() # LineOptions class
	HasChartFill = False
	ChartFill = FillOptions() # FillOptions class
	HasBkgdFill = False
	BkgdFill = FillOptions() # FillOptions class
	ChartFill.Color = 0xFFFFFF
	BkgdFill.Color = 0xFFFFFF

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
