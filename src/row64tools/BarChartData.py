class BarChartData:
	
	Name = "" # Name of the series
	Values = "" # Cell reference of the values in the series (list or cell reference like Excel)
	Labels = ""  # Lables on the series (list or cell reference like Excel)
	ColorMode = 1 # int32 - 0=solid, 1=simple gradient, 2=four-color gradient, 3=series multi
	Colors = [0x547B9F,0x547B9F,0x547B9F,0x547B9F] # int32vec - Color theme for the series ( for ColorMode 2 & 3)
	Alphas = [1.0, 1.0, 1.0, 1.0] # floatvec - Alphas for the series ( currently we are only using Alphas[0], but can expand this in the future )
	
	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)