class WidgetPaneLayout:
	
	SheetName = "" # String - Dashboard sheet name
	Type = "" # String - Widget Type, use is_type_valid() to check if valid
	Label = "" # String -  Widget Label
	Column = "" # String - Linked column in A1 notation
	Padding = 0.23 # Float -  Display padding
	Grid = [] # vector<vector<string>> - Grid of expandable items
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
	
	def is_type_valid(self,inType):
		WidgetTypes = {
			"Date Range":None,
			"Date & Time Range":None,
			"Date Presets":None,
			"Slider":None,
			"Slider - Integer":None,
			"Range Slider":None,
			"Range Slider - Date":None,
			"Combo - Auto Filter":None,
			"Combo - Set Filters":None,
			"Combo - Value Ranges":None,
			"Combo - Column Switcher":None,
			"Checkbox Combo - Auto Filter":None,
			"Image Button":None,
			"Text - Search Box":None
		}
		if inType in WidgetTypes:return True
		return False

