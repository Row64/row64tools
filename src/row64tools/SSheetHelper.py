import struct
import io
import os

# Converts A1 column letters to a 1-based column index (i.e., A --> 1)
def a1_col_to_int(inCol):
	if inCol=="":return 0
	col = inCol.upper()
	parts = col.split(":")
	ccol = parts[0]
	retVal = 0 
	for i in range(len(ccol)-1,-1,-1):retVal += (ord(ccol[i])-64)*int(pow(26,len(ccol)-(i+1)))
	return int(retVal)

# Converts A1 column letters to a 0-based column index (i.e., A --> 0)
def a1_col_to_intz(inCol):
	if inCol=="":return 0
	col = inCol.upper()
	parts = col.split(":")
	ccol = parts[0]
	retVal = 0 
	for i in range(len(ccol)-1,-1,-1):retVal += (ord(ccol[i])-64)*int(pow(26,len(ccol)-(i+1)))
	return int(retVal) - 1
