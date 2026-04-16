import struct
import json
import numpy as np
import pandas as pd
import io
import os
from row64tools.bytestream import bytestream as bStream
from row64tools.AxisOptions import AxisOptions
from row64tools.EquationOptions import EquationOptions
from row64tools.MarkerOptions import MarkerOptions
from row64tools.FontOptions import FontOptions
from row64tools.LineOptions import LineOptions
from row64tools.FillOptions import FillOptions

class DashHelper:
	
	def get_line_options(inBuf):
		lStr = bStream()
		lStr.load_from_buffer(inBuf)
		lo = LineOptions()
		lo.Color = lStr.get_int32("Color")
		lo.Size = lStr.get_float("Size")
		lo.Alpha = lStr.get_float("Alpha")
		return lo

	def get_line_options_buf(inObj):
		lStr = bStream()
		lStr.add_int32("Color", inObj.Color)
		lStr.add_float("Size", inObj.Size)
		lStr.add_float("Alpha", inObj.Alpha)
		return lStr.save_to_buffer()

	def get_fill_options(inBuf):
		fStr = bStream()
		fStr.load_from_buffer(inBuf)
		fo = FillOptions()
		fo.Color = fStr.get_int32("Color")
		fo.Alpha = fStr.get_float("Alpha")
		return fo

	def get_fill_options_buf(inObj):
		lStr = bStream()
		lStr.add_int32("Color", inObj.Color)
		lStr.add_float("Alpha", inObj.Alpha)
		return lStr.save_to_buffer()		

	def get_font_options(inBuf):
		fStr = bStream()
		fStr.load_from_buffer(inBuf)
		fo = FontOptions()
		fo.Font = fStr.get_int32("Font")
		fo.Size = fStr.get_float("Size")
		fo.Color = fStr.get_int32("Color")
		fo.Bold = fStr.get_bool("Bold")
		fo.Italic = fStr.get_bool("Italic")
		fo.Underline = fStr.get_bool("Underline")
		fo.Alpha = fStr.get_float("Alpha")
		return fo	

	def get_font_options_buf(inObj):
		lStr = bStream()
		lStr.add_int32("Font", inObj.Font)
		lStr.add_float("Size", inObj.Size)
		lStr.add_int32("Color", inObj.Color)
		lStr.add_bool("Bold", inObj.Bold)
		lStr.add_bool("Italic", inObj.Italic)
		lStr.add_bool("Underline", inObj.Underline)
		lStr.add_float("Alpha", inObj.Alpha)
		return lStr.save_to_buffer()	

	def get_marker_options(inBuf):
		fStr = bStream()
		fStr.load_from_buffer(inBuf)
		mo = MarkerOptions()
		mo.Shape = fStr.get_int32("Shape")
		mo.Size = fStr.get_float("Size")
		mo.Alpha = fStr.get_float("Alpha")
		mo.Color = fStr.get_int32("Color")
		mo.HasFill = fStr.get_bool("HasFill")
		return mo

	def get_marker_options_buf(inObj):
		lStr = bStream()
		lStr.add_int32("Shape", inObj.Shape)
		lStr.add_float("Size", inObj.Size)
		lStr.add_float("Alpha", inObj.Alpha)
		lStr.add_int32("Color", inObj.Color)
		lStr.add_bool("HasFill", inObj.HasFill)
		return lStr.save_to_buffer()	

	def get_equation_options(inBuf):
		fStr = bStream()
		fStr.load_from_buffer(inBuf)
		eo = EquationOptions()
		eo.RegressionL = DashHelper.get_line_options(fStr.get_stream("RegressionL"))
		eo.ShowEq = fStr.get_bool("ShowEq")
		eo.ShowR = fStr.get_bool("ShowR")
		eo.EquationF = DashHelper.get_font_options(fStr.get_stream("EquationF"))
		eo.ShowTrendline = fStr.get_bool("ShowTrendline")
		eo.Type = fStr.get_int32("Type")
		eo.Loc = fStr.get_float_vector("Loc")
		return eo

	def get_equation_options_buf(inObj):
		lStr = bStream()
		lStr.add_stream("RegressionL", DashHelper.get_line_options_buf(inObj.RegressionL))
		lStr.add_bool("ShowEq", inObj.ShowEq)
		lStr.add_bool("ShowR", inObj.ShowR)
		lStr.add_stream("EquationF", DashHelper.get_font_options_buf(inObj.EquationF))
		lStr.add_bool("ShowTrendline", inObj.ShowTrendline)
		lStr.add_int32("Type", inObj.Type)
		lStr.add_float_vector("Loc", inObj.Loc)
		return lStr.save_to_buffer()
		
	def get_grid_options(inBuf):
		fStr = bStream()
		fStr.load_from_buffer(inBuf)
		go = EquationOptions()
		go.Type = fStr.get_int32("Type")
		go.ShowMajor = fStr.get_bool("ShowMajor")
		go.ShowMinor = fStr.get_bool("ShowMinor")
		go.MajorUnit = fStr.get_double("MajorUnit")
		go.MinorUnit = fStr.get_double("MinorUnit")
		go.AutoMajor = fStr.get_bool("AutoMajor")
		go.AutoMinor = fStr.get_bool("AutoMinor")
		go.MinBound = fStr.get_double("MinBound")
		go.MaxBound = fStr.get_double("MaxBound")
		go.AutoMin = fStr.get_bool("AutoMin")
		go.AutoMax = fStr.get_bool("AutoMax")
		go.PreferZero = fStr.get_bool("PreferZero")
		go.MajorLine = DashHelper.get_line_options(fStr.get_stream("MajorLine"))
		go.Divisions = fStr.get_float("Divisions")
		go.GridBase = fStr.get_int8("GridBase")
		go.MajorBase = fStr.get_int8("MajorBase")
		go.MinorBase = fStr.get_int8("MinorBase")
		go.MajorStart = fStr.get_double("MajorStart")
		return go

	def get_grid_options_buf(inObj):
		lStr = bStream()
		lStr.add_int32("Type", inObj.Type)
		lStr.add_bool("ShowMajor", inObj.ShowMajor)
		lStr.add_bool("ShowMinor", inObj.ShowMinor)
		lStr.add_double("MajorUnit", inObj.MajorUnit)
		lStr.add_double("MinorUnit", inObj.MinorUnit)		
		lStr.add_bool("AutoMajor", inObj.AutoMajor)
		lStr.add_bool("AutoMinor", inObj.AutoMinor)
		lStr.add_double("MinBound", inObj.MinBound)
		lStr.add_double("MaxBound", inObj.MaxBound)
		lStr.add_bool("AutoMin", inObj.AutoMin)
		lStr.add_bool("AutoMax", inObj.AutoMax)
		lStr.add_bool("PreferZero", inObj.PreferZero)
		lStr.add_stream("MajorLine", DashHelper.get_line_options_buf(inObj.MajorLine))
		lStr.add_float("Divisions", inObj.Divisions)
		lStr.add_int8("GridBase", inObj.GridBase)
		lStr.add_int8("MajorBase", inObj.MajorBase)
		lStr.add_int8("MinorBase", inObj.MinorBase)
		lStr.add_double("MajorStart", inObj.MajorStart)		
		return lStr.save_to_buffer()

	def get_axis_options(inBuf):
		fStr = bStream()
		fStr.load_from_buffer(inBuf)
		ao = EquationOptions()
		ao.ShowAxis = fStr.get_bool("ShowAxis")
		ao.ShowMajorTicks = fStr.get_bool("ShowMajorTicks")
		ao.ShowMinorTicks = fStr.get_bool("ShowMinorTicks")
		ao.ShowEndTicks = fStr.get_bool("ShowEndTicks")
		ao.ShowEndLabels = fStr.get_bool("ShowEndLabels")
		ao.TickShift = fStr.get_float("TickShift")
		ao.TickSize = fStr.get_float("TickSize")
		ao.Line = DashHelper.get_line_options(fStr.get_stream("Line"))
		ao.ShowLabels = fStr.get_bool("ShowLabels")
		ao.LabelFont = DashHelper.get_font_options(fStr.get_stream("LabelFont"))
		ao.LabelShift = fStr.get_float("LabelShift")
		ao.LabelFormat = fStr.get_string("LabelFormat")
		ao.LabelAlign = fStr.get_float("LabelAlign")
		ao.LabelRotation = fStr.get_float("LabelRotation")
		ao.ShowTitle = fStr.get_bool("ShowTitle")
		ao.Title = fStr.get_string("Title")
		ao.TitleFont = DashHelper.get_font_options(fStr.get_stream("TitleFont"))
		ao.TitlePos = fStr.get_float_vector("TitlePos")
		return ao

	def get_axis_options_buf(inObj):
		lStr = bStream()
		lStr.add_bool("ShowAxis", inObj.ShowAxis)
		lStr.add_bool("ShowMajorTicks", inObj.ShowMajorTicks)
		lStr.add_bool("ShowMinorTicks", inObj.ShowMinorTicks)
		lStr.add_bool("ShowEndTicks", inObj.ShowEndTicks)
		lStr.add_bool("ShowEndLabels", inObj.ShowEndLabels)
		lStr.add_float("TickShift", inObj.TickShift)
		lStr.add_float("TickSize", inObj.TickSize)
		lStr.add_stream("Line", DashHelper.get_line_options_buf(inObj.Line))
		lStr.add_bool("ShowLabels", inObj.ShowLabels)
		lStr.add_stream("LabelFont", DashHelper.get_font_options_buf(inObj.LabelFont))
		lStr.add_float("LabelShift", inObj.LabelShift)
		lStr.add_string("LabelFormat", inObj.LabelFormat)
		lStr.add_float("LabelAlign", inObj.LabelAlign)
		lStr.add_float("LabelRotation", inObj.LabelRotation)
		lStr.add_bool("ShowTitle", inObj.ShowTitle)
		lStr.add_string("Title", inObj.Title)
		lStr.add_stream("TitleFont", DashHelper.get_font_options_buf(inObj.TitleFont))
		lStr.add_float_vector("TitlePos", inObj.TitlePos)
		return lStr.save_to_buffer()










