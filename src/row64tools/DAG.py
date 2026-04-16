from row64tools.SSheet import SSheet
from row64tools.FormulaParser import FormulaParser, ParseD, Coordinate
from row64tools.TopoSolver import TopoSolver
from row64tools.bytestream import bytestream as bStream

def read_a1_col(inCol): # A1 column letters to a 0-based index (i.e., A --> 0)
	if inCol=="":return -1
	col = inCol.upper()
	parts = col.split(":")
	ccol = parts[0]
	retVal = 0 
	for i in range(len(ccol)-1,-1,-1):retVal += (ord(ccol[i])-64)*int(pow(26,len(ccol)-(i+1)))
	return int(retVal) - 1

def LS(inStr, inW):
	ll = int(inW - len(inStr))
	if ll < 0:ll=0
	print(inStr + ' ' * ll, end='')

def LC(inStr): print(inStr, end='')

def LL(inC, inW): # Log Cell
	fBl = "\033[1m" # bold
	fDi = "\033[2m" # dim
	fR = "\033[31m" # red
	fG = "\033[32m" # green
	fY = "\033[33m" # yellow
	fB = "\033[34m" # blue
	fM = "\033[35m" # magenta
	fA = "\033[36m" # cyan
	fW = "\033[37m" # white
	fC = "\033[0m" # clear
	cellW = 0
	for ci in inC:cellW += len(ci)
	ll = int(inW - cellW)
	if cellW == 0: # log blank cell
		LC(fM)
		ll2 = ll -1
		print('_' + ' ' * ll2, end='') 
		return
	if inC[0] != "":
		LC(fW)
		LC(inC[0])
	if inC[1] != "":
		LC(fG)
		LC(inC[1])
	if inC[2] != "":
		LC(fB)
		LC(inC[2])
	if inC[3] != "":
		LC(fA)
		LC(inC[3])
	if ll < 0:ll=0
	print(' ' * ll, end='')

class DagNode:

	Parse = None; # ParseD result
	Formula = ""
	Value = ""
	Coord = ("",-1,-1) # Tuple for Sheet Coord (sheet name, col, row)
	Index = -1 # Current node index in the DAG_Nodes vector
	Parent = -1 # int for parent index in the DAG
	ParentParseIndex = -1 # parse tree index of parent node Parse
	SkipParent = False # skip adding node as a dependency (this is set to true when the node is part of a row/column link)
	ParseLinks = [] # vector<vector<int>> Vector of vector containing child node indices (parallel to Parse vectors)   
	Cyclic = False # Indicates this node is in a cycle
	DFLink = False # Indicates this node has a dataframe link
	Edges = [] # List of edge connections to parent nodes { Parent Node Index, Parent Parse Index }
	NbUse = 1
	def __init__(self, inCord, inParent,parentParseI=-1,skipParent=False):
		self.Coord = inCord # tuple (sheet name, col, row)
		self.Parent = inParent
		self.ParentParseIndex = parentParseI
		self.SkipParent = skipParent
	def HasEdge(self):return self.Parent != -1 and self.ParentParseIndex != -1
	def Edge(self): return (self.Parent, self.ParentParseIndex)

