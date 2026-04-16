from row64tools.FontOptions import FontOptions
from row64tools.LineOptions import LineOptions

class PieFormat:
	
	LabelTypes = [1, 3, 0] # int32vec - [ primary, secondary1, secondary2 ] where 0 = none, 1 = label, 2 = value, 3 = percent
	PrimarySep = 4 # int32 - 0 = none, 1 = comma, 2 = semicolon, 3 = period, 4 = newline, 5 = space
	SecondarySep = 1 # int32
	Reverse = False # reverses primary & secondary order
	PrimaryFont = FontOptions() # FontOptions class
	SecondaryFont = FontOptions() # FontOptions class
	FontAlignment = [0.0, 0.6] # floatvec -[x alignment, y alignment]
	ShowLine = True
	LeaderLine = LineOptions() # LineOptions class
	LeaderPos = 1.3 # float
	LeaderDotSize = 6.0 # float
	LabelShift = [10.0, 0.0] # floatvec - whole label shift
	LineEnd = 0.12 # float
	SpacingByAngle = 0 # float - warps the spacing of the leader line where slices are thing to reduce crowding & text overlap
	SpacingByLength = 0 # float
	SpacingArea = 0.5 # float
	Doughnut = 0.46 # float
	FitScale = 1 # float - Scale down to fit in LayoutBB

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)