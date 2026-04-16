from row64tools.FontOptions import FontOptions

class GeoPaneLayout:

	EventCC = False # bool - Coord click event
	EventCD = False # bool - Coord double click event
	EventCS = False # bool - Coord selection event

	EventDF = False # bool - use javascript events for linked dataframes
	EventSrc = None # vector<string> - event source dataframe
	EventCol = None # vector<int> - event source dataframe column indices
	EventAct = None # vector<string> - event action if clicked
	
	def __getitem__(self, key):
		return getattr(self, key) 
	def __setitem__(self, key, value):
		setattr(self, key, value)


