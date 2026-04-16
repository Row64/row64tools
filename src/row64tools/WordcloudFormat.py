from row64tools.AxisOptions import AxisOptions
from row64tools.GridOptions import GridOptions
from row64tools.FontOptions import FontOptions

class WordcloudFormat:
	
	MaxSize = 1000 # int - max number of words to display
	PreferHorizontal = 0.95 # float
	WordDensity = 1.0 # float

	def __init__(self):pass

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)