from row64tools.ChartLegend import ChartLegend
from row64tools.ChartLayout import ChartLayout
from row64tools.ChartAnimation import ChartAnimation
from row64tools.FontOptions import FontOptions

class ChartDetails:

	Type = "" # string - Pie, VerticalBar, HorizontalBar, etc.
	Title = "" # string
	ColorTheme = [0x061B42, 0x225EA8, 0x7FCDBB, 0xFFFFD9] # int32vec
	ColorSmooth = 0.1 # float - 0 = pure linear, 1 = pure bezier
	ColorHighlights = [-1,-1] # int32vec
	HighlightSlices = [.1, .25] # FloatVec
	Gaps = [] # floatvec - For storing any gap sizes (i.e., bar chart stores 2 gap sizes)
	GroupType = 0 # int32 - 0 = Series Not Grouped, 1 = Series are Grouped
	Legend = ChartLegend() # ChartLegend class
	ShowTitle = True
	TitleFont = FontOptions # FontOptions class
	TitlePos = [0.5, 0.05] # floatvec - Title Pos in perc
	Layout = ChartLayout() # ChartLayout class
	Animation = ChartAnimation() # ChartAnimation class
	# [DEPRECATED] Variables for compatibility with past versions
	AxisBound = [] # doublevec
	AxisBoundFlag = [] # int32vec

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)