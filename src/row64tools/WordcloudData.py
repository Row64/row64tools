class WordcloudData:
	
	Words = "" # string - words
	Freqs = "" # string - frequencies
	Sents = "" # string - sentiment values ( from -1 to 1 )

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)