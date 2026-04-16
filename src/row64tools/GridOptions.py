from row64tools.LineOptions import LineOptions

class GridOptions:
	
	Type = -1 # int32, -1=grid_none, 0=grid_categorical, 1=grid_numeric, 2=grid_datetime
	ShowMajor = True # bool - show major gridlines
	ShowMinor = False # bool - show minor gridlines 
	MajorUnit = 1.0 # double
	MinorUnit = 0.2 # double
	AutoMajor = True # bool
	AutoMinor = True # bool
	MinBound =  0.0 # double
	MaxBound =  0.0 # double
	AutoMin = True # bool
	AutoMax = True # bool
	PreferZero = True # bool
	MajorLine = LineOptions() # LineOptions class
	Divisions = 5 # float
	GridBase = 68 # int8 / char - // 0 = not set, 68 = 'D' day, 77 = 'M' month, 89 = 'Y' year
	MajorBase = 0 # int8 / char - // 0 = not set, 68 = 'D' day, 77 = 'M' month, 89 = 'Y' year
	MinorBase = 0 # int8 / char - // 0 = not set, 68 = 'D' day, 77 = 'M' month, 89 = 'Y' year
	MajorStart = 0 # double

	def __init__(self):
		self.MajorLine.Color =	0xD5D5D5
		
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)