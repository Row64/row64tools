from row64tools.AxisOptions import AxisOptions
from row64tools.GridOptions import GridOptions
from row64tools.FontOptions import FontOptions
from row64tools.LineOptions import LineOptions

class TrellisFormat:
	
	GridType = 0 # int - 0 = 1D Dimensions, 1 = 2D Dimensions
	GridLookup = "" # string - link to reference for grid index label lookup
	NbRows = -1 # int, -1 = auto-fit
	NbCols = -1 # int, -1 = auto-fit
	FitW = True # bool
	FitH = True # bool
	BoxW = 200 #  float - width of grid box (content space)
	BoxH = 200 #  float - height of grid box (content space)
	Pad = 0 # float - per chart padding
	Mode = 0 # int - Display mode 0 = Trellis, 1 = Panel
	ShowOutline = True # Show grid boundary outline
	Outline = LineOptions() # Grid boundary outline options
	
	RLabelFont = FontOptions() # grid row label font
	RLabelRotate = False # grid row label rotate sideways
	RLabelShift = 5 # float - 0 = base, < 0 = shift out, > 0 = shift in
	CLabelFont = FontOptions() # grid col label font
	CLabelShift = 5 # float - 0 = base, < 0 = shift out, > 0 = shift in

	Type = "" # string - chart type (same types used as ChartBase::Type)
	Line = None # LinePlotFormat()
	Bar = None # BarChartFormat()
	Pie = None # PieChartFormat()
	Scatter = None # ScatterPlotFormat()
	Bubble = None # BubblePlotFormat()

	def __init__(self):
		self.Outline = LineOptions()
		self.RLabelFont = FontOptions()
		self.CLabelFont = FontOptions()

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)