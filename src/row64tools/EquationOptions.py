from row64tools.FontOptions import FontOptions
from row64tools.LineOptions import LineOptions

class EquationOptions:
	
	RegressionL = LineOptions() # LineOptions class
	ShowEq = False # bool - show equation
	ShowR = False # bool - show regression line 
	EquationF = FontOptions() # FontOptions class
	ShowTrendline = False # For the regression line int for mode
	Type = 0 # int32 - 0 = linear, ...Add as more are added.
	Loc = [0.25,0.75] # floatvector - [% X going right, % Y going down] relative to the Table BB

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)