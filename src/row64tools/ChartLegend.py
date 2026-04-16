from row64tools.FontOptions import FontOptions
from row64tools.LineOptions import LineOptions
from row64tools.FillOptions import FillOptions

class ChartLegend:
	
	Show = False # show legend
	Pos = [ 0.755, 0.15]  # floatvec chart x,y percentage of dimensions
	Dim = [100.0, 100.0] # floatvec chart x,y dimensions
	HasBorder = True
	Border = LineOptions() # LineOptions class
	HasFill = True 
	Fill = FillOptions() # FillOptions class
	Font = FontOptions() # FontOptions class
	ChipSize = 7.0 # float - chip size
	ChipSpacing = 5.0 # float - spacing between chips
	Fill.Color = 0xFFFFFF

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)