from row64tools.FontOptions import FontOptions

class DataframePaneLayout:

	Zoom = 1; # float - Zoom magnification scale
	ShowTitle = True # bool - Show Dataframe Title
	Title = ""  # string - Displayed title text (if blank, then defaults to sheet name)
	TitleFont = FontOptions()  # Title font options
	TitleAlignX = 0; # float -  Horizontal alignment
	ShowRowLabel = True # bool
	AllowCSVDownload = False # bool
	Events = False; # bool - use javascript events
	EventCol = None  # vector<int> - event column indices
	EventAct = None  # vector<string> - event action if clicked
	
	def __getitem__(self, key):
		return getattr(self, key) 
	def __setitem__(self, key, value):
		setattr(self, key, value)


