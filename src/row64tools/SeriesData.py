import struct
import json
import numpy as np
import pandas as pd
import io
import os
from row64tools.bytestream import bytestream as bStream
from row64tools.DashHelper import DashHelper as DH
from row64tools.VennData import VennData
from row64tools.BubblePlotData import BubblePlotData
from row64tools.ScatterPlotData import ScatterPlotData
from row64tools.LinePlotData import LinePlotData
from row64tools.PieChartData import PieChartData
from row64tools.BarChartData import BarChartData
from row64tools.GeoData import GeoData
from row64tools.ShapeLayerData import ShapeLayerData
from row64tools.ShapeAttributes import ShapeAttributes
from row64tools.CoordLayerData import CoordLayerData
from row64tools.CoordAttributes import CoordAttributes
from row64tools.WordcloudData import WordcloudData

class SeriesData: # also known as CData in the .dash format

	def __init__(self):
		self.Items = []

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value):
		setattr(self, key, value)
		
	def load(inType, inSeriesList, inKey):
		sList = []
		for i,buf in enumerate(inSeriesList):
			# print("-------------- Series:",i, ", type:", inType,",key: ",inKey,"--------------")
			if(inType =="Pie"):
				sList.append( SeriesData.get_pie(buf) )
			elif(inType =="LinePlot"):
				sList.append( SeriesData.get_lineplot(buf) )
			elif(inType =="Bar"):
				sList.append( SeriesData.get_bar(buf) )
			elif(inType =="ScatterPlot"):
				sList.append( SeriesData.get_scatter(buf) )
			elif(inType =="BubblePlot"):
				sList.append( SeriesData.get_bubbleplot(buf) )
			elif(inType =="Venn"):
				sList.append( SeriesData.get_venn(buf) )
			elif(inType =="Geo2D"):
				sList.append( SeriesData.get_geo(buf) )
			elif(inType =="WordCloud"):
				sList.append( SeriesData.get_wordcloud(buf) )
			elif(inType =="Trellis"):
				sList.append( SeriesData.get_trellis(buf) )

		return sList

	def get_buffer_list(inSeries, inType, inKey):
		bufList = []
		for i, series in enumerate(inSeries):
			# print("inType:",inType)
			# print("----------------------------- GET SERIES BUFFER: ", inType,", key: ",inKey,"------------------")
			if(inType =="Pie"):
				bufList.append( SeriesData.get_pie_buffer(series) )		
			elif(inType =="LinePlot"):
				bufList.append( SeriesData.get_lineplot_buffer(series,i) )
			elif(inType =="Bar"):
				bufList.append( SeriesData.get_bar_buffer(series) )
			elif(inType =="ScatterPlot"):
				bufList.append( SeriesData.get_scatter_buffer(series) )
			elif(inType =="BubblePlot"):
				bufList.append( SeriesData.get_bubble_buffer(series) )
			elif(inType =="Venn"):
				bufList.append( SeriesData.get_venn_buffer(series) )
			elif(inType =="Geo2D"):
				bufList.append( SeriesData.get_geo_buffer(series) )
			elif(inType =="WordCloud"):
				bufList.append( SeriesData.get_wordcloud_buffer(series) )
			elif(inType =="Trellis"):
				bufList.append( SeriesData.get_trellis_buffer(series) )

		return bufList

	def get_pie(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cda = PieChartData()
		cda.Name = sStr.get_string("Name")
		cda.Values = sStr.get_string("Values")
		cda.Labels = sStr.get_string("Labels")
		return cda

	def get_pie_buffer(inObj):
		dStr = bStream()
		dStr.add_string("Name", inObj.Name)
		dStr.add_string("Values", inObj.Values)
		dStr.add_string("Labels", inObj.Labels)
		return dStr.save_to_buffer()

	def get_bar(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cda = BarChartData()
		cda.Name = sStr.get_string("Name")
		cda.Values = sStr.get_string("Values")
		cda.Labels = sStr.get_string("Labels")
		cda.ColorMode = sStr.get_int32("ColorMode")
		cda.Colors = sStr.get_int32_vector("Colors")
		cda.Alphas = sStr.get_float_vector("Alphas")
		return cda

	def get_bar_buffer(inObj):
		dStr = bStream()
		dStr.add_string("Name", inObj.Name)
		dStr.add_string("Values", inObj.Values)
		dStr.add_string("Labels", inObj.Labels)
		dStr.add_int32("ColorMode", inObj.ColorMode)
		dStr.add_int32_vector("Colors", inObj.Colors)
		dStr.add_float_vector("Alphas", inObj.Alphas)
		return dStr.save_to_buffer()
		
	def get_lineplot(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cda = LinePlotData()
		cda.Name = sStr.get_string("Name")
		cda.Values = sStr.get_string("Values")
		cda.Labels = sStr.get_string("Labels")
		cda.Marker = DH.get_marker_options(sStr.get_stream("Marker"))
		cda.HasLine = sStr.get_bool("HasLine")
		cda.Line = DH.get_line_options(sStr.get_stream("Line"))
		cda.FillType = sStr.get_int32("FillType")
		cda.Fill = []
		fList = sStr.get_stream_vector("Fill")
		for i,buf in enumerate(fList):
			cda.Fill.append( DH.get_fill_options(buf) )
		cda.DR_Marker = DH.get_marker_options(sStr.get_stream("DR_Marker"))
		return cda

	def get_lineplot_buffer(inObj, inInd):
		dStr = bStream()
		dStr.add_string("Name", inObj.Name)
		dStr.add_string("Values", inObj.Values)
		dStr.add_string("Labels", inObj.Labels)
		dStr.add_stream("Marker", DH.get_marker_options_buf(inObj.Marker))
		dStr.add_bool("HasLine", inObj.HasLine)
		dStr.add_stream("Line", DH.get_line_options_buf(inObj.Line))
		dStr.add_int32("FillType", inObj.FillType)
		fillStream = []
		for i,fItem in enumerate(inObj.Fill):
			fillStream.append(DH.get_fill_options_buf(fItem))
		dStr.add_stream_vector("Fill", fillStream)
		dStr.add_stream("DR_Marker", DH.get_marker_options_buf(inObj.DR_Marker))

		lpBuf = dStr.save_to_buffer()

		# print("---------------- CDATA FOR LINEPLOT OUT [",inInd,"]--------------------")
		# bs = bStream()
		# bs.load_from_buffer(lpBuf)
		# bs.log_details()
		# print("-----------------------------------------------------------")
		
		return lpBuf

	def get_scatter(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cda = PieChartData()
		cda.Name = sStr.get_string("Name")
		cda.Labels = sStr.get_string("Labels")
		cda.XValues = sStr.get_string("XValues")
		cda.YValues = sStr.get_string("YValues")		
		cda.ZValues = sStr.get_string("ZValues")
		cda.EQOptions = DH.get_equation_options(sStr.get_stream("EQOptions"))
		cda.Marker = DH.get_marker_options(sStr.get_stream("Marker"))
		cda.HasLine = sStr.get_bool("HasLine")
		cda.FillType = sStr.get_int32("FillType")
		cda.Fill = []
		fList = sStr.get_stream_vector("Fill")
		for i,buf in enumerate(fList):cda.Fill.append( DH.get_fill_options(buf) )
		return cda

	def get_scatter_buffer(inObj):
		dStr = bStream()
		dStr.add_string("Name", inObj.Name)
		dStr.add_string("Labels", inObj.Labels)
		dStr.add_string("XValues", inObj.XValues)
		dStr.add_string("YValues", inObj.YValues)
		dStr.add_string("ZValues", inObj.ZValues)
		dStr.add_stream("EQOptions", DH.get_equation_options_buf(inObj.EQOptions))
		dStr.add_stream("Marker", DH.get_marker_options_buf(inObj.Marker))
		dStr.add_bool("HasLine", inObj.HasLine)
		dStr.add_int32("FillType", inObj.FillType)
		fillStream = []
		for fItem in inObj.Fill:fillStream.append(DH.get_fill_options_buf(fItem))
		dStr.add_stream_vector("Fill", fillStream)
		return dStr.save_to_buffer()

	def get_bubbleplot(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cda = PieChartData()
		cda.Name = sStr.get_string("Name")
		cda.Labels = sStr.get_string("Labels")
		cda.XValues = sStr.get_string("XValues")
		cda.YValues = sStr.get_string("YValues")
		cda.ZValues = sStr.get_string("ZValues")
		cda.EQOptions = DH.get_equation_options(sStr.get_stream("EQOptions"))
		cda.Marker = DH.get_marker_options(sStr.get_stream("Marker"))
		cda.ColorTheme = sStr.get_int32_vector("ColorTheme")
		return cda

	def get_bubble_buffer(inObj):
		dStr = bStream()
		dStr.add_string("Name", inObj.Name)
		dStr.add_string("Labels", inObj.Labels)
		dStr.add_string("XValues", inObj.XValues)
		dStr.add_string("YValues", inObj.YValues)
		dStr.add_string("ZValues", inObj.ZValues)
		dStr.add_stream("EQOptions", DH.get_equation_options_buf(inObj.EQOptions))
		dStr.add_stream("Marker", DH.get_marker_options_buf(inObj.Marker))
		dStr.add_int32_vector("ColorTheme", inObj.ColorTheme)
		return dStr.save_to_buffer()
	
	def get_trellis(inBuf):
		tStr = bStream()
		tStr.load_from_buffer(inBuf)
		td = TrellisData()
		td.Name = tStr.get_string("Name")
		td.Labels = tStr.get_string("Labels")
		td.XValues = tStr.get_string("XValues")
		td.YValues = tStr.get_string("YValues")
		td.ZValues = tStr.get_string("ZValues")
		td.IValues = tStr.get_string("IValues")
		td.JValues = tStr.get_string("JValues")
		if tStr.key_exists("EQOptions"):
			td.EQOptions = DH.get_equation_options(tStr.get_stream("EQOptions"))
		td.ColorMode = tStr.get_int32("ColorMode")
		td.Color = tStr.get_int32_vector("Color")
		if tStr.key_exists("Marker"):
			td.Marker = DH.get_marker_options(tStr.get_stream("Marker"))
		td.HasLine = tStr.get_bool("HasLine")
		if tStr.key_exists("Line"):
			td.Line = DH.get_line_options(tStr.get_stream("Line"))
		td.FillType = tStr.get_int32("FillType")
		if tStr.key_exists("Fill"):
			td.Fill = []
			fList = tStr.get_stream_vector("Fill")
			for i,buf in enumerate(fList):td.Fill.append( DH.get_fill_options(buf) )
		return td

	def get_trellis_buffer(inObj):
		tStr = bStream()
		tStr.add_string("Name", inObj.Name)
		tStr.add_string("Labels", inObj.Labels)
		tStr.add_string("XValues", inObj.XValues)
		tStr.add_string("YValues", inObj.YValues)
		tStr.add_string("ZValues", inObj.ZValues)
		tStr.add_string("IValues", inObj.IValues)
		tStr.add_string("JValues", inObj.JValues)
		if inObj.EQOptions != None:
			tStr.add_stream("EQOptions", DH.get_equation_options_buf(inObj.EQOptions))
		tStr.add_int32("ColorMode", inObj.ColorMode)
		tStr.add_int32_vector("Color", inObj.Color)
		if inObj.Marker != None:
			tStr.add_stream("Marker", DH.get_marker_options_buf(inObj.Marker))
		tStr.add_bool("HasLine", inObj.HasLine)
		if inObj.Line != None:
			tStr.add_stream("Line", DH.get_line_options_buf(inObj.Line))
		tStr.add_int32("FillType", inObj.FillType)
		if inObj.Fill != None:
			fillStream = []
			for i,fItem in enumerate(inObj.Fill):
				fillStream.append(DH.get_fill_options_buf(fItem))
			tStr.add_stream_vector("Fill", fillStream)
		return tStr.save_to_buffer()
	
	def get_wordcloud(inBuf):
		wStr = bStream()
		wStr.load_from_buffer(inBuf)
		wcd = WordcloudData()
		wcd.Words = wStr.get_string("Words")
		wcd.Freqs = wStr.get_string("Freqs")
		wcd.Sents = wStr.get_string("Sents")
		return wcd

	def get_wordcloud_buffer(inObj):
		dStr = bStream()
		dStr.add_string("Words", inObj.Words)
		dStr.add_string("Freqs", inObj.Freqs)
		dStr.add_string("Sents", inObj.Sents)
		return dStr.save_to_buffer()

	def get_venn(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		cda = PieChartData()
		cda.Name = sStr.get_string("Name")
		cda.Values = sStr.get_string("Values")
		cda.Labels = sStr.get_string("Labels")
		return cda

	# Name = "" # Name of the series
	# Values = ["","",""] # Cell reference of the values in the series (list or cell reference like Excel)
	# Labels = ""  # Lables on the series (list or cell reference like Excel)
	

	def get_venn_buffer(inObj):
		dStr = bStream()
		dStr.add_string("Name", inObj.Name)
		dStr.add_string_vector("Values", inObj.Values)
		dStr.add_string("Labels", inObj.Labels)
		return dStr.save_to_buffer()

	def get_shape_layer(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		sld = ShapeLayerData()
		sld.Locations = sStr.get_string("Locations")
		sld.ColorValues = sStr.get_string("ColorValues")
		sld.TimeValues = sStr.get_string("TimeValues")
		sld.FeatureIDs = sStr.get_string_vector("FeatureIDs")
		sld.FeatureListSelectedIndex = sStr.get_int32("FeatureListSelectedIndex")
		sld.ShapeColor = sStr.get_int32("ShapeColor")
		sld.ShapeAlpha = sStr.get_float("ShapeAlpha")
		sld.LineSize = sStr.get_float("LineSize")
		sld.Visible = sStr.get_uint8("Visible")
		# sld.AttrLookup = sStr.get_string_vector("AttrLookup") - Studio Only
		return sld

	def get_coord_att(inBuf):
		aStr = bStream()
		aStr.load_from_buffer(inBuf)
		cad = CoordAttributes()
		cad.Mode = aStr.get_int32("Mode")
		cad.Radius = aStr.get_float("Radius")
		cad.Alpha = aStr.get_float("Alpha")
		cad.SpriteColor = aStr.get_int32("SpriteColor")
		cad.BubbleRingColor = aStr.get_int32("BubbleRingColor")
		cad.BubbleRingSize = aStr.get_float("BubbleRingSize")
		cad.BubbleColorPalette = aStr.get_int32_vector("BubbleColorPalette")
		cad.SpritePath = aStr.get_string("SpritePath")
		return cad

	def get_coord_layer(inBuf):
		cStr = bStream()
		cStr.load_from_buffer(inBuf)
		cld = CoordLayerData()
		cld.Name = cStr.get_string("Name")
		cld.Lat = cStr.get_string("Lat")
		cld.Lon = cStr.get_string("Lon")
		cld.Radius = cStr.get_string("Radius")
		cld.Color = cStr.get_string("Color")
		cld.Visible = cStr.get_uint8("Visible")
		if cStr.key_exists("Attributes"):
			cld.Attributes = SeriesData.get_coord_att(cStr.get_stream("Attributes"))
		return cld
	
	def get_shape_att(inBuf):
		aStr = bStream()
		aStr.load_from_buffer(inBuf)
		sad = ShapeAttributes()
		sad.TimeSeriesAccum = aStr.get_uint8("TimeSeriesAccum")
		sad.AntiAliasing = aStr.get_uint8("AntiAliasing")
		return sad

	def get_geo(inBuf):
		sStr = bStream()
		sStr.load_from_buffer(inBuf)
		gda = GeoData()
		gda.ProjectionMode = sStr.get_int32("ProjectionMode")
		gda.ProjectionData = sStr.get_double_vector("ProjectionData")
		gda.ShapeLayerData = []
		sList = sStr.get_stream_vector("ShapeLayerData")
		for i,buf in enumerate(sList):
			gda.ShapeLayerData.append( SeriesData.get_shape_layer(buf))
		gda.CoordLayerData = []
		cList = sStr.get_stream_vector("CoordLayerData")
		for i,buf in enumerate(cList):
			gda.CoordLayerData.append( SeriesData.get_coord_layer(buf))
		if sStr.key_exists("ShapeAttributes"):
			gda.ShapeAttributes = SeriesData.get_shape_att(sStr.get_stream("ShapeAttributes"))
		gda.ViewNames = sStr.get_string_vector("ViewNames")
		gda.ViewRects = sStr.get_double_vector2d("ViewRects")
		gda.ShowBaseMap =  sStr.get_bool("ShowBaseMap")
		return gda

	def get_shape_layer_buf(inLDat):

		sStr = bStream()
		sStr.add_string("Locations", inLDat.Locations)
		sStr.add_string("ColorValues", inLDat.ColorValues)
		sStr.add_string("TimeValues", inLDat.TimeValues)
		sStr.add_string_vector("FeatureIDs", inLDat.FeatureIDs)
		sStr.add_int32("FeatureListSelectedIndex", inLDat.FeatureListSelectedIndex)		
		sStr.add_int32("ShapeColor", inLDat.ShapeColor)	
		sStr.add_float("ShapeAlpha", inLDat.ShapeAlpha)	
		sStr.add_float("LineSize", inLDat.LineSize)	
		sStr.add_int8("Visible", inLDat.Visible)	
		# sStr.add_string_vector("AttrLookup", inLDat.AttrLookup)
		return sStr.save_to_buffer()

	def get_coord_att_buf(inSAtt):
		aStr = bStream()
		aStr.add_int32("Mode", inSAtt.Mode)
		aStr.add_float("Radius", inSAtt.Radius)
		aStr.add_float("Alpha", inSAtt.Alpha)
		aStr.add_int32("SpriteColor", inSAtt.SpriteColor)
		aStr.add_int32("BubbleRingColor", inSAtt.BubbleRingColor)
		aStr.add_float("BubbleRingSize", inSAtt.BubbleRingSize)
		aStr.add_int32_vector("BubbleColorPalette", inSAtt.BubbleColorPalette)
		aStr.add_string("SpritePath", inSAtt.SpritePath)
		return aStr.save_to_buffer()
		
	def get_coord_layer_buf(inCDat):
		cStr = bStream()
		cStr.add_string("Name", inCDat.Name)
		cStr.add_string("Lat", inCDat.Lat)
		cStr.add_string("Lon", inCDat.Lon)
		cStr.add_string("Radius", inCDat.Radius)
		cStr.add_string("Color", inCDat.Color)
		cStr.add_int8("Visible", inCDat.Visible)
		if inCDat.Attributes is not None:
			cStr.add_stream("Attributes",SeriesData.get_coord_att_buf(inCDat.Attributes))
		return cStr.save_to_buffer()

	def get_shape_att_buf(inSAtt):
		aStr = bStream()
		aStr.add_int8("TimeSeriesAccum", inSAtt.TimeSeriesAccum)
		aStr.add_int8("AntiAliasing", inSAtt.AntiAliasing)
		return aStr.save_to_buffer()

	def get_geo_buffer(inObj):
		gStr = bStream()
		gStr.add_int32("ProjectionMode", inObj.ProjectionMode)
		gStr.add_double_vector("ProjectionData", inObj.ProjectionData)
		shapeStrList = []
		for sDat in inObj.ShapeLayerData:
			shapeStrList.append(SeriesData.get_shape_layer_buf(sDat))
		gStr.add_stream_vector("ShapeLayerData",shapeStrList)
		coordStrList = []
		for cDat in inObj.CoordLayerData:
			coordStrList.append(SeriesData.get_coord_layer_buf(cDat))
		gStr.add_stream_vector("CoordLayerData",coordStrList)
		if inObj.ShapeAttributes is not None:
			gStr.add_stream("ShapeAttributes",SeriesData.get_shape_att_buf(inObj.ShapeAttributes))
		gStr.add_string_vector("ViewNames", inObj.ViewNames)
		gStr.add_double_vector2d("ViewRects", inObj.ViewRects)
		gStr.add_bool("ShowBaseMap", inObj.ShowBaseMap)
		return gStr.save_to_buffer()

	











