import struct
import json
import numpy as np
import pandas as pd
import io
import os
from row64tools.bytestream import bytestream as bStream
from row64tools.DashHelper import DashHelper as DH
from row64tools.SeriesData import SeriesData
from row64tools.DashFormatData import FormatData
from row64tools.ColumnFormat import ColumnFormat
from row64tools.TableFormat import TableFormat
from row64tools.Sheet import Sheet
from row64tools.ChartAnimation import ChartAnimation
from row64tools.ChartLayout import ChartLayout
from row64tools.ChartLegend import ChartLegend
from row64tools.ChartDetails import ChartDetails

class DashSheets:

	def __init__(self):
		self.Items = [] # array of DashSheet class
		self.Names = [] # array of Sheet Names

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
			
	def load(self, inBuf):
		bStr = bStream()
		bStr.load_from_buffer(inBuf)
		for ki in range(bStr.nb):
			self.load_sheet(bStr.get_stream(bStr.keys[ki]), bStr.keys[ki])
			self.Names.append(bStr.keys[ki])
		
	def is_sheet_name_unique(self, inName): # check if a sheet name is unique
		for nm in self.Names: 
			if nm == inName: return False
		return True

	def loadColFormat(self, inBuf):
		cfStr = bStream()
		cfStr.load_from_buffer(inBuf)
		cf = ColumnFormat()
		cf.Code = cfStr.get_string("Code")
		cf.Formula = cfStr.get_string("Formula")
		cf.Theme = cfStr.get_int32_vector("Theme")
		cf.DisplayName = cfStr.get_string("DisplayName")
		return cf

	def get_ColFormat_buf(self, inCF):
		cStr = bStream()
		cStr.add_string("Code", inCF.Code)
		cStr.add_string("Formula", inCF.Formula)
		cStr.add_int32_vector("Theme", inCF.Theme)
		cStr.add_string("DisplayName", inCF.DisplayName)
		return cStr.save_to_buffer()
		
	def loadTableFormat(self, inBuf):
		tfStr = bStream()
		tfStr.load_from_buffer(inBuf)
		tf = TableFormat()
		if tfStr.key_exists("HeaderHeight"):
			tf.HeaderHeight = tfStr.get_float("HeaderHeight")
		if tfStr.key_exists("ApplyFormat"):
			tf.ApplyFormat = tfStr.get_bool("ApplyFormat")
		tf.BkgdColor = tfStr.get_int32("BkgdColor")
		tf.TxtColor = tfStr.get_int32("TxtColor")
		tf.Bold = tfStr.get_bool("Bold")
		tf.Italic = tfStr.get_bool("Italic")
		tf.Underline = tfStr.get_bool("Underline")
		tf.LMRAlign = tfStr.get_int32("LMRAlign")
		tf.ShowHeadBorder = tfStr.get_bool("ShowHeadBorder")
		tf.ShowDataframeBorder = tfStr.get_bool("ShowDataframeBorder")			
		tf.BorderColor = tfStr.get_int32("BorderColor")
		tf.BorderThickness = tfStr.get_float("BorderThickness")
		# tf.log()
		return tf

	def get_sheet_ind(self, inSheetName): # Given a sheetname, get index
		for i,sName in enumerate(self.Names):
			if inSheetName == sName:return i
		return -1

	def get_tab_type(self, inSheetName): # Given a sheetname, get the type...
		for i,sName in enumerate(self.Names):
			if inSheetName == sName:
				return self.Items[i].Type
		return ""

	def get_sheet_dim(self, inSheetName):
		for i,sName in enumerate(self.Names):
			if inSheetName == sName:
				return self.Items[i].SetArea
		return [-1, -1, -1, -1]

	def load_sheet(self, inBuf, inKey):

		cStr = bStream()
		cStr.load_from_buffer(inBuf)
		cSheet = Sheet()
		cSheet.Key = inKey
		if cStr.key_exists("Type"): # This is a chart
			cSheet.Type = cStr.get_string("Type")
			cSheet.Category = cStr.get_string("Category")
			cSheet.Details = self.load_details( cStr.get_stream("Details") )
			sData = SeriesData.load( cSheet.Type, cStr.get_stream_vector("CData"), cSheet.Key )
			cSheet.CData = sData;
			if cStr.key_exists("FData"):
				cSheet.FData = FormatData.load(cSheet.Type, cStr.get_stream("FData") )

		elif cStr.key_exists("SetArea"): # This is a Spreadsheet
			cSheet.Type = "Spreadsheet"
			if cStr.key_exists("FontSize"):
				cSheet.FontSize = cStr.get_float("FontSize")
			if cStr.key_exists("RowHeights"):
				cSheet.RowHeight = cStr.get_double_vector("RowHeights")
			if cStr.key_exists("ColumnWidths"):
				cSheet.ColumnWidths = cStr.get_double_vector("ColumnWidths")
			cSheet.SetArea = cStr.get_int64_vector("SetArea")
			# Don't load "DFList".  It needs to be generated on save to be synced to any edits
			
		else: # This is a Dataframe 
			# print("-------------------------- process DATAFRAME: ",inKey," ----------------")
			bs = bStream()
			bs.load_from_buffer(inBuf)
			# bs.log_details()
			cSheet.Type = "DataFrame"
			if cStr.key_exists("FontSize"):
				cSheet.FontSize = cStr.get_float("FontSize")
			if cStr.key_exists("RowHeight"):
				cSheet.RowHeight = cStr.get_double("RowHeight")
			if cStr.key_exists("ColumnWidths"):
				cSheet.ColumnWidths = cStr.get_double_vector("ColumnWidths")
			if cStr.key_exists("ColFormat"):
				if cStr.get_type("ColFormat") == 54: # 54 = stream_vector, old ColFormat is string_vector
					cFormatList = cStr.get_stream_vector("ColFormat")
					cSheet.ColFormat = []
					for i,cf in enumerate(cFormatList):
						cSheet.ColFormat.append(self.loadColFormat(cf))
			if cStr.key_exists("TF"):
				cSheet.TableFormat = self.loadTableFormat(cStr.get_stream("TF"))
			# cSheet.log_df()
		self.Items.append(cSheet)
	
	def get_empty_buf(self):
		bs = bStream()
		return bs.save_to_buffer()

	def get_buffer(self, inDAG):
		listStr = bStream()
		for i,sheet in enumerate(self.Items):
			sheetStr = bStream()
			if sheet.Category != "":
				sheetStr.add_string("Category",sheet.Category)
				sheetStr.add_string("Type",sheet.Type)
				sheetStr.add_stream("Details", self.get_detailed_buf(sheet.Details))
				sheetStr.add_stream_vector("CData", SeriesData.get_buffer_list(sheet.CData, sheet.Type, sheet.Key))
				if sheet.FData is not None:
					sheetStr.add_stream("FData", FormatData.get_buffer(sheet.FData))
				else:sheetStr.add_stream("FData", self.get_empty_buf()) # add empty stream
				# print("-------------------------- SHEET OUT: ",sheet.Key," ----------------")
				# bs = bStream()
				# bs.load_from_buffer(sheetStr.save_to_buffer())
				# bs.log_details()
			if sheet.SetArea is not None: # spreadsheet
				sheetStr.add_float("FontSize",sheet.FontSize)
				sheetStr.add_double_vector("RowHeights",sheet.RowHeights)
				sheetStr.add_double_vector("ColumnWidths",sheet.ColumnWidths)
				sheetStr.add_int64_vector("SetArea", sheet.SetArea)
				dFList = inDAG.get_df_list(self.Names[i])
				if len(dFList) > 0: sheetStr.add_string_vector("DFList", dFList)
			else: # dataframe
				sheetStr.add_float("FontSize",sheet.FontSize)
				sheetStr.add_double("RowHeight",sheet.RowHeight)
				sheetStr.add_double_vector("ColumnWidths",sheet.ColumnWidths)
				if sheet.TableFormat is not None:
					sheetStr.add_stream("TF", self.get_TF_Buffer(sheet.TableFormat))
				if sheet.ColFormat is not None:
					bufList = []
					for i, cFormat in enumerate(sheet.ColFormat):
						bufList.append(self.get_ColFormat_buf(cFormat))
					if len(bufList)>0:sheetStr.add_stream_vector("ColFormat", bufList)
			listStr.add_stream(sheet.Key, sheetStr.save_to_buffer())

		sheetBuffer = listStr.save_to_buffer()
		# print("-------------------------- SHEETS ----------------")
		# bs = bStream()
		# bs.load_from_buffer(sheetBuffer)
		# bs.log_details()
		return sheetBuffer

	def get_TF_Buffer(self, inTF):
		tStr = bStream()
		tStr.add_float("HeaderHeight", inTF.HeaderHeight)
		tStr.add_bool("ApplyFormat", inTF.ApplyFormat)
		tStr.add_int32("BkgdColor", inTF.BkgdColor)
		tStr.add_int32("TxtColor", inTF.TxtColor)
		tStr.add_bool("Bold", inTF.Bold)
		tStr.add_bool("Italic", inTF.Italic)		
		tStr.add_bool("Underline", inTF.Underline)
		tStr.add_int32("LMRAlign", inTF.LMRAlign)
		tStr.add_bool("ShowHeadBorder", inTF.ShowHeadBorder)
		tStr.add_bool("ShowDataframeBorder", inTF.ShowDataframeBorder)
		tStr.add_int32("BorderColor", inTF.BorderColor)
		tStr.add_float("BorderThickness", inTF.BorderThickness)
		return tStr.save_to_buffer()

	def get_detailed_buf(self, inDet):
		dStr = bStream()
		dStr.add_string("Type", inDet.Type)
		dStr.add_string("Title", inDet.Title)
		dStr.add_int32_vector("ColorTheme", inDet.ColorTheme)
		dStr.add_float("ColorSmooth", inDet.ColorSmooth)
		dStr.add_int32_vector("ColorHighlights", inDet.ColorHighlights)
		dStr.add_float_vector("HighlightSlices", inDet.HighlightSlices)
		dStr.add_double_vector("AxisBound", inDet.AxisBound)
		dStr.add_int32_vector("AxisBoundFlag", inDet.AxisBoundFlag)
		dStr.add_float_vector("Gaps", inDet.Gaps)
		dStr.add_int32("GroupType", inDet.GroupType)
		dStr.add_stream("Legend", self.get_legend_buf(inDet.Legend))
		dStr.add_bool("ShowTitle", inDet.ShowTitle)
		dStr.add_stream("TitleFont", DH.get_font_options_buf(inDet.TitleFont))
		dStr.add_float_vector("TitlePos", inDet.TitlePos)
		dStr.add_stream("Layout", self.get_layout_buffer(inDet.Layout))
		dStr.add_stream("Animation", self.get_animation_buf(inDet.Animation))
		dBuf = dStr.save_to_buffer()
		# print("------------------ DETAIL BUFFER OUT ------------------")
		# bs = bStream()
		# bs.load_from_buffer(dBuf)
		# bs.log_details()
		# print("------------------ END DETAIL BUFFER OUT ------------------")
		return dBuf

	def get_legend_buf(self, inLeg):
		lStr = bStream()
		lStr.add_bool("Show", inLeg.Show)
		lStr.add_float_vector("Pos", inLeg.Pos)
		lStr.add_float_vector("Dim", inLeg.Dim)
		lStr.add_bool("HasBorder", inLeg.HasBorder)
		lStr.add_stream("Border", DH.get_line_options_buf(inLeg.Border))
		lStr.add_bool("HasFill", inLeg.HasFill)
		lStr.add_stream("Fill", DH.get_fill_options_buf(inLeg.Fill))
		lStr.add_stream("Font", DH.get_font_options_buf(inLeg.Font))
		lStr.add_float("ChipSize", inLeg.ChipSize)
		lStr.add_float("ChipSpacing", inLeg.ChipSpacing)
		return lStr.save_to_buffer()

	def load_details(self, inBuf):
		dStr = bStream()
		dStr.load_from_buffer(inBuf)
		# print("------------------ DETAIL BUFFER IN ------------------")
		# dStr.log_details()
		# print("------------------ END DETAIL BUFFER IN ------------------")
		cDet = ChartDetails()
		cDet.Type = dStr.get_string("Type")
		cDet.Title = dStr.get_string("Title")
		cDet.ColorTheme = dStr.get_int32_vector("ColorTheme")
		cDet.ColorSmooth = dStr.get_float("ColorSmooth")
		cDet.ColorHighlights = dStr.get_int32_vector("ColorHighlights")
		cDet.HighlightSlices = dStr.get_float_vector("HighlightSlices")
		cDet.Gaps = dStr.get_float_vector("Gaps")
		cDet.GroupType = dStr.get_int32("GroupType")
		cDet.Legend = self.load_legend( dStr.get_stream("Legend") )
		cDet.ShowTitle = dStr.get_bool("ShowTitle")
		cDet.TitleFont = DH.get_font_options(dStr.get_stream("TitleFont"))
		cDet.TitlePos = dStr.get_float_vector("TitlePos")
		cDet.Layout = self.load_layout( dStr.get_stream("Layout") )
		cDet.Animation = self.load_animation( dStr.get_stream("Animation") )
		cDet.AxisBound = dStr.get_double_vector("AxisBound")
		cDet.AxisBoundFlag = dStr.get_int32_vector("AxisBoundFlag")
		return cDet

	def load_animation(self, inBuf):
		lStr = bStream()
		lStr.load_from_buffer(inBuf)
		cai = ChartAnimation()
		cai.Style = lStr.get_string("Style")
		cai.HasTimeSeries = lStr.get_bool("HasTimeSeries")
		cai.TimeValues = lStr.get_string("TimeValues")
		cai.Frames = lStr.get_uint64("Frames")
		cai.FPS = lStr.get_uint64("FPS")
		cai.CurrentFrame = lStr.get_uint64("CurrentFrame")
		cai.Mode = lStr.get_int32("Mode")
		cai.Smooth = lStr.get_bool("Smooth")
		return cai

	def get_animation_buf(self, inObj):
		lStr = bStream()
		lStr.add_string("Style", inObj.Style)
		lStr.add_bool("HasTimeSeries", inObj.HasTimeSeries)
		lStr.add_string("TimeValues", inObj.TimeValues)
		lStr.add_uint64("Frames", inObj.Frames)
		lStr.add_uint64("FPS", inObj.FPS)
		lStr.add_uint64("CurrentFrame", inObj.CurrentFrame)
		lStr.add_int32("Mode", inObj.Mode)
		lStr.add_bool("Smooth", inObj.Smooth)
		return lStr.save_to_buffer()

	def load_legend(self, inBuf):
		lStr = bStream()
		lStr.load_from_buffer(inBuf)
		# print("------------------ LEGEND BUFFER IN ------------------")
		# lStr.log_details()
		# print("------------------ END LEGEND BUFFER IN ------------------")
		clg = ChartLegend()
		clg.Show = lStr.get_bool("Show")
		clg.Pos = lStr.get_float_vector("Pos")
		clg.Dim = lStr.get_float_vector("Dim")		
		clg.HasBorder = lStr.get_bool("HasBorder")
		clg.Border = DH.get_line_options( lStr.get_stream("Border") )
		clg.HasFill = lStr.get_bool("HasFill")
		clg.Fill = DH.get_fill_options( lStr.get_stream("Fill") )
		clg.Font = DH.get_font_options( lStr.get_stream("Font") )	
		clg.ChipSize = lStr.get_float("ChipSize")
		clg.ChipSpacing = lStr.get_float("ChipSpacing")
		return clg

	def load_layout(self, inBuf):
		lStr = bStream()
		lStr.load_from_buffer(inBuf)
		chl = ChartLayout()
		chl.RPadding = lStr.get_float("RPadding")
		chl.LPadding = lStr.get_float("LPadding")
		chl.TPadding = lStr.get_float("TPadding")
		chl.BPadding = lStr.get_float("BPadding")
		chl.Width = lStr.get_float("Width")
		chl.Height = lStr.get_float("Height")
		chl.HasChartBorder = lStr.get_bool("HasChartBorder")
		chl.ChartBorder = DH.get_line_options( lStr.get_stream("ChartBorder") )
		chl.HasChartFill = lStr.get_bool("HasChartFill")
		chl.ChartFill = DH.get_fill_options( lStr.get_stream("ChartFill") )
		chl.HasBkgdFill = lStr.get_bool("HasBkgdFill")
		chl.BkgdFill = DH.get_fill_options( lStr.get_stream("BkgdFill") )
		return chl

	def get_layout_buffer(self, inObj):
		lStr = bStream()
		lStr.add_float("RPadding", inObj.RPadding)
		lStr.add_float("LPadding", inObj.LPadding)
		lStr.add_float("TPadding", inObj.TPadding)
		lStr.add_float("BPadding", inObj.BPadding)
		lStr.add_float("Width", inObj.Width)
		lStr.add_float("Height", inObj.Height)
		lStr.add_bool("HasChartBorder", inObj.HasChartBorder)
		lStr.add_stream("ChartBorder", DH.get_line_options_buf(inObj.ChartBorder))
		lStr.add_bool("HasChartFill", inObj.HasChartFill)
		lStr.add_stream("ChartFill", DH.get_fill_options_buf(inObj.ChartFill))
		lStr.add_bool("HasBkgdFill", inObj.HasBkgdFill)
		lStr.add_stream("BkgdFill", DH.get_fill_options_buf(inObj.BkgdFill))
		return lStr.save_to_buffer()