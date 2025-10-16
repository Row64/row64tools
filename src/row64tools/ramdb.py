import struct
import json
import numpy as np
import pandas as pd
import io
import os
import pathlib
from row64tools import bytestream
import math

i64step = 8
i32step = 4
i16step = 2
i8step = 1

BasicNames = ["null","int","bigint","float","bigfloat","text"]
BasicTypes = [0,0,1,2,3,4,5,5,4,4,5,5,5,4,4,4,4,4,5,5,2]
Steps = [0,4,8,4,8,10] # byte steps for each type
ColumnTypes = ["drop","null","int","bigint","float","bigfloat","text","image","longitude","latitude","3dobj","pdf","url","xcord","ycord","zcord","xperc","yperc","note3d","note2d","datetime","timedelta"]

def save_from_df(inDf, inPath, inFormats=[]):
	inDf = inDf.infer_objects()
	cLen = len(inDf.columns)
	bs = bytestream.bytestream()
	bs.add_string("Name","")
	bs.add_int64("NbCols",cLen)
	bs.add_int64("NbRows",len(inDf))
	bs.add_string_vector("ColNames",inDf.columns)
	cTile = bytearray()
	cMint = bytearray()
	cMintPos = 0
	cSize = [] # the max width of the column in bytes
	cTypes = [] # type of column in FRAD int format

	# NOTE: bytestream is little-endian targeting x86 and ARM chips
	# Python .fromhex is big-endian so we flip any sentinal NULL value to feed the bytes correctly
	for col in inDf.columns:
		if inDf[col].dtype=="int64":
			dSize = inDf[col].abs().ge(2 ** 32).to_numpy().any()
			if not dSize:inDf[col]=inDf[col].astype("int32")
		if inDf[col].dtype=="bool":
			for item in inDf[col] : 
				cTile += bytearray(struct.pack('i', item))
			cTypes.append(2)
			cSize.append(4)
		elif inDf[col].dtype=="int32" or inDf[col].dtype=="Int32":
			for item in inDf[col]:
				if pd.isnull(item):
					cTile += bytes.fromhex("00000080")  # 0x80000000 sentinal NULL value
				else:
					cTile += bytearray(struct.pack('i', item))
			cTypes.append(2)
			cSize.append(4)
		elif inDf[col].dtype=="int64" or inDf[col].dtype=="Int64":
			for item in inDf[col]:
				if pd.isnull(item):
					cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
				else:
					cTile += bytearray(struct.pack('q', item))
			cTypes.append(3)
			cSize.append(8)
		elif inDf[col].dtype=="float32":
			for item in inDf[col]:
				if pd.isnull(item) :
					cTile += bytes.fromhex("FFFFFFFF")  # 0xFFFFFFFF sentinal NULL value
				else: 
					cTile += bytearray(struct.pack('f', item))
			cTypes.append(4)
			cSize.append(8)
		elif inDf[col].dtype=="float64":
			for item in inDf[col]:
				if pd.isnull(item) : 
					cTile += bytes.fromhex("FFFFFFFFFFFFFFFF")  # 0xFFFFFFFFFFFFFFFF sentinal NULL value
				else : 
					cTile += bytearray(struct.pack('d', item))
			cTypes.append(5)
			cSize.append(8)
		elif(str(inDf[col].dtype)[:10] == "datetime64" ):
			dtArr = inDf[col].astype("datetime64[ns]")
			dtArr = dtArr.astype(np.int64)
			for item in dtArr : 
				if pd.isnull(item):
					cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
				else:
					cTile += bytearray(struct.pack('q', item))
			cTypes.append(20)
			cSize.append(8)
		elif(str(inDf[col].dtype)[:11] == "timedelta64" ):
			dtArr = inArr.astype("timedelta64[ns]")
			dtArr = dtArr.astype(np.int64)
			for item in dtArr : 
				if pd.isnull(item):
					cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
				else:
					cTile += bytearray(struct.pack('q', item))
			cTypes.append(3) # convert to int64
			cSize.append(8)
		else:
			maxLen=1;
			lenBuf = bytearray()
			for item in inDf[col]:
				if pd.isnull(item) or pd.isna(item):
					# Ingest NaN or Null string value into "" blank zero length string
					# We do have NULL strings in Row64 but we follow the ingest conventions of Row64 Studio
					cTile += bytearray(struct.pack('Q', cMintPos)) #uint 64 
					lenBuf += bytearray(struct.pack('H', 0)) #uint 16
				else:
					eItem = item.encode('ascii')
					iLen = len(eItem);					
					if iLen > maxLen:maxLen=iLen
					cMint+=eItem
					cTile += bytearray(struct.pack('Q', cMintPos)) #uint 64 
					lenBuf += bytearray(struct.pack('H', iLen)) #uint 16
					cMintPos+=iLen
			cTile+= lenBuf
			cTypes.append(6)
			cSize.append(maxLen)
	bs.add_int32_vector("ColTypes",cTypes)
	bs.add_int32_vector("ColSizes",cSize)
	if len(inFormats)==cLen:bs.add_string_vector("ColFormat",inFormats)
	else:bs.add_string_vector("ColFormat",['' for _ in range(cLen)])
	bs.add_buffer("cTile",cTile)
	bs.add_buffer("cMint",cMint)
	bs.save(inPath)

