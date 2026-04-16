import struct
import json
import numpy as np
import pandas as pd
import io
import os

class GraphNode:

	def __init__(self):
		self.Name = "" # global graph node name
		self.Parent = -1 # Index of the parent node
		self.Children = [] # int32vec - children of this node, build from Parent connections
		self.Type = 0 # int32 - 0=Root, 1=Spreadsheet, 2=DF, 3=LiveDF, 4=CrossLink, 5=Operator, 6=Chart
		self.Op = "" # string - operation being performed, for example GroupSum
		self.Args = [] # stringVec - Args for each node in the global graph
		self.Types = [] # int32vec - Type for each of the Args (matches with RecipeManager::ConvertType(...) )
		self.CMap = [] # int32vec - Column map: CMap[current df column index] --> parent df column index

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
		