# info about data within a dataframe
class DfInfo:
	Valid = True
	Path = "" # full path to source file
	Conn = "" # connection string for ramdb
	Db = "" # db string for ramdb
	Table = "" # table string for ramdb
	NbCols = 0
	NbRows = 0
	ColNames = [] # vector of string
	ColTypes = [] # vector of int32
	ColSizes = [] # vector of int32
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)