from row64tools.OpStrengths import OpStrengths
import copy

class Coordinate:
	def __init__(self):
		self.start = [-1,-1] # array<int64_t, 2> - start of the range, in 0-based index, {col,row}
		self.end = [-1,-1] # array<int64_t, 2> - start of the range, in 0-based index, {col,row}
		self.sheetName = ""

	def log(self):
		print("Coordinate: " + self.sheetName + ", start["+str(self.start[0])+","+str(self.start[1])+"]",end="")
		print(", end["+str(self.end[0])+","+str(self.end[1])+"]")

	def Set(self, inStartStr, inEndStr, inSName):
		self.sheetName = inSName
		self.start = self.parse_single(inStartStr)
		self.end = self.parse_single(inEndStr)
	
	def parse_single(self, inStr):
		if inStr == "":return [-1,-1]
		digits = ''.join(filter(str.isdigit, inStr))
		alphas = ''.join(filter(str.isalpha, inStr))
		if digits == "" and alphas == "":return [-1,-1]
		if digits == "": return [self.read_a1_col(alphas), -1]
		if alphas == "": return [-1, int(digits)-1]
		return [self.read_a1_col(alphas), int(digits)-1]
	
	def read_a1_col(self,inCol): # A1 column letters to a 0-based index (i.e., A --> 0)
		if inCol=="":return -1
		col = inCol.upper()
		parts = col.split(":")
		ccol = parts[0]
		retVal = 0 
		for i in range(len(ccol)-1,-1,-1):retVal += (ord(ccol[i])-64)*int(pow(26,len(ccol)-(i+1)))
		return int(retVal) - 1

class ParseD:
	def __init__(self):
		self.Values = [] # vector<string>
		self.Types = [] # vector<int>
		self.Children = [] # vector<vector<int>>
		self.Parents = [] # vector<int>
		self.ParsedRanges = [] # vector of Coordinate

class Node:
	val = "" # string 
	index = -1 # int
	parent = -1 # int	
	cast = -1 # int	
	children = [] # vector<int> 
	def __init__(self, inVal, inIndex, inParent, inCast):
		self.val = inVal
		self.index = inIndex
		self.cast = inCast
		self.parent = inParent
		self.children = []

class Card:
	val = "" # single character string
	strength = 0 # int - default string & number strength
	index = 0 # int
	parent = -1 # int
	bubble = -1 # int
	cast = 0 # int
	parentBubble = -1 # int - index of parent buble for carry across
	fBubbles = [] # vector<int> - functions have n bubbles, the indicies are here
	token = "" # string
	function = "" # string - function name for carry across
	fIndex = -1 # int - function index for carry across
	fIndexMem = -1 # int - function index for parenthesis that might become function ARGLIST
	unaryMem = -1 # int - index for unary character(s) on unary function.  This index is to the unary character that becomes '(' before the function

	def init(self, inVal, inStrength, inIndex): # char inVal, int inStrength, int inIndex
		self.val = inVal
		self.strength = inStrength
		self.index = inIndex
		self.parent = -1
		self.bubble = -1
		self.cast = 0
		self.parentBubble = -1
		self.fBubbles = []
		self.token = ""
		self.function = ""
		self.fIndex = -1
		self.fIndexMem = -1
		self.unaryMem = -1

