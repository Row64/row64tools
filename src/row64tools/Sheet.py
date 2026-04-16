from row64tools.ChartDetails import ChartDetails
from row64tools.TableFormat import TableFormat
from decimal import Decimal, ROUND_HALF_UP

# Dataframe Sheet - note this is different than a spreadsheet
# Dataframes are tables of data where each column has a type

class Sheet:

	def __init__(self):
		#--------------------------- Chart Specific Sheet Parameters ---------------------------
		self.Key = "" # name of this sheet in the Charts stream
		self.Type = "" # string - sheet name
		self.Category = "" # string of Chart Category
		self.Details = ChartDetails() # ChartDetails class
		self.CData = [] # binding point for List of SeriesData classes, ex: multiple lines in a line chart
		self.FData = None # binding point for variant FormatData class (aka FData), ex: color of pie slices in a pie chart
		
		#------------------------- Spreadsheet & Dataframe shared parameters
		self.FontSize = 12 # float
		self.ColumnWidths = [150,150,150,150] # double vec - array of column widths, default is 150

		#------------------------- Spreadsheet Specific Sheet Parameters -------------------------
		self.RowHeights = [20,20,20,20] # double vec - array of row Heights, default is 20
		self.SetArea = None # ex: [0, 0, 5, 5] - Dimensions (by cell count) of spreadsheet area visible on a dashboard
		# A SetArea range covering A1:A3 = [0,0,0,2] - covers row 0 to 0 on x (1 column wide), and from 0 to 2 (3 rows long)
		
		#------------------------- Dataframe Specific Sheet Parameters -------------------------
		self.RowHeight = 20 # double - height of rows
		self.ColFormat = [] # list of ColumnFormat(), stream_vector
		self.TableFormat = TableFormat()

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
	
	def log_df(self): # log dataframe data
		dl=""
		for cw in self.ColumnWidths:
			rw = Decimal(cw).quantize(Decimal("1e-2"), rounding=ROUND_HALF_UP)
			print(dl+str(rw),end='')
			dl=", "
		print("]")
		# todo, log ColFormat & TableFormat

