import struct
import json
import numpy as np
import pandas as pd
import io
import os
from row64tools.bytestream import bytestream as bStream
from row64tools.DashPane import DashPane

from row64tools.DataframePaneLayout import DataframePaneLayout
from row64tools.WidgetPaneLayout import WidgetPaneLayout
from row64tools.GeoPaneLayout import GeoPaneLayout
from row64tools.SSheetPaneLayout import SSheetPaneLayout

from row64tools.DashHelper import DashHelper as DH

def LS(inStr, inW):
	ll = int(inW - len(inStr))
	if ll < 0:ll=0
	print(inStr + ' ' * ll, end='')

def LC(inStr): print(inStr, end='')

class DashLayout:
	
	def __init__(self):
		self.Panes = [] # list of DashPane class
		self.BkgdColor = [0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF] # int32vector
		self.BkgdMode = 0 #  int32 - 0 = solid, 1 = simple gradient, 2 = four color gradient
		self.HasBorder = True # has a border around the dashboard
		self.BorderColor = 0xCDCDCD # int32
		self.BorderSize = 1 # float
		self.BrowserFitW = False  # bool
		self.BrowserFitH = False # bool
		self.PaneStretch = True # bool
		self.ShowDTF = True # Show the datetime filter
		self.DTFColumn = "" # string - Column link associated with the datetime filter
		self.AutoUpdate = True  # bool - Flag to auto-update data streaming to the dashboard
		self.LinkMap = [] # string vector 2D - sheet Link Pairs

		# app data not part of the .dash format
		self.PaneID = {} # given a pane name get the id

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
		
	def get_buffer(self):
		# first get the buffers for the Panes
		lStr = bStream()
		pList = []
		for i,pane in enumerate(self.Panes):
			pList.append(self.get_pane_buf(pane))

		lStr.add_stream_vector("Panes",pList)
		lStr.add_int32_vector("BkgdColor", self.BkgdColor)
		lStr.add_int32("BkgdMode", self.BkgdMode)
		lStr.add_bool("HasBorder", self.HasBorder)
		lStr.add_int32("BorderColor", self.BorderColor)
		lStr.add_float("BorderSize", self.BorderSize)
		lStr.add_bool("BrowserFitW", self.BrowserFitW)
		lStr.add_bool("BrowserFitH", self.BrowserFitH)
		lStr.add_bool("PaneStretch", self.PaneStretch)
		lStr.add_bool("ShowDTF", self.ShowDTF)
		lStr.add_string("DTFColumn",self.DTFColumn)
		lStr.add_string_vector2d("LinkMap", self.LinkMap)
		lStr.add_bool("AutoUpdate", self.AutoUpdate)
		return lStr.save_to_buffer()

	def get_widget_pane_buf(self,inWidget):
		wStr = bStream()
		wStr.add_string("SheetName", inWidget.SheetName)
		wStr.add_string("Type", inWidget.Type)
		wStr.add_string("Label", inWidget.Label)
		wStr.add_string("Column", inWidget.Column)		
		wStr.add_float("Padding", inWidget.Padding)
		wStr.add_string_vector2d("Grid",inWidget.Grid)
		return wStr.save_to_buffer()

	def get_dataframe_pane_buf(self,inDFS):
		dStr = bStream()
		dStr.add_float("Zoom", inDFS.Zoom)
		dStr.add_bool("ShowTitle", inDFS.ShowTitle)
		dStr.add_string("Title", inDFS.Title)
		dStr.add_stream("TitleFont", DH.get_font_options_buf(inDFS.TitleFont))
		dStr.add_float("TitleAlignX", inDFS.TitleAlignX)
		dStr.add_bool("ShowRowLabel", inDFS.ShowRowLabel)
		dStr.add_bool("AllowCSVDownload", inDFS.AllowCSVDownload)
		dStr.add_bool("Events", inDFS.Events)
		if inDFS.EventCol != None:
			dStr.add_int32_vector("EventCol", inDFS.EventCol)
		if inDFS.EventAct != None:
			dStr.add_string_vector("EventAct", inDFS.EventAct)
		return dStr.save_to_buffer()

	def get_geo_pane_buf(self,inGeoS):
		gStr = bStream()
		gStr.add_bool("EventCC", inGeoS.EventCC)
		gStr.add_bool("EventCD", inGeoS.EventCD)
		gStr.add_bool("EventCS", inGeoS.EventCS)
		gStr.add_bool("EventDF", inGeoS.EventDF)
		if inGeoS.EventSrc != None:
			gStr.add_string_vector("EventSrc", inGeoS.EventSrc)
		if inGeoS.EventCol != None:
			gStr.add_int32_vector("EventCol", inGeoS.EventCol)
		if inGeoS.EventAct != None:
			gStr.add_string_vector("EventAct", inGeoS.EventAct)
		return gStr.save_to_buffer()
	
	def get_ssheet_pane_buf(self,inSSS):
		sStr = bStream()
		sStr.add_uint8("Fit", inSSS.Fit)
		sStr.add_float("Zoom", inSSS.Zoom)
		sStr.add_bool("ShowLines", inSSS.ShowLines)
		sStr.add_stream("OuterLines", DH.get_line_options_buf(inSSS.OuterLines))
		sStr.add_stream("InnerLines", DH.get_line_options_buf(inSSS.InnerLines))
		return sStr.save_to_buffer()

	def get_pane_buf(self,inPane):
		pStr = bStream()
		pStr.add_string("Name", inPane.Name)
		pStr.add_string("WidthExp", inPane.WidthExp)
		pStr.add_string("HeightExp", inPane.HeightExp)
		pStr.add_string("Split", inPane.Split)
		pStr.add_string("Mode", inPane.Mode)
		pStr.add_string("FloatX", inPane.FloatX)
		pStr.add_string("FloatY", inPane.FloatY)
		pStr.add_string("Type", inPane.Type)
		pStr.add_string("Sheet", inPane.Sheet)
		pStr.add_int32("Color", inPane.Color)
		pStr.add_int32("FontColor", inPane.FontColor)
		pStr.add_int32("OutlineColor", inPane.OutlineColor)
		pStr.add_float("OutlineThickness", inPane.OutlineThickness)
		pStr.add_float("Pad", inPane.Pad)
		pStr.add_string("Html", inPane.Html)
		pStr.add_int32("CrossLinking", inPane.CrossLinking)
		pStr.add_int32("Parent", inPane.Parent)
		pStr.add_string("Text", inPane.Text)
		pStr.add_string("Equation", inPane.Equation)
		pStr.add_string("Text2", inPane.Text2)
		if inPane.Stream is None: 
			ss = bStream()
			pStr.add_stream("Stream", ss.save_to_buffer())
		else:
			if inPane.Type == "DataFrame":
				pStr.add_stream("Stream", self.get_dataframe_pane_buf(inPane.Stream))
			elif inPane.Type == "SpreadSheet":
				pStr.add_stream("Stream", self.get_ssheet_pane_buf(inPane.Stream))
			elif inPane.Type == "Geo2D":
				pStr.add_stream("Stream", self.get_geo_pane_buf(inPane.Stream))
			elif inPane.Type == "Widget":
				pStr.add_stream("Stream", self.get_widget_pane_buf(inPane.Stream))
		
		return pStr.save_to_buffer()

	def load(self, inBuf):
		bStr = bStream()
		bStr.load_from_buffer(inBuf)
		self.BkgdColor = bStr.get_int32_vector("BkgdColor")
		self.BkgdMode = bStr.get_int32("BkgdMode")
		self.HasBorder = bStr.get_bool("HasBorder")
		self.BorderColor = bStr.get_int32("BorderColor")
		self.BorderSize = bStr.get_float("BorderSize")
		self.BrowserFitW = bStr.get_bool("BrowserFitW")
		self.BrowserFitH = bStr.get_bool("BrowserFitH")
		self.PaneStretch = bStr.get_bool("PaneStretch")
		self.ShowDTF = bStr.get_bool("ShowDTF")
		self.DTFColumn = bStr.get_string("DTFColumn")
		if bStr.key_exists("AutoUpdate"):
			self.AutoUpdate = bStr.get_bool("AutoUpdate")
		if bStr.key_exists("LinkMap"):
			self.LinkMap = bStr.get_string_vector2d("LinkMap")
		# next cycle the panes
		self.Panes = []
		paneList = bStr.get_stream_vector("Panes")
		for i,pane in enumerate(paneList):self.load_pane(pane)
		# self.log_panes()

	def log(self):
		print("-------------------- Pane Data -------------------")
		print("Nb of Panes:",len(self.Panes))
		LC("BkgdColor: [")
		dl =""
		for bc in self.BkgdColor:
			LC(dl+"{:06x}".format(bc))
			dl=", "
		LC("]\n")
		print("BkgdMode:",self.BkgdMode)
		print("HasBorder:",self.HasBorder)
		print("BorderColor:","{:06x}".format(self.BorderColor))
		print("BorderSize:",self.BorderSize)
		print("BrowserFitW:",self.BrowserFitW)
		print("BrowserFitH:",self.BrowserFitH)
		print("PaneStretch:",self.PaneStretch)
		print("ShowDTF:",self.ShowDTF)
		print("DTFColumn:",self.DTFColumn)
		print("AutoUpdate:",self.AutoUpdate)
		print("LinkMap:",self.LinkMap)

	def log_panes(self):
		print("-------------------- Pane List -------------------")
		fBl = "\033[1m" # bold
		fDi = "\033[2m" # dim
		fM = "\033[35m" # magenta
		fG = "\033[32m" # green
		fW = "\033[37m" # white
		fC = "\033[0m" # clear
		for i,pn in enumerate(self.Panes):
			LS("["+str(i)+"]",4)
			LC(fDi)
			LS(pn.Name,14)
			LC(fC)
			pStr = "" if pn.Parent == -1 else str(pn.Parent)
			LS(pStr,4)
			LC(fM)
			LS(pn.WidthExp,12)
			LS(pn.HeightExp,12)
			LC(fG)
			LS(pn.Split,3 )
			LC(fDi + fW)
			LS(pn.Text,15)
			LC(fC+"\n")

	def get_pane_index(self,inName):
		# Given a pane name get the index in the Pane List
		# if not found, return -1
		if inName in self.PaneID: return self.PaneID[inName]
		return -1

	def update_paneid(self): # update the PaneID
		for i,li in enumerate(self.Panes):
			self.PaneID[li.Name] = i
	
	def divide_pane(self, inIndex, inFirst, inXY, inExp, inName):
		# divide a pane and give it a new name
		# if inFirst=True it will take top on y division or left on x division
		p = self.Panes[inIndex]
		newName = "Root" + p.Name
		if inXY == "y": # sub im new parent mimicking the pane setup
			self.insert_pane( inIndex, newName, p.Parent, p.WidthExp, p.HeightExp, "y") 
			if inFirst:self.insert_pane( inIndex+1, inName, inIndex, "*", inExp, "")
			else:self.insert_pane( inIndex+2, inName, inIndex, "*", inExp, "")
		else:
			self.insert_pane( inIndex, newName, p.Parent, p.WidthExp, p.HeightExp, "x") 
			if inFirst:self.insert_pane( inIndex+1, inName, inIndex, inExp, "*", "")
			else:self.insert_pane( inIndex+2, inName, inIndex, inExp, "*", "")
		p.WidthExp = "*"
		p.HeightExp = "*"
		p.Parent = inIndex
		
	def insert_pane(self, inIndex, inName, inParentI, inWExp, inHExp, inSplit):
		dp = DashPane()
		dp.Name = inName
		dp.Parent = inParentI
		dp.WidthExp = inWExp
		dp.HeightExp = inHExp
		dp.Split = inSplit
		# parenting will be offset by an insert.
		# step up the parenting index of any parent below the insert index
		for i in range(inIndex, len(self.Panes)):
			if self.Panes[i].Parent > inIndex - 1:
				self.Panes[i].Parent+=1
		self.Panes.insert(inIndex,dp)
		self.update_paneid()

	def set_panes(self,inList): 
		# 2D List sets Pane List, will replace any current Pane List
		# Not detailed only filling [Name, Parent Name, WidthExp, HeightExp, Split]
		self.PaneID = {} # lookup ID from Name
		for i,li in enumerate(inList):
			if len(li) < 5:
				print("set_panes: ERROR, pane row had:",len(li)," items, expected 5")
				return
			self.PaneID[li[0]] = i
		self.Panes = []
		for i,li in enumerate(inList):
			dp = DashPane()
			dp.Name = li[0]
			if li[1] in self.PaneID: dp.Parent = self.PaneID[li[1]]
			dp.WidthExp = li[2]
			dp.HeightExp = li[3]
			dp.Split = li[4]
			self.Panes.append(dp)
	
	def get_widget_pane(inBuf):
		wStr = bStream()
		wStr.load_from_buffer(inBuf)
		wd = WidgetPaneLayout()
		if not wStr.key_exists("SheetName"): return None
		wd.SheetName = wStr.get_string("SheetName")
		wd.Type = wStr.get_string("Type")		
		wd.Label = wStr.get_string("Label")	
		wd.Column = wStr.get_string("Column")	
		wd.Padding = wStr.get_float("Padding")	
		wd.Grid = wStr.get_string_vector2d("Grid")	
		return wd

	def get_dataframe_pane(inBuf):
		dStr = bStream()
		dStr.load_from_buffer(inBuf)
		dpl = DataframePaneLayout()
		if not dStr.key_exists("ShowTitle"): return None
		dpl.Zoom = dStr.get_float("Zoom")
		dpl.ShowTitle = dStr.get_bool("ShowTitle")
		dpl.Title = dStr.get_string("Title")
		dpl.TitleFont = DH.get_font_options(dStr.get_stream("TitleFont"))
		dpl.TitleAlignX = dStr.get_float("TitleAlignX")
		if dStr.key_exists("ShowRowLabel"):
			dpl.ShowRowLabel = dStr.get_bool("ShowRowLabel")
		if dStr.key_exists("AllowCSVDownload"):
			dpl.AllowCSVDownload = dStr.get_bool("AllowCSVDownload")
		if dStr.key_exists("Events"):
			dpl.Events = dStr.get_bool("Events")
		if dStr.key_exists("EventCol"):
			dpl.EventCol = dStr.get_int32_vector("EventCol")
		if dStr.key_exists("EventAct"):
			dpl.EventAct = dStr.get_string_vector("EventAct")
		return dpl
	
	def get_ssheet_pane(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		spl = SSheetPaneLayout()
		if not sStr.key_exists("Fit"): return None
		spl.Fit = sStr.get_uint8("Fit")
		spl.Zoom = sStr.get_float("Zoom")
		spl.ShowLines = sStr.get_bool("ShowLines")
		dpl.OuterLines = DH.get_line_options(dStr.get_stream("OuterLines"))
		dpl.InnerLines = DH.get_line_options(dStr.get_stream("InnerLines"))
		return spl

	def get_geo_pane(inBuf):
		gStr = bStream()
		gStr.load_from_buffer(inBuf)
		gpl = GeoPaneLayout()
		if not gStr.key_exists("EventCC"): return None
		gpl.EventCC = gStr.get_bool("EventCC")
		gpl.EventCD = gStr.get_bool("EventCD")
		gpl.EventCS = gStr.get_bool("EventCS")
		gpl.EventDF = gStr.get_bool("EventDF")
		if gStr.key_exists("EventSrc"):
			gpl.EventCol = gStr.get_int32_vector("EventSrc")
		if gStr.key_exists("EventCol"):
			gpl.EventCol = gStr.get_int32_vector("EventCol")
		if gStr.key_exists("EventAct"):
			gpl.EventAct = gStr.get_string_vector("EventAct")
		return gpl

	def load_pane(self, inBuf):
		pStr = bStream()
		pStr.load_from_buffer(inBuf)
		dp = DashPane()
		dp.Name = pStr.get_string("Name")
		dp.WidthExp = pStr.get_string("WidthExp")
		dp.HeightExp = pStr.get_string("HeightExp")
		dp.Split = pStr.get_string("Split")
		dp.Mode = pStr.get_string("Mode")
		dp.FloatX = pStr.get_string("FloatX")
		dp.FloatY = pStr.get_string("FloatY")
		dp.Type = pStr.get_string("Type")
		dp.Sheet = pStr.get_string("Sheet")
		dp.Color = pStr.get_int32("Color")
		dp.FontColor = pStr.get_int32("FontColor")
		dp.OutlineColor = pStr.get_int32("OutlineColor")
		dp.OutlineThickness = pStr.get_float("OutlineThickness")
		if pStr.key_exists("Pad"): dp.Pad = pStr.get_float("Pad")
		dp.Html = pStr.get_string("Html")
		if pStr.key_exists("Stream"):
			if dp.Type == "DataFrame":
				dp.Stream = DashLayout.get_dataframe_pane(pStr.get_stream("Stream"))
			elif dp.Type == "Spreadsheet":
				dp.Stream = DashLayout.get_ssheet_pane(pStr.get_stream("Stream"))
			elif dp.Type == "Geo2D":
				dp.Stream = DashLayout.get_geo_pane(pStr.get_stream("Stream"))
			elif dp.Type == "Widget":
				dp.Stream = DashLayout.get_widget_pane(pStr.get_stream("Stream"))
		dp.Parent = pStr.get_int32("Parent")
		dp.Text = pStr.get_string("Text")
		dp.Equation = pStr.get_string("Equation")
		dp.Text2 = pStr.get_string("Text2")
		if pStr.key_exists("CrossLinking"):
			dp.CrossLinking = pStr.get_int32("CrossLinking")
		# print(pStr.GetTypedJson()) # uncomment to log the pane in JSON
		self.Panes.append(dp)