class FormulaParser:

	#### self. #######
	wins = [] # vector<int>
	bIndex = 0 # bubble index

	Values = [] # vector<string>
	Types = [] # vector<int>
	Children = [] # vector<vector<int>>
	Parents = [] # vector<int>
	ParsedRanges = [] # vector of Coordinate
	CardSlots = [] # vector<Card>
	Bubbles = [[]] # start with 1 empty bubble
	ReMap = {} #  dictionary <int, int> # remaps from index of order recieved to final index
	
	sCast = 0 # int -  0=uncast, 1=op, 2=function, 3=array, 4=int, 6=float, 8=Unquoted Text, 9=Single Quoted, 10=Double Quoted
	nbP = 0 # int - number of periods in string
	funcParent = 0 # int
	funcIndex = 0 # int
	slotVal = "" # string

	UnaryCycleBack = 0; # int - 0=no cycle back, 1=half cycle back to insert unary operator to complete NEG function
	parentBubbleMem = -1 # parent bubble memory, used to end unary operators
	fIndexMem = -1 # int - fIndex memory, used to end unary operators
	unaryI = -1 # int - memory for Stack lookup of unary index

	GatherUnary1 = 0 # int - 0 = do nothing, 1 = Gather #1 Unary Type 1 - Number/Link on next token
	GatherUnary3 = 0 # int - 0 = do nothing, 1 = Tag next function '(' as UNARY STAGE B - Type 3 - Function

	
	CurCard = Card()
	LastCard = Card()
	CarryForward = "" # string
	

	priorChar = 0 # int
	priorStrength = 0 # int
	forceEndStr = False # bool
	nextStrength = 0 # int
	valFP = "" # string
	coFP = Coordinate()

	def parse(self, inFormula):
		
		self.ParsedRanges = []
		self.ReMap = []
		self.CardSlots = []
		self.Bubbles = [[]]
		self.bIndex = 0 # bubble index
		self.UnaryCycleBack = 0
		
		Quoted = 0 # int - 0 = not in quote, 1 = in double quote, 2 = in single quote

		sCast = 0 # 0=uncast, 1=op, 2=function, 4=int, 6=float, 8=Unquoted Text, 9=Single Quoted, 10=Double Quoted
		
		nbP = 0 # number of periods in string
		slotVal = ""
		cInt = 0 # current char as an int

		GatherUnary1 = 0 
		GatherUnary3 = 0

		nextInt = 0 # lookahead, next char as int
		qMap = [8,10,9] # quote to cast map, 8=Unquoted Text, 9=Single Quoted, 10=Double Quoted
		self.formulaSize = len(inFormula)
		# for i in range(self.formulaSize):
		i = 0
		while i < self.formulaSize:
			if self.UnaryCycleBack != 1:
				c = inFormula[i]
				cInt = ord(c)
				# print(" --------------------- c: " +c+ "     -i: " + str(i))
				self.CurCard = Card()
				self.CurCard.init(c,0,i) # Initialize the current card
				self.wins = []
				self.CurCard.strength = OpStrengths[cInt]
			
			################################### Tolken Gathering Section  ###################################
			# This section gathers characters together into tokens, it does not proceed to the card game until a tolken is complete
			if self.UnaryCycleBack==1: pass # skip forward to the Unary Cycle Landing Point (no goto in Python)
			elif c==' ' and Quoted==0:
				self.LastCard = copy.deepcopy(self.CurCard)
				i+=1
				continue
			elif c=='"': # double quote
				while i < self.formulaSize-1: # quick crawl
					i+=1
					c = inFormula[i]
					if c == '"':
						if i < self.formulaSize -1 and inFormula[i+1] == '"':i+=1
						else: break
					self.CurCard.token += c
					if i == self.formulaSize -1:return
					sCast=10
			elif c=='\'': # single quote
				if Quoted == 2:
					self.CurCard.token = self.CarryForward
					self.CarryForward = ""
					Quoted = 0
				else:
					Quoted = 2
					if i < self.formulaSize-1:
						self.LastCard = copy.deepcopy(self.CurCard)
						i+=1
						continue
			elif c=='}': # treat array like parenthesis with array function
				c = ')'
				self.CurCard.val = ')'
			elif (c == '-' or c=='+') and i < self.formulaSize -1: # handle unary operators
				isUnary=False
				if i==0:isUnary=True
				else:
					pc = "" # find prior character before not including spaces - cycle back to skip spaces
					pcI = i # prior character index, for white space at start cases like:  "   -  30"
					j=i
					while j > 0:
						j-=1
						if inFormula[j] != " ":pc = inFormula[j];break
						if j==0: pcI=0
					if pcI==0:isUnary=True
					elif pc=='%' or pc=='^' or pc=='*' or pc=='/' or pc=='+' or pc=='-' or pc=='&' or pc=='<' or pc=='=' or pc=='>' or pc==',' or pc=='(':
						isUnary=True
				if isUnary:
					# first quick crawl to grab unary operators, they can be chained like -+-A1 which is valid in many spreadsheet formulas
					# Process '-' Symbol, Becomes '(' Symbol, Build NEG function
					sign = -1
					if c=='+':sign=1
					while i<self.formulaSize-1: # quick crawl to gather a set of multiple unary operators, Ex: =-+3
						if inFormula[i+1]=='-':sign*=-1
						elif inFormula[i+1]==' ':pass
						elif inFormula[i+1]!='+':break
						i+=1
					if sign==1: 
						self.LastCard = copy.deepcopy(self.CurCard); 
						i+=1
						continue # if the chain of unary operators is positive, discard them
					elif i < self.formulaSize -1:
						self.CurCard.token = "~" #  only a unary op can have val='(' and token="~"
						self.CurCard.val = '('
						c='('
						sCast=2
						self.CurCard.strength = 100
						self.CurCard.function = "NEG"
						if inFormula[i+1] == '(': # UNARY TYPE #2 - Unary Parenthesis, Ex: =-(3)
							self.CurCard.unaryMem = -12
							self.CurCard.parentBubble = self.bIndex
							self.CurCard.fIndex = i
							i+=1 # advance to absorb the parenthesis and make it a NEG function
						else:
							ucase=0
							j=i
							while j < self.formulaSize-1:
								j+=1
								FC=inFormula[j]
								if FC=='(':
									ucase = 3
									break
								elif FC==')' or FC=='}' or FC=='%' or FC=='^' or FC=='*' or FC=='/' or FC=='+' or FC=='-' or FC=='&' or FC=='<' or FC=='=' or FC=='>' or FC==',' or FC=='{' or FC==' ':
									ucase = 2
									break
							if ucase==0:ucase=2
							if ucase==2: # UNARY TYPE #1 - Unary Number or Link, Ex: =-A1
								self.CurCard.strength=0
								self.CurCard.unaryMem = -11
								GatherUnary1 = 1
							else: # UNARY TYPE #3 - Unary Function, Ex: =-PI()
								self.CurCard.unaryMem = -13
								GatherUnary3 = 1
						self.CurCard.fIndex = i

			elif self.CurCard.strength < 4: # carry forward current char to build text & numbers
				if self.CarryForward != "": self.CurCard.token = self.CarryForward
				self.CurCard.token += self.CurCard.val
				forceEndStr = False
				if i < self.formulaSize -1:
					if inFormula[i+1]==' ' and Quoted==False: forceEndStr = True # if next char is a space, it's the end of this string

				if forceEndStr == False:
					# print("i,self.formulaSize:",i,",",self.formulaSize)
					if i < self.formulaSize -1:
						# if the next card is a open paren ( with no operator inbetween, then this is the end of a function 
						# functions delete themselves and are carried forward in the stack as data.
						# they are then regenerated as the parent of the function bubbles when the function is defeated (card after function close)
						if inFormula[i+1] == '(':
							self.LastCard = copy.deepcopy(self.CurCard)
							i+=1
							continue
						# else if next card is not an operator, continue building the text / number
						nextStrength = 0
						nextInt = ord(inFormula[i+1])
						nextStrength = OpStrengths[nextInt]
						if nextStrength < 4:
							if sCast < 8:
								if sCast == 6: # float
									if c.isdigit() or c=='.':
										if c=='.':
											nbP+=1
											if nbP>1:sCast = qMap[Quoted]
									else:sCast = qMap[Quoted]
								elif sCast == 4: # int
									if c.isdigit(): pass # int - no recast keep going
									elif c=='.': 
										sCast = 6
										nbP+=1
									else:sCast = qMap[Quoted]
								elif sCast < 4:  # first character analysis
									if c.isdigit() or c=='-' or c=='+': sCast = 4
									elif c=='.':
										sCast = 6
										nbP=1
									else:sCast = qMap[Quoted]
							self.CarryForward = self.CurCard.token
							self.LastCard = copy.deepcopy(self.CurCard)
							i+=1
							continue
				if sCast < 8:
					if sCast == 6: # float
						if c.isdigit() or c=='.':
							if c=='.':
								nbP+=1
								if nbP>1:sCast = qMap[Quoted]
						else:sCast = qMap[Quoted]
					elif sCast == 4: # int
						if c.isdigit(): pass # int - no recast keep going
						elif c=='.': 
							sCast = 6
							nbP+=1
						else:sCast = qMap[Quoted]
					elif sCast < 4:  # first character analysis
						if c.isdigit() or c=='-' or c=='+': sCast = 4
						elif c=='.':
							sCast = 6
							nbP=1
						else:sCast = qMap[Quoted]
			elif c=='<': # carry forward multi-chararacter operators <= and <>
				if inFormula[i+1] == '=' or inFormula[i+1] == '>':
					sCast = 1
					self.LastCard = copy.deepcopy(self.CurCard)
					i+=1
					continue
			elif c=='>':
				if inFormula[i+1] == '=':
					sCast = 1
					self.LastCard = self.CurCard.copy()
					i+=1
					continue
			elif c=='=' and i>0: # = sign
				if self.LastCard.val == '<':
					sCast = 1
					self.CurCard.token = "<="
				elif self.LastCard.val == '>':
					sCast = 1
					self.CurCard.token = ">="

			######################################## PROCESS TOKEN SECTION #######################################
			if GatherUnary1==1 and c!='(':
				# print("--------------------------- UNARY STAGE C - Type 1 - Number/Link --------------------------------")
				parentBubbleMem = self.LastCard.parentBubble
				fIndexMem = self.LastCard.fIndex
				self.CurCard.cast = sCast
				self.CardSlots.append(self.CurCard)
				self.LastCard = copy.deepcopy(self.CurCard)
				sCast = 0
				c=')'
				self.CurCard = Card()
				self.CurCard.init(')',5, self.bIndex)
				self.CurCard.token = ")"
				self.CurCard.bubble = self.bIndex
				self.CurCard.cast = 2
				self.CurCard.function = "NEG"
				self.CurCard.parentBubble = parentBubbleMem
				self.CurCard.fIndex = fIndexMem
				GatherUnary1 = 0
			elif self.UnaryCycleBack==1: # end of unary op applied to function, back-patch UnaryMem

				# print("########################### Unary Cycle Landing Point ###########################")
				# ------------------ UNARY STAGE C - Type 3 - Function -----------------------
				fIndexMem = self.CurCard.unaryMem
				self.wins = []
				c=')'
				self.CurCard = Card()
				self.CurCard.init(')',5, self.bIndex)
				self.CurCard.token = "~" # only a unary close can have val=')' and token="~"
				self.CurCard.fIndex = fIndexMem
				self.CurCard.cast = 2
				self.CurCard.function = "NEG"
				self.CurCard.fBubbles.append(self.bIndex+1)
				self.UnaryCycleBack=0

			############################### CARD GAME  ###############################
			# battle between cards resolves dependency graph

			self.CarryForward = ""
			if c=='(' or c=='{': # ( = start a new parentheses, array bubble or function
				sCast = 0
				self.CurCard.parentBubble = self.bIndex
				self.bIndex = len(self.Bubbles) # enter new bubble
				newBubble = [] # vector<Node>
				if c=='{': # array
					self.CurCard.function = "{"
					self.CurCard.fIndex = i
					self.CurCard.fBubbles.append(self.bIndex)
					c = '(' # 40
					self.CurCard.val = '(' # 40
				elif self.CurCard.function == "NEG" and self.CurCard.token=="~": # only a unary op can have val='(' and token="~"
					#  ------------------------------- UNARY STAGE A2 -------------------------------
					self.CurCard.fBubbles.append(self.bIndex)
					self.CurCard.bubble = self.bIndex
				elif i > 0 and self.LastCard.strength < 4 and len(self.LastCard.token) > 0: # function or array
					self.CurCard.function = self.LastCard.token
					self.CurCard.fIndex = self.LastCard.index
					self.CurCard.fBubbles.append(self.bIndex)
					if GatherUnary3 == 1:
						# -------------------- UNARY STAGE B - Type 3 - Function ------------------
						if len(self.CardSlots) > 0:
							unaryI = len(self.CardSlots)-1
							self.CurCard.unaryMem = self.CardSlots[unaryI].fIndex
						GatherUnary3 = 0
				else: # parentheses
					self.CurCard.fIndexMem = i # here in case you hit a comma and this turns into a ARGLIST function
					self.CurCard.bubble = self.bIndex
				self.Bubbles.append(newBubble)
			else:
				if c==')': # end of parentheses bubble or function
					j = len(self.CardSlots)
					while j > 0:
						j-=1
						self.wins.append(j)
						if self.CardSlots[j].val == '(' or self.CardSlots[j].val == ',':
							self.CurCard.parentBubble = self.CardSlots[j].parentBubble
							if self.CardSlots[j].unaryMem>=0: self.UnaryCycleBack=1
							if self.CardSlots[j].fIndex == -1:  #  parentheses
								self.CurCard.bubble = self.CardSlots[j].bubble
							else: # function
								self.CurCard.function = self.CardSlots[j].function
								self.CurCard.fIndex = self.CardSlots[j].fIndex
								self.CurCard.fBubbles = self.CardSlots[j].fBubbles
								self.CurCard.unaryMem = self.CardSlots[j].unaryMem
							break
				elif c==',': # pass on comma data
					j = len(self.CardSlots)
					while j > 0:
						j-=1
						self.wins.append(j)
						if self.CardSlots[j].val == '(' or self.CardSlots[j].val == ',': # if '(' or ',' carry across data
							self.CurCard.parentBubble = self.CardSlots[j].parentBubble
							if self.CardSlots[j].function == "": # this is a parenthesis acting like a function - turn it into a ARGLIST function
								self.CardSlots[j].function = "ARGLIST"
								old_bIndex = self.CardSlots[j].bubble
								self.CardSlots[j].fBubbles.append(old_bIndex)
								self.CardSlots[j].fIndex = self.CardSlots[j].fIndexMem
							self.CurCard.function = self.CardSlots[j].function
							self.CurCard.fIndex = self.CardSlots[j].fIndex
							self.CurCard.fBubbles = self.CardSlots[j].fBubbles
							self.CurCard.unaryMem = self.CardSlots[j].unaryMem
							break
				else: 
					j = len(self.CardSlots)
					while j > 0: # main card battle
						j-=1
						if self.CurCard.strength < self.CardSlots[j].strength:break
						self.wins.append(j)
				nbWins = len(self.wins)

				j=0
				while j < nbWins:
					if (self.CardSlots[self.wins[j]].val == ',' or self.CardSlots[self.wins[j]].val == '(') and c==',': # process comma bubble when it's a card (not a carry forward)
						self.bIndex = len(self.Bubbles)
						self.CurCard.fBubbles.append(self.bIndex)
						newBubble = [] # vector<Node>
						self.Bubbles.append(newBubble)
						break
					elif self.CardSlots[self.wins[j]].val == '(': # end of bubble carry forward to be captured next card
						self.CardSlots[self.wins[j]].val = ')'
					elif self.CardSlots[self.wins[j]].val == ')': # bubble, function or array is captured - now gather 
						endParen = self.CardSlots[self.wins[j]]
						self.bIndex = endParen.parentBubble
						if endParen.fIndex == -1: # parentheses
							gatherI = endParen.bubble
							if gatherI < 0: 
								i+=1
								continue
							k=0
							while k < len(self.Bubbles[gatherI]):
								if k == len(self.Bubbles[gatherI]) - 1:
									newParent = i # index of winning card
									if j<nbWins-1: newParent = self.CardSlots[ self.wins[j+1] ].index
									self.Bubbles[gatherI][k].parent = newParent
								self.Bubbles[self.bIndex].append(self.Bubbles[gatherI][k])
								if self.bIndex == 0:
									self.ReMap.append( [self.Bubbles[gatherI][k].index, len(self.Bubbles[0])-1] )
								k+=1
						else: # function
							funcParent = i # the operator after a func is it's parent
							if j<nbWins-1: funcParent = self.CardSlots[ self.wins[j+1] ].index
							funcIndex = self.CardSlots[self.wins[j]].fIndex
							for bubbleI in endParen.fBubbles:
								k=0
								while k < len(self.Bubbles[bubbleI]):
									if k == len(self.Bubbles[bubbleI]) - 1: self.Bubbles[bubbleI][k].parent = funcIndex
									self.Bubbles[self.bIndex].append(self.Bubbles[bubbleI][k])
									if self.bIndex == 0:self.ReMap.append( [self.Bubbles[bubbleI][k].index, len(self.Bubbles[0])-1] )
									k+=1
								self.Bubbles[bubbleI] = []
							self.bIndex = endParen.parentBubble
							if endParen.function != "":
								if endParen.function[0] == '{': sCast = 3
								else: sCast = 2
							else: sCast=2
							functionNode = Node(self.CardSlots[self.wins[j]].function, funcIndex, funcParent, sCast)
							sCast = 0
							self.Bubbles[self.bIndex].append( functionNode )
							if self.bIndex == 0:
								self.ReMap.append( [functionNode.index, len(self.Bubbles[0])-1] )
					elif self.CardSlots[self.wins[j]].val==',': pass # if you hit a comma carry forward stop
					else: # main path to process wins from the battle between cards
						newParent = i
						if j<nbWins-1: newParent = self.CardSlots[self.wins[j+1]].index
						slotVal = self.CardSlots[self.wins[j]].token
						if self.CardSlots[self.wins[j]].cast != 10 and slotVal == "":
							slotVal = self.CardSlots[self.wins[j]].val
						self.Bubbles[self.bIndex].append( Node(slotVal, self.CardSlots[self.wins[j]].index, newParent, self.CardSlots[self.wins[j]].cast) )
						if self.bIndex == 0:
							self.ReMap.append( [self.CardSlots[self.wins[j]].index, len(self.Bubbles[0])-1] )
					j+=1

				if nbWins > 0:self.CardSlots = self.CardSlots[:-nbWins] # Reduce size by nbWins

			if self.CurCard.strength >= 40 and self.CurCard.strength <= 90: self.CurCard.cast = 1
			else: self.CurCard.cast = sCast
			self.CardSlots.append(copy.deepcopy(self.CurCard))
			sCast = 0
			self.LastCard = copy.deepcopy(self.CurCard)
			if self.UnaryCycleBack==1:
				# print("@@@@@@@@@@@@@@@@@@@@@@@@@@@ UNARY CYCLE BACK @@@@@@@@@@@@@@@@@@@@@@@@@@@")
				continue

			# self.log_card_slots()
			# self.log_bubbles(self.bIndex)
			i+=1

		# print(" ########## END OF STRING - FINAL CAPTURE ##########")

		############################ Capture all card slots ############################
		j = len(self.CardSlots)
		while j > 0: # main card battle
			j-=1
			if self.CardSlots[j].val == ')':  # bubble is captured, gather all cards within
				endParen = self.CardSlots[j]
				self.bIndex = endParen.parentBubble
				if endParen.fIndex == -1: # parentheses
					gatherI = endParen.bubble
					k=0
					while k < len(self.Bubbles[gatherI]):
						if k == len(self.Bubbles[gatherI]) - 1:
							newParent = -1 # index of winning card
							if j>0: newParent = self.CardSlots[j-1].index
							self.Bubbles[gatherI][k].parent = newParent
						self.Bubbles[self.bIndex].append(self.Bubbles[gatherI][k])
						if self.bIndex == 0: self.ReMap.append([ self.Bubbles[gatherI][k].index, len(self.Bubbles[0])-1 ])
						k+=1	
				else: # function
					funcParent = -1
					if j>0: funcParent = self.CardSlots[j-1].index
					funcIndex = endParen.fIndex
					for bubbleI in endParen.fBubbles:
						k=0
						while k < len(self.Bubbles[bubbleI]):
							if k == len(self.Bubbles[bubbleI]) - 1:
								self.Bubbles[bubbleI][k].parent = funcIndex
							self.Bubbles[self.bIndex].append(self.Bubbles[bubbleI][k])
							if self.bIndex == 0:
								self.ReMap.append([ self.Bubbles[bubbleI][k].index, len(self.Bubbles[0])-1 ])
							k+=1
						self.Bubbles[bubbleI] = []
					self.bIndex = endParen.parentBubble
					if endParen.function == "": sCast=2
					else:
						if endParen.function[0] == '{':sCast = 3
						else: sCast = 2
					functionNode = Node(endParen.function, funcIndex, funcParent, sCast)
					sCast = 0
					self.Bubbles[self.bIndex].append( functionNode )
					if self.bIndex == 0: self.ReMap.append([ functionNode.index, len(self.Bubbles[0])-1 ])
			else:
				newParent = -1
				if j>0: newParent = self.CardSlots[j-1].index
				slotVal = self.CardSlots[j].token
				if slotVal == "": slotVal = self.CardSlots[j].val
				self.Bubbles[self.bIndex].append( Node(slotVal, self.CardSlots[j].index, newParent, self.CardSlots[j].cast) )
				sCast = 0
				if self.bIndex == 0:self.ReMap.append([ self.CardSlots[j].index, len(self.Bubbles[0])-1 ])

		# self.log_card_slots()
		# self.log_bubbles(self.bIndex)
		
		######################################## Remap Loop ########################################
		# print("Remap:",self.ReMap)
		
		pResult = ParseD()
		pResult.Children = []
		i=0
		while i < len(self.Bubbles[0]):
			# ReMap dictionary <int, int> # remaps from index of order recieved to final index
			# TODO move remap to Python Dict to be faster
			for key,val in self.ReMap:
				if self.Bubbles[0][i].parent == key: 
					self.Bubbles[0][i].parent = val
					break
			pResult.Children.append([])
			i+=1
		
		a1Type = 0
		i=0
		co = Coordinate()
		while i < len(self.Bubbles[0]):
			co = Coordinate()
			if self.Bubbles[0][i].cast == 8: # 8=Unquoted Text, check for A1
				a1Type = self.get_a1_type(self.Bubbles[0][i].val, co)
				if a1Type != 0: self.Bubbles[0][i].cast = a1Type
				elif self.Bubbles[0][i].cast==8 or self.Bubbles[0][i].cast==2: # unquotedText or function
					if self.Bubbles[0][i].val == "TRUE":
						self.Bubbles[0][i].val = "1"
						self.Bubbles[0][i].cast = 4 # integer
					if self.Bubbles[0][i].val == "FALSE":
						self.Bubbles[0][i].val = "0"
						self.Bubbles[0][i].cast = 4 # integer				
			pResult.Values.append(self.Bubbles[0][i].val)
			pResult.Types.append(self.Bubbles[0][i].cast)
			pResult.Parents.append(self.Bubbles[0][i].parent)
			pResult.ParsedRanges.append(co)
			if self.Bubbles[0][i].parent >= 0:
				parentIdx = self.Bubbles[0][i].parent
				if parentIdx < len(self.Bubbles[0]):
					self.Bubbles[0][parentIdx].children.append(i)
					pResult.Children[parentIdx].append(i)
			i+=1

		######################################## LOG Loop ########################################
		
		# print("------------------ OUTPUT -----------------")
		# self.logv("V: ",pResult.Values)
		# self.logv("T: ",pResult.Types)
		# self.logv("P: ",pResult.Parents)
		# self.logv2("C: ",pResult.Children)
		
		# print("------------------ SUMMARY -----------------")
		# i=0
		# while i < len(self.Bubbles[0]):
		# 	print("["+str(i)+"] Node: ",end="")
		# 	print(self.Bubbles[0][i].val + " - p: " + str(self.Bubbles[0][i].parent) + ", c: ",end="")
		# 	d = ""
		# 	for chld in self.Bubbles[0][i].children:
		# 		print( d + str(chld), end="")
		# 		d = ", "
		# 	print( ", cast: " + str(self.Bubbles[0][i].cast))
		# 	i+=1
		
		return pResult

	def get_a1_type(self, inToken, inCoord):

		# link names contain A-Za-z, 0-9 and _ ' ' (space) (base name, not the aliases)
		# 0=uncast, 1=op, 2=function, 4=int, 6=float, 8=Unquoted Text, 9=Single Quoted, 10=Double Quoted
		# inA1Type: 0= not A1,   no sheet link( 31 =cord, 32=range, 33 = column , 34=row)
		#                           sheet link( 35 =cord, 36=range, 37 = column, 38=row)
		# In this function, we chose not to make the difference between a worksheet and a datasheet
		# absolute or relative is not reported - to be determined later

		if len(inToken) > 87: return 0 # current max of 87 characters for A1 notation
		modeA1 = 0 # 0 = get front str, 1=0 get front num ,2=get second str, 3=get second num, 4= get sheet string, 5 = get column, 6 = get row
		llen = 0
		count=0
		link = 0 # 0 = no link, 1 = link
		colonIdx = -1
		sheetSepIdx = -1
		
		for i, c in enumerate(inToken):
			# print("i,c:",i,",",c)
			if modeA1==0:  # ---- FIRST A1: A-Za-z ----
				if c=='$':continue
				elif c.isalpha():
					llen+=1
					continue
				elif c.isdigit():
					if llen==0:
						modeA1=6
						llen=1
						count=0
						continue
					modeA1 = 1
					llen=1
					continue
				elif c==':':
					if llen==0:return 0
					modeA1=5
					llen=0
					colonIdx=i
					continue
				elif c=='!':
					if llen==0:return 0
					modeA1=0
					llen=0
					colonIdx=i
					continue
				elif c=='_' or c==' ':
					modeA1=4
					continue
				else: return 0
			elif modeA1==1: # ---- FIRST A1: 0-9 ----
				if c=='$':continue
				elif c.isdigit():
					llen+=1
					continue
				elif c=='!':
					if llen==0:return 0
					sheetSepIdx=i
					modeA1=0
					llen=0
					link=1
					continue
				elif c==':':
					if llen==0:return 0
					colonIdx=i
					modeA1 = 2
					llen=0
					continue
				elif c=='_' or c==' ':
					modeA1=4
					continue
				else:
					modeA1=4
					continue
			elif modeA1==2: # ---- SECOND A1: A-Za-z ----
				if c=='$':continue
				elif c.isalpha():
					llen+=1
					continue
				elif c.isdigit():
					if llen==0:return 0
					modeA1 = 3
					llen=1
					continue
				else:return 0
			elif modeA1==3: # ---- SECOND A1: 0-9 ----
				if c=='$':continue
				elif c.isdigit():
					llen+=1
					continue
				else: return 0
			elif modeA1==4: # ---- LINK SCANNING ----
				if c.isalnum():continue
				elif c=='_' or c==' ':
					continue
				elif c=='!':
					modeA1=0
					llen=0
					sheetSepIdx=i
					link=1
					continue
			elif modeA1==5: # ----  A1 COLUMN: ----  example: B:B
				if c.isalpha():
					llen+=1
					continue
				else:return 0
			elif modeA1==6: # ---- A1 ROW: ----  example: 4:4
				if c==':':
					if count>0:return 0
					colonIdx=i
					count+=1
					continue
				elif c.isdigit():
					if llen==0:return 0
					llen+=1
					continue
				if c.isalpha() or c=='_' or c==' ':
					modeA1=4
					llen+=1
					continue
				else: return 0

		retcode = 0
		if link==0:
			if modeA1==1 and llen>0: retcode = 31
			elif modeA1 == 3 and llen>0: retcode = 32
			elif modeA1 == 5 and llen>0: retcode = 33
			elif modeA1 == 6 and llen>0 and count==1: retcode = 34
		else:
			if modeA1==1 and llen>0: retcode = 35
			elif modeA1 == 3 and llen>0: retcode = 36
			elif modeA1 == 5 and llen>0: retcode = 37
			elif modeA1 == 6 and llen>0 and count==1: retcode = 38

		if retcode != 0:
			startSV = ""
			endSV = ""
			sheetNameSV = ""
			if sheetSepIdx != -1:
				sheetNameSV = inToken[0:sheetSepIdx]
				sheetSepIdx+=1 # skip the '!'
			else: sheetSepIdx = 0
			endIdx = len(inToken)
			if colonIdx == -1:
				startSV = inToken[sheetSepIdx:endIdx]
			else:
				startSV = inToken[sheetSepIdx:colonIdx]
				endSV = inToken[colonIdx+1:endIdx]
			inCoord.Set(startSV, endSV, sheetNameSV)
		return retcode
	
	def log_coord(self,inStr, inCo):
		print(inStr + inCo.sheetName,end="")
		print(", start["+str(inCo.start[0])+","+str(inCo.start[1])+"], ",end="")
		print(", end["+str(inCo.end[0])+","+str(inCo.end[1])+"]")
	
	def logv(self, inStr, inList):
		print(inStr,end="")
		for val in inList: print(str(val) + " ",end="")
		print()
		
	def logv2(self, inStr, inList):
		print(inStr,end="")
		print("{",end="")
		for subl in inList: 
			print("{",end="")
			dl=""
			for val in subl:
				print(dl + str(val),end="")
				dl=","
			print("}",end="")
		print("}")

	def log_card_slots(self):
		print("============ ",end="")
		d = ""
		for card in self.CardSlots:
			if card.val ==' ': print(d + card.token,end="")
			else: print(d + card.val,end="")
			d = "  "
		print()

	def log_bubbles(self, inCurrentI):
		i=0
		while i < len(self.Bubbles):
			if i==inCurrentI: print(str(i)+"[X]      ~~~ ",end="")
			else: print(str(i)+"[ ]      ~~~ ",end="")
			d = ""
			for node in self.Bubbles[i]:
				print(d+ node.val,end="")
				d = "  "
			print()
			i+=1