class DAG:

	CurrentSheet = "" # Cache the current sheet name when processing DAG
	Sheets = None # global Dash64 list of sheets in the API for cross checking links
	SSheets = [] # list of SSheet() objects
	ValueCells = {} # dict <SheetCord Tuple, string>
	DAG_Nodes = [] # list of DagNode()
	DAG_Map = {} # map<SheetCord, int> - Map to look up DAG_Nodes indices
	DAG_Edges = [] # vector<int,int> - Edges are pairs of indicies in DAG_Nodes
	CoordMap = {} # map<SheetCord, vector<SheetCord>>
	DFLists = {} # key = Shee Name, value is a list of Dataframe Sheet names linked by this sheet
	SLookup = {} # build quick lookup for sheet names Index

	# CoordMap tracks dependencies between sheet coords
	# all key coords are formula cells
	# 	{ key coord, list of coords that the key coord depends on }
	#  - SheetCords representing an entire row have the form :    { sheetname,  -1, row }
	#  - SheetCords representing an entire column have the form : { sheetname, col,  -1 }
	#  - SheetCords representing an entire sheet have the form:   { sheetname,  -1,  -1 }

	def __init__(self):
		self.DAG_Nodes.append( DagNode( ("root", -1, -1), -1 ) ) # root node with no parent must be DAG_Nodes[0]
	
	def set_cell(self, inA1, inCellDef):
		co = Coordinate()
		FP = FormulaParser()
		cType = FP.get_a1_type(inA1,co)
		cList = []
		self.expand_cord(cType,co,cList)
		# print(cList)
		# co.log()
		for c in cList:
			for j,cStr in enumerate(inCellDef):
				if cStr == None: continue
				si = self.SLookup[c[0]] # sheet index
				self.SSheets[si].Data[c[1]][c[2]][j] = cStr
		# self.log_sheet(self.SSheets[0].Data)

	def expand_cord(self, inType, co, cList):
		if not self.is_ws_link(inType): return # EXIT if coordinate is not a spreadsheet link
		if inType == 35: # WSCord - single coordinate, ex. Sheet1!A1
			cList.append(  (co.sheetName, co.start[0],co.start[1]) )
		elif inType == 36: # WSRange - cell range, ex. Sheet1!A1:A99
			for i in range(co.start[0], co.end[0]+1):
				for j in range(co.start[1], co.end[1]+1): cList.append( (co.sheetName, i,j) )
		elif inType == 37: # WSColumn - column range, ex. Sheet1!C:C
			sDim = self.Sheets.get_sheet_dim(co.sheetName)
			nbR = sDim[3]
			for i in range(co.start[0], co.end[0]+1):
				for j in range(0, nbR+1): cList.append( (co.sheetName, i,j) )
		elif inType == 38: # WSRow - row range, ex. Sheet1!3:3
			sDim = self.Sheets.get_sheet_dim(co.sheetName)
			for j in range(co.start[1], co.end[1]+1):
				for i in range(0, sDim[2]+1): cList.append( (co.sheetName, i,j) )

	def load(self, inBuf, inSheets):
		self.Sheets = inSheets # global list of sheets
		bs = bStream()
		bs.load_from_buffer(inBuf)
		for i,sItem in enumerate(inSheets.Items):
			if sItem.Type == "Spreadsheet":
				self.add_sheet(inSheets.Names[i], sItem.SetArea, []) # add a blank sheet in the DAG
		sheets = bs.get_string_vector( "Cells_sheet" )
		cols = bs.get_int64_vector( "Cells_col" )
		rows = bs.get_int64_vector( "Cells_row" )
		cells = bs.get_string_vector( "Cells_str" )
		i=0
		while i < len(cells): # fill self.SSheets with cells that are not part of the DAG
			si = self.SLookup[sheets[i]] # sheet index
			parts = cells[i].split(chr(19)) # dc3 / Device Control Three
			for j,cStr in enumerate(parts):self.SSheets[si].Data[rows[i]][cols[i]][j] = cStr
			i+=1
		DagList = bs.get_stream_vector( "DAG" )
		for i,dBuf in enumerate(DagList):
			dbs = bStream()
			dbs.load_from_buffer(dBuf)
			col = dbs.get_int64("Col")
			row = dbs.get_int64("Row")
			cell = dbs.get_string("Cell")
			parts = cell.split(chr(19)) # split by dc3 / Device Control Three
			for j,cStr in enumerate(parts):self.SSheets[si].Data[row][col][j] = cStr
		# self.log_sheet(self.SSheets[0].Data)
		
	def add_sheet(self, inName, inDim, inDef):
		for sSheet in self.SSheets: # don't add a sheet if it already exists
			if sSheet.Name == inName: return
		ss = SSheet()
		ss.SetArea = inDim
		d = [] # fill blank cell data
		for i in range(0, inDim[3]+1): # rows
			row = []
			for j in range(0, inDim[2]+1): row.append(["","","","",""]) # columns
			d.append(row)
		for cd in inDef:
			if cd[1]==None:cd[1]=""
			coord = self.get_coord(cd[0])
			val = str(cd[1])
			if len(val)>0 and val[0] == "=":d[coord[1]][coord[0]][1] = val[1:]
			else:d[coord[1]][coord[0]][0] = val
			if len(cd) > 2:d[coord[1]][coord[0]][2] = cd[2]
			if len(cd) > 3:d[coord[1]][coord[0]][3] = cd[3]
			if len(cd) > 4:d[coord[1]][coord[0]][4] = cd[4]
		ss.Data = d
		ss.Name = inName
		ss.SetArea = inDim
		self.DFLists[inName] = []
		self.SSheets.append(ss)
		# self.log_sheet(d)
		self.SLookup = {} # update sheet name lookup
		for i, sItem in enumerate(self.SSheets): self.SLookup[sItem.Name] = i
	
	def log(self, inSheetName):
		sInd = -1
		for i,sSheet in enumerate(self.SSheets): # don't add a sheet if it already exists
			if sSheet.Name == inSheetName:
				sInd = i
				break
		if sInd == -1:
			print("Spreadsheet Log, inSheetName:",inSheetName,"not found")
			return
		self.log_sheet(self.SSheets[sInd].Data)
			
	def log_sheet(self, inD):
		print("-------------------- Sheet -------------------")
		for i,row in enumerate(inD):
			for j,cell in enumerate(row):
				LL(cell, 30)
			LC("\033[37m\n") # terminal color back to white

	def get_sheet_coord(self, inSName, inA1): # sheet coord is a tuple: sheet name, col, row
		if inA1 == "":return [-1,-1]
		digits = ''.join(filter(str.isdigit, inA1))
		alphas = ''.join(filter(str.isalpha, inA1))
		if digits == "":return [-1,-1]
		if alphas == "":return [-1,-1]
		return (inSName, read_a1_col(alphas), int(digits)-1)
	
	def get_coord(self, inA1): # get: col, row
		if inA1 == "":return [-1,-1]
		digits = ''.join(filter(str.isdigit, inA1))
		alphas = ''.join(filter(str.isalpha, inA1))
		if digits == "":return [-1,-1]
		if alphas == "":return [-1,-1]
		return (read_a1_col(alphas), int(digits)-1)
	
	def add_dependency(self, co, coDepend): # Add to CoordMap
		if co[1] < 0 and co[2] < 0: 
			print("CoordMap key must be a valid cell coord")
			return
		if self.CoordMap.get(co) is not None: # cord exists
			# Only insert of coord dependency if there is no overlapping dependency
			if coDepend not in self.CoordMap[co]:
				self.CoordMap[co].append(coDepend)
		else:self.CoordMap[co] = [coDepend]

	def get_dag_node_ind(self, inCoord):
		for i,coord in enumerate(self.DAG_Nodes):
			if coord == inCoord:return i
		return -1
	
	def insert_dag_node(self, inDNode):
		# If the node has a parent, then add the dependency to the CoordMap
		if inDNode.Parent != -1 and inDNode.SkipParent == False:
			parent = self.DAG_Nodes[ inDNode.Parent ]
			if parent.Coord[1] != -1: # parent.Col != -1
				self.add_dependency( parent.Coord, inDNode.Coord )
		# Update or add the node to DAG_Nodes.
        # If the node has has an edge connection to a parent, then
        # add the current node index to the parent node ParseLinks
		nodeI = self.get_dag_node_ind( inDNode.Coord )
		if nodeI != -1: # DagNode found, update the edges data
			existingNode = DAG_Nodes[ nodeI ]
			if inDNode.HasEdge():
				edge = inDNode.Edge()
				parent = DAG_Nodes[ edge[0] ]
				parent.ParseLinks[ edge[1] ].append( nodeI )
				existingNode.Edges.append( edge )
			existingNode.NbUse+=1
		else:
			# DagNode not found, add to DAG_Nodes
			# The first time you insert a node, remove it from the CoordMap
			# since prior known dependencies may have changed
			self.CoordMap.pop(inDNode.Coord, None) # remove coord from CoordMap if key exists
			nodeI = len(self.DAG_Nodes)
			if inDNode.HasEdge():
				edge = inDNode.Edge()
				parent = self.DAG_Nodes[ edge[0] ]
				parent.ParseLinks[ edge[1] ].append( nodeI )
			self.DAG_Map[ inDNode.Coord ] = len(self.DAG_Nodes)
			self.DAG_Nodes.append(inDNode)
		return nodeI

	def parse_formula(self, inN):
		c1 = inN.Formula.count('(')
		c2 = inN.Formula.count(')')
		if c1 != c2:
			Parse = ParseD()
			Parse.Values.append( inN.Formula )
			Parse.Types.append( 8 ) # 8=Unquoted Text
			Parse.Children.append( [] )
			Parse.Parents.append(-1)
			Parse.ParsedRanges.append( Coordinate() )
			inN.ParseLinks = [[]]
			print("Invalid Formula - parenthesis mismatch:",inN.Formula)
			return
		FP = FormulaParser()
		inN.Parse = FP.parse( inN.Formula )
		inN.ParseLinks = []
		i=0
		for i in range(len(inN.Parse.Values)):inN.ParseLinks.append([])
		i=0
		while i < len(inN.Parse.ParsedRanges): # process links to other worksheets or dataframes
			prange = inN.Parse.ParsedRanges[i]
			ptype = inN.Parse.Types[i]
			if self.is_ws_link(ptype) and prange.sheetName == "":
				inN.Parse.ParsedRanges[i].sheetName = inN.Coord[0]
				if inN.Parse.Types[i] >= 31 and inN.Parse.Types[i] < 35: # type >= cord && type < WSCord
					# bump / promote link type to WS Range (Worksheet)
					# WSCord=35, WSRange=36, WSColumn=37, WSRow=38
					inN.Parse.Types[i] += 4
			tabType = self.Sheets.get_tab_type(prange.sheetName)
			if tabType == "DataFrame":
				if ptype >= 31: # bump / promote link type to DS Range (Dataframe / Datasheet)
					# DSCord=39, DSRange=40, DSColumn=41, DSRow=42
					if ptype < 35: inN.Parse.Types[i] += 8
					elif ptype < 39: inN.Parse.Types[i] += 4
				inN.DFLink = True
				self.DFLists[inN.Coord[0]] = [prange.sheetName]
			i+=1

	def process_sheet_links(self, eType, co, nodeList, parseIndex, parentIndex):
		# int eType, const Coordinate & co, std::vector<DagNode> & nodeList, int parseIndex, int parentIndex
		# Adds all cells described by the Coordinate that fall within the valid SetArea into the nodeList.
		# If any cell falls outside of a valid SetArea, then only add the first of such cells to the nodeList.
		if not self.is_ws_link(eType): return # EXIT if coordinate is not a spreadsheet link
		if eType == 35: # WSCord - single coordinate, ex. Sheet1!A1
			coord = (co.sheetName, co.start[0],co.start[1])
			nodeList.append( DagNode(coord, parentIndex, parseIndex, False) )
			return
		elif eType == 36: # WSRange - cell range, ex. Sheet1!A1:A99
			cS = co.start[0]
			cE = co.end[0]
			rS = co.start[1]
			rE = co.end[1]
			for i in range(cS, cE+1):
				for j in range(rS, rE+1):
					coord = (co.sheetName, i,j)
					nodeList.append( DagNode(coord, parentIndex, parseIndex, False) )
			return
		elif eType == 37: # WSColumn - column range, ex. Sheet1!C:C
			cS = co.start[0]
			cE = co.end[0]
			sDim = self.Sheets.get_sheet_dim(co.sheetName)
			nbR = sDim[3]
			for i in range(cS, cE+1):
				for j in range(0, nbR+1):
					coord = (co.sheetName, i,j)
					nodeList.append( DagNode(coord, parentIndex, parseIndex, False) )
				# Add the entire column as a dependency
				self.add_dependency(self.DAG_Nodes[parentIndex].Coord, (co.sheetName, i, -1))
			return
		elif eType == 38: # WSRow - row range, ex. Sheet1!3:3
			rS = co.start[1]
			rE = co.end[1]
			sDim = self.Sheets.get_sheet_dim(co.sheetName)
			nbC = sDim[2]
			for j in range(rS, rE+1):
				for i in range(0, nbC+1):
					coord = (co.sheetName, i,j)
					nodeList.append( DagNode(coord, parentIndex, parseIndex, False) )
				# Add the entire row as a dependency
				self.add_dependency(self.DAG_Nodes[parentIndex].Coord, (co.sheetName, -1, j))
			return

	def formula_crawl(self, inCellD, inParent, inDepth, inDNode):
		inDNode.Parent = inParent
		nodeIndex = self.insert_dag_node(inDNode)
		node = self.DAG_Nodes[nodeIndex]
		if node.NbUse == 1:
			node.Formula = inCellD[1]
			node.Value = inCellD[0]
			self.parse_formula(node)
			if node.DFLink: # Register dataframes in the CoordMap
				i=0
				while i < len(node.Parse.ParsedRanges):
					if self.is_ds_link(node.Parse.Types[i]): # is it a dafaframe link
						self.add_dependency(node.Coord, (node.Parse.ParsedRanges[i].sheetName, -1, -1))
					i+=1
		self.DAG_Edges.append( [inParent, nodeIndex] )
		# If we have already come across this node, just look for cycles and do not crawl children
		if self.DAG_Nodes[nodeIndex].NbUse > 1:
			return
		if node.Formula == "" and inDepth > 0: pass # empty formula
		else:
			# Cycle through the Parse to get the list of child nodes
			childNodes = [] # vector<DagNode>
			i=0
			while i < len(node.Parse.Values):
				self.process_sheet_links(node.Parse.Types[i], node.Parse.ParsedRanges[i],childNodes, i, nodeIndex)
				i+=1
			# Formula crawl the child nodes
			for cNode in childNodes:
				cData = self.get_cell_data(cNode.Coord)
				self.formula_crawl( cData, nodeIndex, inDepth+1, cNode )
	
	# --------------------------------- IMPORTANT NOTE -----------------------------------
	# You need to use the API to create all your sheets & dataframes first
	# BEFORE running LinkSheets and wiring the formulas. This includes both spreadsheets 
	# and dataframes.  Otherwise the links will crawled and found to be invalid
	
	def get_cell_data(self, inCoord): # returns the Value & Formula of a cell
		for sheet in self.SSheets:
			if sheet.Name == inCoord[0]:
				dat = sheet.Data[inCoord[2]][inCoord[1]]
				return [dat[0],dat[1]]

	def get_cell_buf(self, inCoord):
		# returns cell as a single string seperated by DC3 chars
		for sheet in self.SSheets:
			if sheet.Name == inCoord[0]:
				dat = sheet.Data[inCoord[2]][inCoord[1]]
				nbBlank = 0 # number of blank slots from the back of the cell
				j = len(dat)
				while j > 0:
					j-=1
					if dat[j] != "":break
					nbBlank+=1
				buf = dat[0]
				nb = 5 - nbBlank
				for i in range(1,nb):buf += chr(19) + dat[i] # 19 = dc3 / Device Control Three
				return buf
		return ""

	def get_cell_str(self, inCellList): # returns cell as a single string seperated by DC3 chars
		nbBlank = 0 # number of blank slots from the back of the cell
		j = len(inCellList)
		while j > 0:
			j-=1
			if inCellList[j] != "":break
			nbBlank+=1
		buf = inCellList[0]
		nb = 5 - nbBlank
		for i in range(1,nb):buf += chr(19) + inCellList[i] # 19 = dc3 / Device Control Three
		return buf

	def is_ws_link(self, inTp): # is the link type a type of worksheet
		return (inTp >= 31 and inTp <= 38)

	def is_ds_link(self, inTp): # is the link type a type of datasheet
		return (inTp >= 39 and inTp <= 42)
	
	def is_column_range(self, inC): # inC = Coordinate [col,row]
		return ((inC.start[1]==-1) and (inC.end[1]==-1) and (inC.start[0]>=0) and (inC.end[0]>=0))

	def is_row_range(self, inC): # inC = Coordinate [col,row]
		return ((inC.start[0]==-1) and (inC.end[0]==-1) and (inC.start[1]>=0) and (inC.end[1]>=0))
 
	def is_valid_range(self, inC): # inC = Coordinate [col,row]
		if inC.start == inC.end: return False
		if inC.start[0] < 0: return False
		if inC.start[1] < 0: return False
		if inC.end[0] < 0: return False
		if inC.end[1] < 0: return False
		return True

	def get_a1_col(self, inN):
		astr = ''
		while inN > 25:   
			astr += chr(65 + int(inN/26) - 1)
			inN = inN - (int(inN/26))*26
		astr += chr(65 + inN)
		return astr
	
	def get_a1_string(self, inC): # inC = Coordinate [col,row]
		prefix = ""
		if inC.sheetName != "": prefix = inC.sheetName + "!"
		if self.is_valid_range(inC):
			return prefix+self.get_a1_col(inC.start[0])+str(inC.start[1]+1)+":"+self.get_a1_col(inC.end[0])+str(inC.end[1]+1)
		elif self.is_column_range(inC):
			return prefix+self.get_a1_col(inC.start[0])+":"+self.get_a1_col(inC.end[0])
		elif self.is_row_range(inC):
			return prefix+str(inC.start[1]+1)+":"+str(inC.end[1]+1)
		return prefix+self.get_a1_col(inC.start[0])+str(inC.start[1]+1)

	def write_node(self, inDNode, inOrderedNodes):
		NodeStream = bStream()
		NodeStream.add_string("Sheet", inDNode.Coord[0])
		NodeStream.add_int64("Col", inDNode.Coord[1])
		NodeStream.add_int64("Row", inDNode.Coord[2])
		NodeStream.add_string("Cell", self.get_cell_buf(inDNode.Coord))
		NodeStream.add_bool("Cyclic", inDNode.Cyclic)
		NodeStream.add_bool("DFLink", inDNode.DFLink)
		if inDNode.Formula != "":
			NodeStream.add_string_vector( "P_Values", inDNode.Parse.Values )
			NodeStream.add_int32_vector( "P_Types", inDNode.Parse.Types )
			NodeStream.add_int32_vector2d( "P_Children", inDNode.Parse.Children )
			NodeStream.add_int32_vector( "P_Parents", inDNode.Parse.Parents )
			pranges = [""] * len(inDNode.Parse.ParsedRanges)
			i=0
			while i < len(pranges):
				if self.is_ws_link(inDNode.Parse.Types[i]) or self.is_ds_link(inDNode.Parse.Types[i]):
					pranges[i] = self.get_a1_string(inDNode.Parse.ParsedRanges[i])
				i+=1
			NodeStream.add_string_vector( "P_ParsedRanges", pranges )
		inOrderedNodes.append(NodeStream)
		# Remove from ValueCells since the cell data is in the DAG
		self.ValueCells.pop(inDNode.Coord, None) # remove coord key if it exists

	def get_df_list(self, inName):
		return self.DFLists[inName]
	
	# Generates and exports the DAG_Nodes based off of the EvalList into a Bytestream Buffer
	def get_buffer(self, inSheets):
		self.Sheets = inSheets # global list of sheets for checking connections across sheets
		for sSheet in self.SSheets:
			self.CurrentSheet = sSheet
			for i,row in enumerate(sSheet.Data):
				for j,cell in enumerate(row):
					if cell[1] == "": # not a formula
						# self.ValueCells[ (sSheet.Name, j,i) ] = cell[0]

						self.ValueCells[ (sSheet.Name, j,i) ] = self.get_cell_str(cell)
					else:
						cData = [cell[0],cell[1]] 
						dNode = DagNode((sSheet.Name, j,i), 0)
						self.formula_crawl(cData, 0,0, dNode )
		# print("================= SOLVING DAG & TOPOLOGICAL SORT ==================")
		# print(self.DAG_Edges)
		ts = TopoSolver(len(self.DAG_Edges)+1)
		for edge in self.DAG_Edges:
			# print("Adding Edge:",edge[0],edge[1])
			ts.add_edge(edge[0],edge[1])
		# ts.log_graph()
		OrderedDag = ts.topo_sort()
		MapTo = [-1] * len(self.DAG_Nodes) # vector<int>
		MapFrom = [] # vector<int>
		ind = 0
		OrderedNodes = []  # vector<ByteStream>
		count=0
		while OrderedDag:
			evalI = OrderedDag[len(OrderedDag)-1]
			dn = self.DAG_Nodes[evalI]
			if evalI == 0:break
			MapTo[evalI] = count
			MapFrom.append( evalI )
			self.write_node( dn, OrderedNodes )
			OrderedDag.pop()
			count+=1
		i=0
		OrderedNodesBuf = []
		while i < len(OrderedNodes): # Remap the ParseLinks
			dn = self.DAG_Nodes[ MapFrom[i] ]
			j=0
			while j < len(dn.ParseLinks):
				k=0
				while k < len(dn.ParseLinks[j]):
					dn.ParseLinks[j][k] = MapTo[dn.ParseLinks[j][k]]
					k+=1
				j+=1
			OrderedNodes[i].add_int32_vector2d( "ParseLinks", dn.ParseLinks )
			OrderedNodesBuf.append(OrderedNodes[i].save_to_buffer())
			i+=1
		# Prepare the non-formula cells (as parallel vectors)
		sheets = [] # vector<string>
		cols = [] # vector<int64_t>
		rows = [] # vector<int64_t>
		cells = [] # vector<string>
		for coord, val in self.ValueCells.items():
			sheets.append(coord[0])
			cols.append(coord[1])
			rows.append(coord[2])
			cells.append(val)
		BStream = bStream()
		BStream.add_stream_vector( "DAG", OrderedNodesBuf )
		BStream.add_string_vector( "Cells_sheet", sheets )
		BStream.add_int64_vector( "Cells_col", cols )
		BStream.add_int64_vector( "Cells_row", rows )
		BStream.add_string_vector( "Cells_str", cells )
		dagBuffer = BStream.save_to_buffer()
		return dagBuffer