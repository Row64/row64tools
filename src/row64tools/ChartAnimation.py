class ChartAnimation:
	
	Style = "" # string
	HasTimeSeries = False
	TimeValues = "" # string
	Frames = 300 # uint64 - length of animation
	FPS = 30 # uint64
	CurrentFrame = 0 # uint64
	Mode = 0 # int32 - 0 = Frames, 1 = Duration, 2 = Time Values
	Smooth = False # Smooth between keyframes or step

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)