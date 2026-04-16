class ColumnFormat:

	def __init__(self):
		self.Code = "" # string - text formatting code
		self.Formula = "" # string - conditional formatting formula
		self.Theme = [] # vector<int> - conditional formatting 4-color theme
		self.DisplayName = "" # string - Display column name

	def log(self):
		print(" Code:",self.Code)
		print(" Formula:",self.Formula)
		print("Theme: [", end='')
		dl =""
		for tc in self.Theme:
			print(dl+"{:06x}".format(tc), end='')
			dl=", "
		print("]")
		print(" DisplayName:",self.DisplayName)

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)