class VennData:
	
	Name = "" # Name of the series
	Values = ["","",""] # Cell reference of the values in the series (list or cell reference like Excel)
	Labels = ""  # Lables on the series (list or cell reference like Excel)
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)