class CoordLayerData:

	Name = "" # string - Name of Layer
	Lat = "" # string - sheet/dataframe ref to cord location
	Lon = "" # string - sheet/dataframe ref to cord location
	Radius = "" # string - sheet/dataframe ref to cord radius
	Color = "" # string - sheet/dataframe ref to cord color
	Visible = True # bool - layer visibility
	Attributes = None # CoordAttributes() - Coord layer attributes
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)