def log(inPath):
	bs = bytestream.bytestream()
	bs.read( inPath )
	bs.log_info()

def example_path():
	bPath = pathlib.Path(__file__).parent
	fName = "example.ramdb"
	fPath = os.path.join(bPath, fName)
	return fPath

def load_to_df(inPath): # load to dataframe
	bs = bytestream.bytestream()
	bs.read( inPath )
	FName = bs.get_string("Name")
	NbCols = bs.get_int64("NbCols")
	NbRows = bs.get_int64("NbRows")
	ColNames = bs.get_string_vector("ColNames")
	ColTypes = bs.get_int32_vector("ColTypes")
	ColSizes = bs.get_int32_vector("ColSizes")
	ColFormat = bs.get_string_vector("ColFormat")
	kInd = bs.get_key_ind("cTile","FRAD.Read",-1)
	kInd2 = bs.get_key_ind("cMint","FRAD.Read",-1)
	if(kInd==-1 or kInd2==-1):return
	f = bs.EL[kInd][0] # rolling index in FRAD buffer
	cTileI = bs.EL[kInd2][0] # index in cTile

	TypeDesc = []
	for i in range(NbCols):TypeDesc.append(BasicNames[BasicTypes[ColTypes[i]]])
	rtnObj = {"Name":FName,"NbCols":NbCols,"NbRows":NbRows,"ColNames":ColNames,"ColTypes":TypeDesc,"ColFormat":ColFormat,"Tables":[]}
	for i in range(NbCols):
		cbt = BasicTypes[ColTypes[i]]
		step = Steps[cbt]
		nextf = f + NbRows * step
		if cbt==0:continue
		elif cbt==1:rtnObj["Tables"].append(np.frombuffer(bs.B[f:nextf], dtype="int32"))
		elif cbt==2:rtnObj["Tables"].append(np.frombuffer(bs.B[f:nextf], dtype="int64"))
		elif cbt==3:rtnObj["Tables"].append(np.frombuffer(bs.B[f:nextf], dtype="float32"))
		elif cbt==4:rtnObj["Tables"].append(np.frombuffer(bs.B[f:nextf], dtype="float64"))
		elif cbt==5:
			tInd = len(rtnObj["Tables"])
			rtnObj["Tables"].append([])
			cInd = f # cMint offset rolling index
			lInd = f + NbRows * 8 # cMint length rolling index
			for j in range(NbRows):
				tPos = struct.unpack('Q', bs.B[cInd:cInd+8])[0] # uint 64
				cInd+=8
				tLen = struct.unpack('H', bs.B[lInd:lInd+2])[0] # uint 16
				lInd+=2
				cstart = cTileI+tPos
				rtnObj["Tables"][tInd].append(str(bs.B[cstart:cstart+tLen],'ascii'))
			f=lInd
		if cbt<5:f=nextf
	fdf=pd.DataFrame(data=rtnObj["Tables"]).T
	fdf.columns=ColNames
	fdf = fdf.infer_objects()
	for i,col in enumerate(fdf.columns):
		if ColTypes[i]==20:fdf[col] = fdf[col].astype("datetime64[ns]")
		elif ColTypes[i]==21:fdf[col] = fdf[col].astype("timedelta64[ns]")
	return fdf

