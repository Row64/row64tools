import copy
import io
import json
import numpy as np
import os
import pandas as pd
import row64tools.ramdb
import shutil
import row64tools.SSheetHelper as SSheetHelper
import struct
import zlib
import pathlib
from pathlib import Path
from row64tools.BarChartData import BarChartData
from row64tools.BarFormat import BarFormat
from row64tools.BubblePlotData import BubblePlotData
from row64tools.BubblePlotFormat import BubblePlotFormat
from row64tools.bytestream import bytestream as bStream
from row64tools.ChartDetails import ChartDetails
from row64tools.ColumnFormat import ColumnFormat
from row64tools.CoordAttributes import CoordAttributes
from row64tools.CoordLayerData import CoordLayerData
from row64tools.DAG import DAG
from row64tools.DashGraph import DashGraph
from row64tools.DashLayout import DashLayout
from row64tools.DashSheets import DashSheets
from row64tools.DataframePaneLayout import DataframePaneLayout
from row64tools.DfInfo import DfInfo
from row64tools.FunctionArgTypes import FunctionArgTypes
from row64tools.GeoData import GeoData
from row64tools.GeoFile import GeoFile
from row64tools.GeoPaneLayout import GeoPaneLayout
from row64tools.GraphNode import GraphNode
from row64tools.GridAxisTypes import GridAxisTypes
from row64tools.ImageData import ImageData
from row64tools.LineOptions import LineOptions
from row64tools.LinePlotData import LinePlotData
from row64tools.LinePlotFormat import LinePlotFormat
from row64tools.MarkerExamples import MarkerExamples
from row64tools.PieChartData import PieChartData
from row64tools.PieFormat import PieFormat
from row64tools.ScatterPlotData import ScatterPlotData
from row64tools.ScatterPlotFormat import ScatterPlotFormat
from row64tools.ShapeLayerData import ShapeLayerData
from row64tools.Sheet import Sheet
from row64tools.SSheetPaneLayout import SSheetPaneLayout
from row64tools.TrellisData import TrellisData
from row64tools.TrellisFormat import TrellisFormat
from row64tools.VennData import VennData
from row64tools.VennFormat import VennFormat
from row64tools.WidgetPaneLayout import WidgetPaneLayout
from row64tools.WordcloudData import WordcloudData
from row64tools.WordcloudFormat import WordcloudFormat

