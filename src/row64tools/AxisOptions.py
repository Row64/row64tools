from row64tools.LineOptions import LineOptions
from row64tools.FontOptions import FontOptions

class AxisOptions:
	
	ShowAxis = True # bool
	ShowMajorTicks = True # bool 
	ShowMinorTicks = False # bool 
	ShowEndTicks = False # bool 
	ShowEndLabels = True # bool 
	TickShift = 0 # float - 0 = center, < 0 = shift out (left or down), > 0 = shift in (right or up)
	TickSize = 10 # float - size of tick in pixels
	Line = LineOptions() # LineOptions class
	ShowLabels = True # bool
	LabelFont = FontOptions() # FontOptions class
	LabelShift =  0 # float - 0 = base, < 0 = shift out (left or down), > 0 = shift in (right or up)
	LabelFormat = "#,##0" # string
	LabelAlign = 0 # float - 0 = center, < 0 = align bottom (or left), > 0  align top (or right) 
	LabelRotation = 0 #  float - 0 = no rotation, <0 swing clockwise up to -90 deg, >0 swing counter-clockwise up to 90 deg
	ShowTitle = False # bool
	Title = "" # string
	TitleFont = FontOptions() # FontOptions class
	TitlePos = [0.5,0.5] # floatvec
	TitleFont.Bold = True
		
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)