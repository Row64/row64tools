import struct
import json
import numpy as np
import pandas as pd
import io
import os
from row64tools.bytestream import bytestream as bStream
from row64tools.DashHelper import DashHelper as DH
from row64tools.PieFormat import PieFormat
from row64tools.BarFormat import BarFormat
from row64tools.LinePlotFormat import LinePlotFormat
from row64tools.ScatterPlotFormat import ScatterPlotFormat
from row64tools.BubblePlotFormat import BubblePlotFormat
from row64tools.VennFormat import VennFormat
from row64tools.WordcloudFormat import WordcloudFormat
from row64tools.TrellisFormat import TrellisFormat

class FormatData: # also known as CData in the .dash format

	def __init__(self):pass

	def load(inType, inBuf):
		if(inType =="Pie"):
			return FormatData.get_pie_format(inBuf)
		elif(inType=="LinePlot"):
			return FormatData.get_lineplot_format(inBuf)
		elif(inType=="Bar"):
			return FormatData.get_bar_format(inBuf)
		elif(inType=="ScatterPlot"):
			return FormatData.get_scatterplot_format(inBuf)
		elif(inType=="BubblePlot"):
			return FormatData.get_bubbleplot_format(inBuf)
		elif(inType=="Venn"):
			return FormatData.get_venn_format(inBuf)
		elif(inType=="WordCloud"):
			return FormatData.get_wordcloud_format(inBuf)
		elif(inType=="Trellis"):
			return FormatData.get_trellis_format(inBuf)

	def get_buffer(inObj):
		cType = inObj.__class__.__name__
		if(cType=="PieFormat"):
			return FormatData.get_pie_buffer(inObj)
		elif(cType=="BarFormat"):
			return FormatData.get_bar_buffer(inObj)
		elif(cType=="LinePlotFormat"):
			return FormatData.get_lineplot_buffer(inObj)
		elif(cType=="ScatterPlotFormat"):
			return FormatData.get_scatterplot_buf(inObj)
		elif(cType=="BubblePlotFormat"):
			return FormatData.get_bubbleplot_buf(inObj)
		elif(cType=="VennFormat"):
			return FormatData.get_venn_buffer(inObj)
		elif(cType=="WordcloudFormat"):
			return FormatData.get_wordcloud_buffer(inObj)
		elif(cType=="TrellisFormat"):
			return FormatData.get_trellis_buffer(inObj)
	
	def get_pie_format(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cfm = PieFormat()
		cfm.LabelTypes = sStr.get_int32_vector("LabelTypes")
		cfm.PrimarySep = sStr.get_int32("PrimarySep")
		cfm.SecondarySep = sStr.get_int32("SecondarySep")
		cfm.Reverse = sStr.get_bool("Reverse")
		cfm.PrimaryFont = DH.get_font_options(sStr.get_stream("PrimaryFont"))
		cfm.SecondaryFont = DH.get_font_options(sStr.get_stream("SecondaryFont"))
		cfm.FontAlignment = sStr.get_float_vector("FontAlignment")
		cfm.ShowLine = sStr.get_bool("ShowLine")
		cfm.LeaderLine = DH.get_line_options(sStr.get_stream("LeaderLine"))
		cfm.LeaderPos = sStr.get_float("LeaderPos")
		cfm.LeaderDotSize = sStr.get_float("LeaderDotSize")
		cfm.LabelShift = sStr.get_float_vector("LabelShift")	
		cfm.LineEnd = sStr.get_float("LineEnd")
		cfm.SpacingByAngle = sStr.get_float("SpacingByAngle")
		cfm.SpacingByLength = sStr.get_float("SpacingByLength")
		cfm.SpacingArea = sStr.get_float("SpacingArea")
		cfm.Doughnut = sStr.get_float("Doughnut")
		cfm.FitScale = sStr.get_float("FitScale")
		return cfm

	def get_pie_buffer(inObj):
		dStr = bStream()
		dStr.add_int32_vector("LabelTypes", inObj.LabelTypes)
		dStr.add_int32("PrimarySep", inObj.PrimarySep)
		dStr.add_int32("SecondarySep", inObj.SecondarySep)
		dStr.add_bool("Reverse", inObj.Reverse)
		dStr.add_stream("PrimaryFont", DH.get_font_options_buf(inObj.PrimaryFont))
		dStr.add_stream("SecondaryFont", DH.get_font_options_buf(inObj.SecondaryFont))
		dStr.add_float_vector("FontAlignment", inObj.FontAlignment)
		dStr.add_bool("ShowLine", inObj.ShowLine)
		dStr.add_stream("LeaderLine", DH.get_line_options_buf(inObj.LeaderLine))
		dStr.add_float("LeaderPos", inObj.LeaderPos)
		dStr.add_float("LeaderDotSize", inObj.LeaderDotSize)
		dStr.add_float_vector("LabelShift", inObj.LabelShift)	
		dStr.add_float("LineEnd", inObj.LineEnd)
		dStr.add_float("SpacingByAngle", inObj.SpacingByAngle)
		dStr.add_float("SpacingByLength", inObj.SpacingByLength)
		dStr.add_float("SpacingArea", inObj.SpacingArea)
		dStr.add_float("Doughnut", inObj.Doughnut)
		dStr.add_float("FitScale", inObj.FitScale)
		return dStr.save_to_buffer()


	def get_lineplot_format(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cfm = LinePlotFormat()
		cfm.GridlineX = DH.get_grid_options(sStr.get_stream("GridlineX"))
		cfm.GridlineY = DH.get_grid_options(sStr.get_stream("GridlineY"))
		cfm.AxisX = DH.get_axis_options(sStr.get_stream("AxisX"))
		cfm.AxisY = DH.get_axis_options(sStr.get_stream("AxisY"))
		cfm.DataLabelPos = sStr.get_int32("DataLabelPos")
		cfm.PrimarySep = sStr.get_int32("PrimarySep")
		cfm.SecondarySep = sStr.get_int32("SecondarySep")
		cfm.LabelTypes = sStr.get_int32_vector("LabelTypes")
		cfm.Reverse = sStr.get_bool("Reverse")
		cfm.PrimaryFont = DH.get_font_options(sStr.get_stream("PrimaryFont"))
		cfm.SecondaryFont = DH.get_font_options(sStr.get_stream("SecondaryFont"))
		cfm.FontAlignment = sStr.get_float_vector("FontAlignment")
		cfm.LabelShift = sStr.get_float("LabelShift")
		cfm.ChartPadX = sStr.get_float_vector("ChartPadX")
		cfm.InterpolateNull = sStr.get_bool("InterpolateNull")
		cfm.DR_DataLabelPos = sStr.get_int32("DR_DataLabelPos")
		cfm.DR_PrimarySep = sStr.get_int32("DR_PrimarySep")		
		cfm.DR_SecondarySep = sStr.get_int32("DR_SecondarySep")	
		cfm.DR_LabelTypes = sStr.get_int32_vector("DR_LabelTypes")
		cfm.DR_Reverse = sStr.get_bool("DR_Reverse")
		cfm.DR_PrimaryFont = DH.get_font_options(sStr.get_stream("DR_PrimaryFont"))
		cfm.DR_SecondaryFont = DH.get_font_options(sStr.get_stream("DR_SecondaryFont"))
		cfm.DR_FontAlignment = sStr.get_float_vector("DR_FontAlignment")
		cfm.DR_LabelShift = sStr.get_float("DR_LabelShift")
		return cfm

	def get_lineplot_buffer(inObj):
		dStr = bStream()
		dStr.add_stream("GridlineX", DH.get_grid_options_buf(inObj.GridlineX))
		dStr.add_stream("GridlineY", DH.get_grid_options_buf(inObj.GridlineY))
		dStr.add_stream("AxisX", DH.get_axis_options_buf(inObj.AxisX))
		dStr.add_stream("AxisY", DH.get_axis_options_buf(inObj.AxisY))
		dStr.add_int32("DataLabelPos", inObj.DataLabelPos)
		dStr.add_int32("PrimarySep", inObj.PrimarySep)
		dStr.add_int32("SecondarySep", inObj.SecondarySep)
		dStr.add_int32_vector("LabelTypes", inObj.LabelTypes)
		dStr.add_bool("Reverse", inObj.Reverse)
		dStr.add_stream("PrimaryFont", DH.get_font_options_buf(inObj.PrimaryFont))
		dStr.add_stream("SecondaryFont", DH.get_font_options_buf(inObj.SecondaryFont))
		dStr.add_float_vector("FontAlignment", inObj.FontAlignment)
		dStr.add_float("LabelShift", inObj.LabelShift)
		dStr.add_float_vector("ChartPadX", inObj.ChartPadX)
		dStr.add_bool("InterpolateNull", inObj.InterpolateNull)
		dStr.add_int32("DR_DataLabelPos", inObj.DR_DataLabelPos)
		dStr.add_int32("DR_PrimarySep", inObj.DR_PrimarySep)	
		dStr.add_int32("DR_SecondarySep", inObj.DR_SecondarySep)	
		dStr.add_int32_vector("DR_LabelTypes", inObj.DR_LabelTypes)
		dStr.add_bool("DR_Reverse", inObj.DR_Reverse)
		dStr.add_stream("DR_PrimaryFont", DH.get_font_options_buf(inObj.DR_PrimaryFont))
		dStr.add_stream("DR_SecondaryFont", DH.get_font_options_buf(inObj.DR_SecondaryFont))		
		dStr.add_float_vector("DR_FontAlignment", inObj.DR_FontAlignment)
		dStr.add_float("DR_LabelShift", inObj.DR_LabelShift)
		return dStr.save_to_buffer()	

	def get_bar_format(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cfm = BarFormat()
		cfm.AxisX = DH.get_axis_options(sStr.get_stream("AxisX"))
		cfm.AxisY = DH.get_axis_options(sStr.get_stream("AxisY"))
		cfm.GridlineY = DH.get_grid_options(sStr.get_stream("GridlineY"))
		cfm.LineToBarGap = sStr.get_float("LineToBarGap")
		cfm.ShowLabels = sStr.get_bool("ShowLabels")
		cfm.LabelFont = DH.get_font_options(sStr.get_stream("LabelFont"))
		cfm.LabelShift = sStr.get_float("LabelShift")
		cfm.Rounding = sStr.get_float("Rounding")
		cfm.BottomRound = sStr.get_bool("BottomRound")
		cfm.ChartPadX = sStr.get_float_vector("ChartPadX")
		cfm.AutoFit = sStr.get_bool("AutoFit")
		cfm.BarSize = sStr.get_float("BarSize")
		cfm.StackedBar = sStr.get_bool("StackedBar")
		cfm.HorizontalBar = sStr.get_bool("HorizontalBar")
		cfm.BarOrder = sStr.get_int32("BarOrder")
		cfm.ReorderSpeed = sStr.get_float("ReorderSpeed")
		return cfm

	def get_bar_buffer(inObj):
		dStr = bStream()
		dStr.add_stream("AxisX", DH.get_axis_options_buf(inObj.AxisX))
		dStr.add_stream("AxisY", DH.get_axis_options_buf(inObj.AxisY))
		dStr.add_stream("GridlineY", DH.get_grid_options_buf(inObj.GridlineY))
		dStr.add_float("LineToBarGap", inObj.LineToBarGap)
		dStr.add_bool("ShowLabels", inObj.ShowLabels)
		dStr.add_stream("LabelFont", DH.get_font_options_buf(inObj.LabelFont))
		dStr.add_float("LabelShift", inObj.LabelShift)
		dStr.add_float("Rounding", inObj.Rounding)
		dStr.add_bool("BottomRound", inObj.BottomRound)
		dStr.add_float_vector("ChartPadX", inObj.ChartPadX)
		dStr.add_bool("AutoFit", inObj.AutoFit)
		dStr.add_float("BarSize", inObj.BarSize)
		dStr.add_bool("StackedBar", inObj.StackedBar)
		dStr.add_bool("HorizontalBar", inObj.HorizontalBar)
		dStr.add_int32("BarOrder", inObj.BarOrder)
		dStr.add_float("ReorderSpeed", inObj.ReorderSpeed)
		return dStr.save_to_buffer()


	def get_scatterplot_format(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cfm = ScatterPlotFormat()
		cfm.GridlineX = DH.get_grid_options(sStr.get_stream("GridlineX"))
		cfm.GridlineY = DH.get_grid_options(sStr.get_stream("GridlineY"))
		cfm.AxisX = DH.get_axis_options(sStr.get_stream("AxisX"))
		cfm.AxisY = DH.get_axis_options(sStr.get_stream("AxisY"))
		cfm.DataLabelPos = sStr.get_int32("DataLabelPos")
		cfm.PrimarySep = sStr.get_int32("PrimarySep")
		cfm.SecondarySep = sStr.get_int32("SecondarySep")
		cfm.LabelTypes = sStr.get_int32_vector("LabelTypes")
		cfm.Reverse = sStr.get_bool("Reverse")
		cfm.PrimaryFont = DH.get_font_options(sStr.get_stream("PrimaryFont"))
		cfm.SecondaryFont = DH.get_font_options(sStr.get_stream("SecondaryFont"))
		cfm.FontAlignment = sStr.get_float_vector("FontAlignment")
		cfm.LabelShift = sStr.get_float("LabelShift")
		return cfm

	def get_scatterplot_buf(inObj):
		dStr = bStream()
		dStr.add_stream("GridlineX", DH.get_grid_options_buf(inObj.GridlineX))
		dStr.add_stream("GridlineY", DH.get_grid_options_buf(inObj.GridlineY))
		dStr.add_stream("AxisX", DH.get_axis_options_buf(inObj.AxisX))
		dStr.add_stream("AxisY", DH.get_axis_options_buf(inObj.AxisY))
		dStr.add_int32("DataLabelPos", inObj.DataLabelPos)
		dStr.add_int32("PrimarySep", inObj.PrimarySep)
		dStr.add_int32("SecondarySep", inObj.SecondarySep)
		dStr.add_int32_vector("LabelTypes", inObj.LabelTypes)
		dStr.add_bool("Reverse", inObj.Reverse)
		dStr.add_stream("PrimaryFont", DH.get_font_options_buf(inObj.PrimaryFont))
		dStr.add_stream("SecondaryFont", DH.get_font_options_buf(inObj.SecondaryFont))
		dStr.add_float_vector("FontAlignment", inObj.FontAlignment)
		dStr.add_float("LabelShift", inObj.LabelShift)
		return dStr.save_to_buffer()

	def get_bubbleplot_format(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cfm = BubblePlotFormat()
		cfm.GridlineX = DH.get_grid_options(sStr.get_stream("GridlineX"))
		cfm.GridlineY = DH.get_grid_options(sStr.get_stream("GridlineY"))
		cfm.AxisX = DH.get_axis_options(sStr.get_stream("AxisX"))
		cfm.AxisY = DH.get_axis_options(sStr.get_stream("AxisY"))
		cfm.DataLabelPos = sStr.get_int32("DataLabelPos")
		cfm.PrimarySep = sStr.get_int32("PrimarySep")
		cfm.SecondarySep = sStr.get_int32("SecondarySep")
		cfm.LabelTypes = sStr.get_int32_vector("LabelTypes")
		cfm.Reverse = sStr.get_bool("Reverse")
		cfm.PrimaryFont = DH.get_font_options(sStr.get_stream("PrimaryFont"))
		cfm.SecondaryFont = DH.get_font_options(sStr.get_stream("SecondaryFont"))
		cfm.FontAlignment = sStr.get_float_vector("FontAlignment")
		cfm.LabelShift = sStr.get_float("LabelShift")
		cfm.MinChipSize = sStr.get_float("MinChipSize")
		return cfm

	def get_bubbleplot_buf(inObj):
		dStr = bStream()
		dStr.add_stream("GridlineX", DH.get_grid_options_buf(inObj.GridlineX))
		dStr.add_stream("GridlineY", DH.get_grid_options_buf(inObj.GridlineY))
		dStr.add_stream("AxisX", DH.get_axis_options_buf(inObj.AxisX))
		dStr.add_stream("AxisY", DH.get_axis_options_buf(inObj.AxisY))
		dStr.add_int32("DataLabelPos", inObj.DataLabelPos)
		dStr.add_int32("PrimarySep", inObj.PrimarySep)
		dStr.add_int32("SecondarySep", inObj.SecondarySep)
		dStr.add_int32_vector("LabelTypes", inObj.LabelTypes)
		dStr.add_bool("Reverse", inObj.Reverse)
		dStr.add_stream("PrimaryFont", DH.get_font_options_buf(inObj.PrimaryFont))
		dStr.add_stream("SecondaryFont", DH.get_font_options_buf(inObj.SecondaryFont))
		dStr.add_float_vector("FontAlignment", inObj.FontAlignment)
		dStr.add_float("LabelShift", inObj.LabelShift)
		dStr.add_float("MinChipSize", inObj.MinChipSize)
		return dStr.save_to_buffer()

	def get_trellis_format(inBuf):
		tStr = bStream()
		tStr.load_from_buffer(inBuf)
		tfm = TrellisFormat()
		tfm.GridType = tStr.get_int32("GridType")
		tfm.GridLookup = tStr.get_string("GridLookup")
		tfm.NbRows = tStr.get_int32("NbRows")
		tfm.NbCols = tStr.get_int32("NbCols")
		tfm.FitW = tStr.get_bool("FitW")
		tfm.FitH = tStr.get_bool("FitH")
		tfm.BoxW = tStr.get_float("BoxW")
		tfm.BoxH = tStr.get_float("BoxH")
		tfm.Pad = tStr.get_float("Pad")
		tfm.Mode = tStr.get_int32("Mode")
		tfm.ShowOutline = tStr.get_bool("ShowOutline")
		if tStr.key_exists("Outline"):
			cfm.Outline = DH.get_line_options(tStr.get_stream("Outline"))
		if tStr.key_exists("RLabelFont"):
			cfm.Outline = DH.get_font_options(tStr.get_stream("RLabelFont"))
		tfm.RLabelRotate = tStr.get_bool("RLabelRotate")
		tfm.RLabelShift = tStr.get_float("RLabelShift")
		if tStr.key_exists("CLabelFont"):
			cfm.CLabelFont = DH.get_font_options(tStr.get_stream("CLabelFont"))
		tfm.CLabelShift = tStr.get_float("CLabelShift")
		tfm.Type = tStr.get_string("Type")
		if cStr.key_exists("Line"):
			tfm.Line = FormatData.get_lineplot_format( cStr.get_stream("Line") )
		if cStr.key_exists("Bar"):
			tfm.Bar = FormatData.get_bar_format( cStr.get_stream("Bar") )
		if cStr.key_exists("Pie"):
			tfm.Pie = FormatData.get_pie_format( cStr.get_stream("Pie") )
		if cStr.key_exists("Scatter"):
			tfm.Scatter = FormatData.get_scatterplot_format( cStr.get_stream("Scatter") )
		if cStr.key_exists("Bubble"):
			tfm.Bubble = FormatData.get_bubbleplot_format( cStr.get_stream("Bubble") )
		return tfm
	
	def get_trellis_buffer(inObj):
		tStr = bStream()
		tStr.add_int32("GridType", inObj.GridType)
		tStr.add_string("GridLookup", inObj.GridLookup)
		tStr.add_int32("NbRows", inObj.NbRows)
		tStr.add_int32("NbCols", inObj.NbCols)
		tStr.add_bool("FitW", inObj.FitW)
		tStr.add_bool("FitH", inObj.FitH)
		tStr.add_float("BoxW", inObj.BoxW)
		tStr.add_float("BoxH", inObj.BoxH)
		tStr.add_float("Pad", inObj.Pad)
		tStr.add_int32("Mode", inObj.Mode)
		tStr.add_bool("ShowOutline", inObj.ShowOutline)
		if inObj.Outline != None:
			tStr.add_stream("Outline", DH.get_line_options_buf(inObj.Outline))
		if inObj.RLabelFont != None:
			tStr.add_stream("RLabelFont", DH.get_font_options_buf(inObj.RLabelFont))
		tStr.add_bool("RLabelRotate", inObj.RLabelRotate)
		tStr.add_float("RLabelShift", inObj.RLabelShift)
		if inObj.CLabelFont != None:
			tStr.add_stream("CLabelFont", DH.get_font_options_buf(inObj.CLabelFont))
		tStr.add_float("CLabelShift", inObj.CLabelShift)
		tStr.add_string("Type", inObj.Type)
		if inObj.Line != None:
			tStr.add_stream("Line", FormatData.get_lineplot_buffer(inObj.Line))
		if inObj.Bar != None:
			tStr.add_stream("Bar", FormatData.get_bar_buffer(inObj.Bar))
		if inObj.Pie != None:
			tStr.add_stream("Pie", FormatData.get_pie_buffer(inObj.Pie))
		if inObj.Scatter != None:
			tStr.add_stream("Scatter", FormatData.get_scatterplot_buf(inObj.Scatter))
		if inObj.Bubble != None:
			tStr.add_stream("Bubble", FormatData.get_bubbleplot_buf(inObj.Bubble))
		return tStr.save_to_buffer()

	def get_wordcloud_format(inBuf):
		wStr = bStream()
		wStr.load_from_buffer(inBuf)
		wfm = WordcloudFormat()
		wfm.MaxSize = wStr.get_int32("MaxSize")
		wfm.PreferHorizontal = wStr.get_float("PreferHorizontal")
		wfm.WordDensity = wStr.get_float("WordDensity")
		return wfm

	def get_wordcloud_buffer(inObj):
		dStr = bStream()
		dStr.add_int32("MaxSize", inObj.MaxSize)
		dStr.add_float("PreferHorizontal", inObj.PreferHorizontal)
		dStr.add_float("WordDensity", inObj.WordDensity)
		return dStr.save_to_buffer()

	def get_venn_format(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cfm = VennFormat()
		cfm.PrimarySep = sStr.get_int32("PrimarySep")
		cfm.SecondarySep = sStr.get_int32("SecondarySep")
		cfm.LabelTypes = sStr.get_int32_vector("LabelTypes")
		cfm.Reverse = sStr.get_bool("Reverse")
		cfm.PrimaryFont = DH.get_font_options(sStr.get_stream("PrimaryFont"))		
		cfm.SecondaryFont = DH.get_font_options(sStr.get_stream("SecondaryFont"))
		cfm.FontAlignment = sStr.get_float_vector("FontAlignment")
		cfm.LabelShift = sStr.get_float("LabelShift")
		cfm.RadiusScale = sStr.get_float("RadiusScale")
		cfm.FillAlpha = sStr.get_float("FillAlpha")
		cfm.FlipVenn3 = sStr.get_bool("FlipVenn3")
		cfm.RotateIndex = sStr.get_int32("RotateIndex")
		return cfm

	def get_venn_buffer(inObj):
		dStr = bStream()
		dStr.add_int32("PrimarySep", inObj.PrimarySep)
		dStr.add_int32("SecondarySep", inObj.SecondarySep)
		dStr.add_int32_vector("LabelTypes", inObj.LabelTypes)
		dStr.add_bool("Reverse", inObj.Reverse)
		dStr.add_stream("PrimaryFont", DH.get_font_options_buf(inObj.PrimaryFont))
		dStr.add_stream("SecondaryFont", DH.get_font_options_buf(inObj.SecondaryFont))
		dStr.add_float_vector("FontAlignment", inObj.FontAlignment)
		dStr.add_float("LabelShift", inObj.LabelShift)
		dStr.add_float("RadiusScale", inObj.RadiusScale)
		dStr.add_float("FillAlpha", inObj.FillAlpha)
		dStr.add_bool("FlipVenn3", inObj.FlipVenn3)
		dStr.add_int32("RotateIndex", inObj.RotateIndex)
		return dStr.save_to_buffer()
		