def load_to_np(inPath): # load to object structure with numpy columns
	bs = bytestream.bytestream()
	bs.read( inPath )
	NbCols = bs.get_int64("NbCols")
	NbRows = bs.get_int64("NbRows")
	ColNames = bs.get_string_vector_np("ColNames")
	ColTypes = bs.get_int32_vector_np("ColTypes")
	ColSizes = bs.get_int32_vector_np("ColSizes")
	ColFormat = bs.get_string_vector_np("ColFormat")
	kInd = bs.get_key_ind("cTile","FRAD.Read",-1)
	kInd2 = bs.get_key_ind("cMint","FRAD.Read",-1)
	if(kInd==-1 or kInd2==-1):return
	f = bs.EL[kInd][0] # rolling index in FRAD buffer
	cTileI = bs.EL[kInd2][0] # index in cTile
	TypeDesc = []
	for i in range(NbCols):TypeDesc.append(BasicNames[BasicTypes[ColTypes[i]]])
	rtnObj = {"NbCols":NbCols,"NbRows":NbRows,"ColNames":ColNames,"ColTypes":TypeDesc,"ColSizes":ColSizes,"ColFormat":ColFormat,"Tables":[]}
	for i in range(NbCols):
		cbt = BasicTypes[ColTypes[i]]
		step = Steps[cbt]
		nextf = f + NbRows * step
		if cbt==0:continue
		elif cbt==1:rtnObj["Tables"].append(np.frombuffer(bs.B[f:nextf], dtype="int32"))
		elif cbt==2:rtnObj["Tables"].append(np.frombuffer(bs.B[f:nextf], dtype="int64"))
		elif cbt==3:rtnObj["Tables"].append(np.frombuffer(bs.B[f:nextf], dtype="float32"))
		elif cbt==4:rtnObj["Tables"].append(np.frombuffer(bs.B[f:nextf], dtype="float64"))
		elif cbt==5:
			tInd = len(rtnObj["Tables"])
			sList = []
			cInd = f # cMint offset rolling index
			lInd = f + NbRows * 8 # cMint length rolling index
			for j in range(NbRows):
				tPos = struct.unpack('Q', bs.B[cInd:cInd+8])[0] # uint 64
				cInd+=8
				tLen = struct.unpack('H', bs.B[lInd:lInd+2])[0] # uint 16
				lInd+=2
				cstart = cTileI+tPos
				sList.append(str(bs.B[cstart:cstart+tLen],'ascii'))
			rtnObj["Tables"].append(np.array(sList))
			f=lInd
		if cbt<5:f=nextf
	return rtnObj

def load_to_json(inPath): # load to json string, useful for a quick look at the data
	bs = bytestream.bytestream()
	bs.read( inPath )
	NbCols = bs.get_int64("NbCols")
	NbRows = bs.get_int64("NbRows")
	ColNames = bs.get_string_vector("ColNames")
	ColTypes = bs.get_int32_vector("ColTypes")
	ColSizes = bs.get_int32_vector("ColSizes")
	ColFormat = bs.get_string_vector("ColFormat")
	kInd = bs.get_key_ind("cTile","FRAD.Read",-1)
	kInd2 = bs.get_key_ind("cMint","FRAD.Read",-1)
	if(kInd==-1 or kInd2==-1):return
	f = bs.EL[kInd][0] # rolling index in FRAD buffer
	cTileI = bs.EL[kInd2][0] # index in cTile
	TypeDesc = []
	for i in range(NbCols):TypeDesc.append(BasicNames[BasicTypes[ColTypes[i]]])
	rtnObj = {"NbCols":NbCols,"NbRows":NbRows,"ColNames":ColNames,"ColTypes":TypeDesc,"ColSizes":ColSizes,"ColFormat":ColFormat,"Tables":[]}
	for i in range(NbCols):
		cbt = BasicTypes[ColTypes[i]]
		step = Steps[cbt]
		nextf = f + NbRows * step
		if cbt==0:continue
		tInd = len(rtnObj["Tables"])
		rtnObj["Tables"].append([])
		if cbt==1:
			for fi in range(f,nextf,4):rtnObj["Tables"][tInd].append(struct.unpack('i', bs.B[fi:fi+4])[0]) #int32 vector
		elif cbt==2:
			for fi in range(f,nextf,8):rtnObj["Tables"][tInd].append(struct.unpack('q', bs.B[fi:fi+8])[0]) #int64 vector
		elif cbt==3:
			for fi in range(f,nextf,4):rtnObj["Tables"][tInd].append(struct.unpack('f', bs.B[fi:fi+4])[0]) #float32 vector
		elif cbt==4:
			for fi in range(f,nextf,8):rtnObj["Tables"][tInd].append(struct.unpack('d', bs.B[fi:fi+8])[0]) #float64 vector
		elif cbt==5: #string vector
			cInd = f # cMint offset rolling index
			lInd = f + NbRows * 8 # cMint length rolling index
			for j in range(NbRows):
				tPos = struct.unpack('Q', bs.B[cInd:cInd+8])[0] # uint 64
				cInd+=8
				tLen = struct.unpack('H', bs.B[lInd:lInd+2])[0] # uint 16
				lInd+=2
				cstart = cTileI+tPos
				rtnObj["Tables"][tInd].append(str(bs.B[cstart:cstart+tLen],'ascii'))
			f=lInd
		if cbt<5:f=nextf
	return json.dumps(rtnObj)



