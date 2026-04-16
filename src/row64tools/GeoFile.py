from row64tools.bytestream import bytestream as bStream
from row64tools.ShapeAttributes import ShapeAttributes
import zlib

class GeoFile:

	Func = "GEOSL" # string - communication tag for Dashboard to load geo, should not change
	File = ""  # string - file path, also parsed for a name in layer on/off UI
	Name = "" # string - sheetname this geoz is connected to
	ShapeI = 0 # int32 - index in Shape Layers
	Proj = 0 # int32 (only for Studio load) - 0 = None, 1 = Mercator, 2 = Mercator HD, 3 = Mercator HDX
	ProjectionData = [] #  vector<double> (only for Studio load) - [Mercator HDX] Raw lon/lat bounding box across all shape levels - { lonMin, lonMax, latMin, latMax, exponent }
	Types = [] # uint8_vector - Types of shape islands
	Verts = [] # float_vector2D - verticies: [shape/poly islands[ vertex x then y]]
	Inds = [] # uint32_vector2D - indicies: [shape/poly islands[ index list]]
	LineLens = [] # uint32_vector2D - list of indicies to start a new line (causing a break between point).  Only applies when the shape is lines
	BB = [] # float_vector - bouncing box
	Attrs = [] # int32_vector - index in ALook/Aname that poly islands connect to data
	ALook = [] # string_vector - string that islands will search for to connect to a row in data
	AName = "" # string - FeatureID Name in the the attribute list , geo data can have many attribute lists this show which one is being use
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
	
	def save_geoz(self, inGeoPath):
		bs = bStream()
		bs.add_string("Func", self.Func)
		bs.add_string("File", self.File)
		bs.add_string("Name", self.Name)
		bs.add_int32("ShapeI", self.ShapeI)
		bs.add_int32("Proj", self.Proj)
		bs.add_double_vector("ProjectionData", self.ProjectionData)
		bs.add_uint8_vector("Types", self.Types)
		bs.add_float_vector2d("Verts", self.Verts)
		bs.add_uint32_vector2d("Inds", self.Inds)
		bs.add_uint32_vector2d("LineLens", self.LineLens)
		bs.add_float_vector("BB", self.BB)
		bs.add_int32_vector("Attrs", self.Attrs)
		bs.add_string_vector("ALook", self.ALook)
		bs.add_string("AName", self.AName)
		bs.save(inGeoPath)
		geozPath = inGeoPath + "z"
		geoBytes = bytearray(b'BS=') + bs.save_to_buffer() # 'BS=' is the bytestream message header
		zcomp = zlib.compressobj( level=9, wbits=-15 ) # negative wbits means no header or checksum
		zdata = zcomp.compress( geoBytes ) + zcomp.flush( zlib.Z_FULL_FLUSH ) # add Z_FULL_FLUSH at the end to ensure permessage deflate clears and finishes
		f = open(geozPath, 'wb')
		f.write(zdata)
		f.close()

	def load(self, inPath, inSheetName, inInd):
		bs = bStream()
		bs.read( inPath )
		if bs.key_exists("File"):
			fstr = bs.get_string("File")
			if fstr != "": self.File = fstr
		self.Name = inSheetName
		self.ShapeI = inInd
		if bs.key_exists("Proj"): self.Proj = bs.get_int32("Proj")
		if bs.key_exists("ProjectionData"): self.ProjectionData = bs.get_double_vector("ProjectionData")
		self.Types = bs.get_uint8_vector("Types")
		self.Verts = bs.get_float_vector2d("Verts")
		self.Inds = bs.get_uint32_vector2d("Inds")
		self.LineLens = bs.get_uint32_vector2d("LineLens")
		self.BB = bs.get_float_vector("BB")
		if bs.key_exists("Attrs"): self.Attrs = bs.get_int32_vector("Attrs")
		if bs.key_exists("ALook"): self.ALook = bs.get_string_vector("ALook")
		if bs.key_exists("AName"): self.AName = bs.get_string("AName")
		