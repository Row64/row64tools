class DashPane:

	def __init__(self):
		self.Name = "" # string - name/id of the pane
		self.WidthExp = "" # string - width expression, options: number in pixels, * for all, 50% for half of avaiable width
		self.HeightExp = "" # string - height expression, options: number in pixels, * for all, 50% for half of avaiable height
		self.Split = "" # "x" for split in x, "y" for split in y
		self.Mode = "" # string of meta-data about window characteristics
		self.Type = "" # type of dashboard pane, ex: Pie, Bar, DataList, DataItem
		self.Sheet = "" # name of the sheet/tab in Row64
		self.Color = -1 # int32 - Color of the pane 
		self.FontColor = -1 # int32 - Color of font
		self.OutlineColor = 0xCDCDCD # int32 - Color of outline 
		self.Pad = 0 # float - padding
		self.OutlineThickness = 1 # int32 - outline thickness
		self.Stream = None # variant PaneLayout Classes: WidgetPaneLayout, DataframePaneLayout
		self.CrossLinking = True # int32 - 0 disables cross filtering for this pane
		self.Parent = -1 # Index of the parent node
		self.Text = "" # string - Top Text     [dc3]     Format (dc3 = ASCII decimal 19)
		self.Equation = "" # string - Formula     [dc3]     Format    [dc3]    Number Format
		self.Text2 = "" # string  - Bottom Text   [dc3]     Format
		
		######################## Unused Bystream Parameters #########################
		self.Html = "" # bookmarked for future html features, Row64 JS API already offers some of this functionality
		self.FloatX = "" # CURRENTLY UNUSED, floating pane x.  Instead, floating panes are done through widget/JS API
		self.FloatY  = "" # CURRENTLY UNUSED, floating pane y, Instead, floating panes are done through widget/JS API

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)