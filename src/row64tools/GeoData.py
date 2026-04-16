from row64tools.ShapeAttributes import ShapeAttributes

class GeoData:
	
	ProjectionMode = "" #  int32 - 0 = None, 1 = Mercator, 2 = Mercator HD, 3 = Mercator HDX
	ProjectionData = [] #  vector<double> - [Mercator HDX] Raw lon/lat bounding box across all shape levels - { lonMin, lonMax, latMin, latMax, exponent }
	ShapeLayerData = []  # stream_vector - ShapeLayerData class - desc of polygon shapes in Geo
	CoordLayerData = [] # stream_vector - CoordLayerData class - desc of Coordinates in Geo
	ShapeAttributes = ShapeAttributes() # stream - ShapeAttributes class - shape layer attributes (applied to all shape layers)
	ViewNames = [] # vector<vector<string>> - Camera view names
	ViewRects = [] # vector<vector<double>> - Camera view rectangles { { minX, minY, maxX, maxY } }
	ShowBaseMap = False # bool - Show base map
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)