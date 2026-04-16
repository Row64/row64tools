from row64tools.FontOptions import FontOptions

class VennFormat:
	
	PrimarySep = 1 # int32 - 0 = none, 1 = comma, 2 = semicolon, 3 = period, 4 = newline, 5 = space
	SecondarySep = 0 # int32 
	LabelTypes = [1, 0]  # int32vec - [primary, secondary]  where 0 = none, 1 = label, 2 = value
	Reverse = False # reverses primary & secondary order
	PrimaryFont = FontOptions() # FontOptions class
	SecondaryFont = FontOptions() # FontOptions class
	FontAlignment = [0.5, 0.6] # floatvec - [x alignment, y alignment]
	LabelShift = 0.0 # float
	RadiusScale = 1.0 # float
	FillAlpha = 0.68 # float
	FlipVenn3 = False
	RotateIndex = 0 # int32
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)