class dash64:
	
	def __init__(self, inPath):
		
		# .dash bytestream structures - mirrored in Python classes
		self.Links = [] # List of dataframes that need to be sent to the client for chart draw, does not include widget or dataframe draw
		self.LinkCols = [] # (optional) Int32Vector2D: This is parallel to Links and contains the corresponding columns needed. If this field is not present, or the vector is blank, then assumes all the columns are needed.
		self.Layout = DashLayout() # layout of the panes and desc of the charts / widgets within them
		self.Graph = DashGraph() # global graph of data connections
		self.Sheets = DashSheets() # This is the ByteStream containing each metadata for each sheet (which show as tabs in Studio)
		self.DAG = DAG() # This is the ByteStream containing DAG nodes and a set of parallel vectors containing non-formula cells data
		
		#### Secondary bytestream support files outside .dash - ex: markers.img
		head, tail = os.path.split(inPath)
		self.Path = os.path.join(head, tail.lower()) # Save Path - knowing the target path before save allows support folder construction
		self.Dir = os.path.basename(os.path.dirname(self.Path))
		self.FName = pathlib.Path(inPath).stem
		self.loadPath = "" 
		self.ImgData = [] # list of image data, 1 for each geo sheet that contains sprites
		self.Ramdb = {} # dictionary of Dataframe names and get_ramdb_info output 

	def get_folder(self):
		return os.path.dirname(os.path.realpath(__file__))

	def save(self):
		bs = bStream()
		saveBuf = bytearray()
		bs.add_stream("Data", self.Layout.get_buffer() ) # Panes
		bs.add_stream("Graph", self.Graph.get_buffer() )
		bs.add_string_vector("Links", self.Links)
		bs.add_int32_vector2d("LinkCols", self.LinkCols)
		dagBuffer = None
		if len(self.DAG.SSheets) > 0: dagBuffer = self.DAG.get_buffer(self.Sheets) 
		bs.add_stream("Sheets", self.Sheets.get_buffer(self.DAG) ) # process Sheets after DAG to get DFLists
		if len(self.DAG.SSheets) > 0: bs.add_stream("DAG", dagBuffer )
		bs.save(self.Path)
		print("Saved Dashboard:")
		print(self.Path)
		print("http://localhost/dash/"+self.Dir+"/"+self.FName)
		
	def new(self):
		self.Links = []
		self.Layout = DashLayout()
		self.Graph = DashGraph()
		self.Sheets = DashSheets()
		self.DAG = DAG()

	def load(self, inPath):
		self.loadPath = inPath
		bs = bStream()
		bs.read( inPath )
		# bs.LogInfo()
		if bs.key_exists("Links"):
			self.Links = bs.get_string_vector("Links")
		if bs.key_exists("LinkCols"):
			self.LinkCols = bs.get_int32_vector2d("LinkCols")
		self.Layout = DashLayout()
		if bs.key_exists("Data"):
			self.Layout.load( bs.get_stream("Data") ) # Data key is dashboard layout description
		self.Graph = DashGraph()
		if bs.key_exists("Graph"):
			self.Graph.load( bs.get_stream("Graph") ) # Global graph of dataframe & data nodes
		self.Sheets = DashSheets()
		if bs.key_exists("Sheets"): # V3.3+ key name (charts, geo, dataframes & spreadsheet sheet descriptions)
			self.Sheets.load( bs.get_stream("Sheets") )
		elif bs.key_exists("Charts"): # V3.2 & earlier key name
			self.Sheets.load( bs.get_stream("Charts") )
		if bs.key_exists("DAG"):
			self.DAG.load( bs.get_stream("DAG"), self.Sheets)
		self.load_img_data()
		
	def load_img_data(self):
		# Find image data by crawling the dash assets folder and seeing if it has markers.img files
		dashName = Path(self.loadPath).stem
		parentDir = os.path.dirname(self.loadPath)
		daFolder = os.path.join(parentDir,dashName)
		if not os.path.exists(daFolder): return
		assetFolder = os.path.join(daFolder,"assets")
		if not os.path.exists(assetFolder):return
		for afld in os.scandir(assetFolder):
			if os.path.isdir(afld):
				mImg = os.path.join(afld.path,"markers.img")
				if os.path.exists(mImg): # confirmed to have marker image data - add a new image entry
					sheetName = afld.name
					sheetFolder = afld.path
					im = ImageData(self.Path, sheetName, sheetFolder)
					im.load()
					self.ImgData.append(im)
		
	def log(self):
		
		bs = bStream()
		saveBuf = bytearray()

		layoutBuf = self.Layout.get_buffer()
		graphBuf = self.Graph.get_buffer()
		sheetBuf = self.Sheets.get_buffer(self.DAG)

		bs.add_stream("Data", layoutBuf)
		bs.add_stream("Graph", graphBuf)
		bs.add_string_vector("Links", self.Links)
		bs.add_stream("Charts", sheetBuf)
		
		print("---------------------------- DashRoot ----------------------------")
		logBuf = bs.save_to_buffer()
		logBs = bStream()
		logBs.load_from_buffer(logBuf)
		logBs.log_details()
		
		print("---------------------------- DashLayout ----------------------------")
		logBs = bStream()
		logBs.load_from_buffer(layoutBuf)
		logBs.log_details()

		print("---------------------------- DashGraph ----------------------------")
		logBs = bStream()
		logBs.load_from_buffer(graphBuf)
		logBs.log_details()

		print("---------------------------- DashSheets ----------------------------")
		logBs = bStream()
		logBs.load_from_buffer(sheetBuf)
		logBs.log_details()


	##############################################################################
	################################ SPREADSHEET #################################
	##############################################################################

	def add_spreadsheet(self, inName, inDim, inDef, inPaneName):
		if not self.Sheets.is_sheet_name_unique(inName):
			print("add_spreadsheet: INVALID inName, not unique")
			return False
		if inPaneName != "":
			if inPaneName not in self.Layout.PaneID: 
				print("add_spreadsheet, invalid inPaneName:",inPaneName,"not found")
				return
		sSheet = Sheet() # generic sheet object
		sSheet.Type = "Spreadsheet"
		sSheet.SetArea = inDim
		sSheet.Key = inName
		sSheet.ColumnWidths = [150] * (inDim[2]+1)
		sSheet.RowHeights = [20] * (inDim[3]+1)
		self.Sheets.Items.append(sSheet)
		self.Sheets.Names.append(inName)
		paneI = self.Layout.PaneID[inPaneName]
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "SpreadSheet"
		self.DAG.add_sheet(inName, inDim, inDef)
		self.DAG.Sheets = self.Sheets
		
	def set_cell(self, inA1, inCellDef):
		self.DAG.set_cell(inA1, inCellDef)

	##############################################################################
	################################### CHARTS ###################################
	##############################################################################

	def add_hbar(self, inName, inPaneName, inDef, inOpt): # Horizontal Bar 
		inOpt.append(["Format","HorizontalBar",True])
		self.add_bar(inName, inPaneName, inDef, inOpt)
	
	def add_bar(self, inName, inPaneName, inDef, inOpt):
		if inPaneName not in self.Layout.PaneID: print("add_bar, invalid inPaneName:",inPaneName,"not found");return
		if type(inDef) is not list or len(inDef) == 0:print("add_bar: INVALID inDef");return
		for drow in inDef:
			if type(drow) is not list or len(drow) != 3:print("add_bar: INVALID inDef");return
		if not self.Sheets.is_sheet_name_unique(inName):print("add_bar: INVALID inName, not unique");return
		bcSheet = Sheet()
		bcSheet.Key = inName
		bcSheet.Type = "Bar"
		bcSheet.Category = "Chart"
		bcSheet.Details = ChartDetails()
		bcSheet.Details.Type = "Bar"
		bcSheet.FData = BarFormat()
		for drow in inDef:
			bcd = BarChartData()
			for pa, i in zip(["Name","Labels","Values"],[0,1,2]):bcd[pa] = drow[i]
			for i in [1,2]: self.add_links_from_formula(drow[i])
			bcSheet.CData.append(bcd)
		paneI = self.Layout.PaneID[inPaneName]
		self.process_options(inOpt, bcSheet.FData, bcSheet.Details, bcSheet.CData, paneI)
		self.Sheets.Items.append(bcSheet)
		self.Sheets.Names.append(inName)
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "Bar"
	
	def add_line(self, inName, inPaneName, inDef, inOpt):
		if inPaneName not in self.Layout.PaneID:print("add_line, invalid inPaneName:",inPaneName,"not found");return
		if type(inDef) is not list or len(inDef) == 0:print("add_line: INVALID inDef");return
		for drow in inDef:
			if type(drow) is not list or len(drow) != 3:print("add_line: INVALID inDef");return
		if not self.Sheets.is_sheet_name_unique(inName):print("add_line: INVALID inName, not unique");return
		bcSheet = Sheet()
		bcSheet.Key = inName
		bcSheet.Type = "LinePlot"
		bcSheet.Category = "Canvas"
		bcSheet.Details = ChartDetails()
		bcSheet.Details.Type = "LinePlot"
		bcSheet.FData = LinePlotFormat()
		paneI = self.Layout.PaneID[inPaneName]
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "Line"
		for pa in ["RPadding","LPadding","TPadding","BPadding"]:bcSheet.Details.Layout[pa] = 5
		bcSheet.CData = []
		for drow in inDef:
			lpd = LinePlotData()
			for pa, i in zip(["Name","Labels","Values"],[0,1,2]):lpd[pa] = drow[i]
			for i in [1,2]: self.add_links_from_formula(drow[i])
			bcSheet.CData.append(lpd)
		self.process_options(inOpt, bcSheet.FData, bcSheet.Details, bcSheet.CData, paneI)
		self.Sheets.Items.append(bcSheet)
		self.Sheets.Names.append(inName)

	def add_scatter(self, inName, inPaneName, inDef, inOpt):
		if inPaneName not in self.Layout.PaneID: 
			print("add_scatter, invalid inPaneName:",inPaneName,"not found");return
		if type(inDef) is not list or len(inDef) == 0:print("add_scatter: INVALID inDef");return
		for drow in inDef:
			if type(drow) is not list or len(drow) != 4:print("add_scatter: INVALID inDef");return
		if not self.Sheets.is_sheet_name_unique(inName):print("add_scatter: INVALID inName, not unique");return
		bcSheet = Sheet()
		bcSheet.Key = inName
		bcSheet.Type = "ScatterPlot"
		bcSheet.Category = "Canvas"
		bcSheet.Details = ChartDetails()
		bcSheet.Details.Type = "ScatterPlot"
		bcSheet.FData = ScatterPlotFormat()
		paneI = self.Layout.PaneID[inPaneName]
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "Scatter"
		for pa in ["RPadding","LPadding","TPadding","BPadding"]:bcSheet.Details.Layout[pa] = 5
		bcSheet.CData = []
		for drow in inDef:
			spd = ScatterPlotData()
			for pa, i in zip(["Name","Labels","XValues","YValues"],[0,1,2,3]):spd[pa] = drow[i]
			for i in [1,2,3]: self.add_links_from_formula(drow[i])
			bcSheet.CData.append(spd)
		self.process_options(inOpt, bcSheet.FData, bcSheet.Details, bcSheet.CData, paneI)
		self.Sheets.Items.append(bcSheet)
		self.Sheets.Names.append(inName)

	def add_bubble(self, inName, inPaneName, inDef, inOpt):
		if inPaneName not in self.Layout.PaneID: print("add_bubble, invalid inPaneName:",inPaneName,"not found");return
		if type(inDef) is not list or len(inDef) == 0:print("add_bubble: INVALID inDef");return
		for drow in inDef:
			if type(drow) is not list or len(drow) != 5:print("add_bubble: INVALID inDef");return
		if not self.Sheets.is_sheet_name_unique(inName):print("add_bubble: INVALID inName, not unique");return
		bcSheet = Sheet()
		bcSheet.Key = inName
		bcSheet.Type = "BubblePlot"
		bcSheet.Category = "Canvas"
		bcSheet.Details = ChartDetails()
		bcSheet.Details.Type = "BubblePlot"
		bcSheet.FData = BubblePlotFormat()
		paneI = self.Layout.PaneID[inPaneName]
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "Bubble"
		for pa in ["RPadding","LPadding","TPadding","BPadding"]:bcSheet.Details.Layout[pa] = 5
		bcSheet.CData = []
		for drow in inDef:
			bpd = BubblePlotData()
			for pa, i in zip(["Name","Labels","XValues","YValues","ZValues"],[0,1,2,3,4]):bpd[pa] = drow[i]
			for i in [1,2,3,4]: self.add_links_from_formula(drow[i])
			bcSheet.CData.append(bpd)
		self.process_options(inOpt, bcSheet.FData, bcSheet.Details, bcSheet.CData, paneI)
		self.Sheets.Items.append(bcSheet)
		self.Sheets.Names.append(inName)

	def add_venn(self, inName, inPaneName, inDef, inOpt):
		if inPaneName not in self.Layout.PaneID:print("AddVenn, invalid inPaneName:",inPaneName,"not found");return
		if type(inDef) is not list or len(inDef) == 0:print("AddVenn: INVALID inDef");return
		for drow in inDef:
			if type(drow) is not list or len(drow) < 2:print("AddVenn: INVALID inDef");return
		if not self.Sheets.is_sheet_name_unique(inName):print("AddVenn: INVALID inName, not unique");return
		vcSheet = Sheet()
		vcSheet.Key = inName
		vcSheet.Type = "Venn"
		vcSheet.Category = "Canvas"
		vcSheet.Details = ChartDetails()
		vcSheet.Details.Type = "Venn"
		vcSheet.Details.Legend.Show = False
		vcSheet.Details.ColorTheme = [0x0086ff,0x1ef4ba,0x00ffb9,0xff216c]
		vcSheet.FData = VennFormat()
		for pa in ["RPadding","LPadding","TPadding","BPadding"]:vcSheet.Details.Layout[pa] = 5
		vcd = VennData() # venn chart doesn't have a series of CData
		vcd.Values = []
		for dRow in inDef:
			if dRow[0] == "Values":
				for i in range(1, len(dRow)):
					vcd.Values.append(dRow[i])
					self.add_links_from_formula(dRow[i])
			if dRow[0] == "Labels":
				vcd.Labels = "={"
				dl = ""
				for i in range(1, len(dRow)):
					vcd.Labels += dl + "\"" + dRow[i] + "\"";dl = ","
				vcd.Labels += "}"
		self.add_links_from_formula(drow[1])
		self.add_links_from_formula(drow[2])
		vcSheet.CData.append(vcd)
		paneI = self.Layout.PaneID[inPaneName]
		self.process_options(inOpt, vcSheet.FData, vcSheet.Details, vcSheet.CData, paneI)
		self.Sheets.Items.append(vcSheet)
		self.Sheets.Names.append(inName)
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "Venn"

	def add_pie(self, inName, inPaneName, inDef, inOpt):
		if inPaneName not in self.Layout.PaneID:print("AddPie, invalid inPaneName:",inPaneName,"not found");return
		if type(inDef) is not list or len(inDef) == 0:print("AddPie: INVALID inDef");return
		for drow in inDef:
			if type(drow) is not list or len(drow) != 3:print("AddPie: INVALID inDef");return
		if not self.Sheets.is_sheet_name_unique(inName):print("AddPie: INVALID inName, not unique");return
		pcSheet = Sheet()
		pcSheet.Key = inName
		pcSheet.Type = "Pie"
		pcSheet.Category = "Chart"
		pcSheet.Details = ChartDetails()
		pcSheet.Details.Type = "Pie"
		pcSheet.Details.Legend.Show = False
		pcSheet.Details.ColorTheme = [0x9bdcd7,0x3aa07d,0x62df93,0x0076be]
		pcSheet.FData = PieFormat()
		pcd = PieChartData() # pie chart doesn't have a series of CData
		for pa, i in zip(["Name","Labels","Values"],[0,1,2]):pcd[pa] = drow[i]
		for i in [1,2]: self.add_links_from_formula(drow[i])
		pcSheet.CData.append(pcd)
		paneI = self.Layout.PaneID[inPaneName]
		self.process_options(inOpt, pcSheet.FData, pcSheet.Details, pcSheet.CData, paneI)
		self.Sheets.Items.append(pcSheet)
		self.Sheets.Names.append(inName)
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "Pie"

	def add_wordcloud(self, inName, inPaneName, inDef, inOpt):
		if inPaneName not in self.Layout.PaneID: print("add_wordcloud, invalid inPaneName:",inPaneName,"not found");return
		if type(inDef) is not list or len(inDef) == 0:print("add_wordcloud: INVALID inDef");return
		for drow in inDef:
			if type(drow) is not list or len(drow) != 4:print("add_wordcloud: INVALID inDef");return
		if not self.Sheets.is_sheet_name_unique(inName):
			print("add_wordcloud: INVALID inName, not unique")
			return False

		print("starting addwordcloud")
		wcSheet = Sheet()
		wcSheet.Key = inName
		wcSheet.Type = "WordCloud"
		wcSheet.Category = "Canvas"
		wcSheet.Details = ChartDetails()
		wcSheet.Details.Type = "WordCloud"
		wcSheet.Details.Legend.Show = False
		wcSheet.Details.Layout.HasChartFill = True
		wcSheet.Details.Layout.ChartFill.Color = 0x000000
		for pa in ["RPadding","LPadding","TPadding","BPadding"]:wcSheet.Details.Layout[pa] = 0
		wcSheet.FData = WordcloudFormat()
		wcd = WordcloudData() # wordcloud doesn't have a series of CData
		for pa, i in zip(["Words","Freqs","Sents"],[1,2,3]):wcd[pa] = drow[i]
		for i in [0,1,2]: self.add_links_from_formula(drow[i])
		wcSheet.CData.append(wcd)
		paneI = self.Layout.PaneID[inPaneName]
		self.process_options(inOpt, wcSheet.FData, wcSheet.Details, wcSheet.CData, paneI)
		self.Sheets.Items.append(wcSheet)
		self.Sheets.Names.append(inName)
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "WordCloud"

	def add_trellis(self, inType, inName, inPaneName, inDef, inOpt):
		if inType != "Line":print("add_trellis Currently Only Supports LinePlot Trellis (inType=\"Line\")");return
		if inPaneName not in self.Layout.PaneID: 
			print("add_trellis, invalid inPaneName:",inPaneName,"not found")
			return
		if type(inDef) is not list or len(inDef) == 0:print("add_trellis: INVALID inDef");return
		for drow in inDef:
			if type(drow) is not list or len(drow) != 4:print("add_trellis: INVALID inDef");return
		if not self.Sheets.is_sheet_name_unique(inName):
			print("add_trellis: INVALID inName, not unique")
			return False
		wcSheet = Sheet()
		wcSheet.Key = inName
		wcSheet.Type = "Trellis"
		wcSheet.Category = "Canvas"
		wcSheet.Details = ChartDetails()
		wcSheet.Details.Type = "Trellis"
		wcSheet.Details.Legend.Show = False
		for pa in ["RPadding","LPadding","TPadding","BPadding"]:wcSheet.Details.Layout[pa] = 0
		wcSheet.FData = TrellisFormat()
		wcSheet.FData.Type = "LinePlot"
		wcSheet.FData.Line = LinePlotFormat()
		for drow in inDef: # Line Chart Trellis: Name, Labels, Values, Index Value
			td = TrellisData()
			for pa, i in zip(["Name","Labels","YValues","IValues"],[0,1,2,3]):td[pa] = drow[i]
			for i in [1,2,3]: self.add_links_from_formula(drow[i])
			wcSheet.CData.append(td)
		paneI = self.Layout.PaneID[inPaneName]
		self.process_options(inOpt, wcSheet.FData, wcSheet.Details, wcSheet.CData, paneI)
		self.Sheets.Items.append(wcSheet)
		self.Sheets.Names.append(inName)
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "Trellis"

	def process_options(self, inOpt, inFData, inDetails, inCData, inPaneI):
		for opt in inOpt:
			if len(opt) < 3:continue
			if opt[0]=="Format": # FData = Format Data, varies per chart/sheet type
				if len(opt) == 3:
					if opt[1]=="Color":self.Layout.Panes[inPaneI].Color = opt[2];continue # color is set on the pane
					if opt[1]=="CrossLinking":self.Layout.Panes[inPaneI].CrossLinking = opt[2];continue # cross-linking is set on the pane
					if opt[1]=="Pad":self.Layout.Panes[inPaneI].Pad = opt[2];continue # pane level padding
				if len(opt) > 2:
					if hasattr(inFData,opt[1]):
						if len(opt) > 3:
							if hasattr(inFData[opt[1]],opt[2]):
								if len(opt) > 4:
									if hasattr(inFData[opt[1]][opt[2]],opt[3]):
										inFData[opt[1]][opt[2]][opt[3]]=opt[4]
									else:print("Format Attribute 3:",opt[3],"not found in:\n  ",opt)
								else:inFData[opt[1]][opt[2]]=opt[3]
							else:print("Format Attribute 2:",opt[2],"not found in:\n  ",opt)
						else:inFData[opt[1]]=opt[2]
					else:print("Format Attribute 1:",opt[1],"not found in:\n  ",opt)
			if opt[0]=="Details": # Details = ChartDetails()
				if len(opt) > 2:
					if hasattr(inDetails, opt[1]):
						if len(opt) > 3:
							if hasattr(inDetails[opt[1]],opt[2]):
								if len(opt) > 4:
									if hasattr(inDetails[opt[1]][opt[2]],opt[3]):
										inDetails[opt[1]][opt[2]][opt[3]]=opt[4]
									else:print("Details Attribute 3:",opt[3],"not found in:\n  ",opt)
								else:inDetails[opt[1]][opt[2]]=opt[3]
							else:print("Details Attribute 2:",opt[2],"not found in:\n  ",opt)
						else:inDetails[opt[1]]=opt[2]
					else:print("Details Attribute 1:",opt[1],"not found in:\n  ",opt)
			elif opt[0]=="Series": # CData = Series Data, varies per chart/sheet type
				if not isinstance(opt[1],int):continue
				if opt[1] >= len(inCData):continue
				if len(opt) > 3:
					if hasattr(inCData[opt[1]],opt[2]):
						if len(opt) > 4:
							if opt[2]=="Fill": # Fill is a special case (single class stored in a list we skip over)
									if hasattr(inCData[opt[1]][opt[2]][0],opt[3]):
										inCData[opt[1]][opt[2]][0][opt[3]]=opt[4]
									else:print("Series Attribute 3:",opt[3],"not found in:\n  ",opt)
							elif hasattr(inCData[opt[1]][opt[2]],opt[3]):
								if len(opt) > 5:
									if hasattr(inCData[opt[1]][opt[2]][opt[3]],opt[4]):
										inCData[opt[1]][opt[2]][opt[3]][opt[4]] = opt[5]
									else:print("Series Attribute 4:",opt[4],"not found in:\n  ",opt)
								else:
									inCData[opt[1]][opt[2]][opt[3]]=opt[4]
							else:print("Series Attribute 3:",opt[3],"not found in:\n  ",opt)
						else:inCData[opt[1]][opt[2]]=opt[3]
					else:print("Series Attribute 2:",opt[2],"not found in:\n  ",opt)

	##############################################################################
	##################################### GEO ####################################
	##############################################################################
	
	def add_geo(self, inName, inPane, inOpt, inShapeO, inCoordO):
		# inOpt = global options, inShapeO = shape layers & options, inCoordO = coordinate layeres & options
		if inPane not in self.Layout.PaneID: 
			print("add_geo, invalid inPane:",inPane,"not found")
			return
		if not self.Sheets.is_sheet_name_unique(inName):
			print("add_geo: INVALID inName, not unique")
			return False
		if type(inOpt) is not list:
			print("add_geo: INVALID inOpt")
			return False
		if type(inShapeO) is not list:
			print("add_geo: INVALID inShapeO")
			return False
		if type(inCoordO) is not list:
			print("add_geo: INVALID inCoordO")
			return False
		sList = [] #-------------------- process Shape List --------------------
		for slDef in inShapeO: 
			sLayer = ShapeLayerData()
			for so in slDef:
				if so[0] == "File":sLayer.File = so[1]
				elif so[0] == "Visible": sLayer.Visible = so[1]
				elif so[0] == "Locations": sLayer.Locations = so[1] #  string - sheet/dataframe ref to list of GEOIDs
				elif so[0] == "ColorValues": sLayer.ColorValues = so[1] # string - sheet/dataframe ref to parallel list of attribute data corresponding to Locations
				elif so[0] == "TimeValues": sLayer.TimeValues = so[1]  # string - sheet/dataframe ref to parallel list of time data corresponding to Locations
				elif so[0] == "FeatureIDs": sLayer.FeatureIDs = so[1] # vector<string> - List of per-shape attributes from the data file
				elif so[0] == "FeatureIndex": sLayer.FeatureListSelectedIndex = so[1]
				elif so[0] == "Name": sLayer.Name = so[1]
				elif so[0] == "Color": sLayer.ShapeColor = so[1]
				elif so[0] == "Alpha": sLayer.ShapeAlpha = so[1]
				elif so[0] == "LineSize": sLayer.LineSize = so[1]
				
			sList.append(sLayer)
		gSheet = Sheet()
		gSheet.Key = inName
		gSheet.Type = "Geo2D"
		gSheet.Title = "Geo2D"
		gSheet.Category = "Canvas"
		gSheet.Details = ChartDetails()
		gSheet.Details.TitleFont.Size = 28
		gSheet.Details.TitleFont.Bold = True
		paneI = self.Layout.PaneID[inPane]
		self.Layout.Panes[paneI].Sheet = inName
		self.Layout.Panes[paneI].Type = "Geo2D"
		gData = GeoData() # Single CData for Geo, layers are in sub stream vectors (ShapeLayerData, CoordLayerData)
		gData.ShapeLayerData = sList
		for opt in inOpt:
			if len(opt) < 2:continue
			if opt[0] == "ColorTheme":
				gSheet.Details.ColorTheme = opt[1];continue
			if opt[0] == "BkgdFill":
				gSheet.Details.Layout.HasBkgdFill = True
				gSheet.Details.Layout.BkgdFill.Color = opt[1]
				continue
			if hasattr(gData,opt[0]):gData[opt[0]]=opt[1]
			else:print("add_geo option 0:",opt[0],"not found in:\n  ",opt)
		cList = [] #-------------------- process Coord List --------------------
		sprites = [] # marker paths or presets
		for clDef in inCoordO:
			cLayer = CoordLayerData()
			cAtt = CoordAttributes()
			for co in clDef:
				if co[0] == "Name":cLayer.Name = co[1]
				elif co[0] == "Visible":cLayer.Visible = co[1]
				elif co[0] == "Lat":cLayer.Lat = co[1] # formula to link data
				elif co[0] == "Lon":cLayer.Lon = co[1] # formula to link data
				elif co[0] == "LinkRadius":cLayer.Radius = co[1] # formula to link data
				elif co[0] == "LinkColor":cLayer.Color = co[1] # formula to link data
				elif co[0] == "Mode":cAtt.set_mode(co[1])
				elif co[0] == "Radius":cAtt.Radius = co[1]
				elif co[0] == "Alpha":cAtt.Alpha = co[1]
				elif co[0] == "Color":cAtt.SpriteColor = co[1]
				elif co[0] == "RingColor":cAtt.BubbleRingColor = co[1]
				elif co[0] == "RingSize":cAtt.BubbleRingSize = co[1]
				elif co[0] == "ColorPalette":cAtt.BubbleColorPalette = co[1]
				elif co[0] == "SpritePath":
					if co[1] != "":cAtt.SpritePath =self.get_sprite_path(co[1])
			cLayer.Attributes = cAtt
			cList.append(cLayer)
			if cAtt.Mode > 1 and cAtt.SpritePath != "":sprites.append(cAtt.SpritePath)
		gData.CoordLayerData = cList
		self.add_shape_geoz( self.Path, sList, inName)
		for pa in ["RPadding","LPadding","TPadding","BPadding"]:gSheet.Details.Layout[pa] = 0
		gSheet.CData.append(gData)
		self.Sheets.Items.append(gSheet)
		self.Sheets.Names.append(inName)
		if len(sprites)>0:self.process_sprites(sprites, inName)

	def add_shape_geoz(self, inPath, inList, inSheetName): # take .geo files and turn them into zlib messages for the client (called .geoz)
		for i,sl in enumerate(inList):
			if sl.File == "":continue
			gf = GeoFile()
			gf.load(sl.File, inSheetName, i)
			gf.File = sl.File
			dashName = Path(inPath).stem
			dashDir = os.path.dirname(inPath)
			dashFolder = os.path.join(dashDir,dashName)
			# path example: /var/www/dashboards/temp/geo1/Geo2D2_S00.geoz
			Path(dashFolder).mkdir(parents=True, exist_ok=True)
			geozPath = os.path.join(dashFolder, inSheetName + "_S"+f'{i:02}'+".geo")
			gf.save_geoz(geozPath)
			
	def get_sprite_path(self, inStr):
		path = inStr
		if inStr.find('/')==-1 and inStr.find('\\')==-1: # it's a preset, not a path
			if inStr in MarkerExamples:
				path = os.path.join(Path.cwd(), "row64tools","markers", MarkerExamples[inStr])
			else:print("ERROR: could not find marker preset:",inStr)
		elif not os.path.exists(inStr):
			print("ERROR: could not find marker image:",inStr)
		return path

	def process_sprites(self,inSList, inSheetName):
		dashName = Path(self.Path).stem
		dashDir = os.path.dirname(self.Path)
		sheetF = os.path.join(dashDir, dashName, "assets", inSheetName)
		Path(sheetF).mkdir(parents=True, exist_ok=True)
		im = ImageData(self.Path, inSheetName, sheetF)
		for mPath in inSList:im.add_single_marker(mPath)
		im.make_sprite_sheets(sheetF)
		self.ImgData.append(im)
	

	##############################################################################
	#################################### DATA ####################################
	##############################################################################

	def add_datanode(self, inName, inDfName, inDef):
		# Creates a new data node with sheet name inName
		# The data node is transforms the datafraem inDfName
		# inDef is a 2D list of [[Function, Function Args, FunctionArgTypes]]
		# In Studio, if no Columns are specified, it will copy all columns
		# In the Python API, you need to list all the columns in the CROSSLINK to copy them all
		if not self.Sheets.is_sheet_name_unique(inName):
			print("add_datanode: INVALID sheet name, not unique")
			return False
		dfI = -1
		for i,nd in enumerate(self.Graph.Nodes):
			if nd.Name == inDfName: dfI = i
		if type(inDef) is not list or len(inDef) == 0:
			print("add_datanode: INVALID inDef")
			return False
		for drow in inDef:
			if type(drow) is not list or len(drow) != 3:
				print("add_datanode: INVALID inDef")
				return False
			for i,ditem in enumerate(drow):
				if i > 0 and type(ditem) is not list:
					print("add_datanode: INVALID inDef")
					return False
		gnInd = len(self.Graph.Nodes)
		dnInd = gnInd # data node index, the start of the chain
		gn = GraphNode()
		gn.Name = inName
		gn.Parent = dfI
		gn.Type = 4 # data node
		self.Graph.Nodes.append(gn)
		for i,drow in enumerate(inDef):
			gn = GraphNode()
			gn.Name = ">Op"
			gn.Parent = gnInd
			gn.Type = 5 # op
			gn.Op = drow[0]
			gn.Args = [str(x) for x in drow[1]]
			ftList = []
			if len(drow[2]) > 0:
				for tItem in drow[2]:
					if str(tItem).isdigit(): ftList.append( int(tItem) )
					elif tItem in FunctionArgTypes:ftList.append( int(FunctionArgTypes[tItem]) )
					else:
						print("add_datanode: INVALID function arg type:",tItem)
						return False
			gn.Types = ftList
			gnInd = len(self.Graph.Nodes)
			self.Graph.Nodes.append(gn)
		self.Graph.update_children()
		self.update_cmap(dnInd)
		dnSheet = Sheet()
		dnSheet.Key = inName
		self.Sheets.Items.append(dnSheet)
		self.Sheets.Names.append(inName)

	def add_ramdb(self, inPath, inSheetName):
		# loads a .ramdb file as a dataframe sheet, and gives it the name from inSheetName
		# it assumes the .ramdb is stored in /var/www/ramdb on the same server so it can get the db details right
		# it's important to load the .ramdb so we get the number of columns right
		ri = self.get_ramdb_info(inPath)
		if ri["Valid"] == False: 
			print("invalid .ramdb path:",inPath)
			return
		self.Ramdb[inSheetName] = ri
		if not self.Sheets.is_sheet_name_unique(inSheetName):
			print("AddDf: INVALID sheet name, not unique")
			return False
		cSheet = Sheet()
		cSheet.Key = inSheetName
		cSheet.ColumnWidths = [150] * ri["NbCols"] # use 150 as default column width
		cSheet.Type = "DataFrame"
		self.Sheets.Items.append(cSheet)
		self.Sheets.Names.append(inSheetName)
		dfInd = len(self.Graph.Nodes) # setup global graph
		gn1 = GraphNode()
		gn1.Name = inSheetName
		gn1.Parent = 0
		gn1.Type = 3 # dataframe
		self.Graph.Nodes.append(gn1)
		gn2 = GraphNode()
		gn2.Name = ">Op"
		gn2.Parent = dfInd
		gn2.Type = 5 # op
		gn2.Op = "CONNECT"
		gn2.Types = [4,4,4]
		gn2.Args = [ri["Conn"],ri["Db"],ri["Table"]]
		self.Graph.Nodes.append(gn2)
		gn3 = GraphNode()
		gn3.Name = ">Op"
		gn3.Parent = dfInd + 1
		gn3.Type = 5 # op
		gn3.Op = "SQL"
		gn3.Types = [4,4,4,4,4,4]
		gn3.Args = ["SELECT","*","FROM",ri["Table"],";",""]
		self.Graph.Nodes.append(gn3)
		self.Graph.update_children()
	
	def get_ramdb_info(self, inPath):

		rp = DfInfo()
		rp.Valid = False
		parts = inPath.split("/")
		if parts[1] != "var" or parts[2] != "www" or parts[3] != "ramdb":
			print("AddDf: INVALID ramdb path, requires /var/www/ramdb")
			return rp
		if not os.path.exists(inPath) or len(parts) < 8:
			print("AddDf: INVALID ramdb path")
			return rp
		if parts[5]=="" or parts[6]=="" or parts[7]=="":
			print("AddDf: INVALID ramdb path")
			return rp
		fparts = parts[7].split(".")
		if len(fparts) != 2:
			print("AddDf: INVALID ramdb path")
			return rp
		if fparts[1] != "ramdb":
			print("AddDf: INVALID ramdb path")
			return rp
		rp.Valid = True
		rp.Path = inPath
		conParts = parts[5].split(".")
		rp.Conn = conParts[len(conParts)-1]
		rp.Db = parts[6]
		rp.Table = fparts[0]
		bs = bStream()
		bs.read( inPath )
		rp.NbCols = bs.get_int64("NbCols")
		rp.NbRows = bs.get_int64("NbRows")
		rp.ColNames = bs.get_string_vector("ColNames")
		rp.ColTypes = bs.get_int32_vector("ColTypes")
		rp.ColSizes = bs.get_int32_vector("ColSizes")
		return rp
	
	##############################################################################
	############################## WIDGETS & PANES ###############################
	##############################################################################

	def set_pane_def(self, inPane, inDef):
		if inPane not in self.Layout.PaneID: 
			print("set_pane_def, invalid inPane:",inPane,"not found")
			return
		paneI = self.Layout.PaneID[inPane]
		for op in inDef:
			if op[0]=="Text" or op[0]=="Equation" or op[0]=="Text2":
				dl = ""
				val = ""
				for i in range(1,len(op)):
					val += dl + op[i]
					dl = chr(19)
				if op[0]=="Text":self.Layout.Panes[paneI].Text = val
				elif op[0]=="Equation":self.Layout.Panes[paneI].Equation = val
				elif op[0]=="Text2":self.Layout.Panes[paneI].Text2 = val
			elif op[0]=="Color":self.Layout.Panes[paneI].Color = op[1]
			elif op[0]=="OutlineColor":self.Layout.Panes[paneI].OutlineColor = op[1]
			elif op[0]=="OutlineThickness":self.Layout.Panes[paneI].OutlineThickness = op[1]
			elif op[0]=="Pad":self.Layout.Panes[paneI].Pad = op[1]
			elif op[0]=="Stream" or op[0]=="Layout":
				if self.Layout.Panes[paneI].Stream == None:
					if self.Layout.Panes[paneI].Type == "DataFrame":
						self.Layout.Panes[paneI].Stream = DataframePaneLayout()
					if self.Layout.Panes[paneI].Type == "SpreadSheet":
						self.Layout.Panes[paneI].Stream = SSheetPaneLayout()
					if self.Layout.Panes[paneI].Type == "Geo2D":
						self.Layout.Panes[paneI].Stream = GeoPaneLayout()
					if self.Layout.Panes[paneI].Type == "Widget":
						self.Layout.Panes[paneI].Stream = WidgetPaneLayout()
				if len(op) > 2:
					if hasattr(self.Layout.Panes[paneI].Stream,op[1]):
						if len(op) > 3:
							if hasattr(self.Layout.Panes[paneI].Stream[op[1]],op[2]):
								print("set op[3]: ",op[3])
								self.Layout.Panes[paneI].Stream[op[1]][op[2]]=op[3]
							else:print("Format Key:",op[2],"not found in:\n  ",op)
						else:self.Layout.Panes[paneI].Stream[op[1]]=op[2]
					else:print("Format Key:",op[1],"not found in:\n  ",op)
		if self.Layout.Panes[paneI].Equation != "":
			self.Layout.Panes[paneI].Type = "Calc"
		elif self.Layout.Panes[paneI].Text != "" or self.Layout.Panes[paneI].Text2 != "":
			self.Layout.Panes[paneI].Type = "Text"
	
	def add_image(self, inPane, inPath, inOpt):
		if inPane not in self.Layout.PaneID: 
			print("add_image, invalid inPane:",inPane,"not found")
			return
		if type(inOpt) is not list:
			print("add_image: INVALID inOpt")
			return False
		wd = WidgetPaneLayout()
		wd.Type = "Image Button"
		imgName = os.path.basename(inPath)
		grid = [["Image","",imgName]]
		for op in inOpt:
			if op[0]=="Padding":wd.Padding=op[1]
			elif op[0]=="Clear Filter":grid.append(["Clear Filter",""])
			elif op[0]=="Link":grid.append([op[0],op[1]])
		wd.Grid = grid
		paneI = self.Layout.PaneID[inPane]
		self.Layout.Panes[paneI].Stream = wd
		self.Layout.Panes[paneI].Type = "Widget"
		dashName = Path(self.Path).stem
		dashDir = os.path.dirname(self.Path)
		imgTarget = os.path.join(dashDir, dashName, "assets")
		imgPath = os.path.join(imgTarget, imgName)
		Path(imgTarget).mkdir(parents=True, exist_ok=True)
		shutil.copyfile(inPath, imgPath)

	def add_widget(self, inType, inPane, inOpt):
		if inPane not in self.Layout.PaneID: 
			print("add_widget, invalid inPane:",inPane,"not found")
			return
		if type(inOpt) is not list:
			print("add_widget: INVALID inDef")
			return False
		for op in inOpt:
			if type(op) is not list or len(op) != 2:
				print("add_widget: INVALID inDef")
				return False
		wd = WidgetPaneLayout()
		wd.Type = inType
		if not wd.is_type_valid(inType):
			print("add_widget: INVALID widget type:",inType)
			return False
		for op in inOpt:
			if hasattr(wd,op[0]):wd[op[0]] = op[1]
			else:print("add_widget: INVALID option:",op[0])
		paneI = self.Layout.PaneID[inPane]
		self.Layout.Panes[paneI].Stream = wd
		self.Layout.Panes[paneI].Type = "Widget"

	def format_text(self, inText, inOpt):
		if type(inOpt) is not list:
			print("FormatText: INVALID inOpt")
			return False
		fs=""
		for op in inOpt:
			if op[0]=="Bold":fs+="B"
			if op[0]=="Italic":fs+="I"
			if op[0]=="Underline":fs+="U"
			if op[0]=="Align":
				if op[1]>.8:fs+="H3"
				elif op[1]>.2:fs+="H2"
			if op[0]=="Color":
				if op[1] != 0x000000: fs+="O" + "{:06x}".format(op[1])
			if op[0]=="FontSize":fs+="S"+str(op[1])
			if op[0]=="VerticalSpace":fs+="E"+str(op[1])
		if fs=="":return inText+chr(19)+"BH2S28" # default format
		return inText+chr(19)+fs # ASCII DC3 seperates text & formatting codes

	def format_equation(self, inText, inOpt):
		if type(inOpt) is not list or len(inOpt) == 0:
			print("FormatEquation: INVALID inOpt")
			return False
		fs=""
		nf="#,##0.00" # default number format, number format follows spreadsheet conventions
		for op in inOpt:
			if op[0]=="Bold":fs+="B"
			if op[0]=="Italic":fs+="I"
			if op[0]=="Underline":fs+="U"
			if op[0]=="Color":
				if op[1] != 0x000000: fs+="O" + "{:06x}".format(op[1])
			if op[0]=="FontSize":fs+="S"+str(op[1])
			if op[0]=="Format":nf=op[1]
		if fs=="":return inText+chr(19)+"BH2S28"+chr(19)+nf # default settings
		return inText+chr(19)+fs+chr(19)+nf # ASCII DC3 seperates text, formatting & number formating

	
	def add_to_pane(self, inPane, inOpt):
		if inPane not in self.Layout.PaneID: 
			print("add_to_pane, invalid inPane:",inPane,"not found")
			return
		if type(inOpt) is not list or len(inOpt) == 0:
			print("AddToPadd_to_paneane: INVALID inOpt")
			return False
		for op in inOpt:
			if type(op) is not list or len(op) != 2:
				print("add_to_pane: INVALID inOpt")
				return False
		paneI = self.Layout.PaneID[inPane]
		for op in inOpt:
			if hasattr(self.Layout.Panes[paneI],op[0]):
				self.Layout.Panes[paneI][op[0]] = op[1]
			else:print("AddToPane: INVALID option:",op[0])
		if self.Layout.Panes[paneI].Equation != "":
			self.Layout.Panes[paneI].Type = "Calc"
		elif self.Layout.Panes[paneI].Text != "" or self.Layout.Panes[paneI].Text2 != "":
			self.Layout.Panes[paneI].Type = "Text"

	##############################################################################
	#################################### HELPER ##################################
	##############################################################################

	def cycle_cmap(self, inInd, inCMap, inParentArgs):
		# cycle functions and caputre cross-filtering map change as each step transforms the column structure 
		newMap = [] # vector<int>
		op = self.Graph.Nodes[inInd].Op
		if op == "CROSSLINK":
			for i,pArg in enumerate(inParentArgs):
				if i==0:continue
				newMap.append(pArg)
			inCMap = newMap
		elif op=="GROUPCOUNT" or op=="GROUPSUM" or op=="GROUPAVERAGE" or op=="GROUPOPS":
			for pArg in inParentArgs:
				grpColIndex = int(pArg)
				if grpColIndex < 0 or grpColIndex >= len(inCMap):newMap.append( -1 )
				else: newMap.append(inCMap[grpColIndex])
			inCMap = newMap
		elif op == "ADDCOLUMN":inCMap.append(-1)
		else: pass # other ops (to date) don't change the inCMap
		# cycle downward through FUNCTIONS until you run out
		if len(self.Graph.Nodes[inInd].Children) == 0: return inCMap
		cInd = self.Graph.Nodes[inInd].Children[0]
		parentArgs = self.Graph.Nodes[cInd].Args
		return self.cycle_cmap(cInd, inCMap, parentArgs)

	def update_cmap(self, inInd):
		# to get the cmap for a data node give a starting index in the global graph
		# cMap is a list of columns that can be cross-filtered and how that filter moves up to the parent
		cMap = [] # vector<int> of parent column indicies
		if not self.Graph.Nodes[inInd].Type == 4:return # has to be a data node
		if len(self.Graph.Nodes[inInd].Children) == 0: return
		cInd = self.Graph.Nodes[inInd].Children[0]
		parentArgs = self.Graph.Nodes[cInd].Args
		newCMap = self.cycle_cmap(cInd, cMap, parentArgs)
		self.Graph.Nodes[inInd].CMap = [int(x) for x in newCMap]

	def add_links_from_formula(self, inLink):
		parts = inLink.split("!")
		if len(parts) != 2:return
		link = parts[0].replace("=", "")
		cInd = SSheetHelper.a1_col_to_intz(parts[1]) # column index
		linkI = -1
		for i,lnk in enumerate(self.Links):
			if lnk == link:linkI = i
		if linkI == -1:
			self.Links.append(link)
			self.LinkCols.append([cInd])
		else:
			self.LinkCols[linkI].append(cInd)
			self.LinkCols[linkI].sort()

	def add_df(self, inSheetName, inPaneName, inPaneDef=None):
		if inPaneName not in self.Layout.PaneID: 
			print("add_df, invalid inPaneName:",inPaneName,"not found")
			return
		paneI = self.Layout.PaneID[inPaneName]
		graphI = -1
		for i,nd in enumerate(self.Graph.Nodes):
			if nd.Name ==inSheetName: graphI = i
		if graphI == -1:
			print("add_df, invalid inSheetName:",inSheetName,"not found")
			return
		self.Layout.Panes[paneI].Sheet = inSheetName
		self.Layout.Panes[paneI].Type = "DataFrame"
		if inPaneDef is not None:
			self.set_df_def(paneI, inSheetName, inPaneDef)

	def set_df_def(self, inPaneI, inSheetName, inPaneDef):
		sheetI = self.Sheets.get_sheet_ind(inSheetName)
		dSheet = self.Sheets.Items[sheetI]
		if inPaneDef is not None:
			for op in inPaneDef:
				if op[0]=="Format":
					if op[1]=="Color":self.Layout.Panes[inPaneI].Color = op[2] # color is set on the pane
					if op[1]=="CrossLinking":self.Layout.Panes[inPaneI].CrossLinking = op[2] # cross-linking is set on the pane
					if op[1]=="Pad":self.Layout.Panes[inPaneI].Pad = op[2] # pane level padding
					elif op[1]=="Header" or op[1]=="HeaderBar": # shortcut to dSheet.TableFormat ("TF" in bytestream)
						if op[2] == "Color":op[2]="BkgdColor"
						if dSheet.TableFormat == None:dSheet.TableFormat = TableFormat()
						if hasattr(dSheet.TableFormat,op[2]):
							if len(op) > 3:
								dSheet.TableFormat["ApplyFormat"]=True
								dSheet.TableFormat[op[2]]=op[3]
							else:print("Format Header Attribute 1:",op[2],"not found in:\n  ",op)
						else:print("Format Header Attribute 1:",op[2],"not found in:\n  ",op)
				elif op[0]=="Row": # shortcut to dSheet.RowHeight
					if op[1]=="Height" and len(op)==3:dSheet.RowHeight = op[2]
					else:print("Row Attribute 1:",op[1],"not found in:\n  ",op)
				elif op[0]=="Column": # shortcut to the list: dSheet.ColFormat
					if len(op) < 4:continue
					if not str(op[1]).isdigit():
						print("Format Header Attribute 1:",op[1],"is not an integer");continue
					# ColFormat needs to filled with ColumnFormat() only when we start
					# add parameter changes, this is to keep the .dash file as small as possible
					# assume that dSheet.ColumnWidths length is synced with the .ramdb being displayed
					if dSheet.ColFormat == None: dSheet.ColFormat = []
					nbCols = len(dSheet.ColumnWidths)
					if inSheetName in self.Ramdb:
						ri = self.Ramdb[inSheetName]
						for i in range(len(dSheet.ColFormat),ri["NbCols"]):
							cf = ColumnFormat()
							dSheet.ColFormat.append(cf)
					else: # we are on a datanode or don't have the .ramdb  Fill in ColFormat until the index we assign 
						for i in range(len(dSheet.ColFormat),op[1]+1):
							cf = ColumnFormat()
							dSheet.ColFormat.append(cf)
					if op[1] > nbCols - 1:
						print("Format Header Attribute 1:",op[1],"invalid index");continue
					if op[2]=="Width":
						dSheet.ColumnWidths[op[1]] = op[3]
						continue
					if hasattr(dSheet.ColFormat[op[1]],op[2]):
						dSheet.ColFormat[op[1]][op[2]] = op[3]
					else:print("Format Header Attribute 2:",op[2],"not found in:\n  ",op);continue
				elif op[0]=="Layout": # shortcut to self.Layout.Panes[inPaneI].Stream
					if self.Layout.Panes[inPaneI].Stream == None:
						self.Layout.Panes[inPaneI].Stream = DataframePaneLayout()
					if len(op) > 2:
						if hasattr(self.Layout.Panes[inPaneI].Stream,op[1]):
							if len(op) > 3:
								if hasattr(self.Layout.Panes[inPaneI].Stream[op[1]],op[2]):
									self.Layout.Panes[inPaneI].Stream[op[1]][op[2]]=op[3]
							else:self.Layout.Panes[inPaneI].Stream[op[1]]=op[2]