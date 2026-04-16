class ShapeLayerData:
	
	Locations = "" #  string - sheet/dataframe ref to list of GEOIDs
	ColorValues = "" # string - sheet/dataframe ref to parallel list of attribute data corresponding to Locations
	TimeValues = "" # string - sheet/dataframe ref to parallel list of time data corresponding to Locations
	FeatureIDs = [] # vector<string> - List of per-shape attributes from the data file
	FeatureListSelectedIndex = -1 # int32 - Index into the drop down list for the currently selected feature ID
	ShapeColor = 0xD4D4D4 # int32 - Color to be used when there are no ColorValues and/or feature data
	ShapeAlpha = 1.0 # float - Transparency value to be applied to shape layer geometry
	LineSize = 1.0 # float - Line thickness
	Visible = True # bool - Layer visibility
	# AttrLookup = [] # vector<string> - Attribute lookup list
	
	### options for processing, not part of the .dash format
	File = "" # File path for .geo
	Name = "" # Name of layer in dashboard on/off check boxes

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)