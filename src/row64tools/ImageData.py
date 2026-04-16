import io
import os
import shutil
import struct
import array
import itertools
from pathlib import Path
from row64tools.bytestream import bytestream as bStream
from row64tools.ImageMarkers import ImageMarkers
from row64tools.ThumbData import ThumbData
from row64tools.SingleMarker import SingleMarker
import row64tools.png as png
import row64tools.rectpack.skyline as skyline
from row64tools.rectpack import newPacker
import row64tools.rectpack.packer as packer
from row64tools.SingleMarker import SingleMarker
from row64tools.SpriteSheet import SpriteSheet

class ImageData:

	# class dedicated to managing, packing and unpacking images into and out of sprite sheets
	def __init__(self, inPath, inSheetName, inSheetFolder):
		self.Path = inPath # Save Path
		self.SheetName = inSheetName
		self.SheetFolder = inSheetFolder
		self.SingleMarkers = [] # List of SingleMarker() - marker for 1 image broken out of sprite sheets
		
	def load(self):
		# Look for a markers.img file and store the data if needed
		mImg = os.path.join(self.SheetFolder,"markers.img")
		if os.path.exists(mImg):
			self.load_sprite_sheets(mImg)
	
	def thumb_to_buf(self, inT):
		buf = bytearray(struct.pack('i', inT.I)) 
		buf += bytearray(struct.pack('i', inT.X)) 
		buf += bytearray(struct.pack('i', inT.Y)) 
		buf += bytearray(struct.pack('i', inT.W)) 
		buf += bytearray(struct.pack('i', inT.H)) 
		buf += bytearray(struct.pack('i', inT.OX)) 
		buf += bytearray(struct.pack('i', inT.OY))
		return buf

	def get_thumb_data(self, inBuf, inId): # Packed UV Data
		i32step = 4
		nbSteps = int(len(inBuf)/i32step)
		intList = []
		bi = 0 # buffer index
		for i in range(nbSteps):
			intVal = struct.unpack('i', inBuf[bi:bi+i32step])[0]
			intList.append(intVal)
			bi+=i32step
		td = ThumbData()
		td.I = intList[0]
		td.X = intList[1]
		td.Y = intList[2]
		td.W = intList[3]
		td.H = intList[4]
		td.OX = intList[5]
		td.OY = intList[6]
		td.ID = inId
		return td

	def png_from_bytes(self, inPngPath, inW, inH, inBytes):
		# Assumes RGBA 8-bit bytes
		info  = {'greyscale': False, 'alpha': True, 'planes': 4, 'bitdepth': 8, 'size': (inW, inH)}
		pixels = array.array('B', inBytes)
		output = open(inPngPath, 'wb')
		writer = png.Writer(inW, inH, **info) # **sdInfo collects all the keyword arguments in a dictionary
		writer.write_array(output, pixels)
		output.close()

	def unpack_sprites(self, inPngPath, inSpriteI, inSpriteList):
		# Thumb data in the Thumb data from markers.img includes padding 
		# The padding needs to be stripped out to convert to .png
		sheetList = [] # get a list of sprite data that applies to this sheet
		for spriteData in inSpriteList:
			if spriteData.I == inSpriteI:sheetList.append(spriteData)
		parentFolder = Path(inPngPath).parent
		byteW = 4 # rgba byte width / stride length
		Pad = 1 # nb pixels to pad on each side
		with open(inPngPath, 'rb') as f:
			r = png.Reader(file=f)
			w, h, rows, info = r.read_flat()
			for i,sd in enumerate(sheetList):
				w2 = sd.W - Pad * 2
				h2 = sd.H - Pad * 2
				x0 = sd.X + Pad
				y0 = sd.Y + Pad
				x1 = x0 + w2
				y1 = y0 + h2
				ba = bytearray()
				for y in range(y0,y1):
					startB = (x0 + y * w) * byteW
					endB = (x1 + y * w) * byteW
					ba += rows[startB:endB]
				mPath = os.path.join(parentFolder,"testMarker"+str(i)+".png")
				self.png_from_bytes(mPath, w2, h2, ba)
				mark = SingleMarker() # SingleMarker data has no padding 
				mark.W=w2
				mark.H=h2
				mark.ID=sd.ID
				mark.Bytes=ba
				self.SingleMarkers.append(mark)
	
	def add_single_marker(self, inPngPath):
		mark = SingleMarker()
		markName = Path(inPngPath).stem
		parts = markName.split("_")
		with open(inPngPath, 'rb') as f:
			r = png.Reader(file=f)
			w, h, rows, info = r.read_flat()
			mark.W=w
			mark.H=h
			mark.ID=inPngPath
			mark.Bytes=bytearray(rows)
			mark.OX = int(w*0.5)
			mark.OY = int(h*0.5)
			if len(parts) > 2:
				if parts[-1].isdigit() and parts[-2].isdigit():
					mark.OY = int(parts[-1])
					mark.OX = int(parts[-2])
			self.SingleMarkers.append(mark)

	def make_sprite_sheets(self, inFolder):
		if len(self.SingleMarkers) == 0:return
		Pad = 1 # nb pixels to pad on each side
		packS = newPacker(pack_algo=skyline.SkylineBl, sort_algo=packer.SORT_AREA, rotation=False)
		for i,mrk in enumerate(self.SingleMarkers):packS.add_rect(mrk.W+Pad*2,mrk.H+Pad*2,i)
		for i in range(10):packS.add_bin(1024, 1024) # Max Target W,H for each bin
		packS.pack()
		ssl = [SpriteSheet() for i in range(len(packS))] # sprite sheet list
		for i,pbin in enumerate(packS):
			for rect in pbin:
				self.SingleMarkers[rect.rid].x = rect.x
				self.SingleMarkers[rect.rid].x = rect.y
				self.SingleMarkers[rect.rid].SheetID = i
				td = ThumbData()
				td.I = i
				td.X = rect.x
				td.Y = rect.y
				td.W = rect.width
				td.H = rect.height
				td.OX = self.SingleMarkers[rect.rid].OX
				td.OY = self.SingleMarkers[rect.rid].OY
				td.ID = self.SingleMarkers[rect.rid].ID
				td.RID = rect.rid
				x2 = td.X + td.W
				y2 = td.Y + td.H
				if x2>ssl[i].W:ssl[i].W = x2
				if y2>ssl[i].H:ssl[i].H = y2
				ssl[i].ImgData.append(td)
		byteW = 4
		for i,sh in enumerate(ssl): # ---------- make sprite sheets -------------
			bSize = sh.W * sh.H * 4
			sa = bytearray(bSize) # sprite sheet pixel byte array
			for td in sh.ImgData: # ThumbData ImgData includes padding, SingleMarkers has no padding
				rid =  td.RID
				ma = self.SingleMarkers[td.RID].Bytes # marker pixel byte array
				w = self.SingleMarkers[td.RID].W
				h = self.SingleMarkers[td.RID].H
				for y in range(h):
					yp = y # yp = y in png
					ys = y+td.Y+Pad # ys = y in sprite sheet
					xp = (yp * w) * byteW # xp = byte x in png
					xs = (td.X+Pad + ys * sh.W) * byteW # xs = byte x in sprite sheet
					for x in range(w):
						sa[xs] = ma[xp]
						sa[xs+1] = ma[xp+1]
						sa[xs+2] = ma[xp+2]
						sa[xs+3] = ma[xp+3]		
						xp+=byteW
						xs+=byteW
			pngPath = os.path.join(self.SheetFolder,"markers_"+str(i)+".png")
			self.png_from_bytes(pngPath, sh.W, sh.H, sa)

		# ------------------------------ make markers.img ---------------------------------
		im = ImageMarkers()
		for i,sh in enumerate(ssl):
			for td in sh.ImgData:
				im.IDList.append(td.ID)
				im.ImgList.append(td.ID)
				im.ImgData.append(self.thumb_to_buf(td))
		iStr = bStream()
		iStr.add_string_vector("IDList", im.IDList)
		iStr.add_string_vector("ImgList", im.ImgList)
		iStr.add_buffer_vector("ImgData", im.ImgData)
		mingPath = os.path.join(self.SheetFolder,"markers.img")
		iStr.save(mingPath)

	def load_sprite_sheets(self, inMiPath):
		print("loadMImg:", inMiPath)
		bs = bStream()
		bs.read( inMiPath )
		im = ImageMarkers()
		im.IDList = bs.get_string_vector("IDList")
		im.ImgList = bs.get_string_vector("ImgList")
		spriteList = []
		bList = bs.get_buffer_vector("ImgData")
		for i,buf in enumerate(bList):
			spriteList.append( self.get_thumb_data(buf, im.IDList[i]))
		MaxIndex = 0 # will indicate the max sprite sheets index (nb -1)
		for idat in spriteList:
			if idat.I > MaxIndex:MaxIndex = idat.I
		for i in range(MaxIndex+1): # cycle through the list of sprite sheets and extract marker data & pixels
			pngPath = os.path.join(self.SheetFolder,"markers_"+str(i)+".png")
			if not os.path.exists(pngPath): 
				print("Invalid marker data, file not found:",pngPath)
				return
			with open(pngPath, 'rb') as f:self.unpack_sprites(pngPath, i, spriteList)
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)