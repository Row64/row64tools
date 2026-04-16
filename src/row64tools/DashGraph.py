import struct
import json
import numpy as np
import pandas as pd
import io
import os
from row64tools.bytestream import bytestream as bStream
from row64tools.GraphNode import GraphNode

def LL(inList, inW): # Log List
	lStr = "["
	dl = ""
	for li in inList:
		lStr += dl + str(li)
		dl = ", "
	lStr += "]"
	ll = int(inW - len(lStr))
	if ll < 0:ll=0
	print(lStr + ' ' * ll, end='')

def LS(inStr, inW):
	ll = int(inW - len(inStr))
	if ll < 0:ll=0
	print(inStr + ' ' * ll, end='')

def LC(inStr): print(inStr, end='')

class DashGraph:

	def __init__(self):
		rn = GraphNode()
		rn.Name = "Root"
		self.Nodes = [rn] # by default has a Root node

	def load(self, inBuf):
		self.Nodes = []
		bStr = bStream()
		bStr.load_from_buffer(inBuf)
		paneList = bStr.get_stream_vector("Nodes")
		for i,pane in enumerate(paneList):self.load_node(pane)
		# self.log()

	def load_node(self, inBuf):
		# print(" inPane Buf: ", inBuf)
		nStr = bStream()
		nStr.load_from_buffer(inBuf)
		gn = GraphNode()
		gn.Name = nStr.get_string("Name")
		gn.Parent = nStr.get_int32("Parent")
		gn.Children = nStr.get_int32_vector("Children")
		gn.Type = nStr.get_int32("Type")
		gn.Op = nStr.get_string("Op")
		gn.Args = nStr.get_string_vector("Args")
		gn.Types = nStr.get_int32_vector("Types")
		gn.CMap = nStr.get_int32_vector("CMap")
		self.Nodes.append(gn)

	def get_buffer(self):
		gStr = bStream()
		nodeStrList = []
		for node in self.Nodes:
			nodeStrList.append(self.get_node_buf(node))
		gStr.add_stream_vector("Nodes",nodeStrList)
		return gStr.save_to_buffer()

	def get_node_buf(self,inNode):
		nStr = bStream()
		nStr.add_string("Name", inNode.Name)
		nStr.add_int32("Parent",inNode.Parent)
		nStr.add_int32_vector("Children",inNode.Children)
		nStr.add_int32("Type",inNode.Type)
		nStr.add_string("Op", inNode.Op)
		nStr.add_string_vector("Args", inNode.Args)
		nStr.add_int32_vector("Types", inNode.Types)	
		nStr.add_int32_vector("CMap", inNode.CMap)
		# bs=bStream()bs.load_from_buffer(nStr.save_to_buffer())
		# print(bs.GetTypedJson())
		return nStr.save_to_buffer()
	
	def update_children(self): # Build Global Graph Children base on parenting
		for i in range(len(self.Nodes)):
			self.Nodes[i].Children = []
		for i in range(len(self.Nodes)):
			parentI = self.Nodes[i].Parent
			if parentI < 0:continue
			self.Nodes[parentI].Children.append(i)

	def log(self):
		print("-------------------- Global Graph Nodes -------------------")
		fBl = "\033[1m" # bold
		fDi = "\033[2m" # dim
		fY = "\033[33m" # yellow
		fB = "\033[34m" # blue
		fM = "\033[35m" # magenta
		fG = "\033[32m" # green
		fA = "\033[36m" # cyan
		fW = "\033[37m" # white
		fC = "\033[0m" # clear

		nList = ["", "Name","Parent","Children", "Type","Op", "Args","Types" ,"CMap"]
		wi =    [5,  12,     8,      12,         6,     11,   42,    20,      12    ]
		for i,ni in enumerate(nList):LS(ni,wi[i])
		LC("\n")
		
		for i,nd in enumerate(self.Nodes):
			LS("["+str(i)+"]",wi[0])
			LC(fDi)
			LS(nd.Name,wi[1])
			LC(fC)
			pStr = "" if nd.Parent == -1 else str(nd.Parent)
			LS(pStr,wi[2])
			
			LC(fW) # Children
			LL(nd.Children,wi[3])
			
			LC(fG) # Type
			LS(str(nd.Type),wi[4])

			LC(fBl)
			LC(fA) # Op
			LS(nd.Op,wi[5])
			LC(fC)

			LC(fB) # Args
			LL(nd.Args, wi[6])

			LC(fG) # Types
			LL(nd.Types, wi[7])

			LC(fW) # CMap
			LL(nd.CMap, wi[8])

			LC(fC+"\n")
