# Spreadsheet Sheet - note this is different than Dataframe Sheet
# These are regular spreadsheet cells and can be any data type and connect together through A1 notation

class SSheet:
	
	def __init__(self):

		self.SetArea = [0, 0, 5, 5] # Dimensions (by cell count) of spreadsheet area visible on a dashboard, copy of self.SetArea data
		# A SetArea range covering A1:A3 = [0,0,0,2] - covers row 0 to 0 on x (1 column wide), and from 0 to 2 on y (3 rows long)
		self.Name = "" # tab name of the spreadsheet
		self.Data = []

		# Note API Data input is simplified and has 4 inputs
		# [0] Cell A1 location [1] input string, [2] format codes, [3] format formula
		# API Input Example: ["=SUM(A1:A3)","BCe0edd6","###,#.0"]
		# API input (list of 4) is parsed to ByteStream cell description (list of 5)
		
		# Data: Grid of Spreadsheet Content: vector<vector<vector<string>>>
		# Data will match the ByteStream output (list of 5) to be fully editable
		# Rows[  Columns[  Cell Content: [value (no format), formula, format codes, format formula, value (with format) ] ]]
		# Example Data:[
		# 	[	[10,"SUM(A1:A3)","BCe0edd6","#,###.0",10.0] 	],
		# 	[	[3,"SUM(\"1\",\"2\")",,3]                		]
		# ]

		# In bytestream output the Cell Content is seperated by DC3 characters
		# [0] value (no format)
		# [1] formula
		# [2] format codes
		# [3] format formula
		# [4] value (with format)


	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)

