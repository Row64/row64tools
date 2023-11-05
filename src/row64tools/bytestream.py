import struct
import json
import numpy as np
import io
import os
import zlib

i64step = 8
i32step = 4
i16step = 2
i8step = 1

class bytestream:

    def __init__(self):
        #------------------------- SAVE DATA ---------------------
        self.bufList = [] # list of entry buffers being added with Add methods, in prep for Save where they are combined
        self.lenList = [] # lengths of each entry buffer, aligned with bufList
        
        #------------------------- READ DATA ---------------------
        self.B = bytearray() # Buffer storage, filled after Read
        self.PL = [] # Position List of entries within buffer
        self.nb = 0 # number of entries in the Bytestream
        self.keys = [] # String list of keys
        self.EL = [] # Entry Lookup: [[50,70],[90,150]] # buffer entry start/end pos.  Does not include Type/KeySize/Key
        self.TL = [] # Type List.  Int code for each type of entry

    ######################################### INPUT / OUTPUT ########################################
    
    def read_compressed(self, inPath):
        bufstream = io.open(inPath, 'rb')
        rawbuf = bufstream.read()
        ucSize = struct.unpack('Q', rawbuf[0:8])[0]
        compBuf = rawbuf[8:len(rawbuf)]
        self.B = zlib.decompress(compBuf)
        b=0 # buffer index currently being read
        self.nb = struct.unpack('Q', self.B[b:b+i64step])[0];b+=i64step
        self.PL = []
        for j in range(self.nb):
            self.PL.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        self.PL.append(struct.unpack('Q', self.B[b:b+i64step])[0]) # file end pos
        self.keys = []
        for ei in range(self.nb):
            # print("-----------------------",self.PL[ei], " to ",self.PL[ei+1],"---------------------------------")      
            b=self.PL[ei]
            self.TL.append(struct.unpack('B', self.B[b:b+i8step])[0]) # entry type
            b+=i8step
            keySize = struct.unpack('Q', self.B[b:b+i64step])[0]
            b+=i64step
            nextB = b+i8step*keySize
            keyBytes = self.B[b:nextB]
            key = str(keyBytes, 'ascii')
            self.keys.append(key)
            self.EL.append([nextB,self.PL[ei+1]])      

    def read(self, inPath):
        bufstream = io.open(inPath, 'rb')
        self.B = bufstream.read()
        b=0 # buffer index currently being read
        self.nb = struct.unpack('Q', self.B[b:b+i64step])[0];b+=i64step
        self.PL = []
        for j in range(self.nb):
            self.PL.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        self.PL.append(struct.unpack('Q', self.B[b:b+i64step])[0]) # file end pos
        self.keys = []
        for ei in range(self.nb):
            # print("-----------------------",self.PL[ei], " to ",self.PL[ei+1],"---------------------------------")      
            b=self.PL[ei]
            self.TL.append(struct.unpack('B', self.B[b:b+i8step])[0]) # entry type
            b+=i8step
            keySize = struct.unpack('Q', self.B[b:b+i64step])[0]
            b+=i64step
            nextB = b+i8step*keySize
            keyBytes = self.B[b:nextB]
            key = str(keyBytes, 'ascii')
            self.keys.append(key)
            self.EL.append([nextB,self.PL[ei+1]])
    
    def load_compressed_buffer(self, inBuf):
        ucSize = struct.unpack('Q', inBuf[0:8])[0]
        compBuf = inBuf[8:len(inBuf)]
        self.B = zlib.decompress(compBuf)
        b=0 # buffer index currently being read
        self.nb = struct.unpack('Q', self.B[b:b+i64step])[0];b+=i64step
        self.PL = []
        for j in range(self.nb):
            itemLen = struct.unpack('Q', self.B[b:b+i64step])[0]
            self.PL.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        self.PL.append(struct.unpack('Q', self.B[b:b+i64step])[0]) # file end pos
        self.keys = []
        for ei in range(self.nb):
            # print("-----------------------",self.PL[ei], " to ",self.PL[ei+1],"---------------------------------")      
            b=self.PL[ei]
            self.TL.append(struct.unpack('B', self.B[b:b+i8step])[0]) # entry type
            b+=i8step
            keySize = struct.unpack('Q', self.B[b:b+i64step])[0]
            b+=i64step
            nextB = b+i8step*keySize
            keyBytes = self.B[b:nextB]
            key = str(keyBytes, 'ascii')
            self.keys.append(key)
            self.EL.append([nextB,self.PL[ei+1]])

    def load_from_buffer(self, inBuf):
        self.B = inBuf
        b=0 # buffer index currently being read
        self.nb = struct.unpack('Q', self.B[b:b+i64step])[0];b+=i64step
        self.PL = []
        for j in range(self.nb):
            itemLen = struct.unpack('Q', self.B[b:b+i64step])[0]
            self.PL.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        self.PL.append(struct.unpack('Q', self.B[b:b+i64step])[0]) # file end pos
        self.keys = []
        for ei in range(self.nb):
            # print("-----------------------",self.PL[ei], " to ",self.PL[ei+1],"---------------------------------")      
            b=self.PL[ei]
            self.TL.append(struct.unpack('B', self.B[b:b+i8step])[0]) # entry type
            b+=i8step
            keySize = struct.unpack('Q', self.B[b:b+i64step])[0]
            b+=i64step
            nextB = b+i8step*keySize
            keyBytes = self.B[b:nextB]
            key = str(keyBytes, 'ascii')
            self.keys.append(key)
            self.EL.append([nextB,self.PL[ei+1]])

    def save(self, inPath):
        bLen = len(self.bufList)
        bList = bytearray(struct.pack('Q', bLen))
        i = i64step + i64step*(bLen+1)
        for b in range(bLen):
            bList += bytearray(struct.pack('Q', i))
            i+=len(self.bufList[b])
        bList += bytearray(struct.pack('Q', i))
        for buf in self.bufList:bList += buf
        f = open(inPath, 'wb')
        f.write(bList)
        f.close()

    def save_compressed(self, inPath):
        bLen = len(self.bufList)
        bList = bytearray(struct.pack('Q', bLen))
        i = i64step + i64step*(bLen+1)
        for b in range(bLen):
            bList += bytearray(struct.pack('Q', i))
            i+=len(self.bufList[b])
        bList += bytearray(struct.pack('Q', i))
        for buf in self.bufList:bList += buf
        # uncompressed buffer size is first 8 bytes
        # then followed by the compressed buffer
        # this allows exact memory allocation on future decompress
        ucSize = len(bList) 
        firstByte = bytearray(struct.pack('Q', ucSize))
        compBuf = firstByte + zlib.compress(bList)
        f = open(inPath, 'wb')
        f.write(compBuf)
        f.close()
        
    def save_to_buffer(self):
        bLen = len(self.bufList)
        bList = bytearray(struct.pack('Q', bLen))
        i = i64step + i64step*(bLen+1)
        for b in range(bLen):
            bList += bytearray(struct.pack('Q', i))
            i+=len(self.bufList[b])
        bList += bytearray(struct.pack('Q', i))
        for buf in self.bufList:bList += buf
        return bList

    def save_compressed_buffer(self):
        bLen = len(self.bufList)
        bList = bytearray(struct.pack('Q', bLen))
        i = i64step + i64step*(bLen+1)
        for b in range(bLen):
            bList += bytearray(struct.pack('Q', i))
            i+=len(self.bufList[b])
        bList += bytearray(struct.pack('Q', i))
        for buf in self.bufList:bList += buf
        ucSize = len(bList)
        firstByte = bytearray(struct.pack('Q', ucSize))
        compBuf = firstByte + zlib.compress(bList)
        return compBuf


    ###################################### LOGGING #####################################
    
    def log_info(self):
        for i in range(self.nb):
            eType = self.TL[i];
            dType = bytestream_types[eType]
            if(eType > 11 and eType <= 28): # 1D _vector
                b = self.EL[i][0]
                lenStr = str(struct.unpack('Q', self.B[b:b+i64step])[0])
                print("Key:",self.keys[i] + ",","Type:",dType+",","Len:",lenStr)
            elif(eType >= 35 and eType <= 45): # 2D _vector
                b = self.EL[i][0]
                len1 = str(struct.unpack('Q', self.B[b:b+i64step])[0])
                b+=i64step
                len2 = str(struct.unpack('Q', self.B[b:b+i64step])[0])
                print("Key:",self.keys[i] + ",","Type:",dType+",","Len:["+str(len1)+","+str(len2)+"]")
            elif(eType >= 52 and eType <= 53): # buffer or stream
                lenStr = str(self.EL[i][1]-self.EL[i][0])
                print("Key:",self.keys[i] + ",","Type:",dType+",","Bytes:",lenStr)
            elif(eType ==54): # _vector of Streams
                b = self.EL[i][0]
                lenStr = str(struct.unpack('Q', self.B[b:b+i64step])[0])
                print("Key:",self.keys[i] + ",","Type:",dType+",","Len:",lenStr)
            else:print("Key:",self.keys[i] + ",","Type:",dType)

    def log_details(self):
        for i in range(self.nb):
            eType = self.TL[i];
            dType = bytestream_types[eType]
            byteLen = str(self.EL[i][1]-self.EL[i][0])
            if(eType > 11 and eType <= 28): # 1D _vector
                b = self.EL[i][0]
                lenStr = str(struct.unpack('Q', self.B[b:b+i64step])[0])
                print("Key:",self.keys[i] + ",","Type:",dType+",","Len:",lenStr,"Bytes:",byteLen)
            elif(eType >= 35 and eType <= 45): # 2D _vector
                b = self.EL[i][0]
                len1 = str(struct.unpack('Q', self.B[b:b+i64step])[0])
                b+=i64step
                len2 = str(struct.unpack('Q', self.B[b:b+i64step])[0])
                print("Key:",self.keys[i] + ",","Type:",dType+",","Len:["+str(len1)+","+str(len2)+"]","Bytes:",byteLen)
            elif(eType >= 52 and eType <= 53): # buffer or stream
                print("Key:",self.keys[i] + ",","Type:",dType+",","Bytes:",byteLen)
            elif(eType ==54): # _vector of Streams
                b = self.EL[i][0]
                lenStr = str(struct.unpack('Q', self.B[b:b+i64step])[0])
                print("Key:",self.keys[i] + ",","Type:",dType+",","Len:",lenStr,"Bytes:",byteLen)
            else:print("Key:",self.keys[i] + ",","Type:",dType,"Bytes:",byteLen)

    def log_record(self, inKey):
        # dType = bytestream_types[t]
        pStr = self.Get(inKey)
        print(pStr)

    #################################### GET OBJECT TREE ##################################
    # these versions are a whole structure at once with Python data structures like JSON & Numpy
    # it replicates all data into this new structure so if you need part of the data, use the functions 
    # to grab only what you need
    # this is not a good way to work with buffers, since they need to be decoded into latin-1 to conform to JSON
    # if you ware working with buffers load the entity directly with get_buffer() or related methods
    
    def get_json(self):
        jo = {}
        for i in range(self.nb):
            val = self.Get(self.keys[i])
            if(self.TL[i] >= 50):
                jsonBytes = val.decode('latin-1').replace("'", '"')
                jo[self.keys[i]] = jsonBytes
            else:jo[self.keys[i]] = val
        jStr = json.dumps(jo)
        return jStr
    
    def get_typed_json(self):
        jo = {}
        for i in range(self.nb):
            val = self.Get(self.keys[i])
            tjObj = {"Type":bytestream_types[self.TL[i]]}
            if(self.TL[i] >= 50):
                jsonBytes = val.decode('latin-1').replace("'", '"')
                tjObj["Val"] = jsonBytes
            else:tjObj["Val"] = val
            jo[self.keys[i]] = tjObj
        jStr = json.dumps(jo)
        return jStr
    
    def get_obj(self):
        jo = {}
        for i in range(self.nb):
            val = self.Get(self.keys[i])
            if(self.TL[i] >= 50):
                jsonBytes = val.decode('latin-1').replace("'", '"')
                jo[self.keys[i]] = jsonBytes
            else:jo[self.keys[i]] = val
        return jo

    def get_obj_np(self): # Same as get_obj, but Numpy arrays for 1D _vectors
        jo = {}
        for i in range(self.nb):
            val = self.get_np(self.keys[i])
            if(self.TL[i] >= 50):
                jsonBytes = val.decode('latin-1').replace("'", '"')
                jo[self.keys[i]] = jsonBytes
            else:jo[self.keys[i]] = val
        return jo

    ######################################### GENERIC GET ######################################
    def get_key_ind(self,inKey,inDesc,inType):
        kInd = -1
        for ki in range(self.nb):
            if self.keys[ki] == inKey:
                kInd = ki
                break
        if(kInd == -1):raise Exception (inDesc + " - Could not located key: " + inKey)
        if(inType==-1):return kInd
        if(self.TL[kInd] != inType):
            print(" Problem with key: ", inKey)
            print(" keyType: ", bytestream_types[self.TL[kInd]], " != ", bytestream_types[inType])
            raise Exception (inDesc + " - requested entry of type: " + bytestream_types[inType])
        return kInd


    def key_exists(self, inKey):
        for ki in range(self.nb):
            if self.keys[ki] == inKey:
                return True
        return False

    def get_type(self, inKey):
        kInd = self.get_key_ind(inKey,"LogRecord",-1)
        if(kInd==-1):return
        return bytestream_types[self.TL[kInd]]

    # would never do this in C++, but the way pyObjects work you can get() and return many different types
    def get(self, inKey):
        kInd = self.get_key_ind(inKey,"log_record",-1)
        if(kInd==-1):return
        t = self.TL[kInd];
        gDat=""
        if(t==1):gDat=self.get_int8(inKey) # ----- single values 
        elif(t==2):gDat=self.get_uint8(inKey)
        elif(t==3):gDat=self.get_int16(inKey)
        elif(t==4):gDat=self.get_uint16(inKey)
        elif(t==5):gDat=self.get_int32(inKey)
        elif(t==6):gDat=self.get_uint32(inKey)
        elif(t==7):gDat=self.get_int64(inKey)
        elif(t==8):gDat=self.get_uint64(inKey)
        elif(t==9):gDat=self.get_float(inKey)
        elif(t==10):gDat=self.get_double(inKey)        
        elif(t==11):gDat=self.get_string(inKey)
        elif(t==18):gDat=self.get_int8_vector(inKey) # ----- 1D _vectors 
        elif(t==19):gDat=self.get_uint8_vector(inKey)
        elif(t==20):gDat=self.get_int16_vector(inKey)
        elif(t==21):gDat=self.get_uint16_vector(inKey)
        elif(t==22):gDat=self.get_int32_vector(inKey)
        elif(t==23):gDat=self.get_uint32_vector(inKey)
        elif(t==24):gDat=self.get_int64_vector(inKey)
        elif(t==25):gDat=self.get_uint64_vector(inKey)
        elif(t==26):gDat=self.get_float_vector(inKey)
        elif(t==27):gDat=self.get_double_vector(inKey)
        elif(t==28):gDat=self.get_string_vector(inKey)
        elif(t==35):gDat=self.get_int8_vector2d(inKey) # ----- 2D _vectors 
        elif(t==36):gDat=self.get_uint8_vector2d(inKey)
        elif(t==37):gDat=self.get_int16_vector2d(inKey)
        elif(t==38):gDat=self.get_uint16_vector2d(inKey)
        elif(t==39):gDat=self.get_int32_vector2d(inKey)
        elif(t==40):gDat=self.get_uint32_vector2d(inKey)
        elif(t==41):gDat=self.get_int64_vector2d(inKey)
        elif(t==42):gDat=self.get_uint64_vector2d(inKey)
        elif(t==43):gDat=self.get_float_vector2d(inKey)
        elif(t==44):gDat=self.get_double_vector2d(inKey)
        elif(t==45):gDat=self.get_string_vector2d(inKey)
        elif(t==52):gDat=self.get_buffer(inKey) # ----- Buffer 
        elif(t==53):gDat=self.get_stream(inKey)
        elif(t==54):gDat=self.get_stream_vector(inKey)
        return gDat

    # same as Get but returns Numpy Arrays for 1D _vectors
    def get_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_np",-1)
        if(kInd==-1):return
        t = self.TL[kInd];
        gDat=""
        if(t==1):gDat=self.get_int8(inKey) # ----- single values 
        elif(t==2):gDat=self.get_uint8(inKey)
        elif(t==3):gDat=self.get_int16(inKey)
        elif(t==4):gDat=self.get_uint16(inKey)
        elif(t==5):gDat=self.get_int32(inKey)
        elif(t==6):gDat=self.get_uint32(inKey)
        elif(t==7):gDat=self.get_int64(inKey)
        elif(t==8):gDat=self.get_uint64(inKey)
        elif(t==9):gDat=self.get_float(inKey)
        elif(t==10):gDat=self.get_double(inKey)        
        elif(t==11):gDat=self.get_string(inKey)
        elif(t==18):gDat=self.get_int8_vector_np(inKey) # ----- 1D _vectors 
        elif(t==19):gDat=self.get_uint8_vector_np(inKey)
        elif(t==20):gDat=self.get_int16_vector_np(inKey)
        elif(t==21):gDat=self.get_uint16_vector_np(inKey)
        elif(t==22):gDat=self.get_int32_vector_np(inKey)
        elif(t==23):gDat=self.get_uint32_vector_np(inKey)
        elif(t==24):gDat=self.get_int64_vector_np(inKey)
        elif(t==25):gDat=self.get_uint64_vector_np(inKey)
        elif(t==26):gDat=self.get_float_vector_np(inKey)
        elif(t==27):gDat=self.get_double_vector_np(inKey)
        elif(t==28):gDat=self.get_string_vector_np(inKey)
        elif(t==35):gDat=self.get_int8_vector2d(inKey) # ----- 2D _vectors 
        elif(t==36):gDat=self.get_uint8_vector2d(inKey)
        elif(t==37):gDat=self.get_int16_vector2d(inKey)
        elif(t==38):gDat=self.get_uint16_vector2d(inKey)
        elif(t==39):gDat=self.get_int32_vector2d(inKey)
        elif(t==40):gDat=self.get_uint32_vector2d(inKey)
        elif(t==41):gDat=self.get_int64_vector2d(inKey)
        elif(t==42):gDat=self.get_uint64_vector2d(inKey)
        elif(t==43):gDat=self.get_float_vector2d(inKey)
        elif(t==44):gDat=self.get_double_vector2d(inKey)
        elif(t==45):gDat=self.get_string_vector2d(inKey)
        elif(t==52):gDat=self.get_buffer(inKey) # ----- Buffer 
        elif(t==53):gDat=self.get_stream(inKey)
        elif(t==54):gDat=self.get_stream_vector(inKey)
        return gDat

    ###################################### GET SINGLE VALUE #####################################

    def get_bool(self, inKey):
        kInd = self.get_key_ind(inKey,"get_bool",2)
        if(kInd==-1):return
        iVal = struct.unpack('b', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i8step])[0]
        if(iVal==1):return True
        else: return False
        
    def get_char(self, inKey):
        kInd = self.get_key_ind(inKey,"get_char",1)
        if(kInd==-1):return
        return chr(struct.unpack('b', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i8step])[0])       
    
    def get_int8(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int8",1)
        if(kInd==-1):return
        return struct.unpack('b', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i8step])[0]

    def get_uint8(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint8",2)
        if(kInd==-1):return
        return struct.unpack('B', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i8step])[0]

    def get_int16(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int16",3)
        if(kInd==-1):return
        return struct.unpack('h', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i16step])[0]

    def get_uint16(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint16",4)
        if(kInd==-1):return
        return struct.unpack('H', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i16step])[0]

    def get_int32(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int32",5)
        if(kInd==-1):return
        return struct.unpack('i', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i32step])[0]

    def get_uint32(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint32",6)
        if(kInd==-1):return
        return struct.unpack('I', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i32step])[0]

    def get_int64(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int64",7)
        if(kInd==-1):return
        return struct.unpack('q', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i64step])[0]

    def get_uint64(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint64",8)
        if(kInd==-1):return
        return struct.unpack('Q', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i64step])[0]   

    def get_float(self, inKey):
        kInd = self.get_key_ind(inKey,"get_float",9)
        if(kInd==-1):return
        return struct.unpack('f', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i32step])[0]

    def get_double(self, inKey):
        kInd = self.get_key_ind(inKey,"get_double",10)
        if(kInd==-1):return
        return struct.unpack('d', self.B[self.EL[kInd][0]:self.EL[kInd][0]+i64step])[0]

    def get_string(self, inKey):
        kInd = self.get_key_ind(inKey,"get_string",11)
        if(kInd==-1):return
        return str(self.B[self.EL[kInd][0]:self.EL[kInd][1]], 'ascii')

    def get_buffer(self, inKey):
        kInd = self.get_key_ind(inKey,"get_buffer",52)
        if(kInd==-1):return
        return self.B[self.EL[kInd][0]:self.EL[kInd][1]]

    def get_stream(self, inKey):
        kInd = self.get_key_ind(inKey,"get_stream",53)
        if(kInd==-1):return
        return self.B[self.EL[kInd][0]:self.EL[kInd][1]]

    ####################################### GET VECTOR 1D #######################################

    def get_int8_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int8_vector",18)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('b', self.B[b:b+i8step])[0])
            b+=i8step
        return intList

    def get_int8_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int8_vector",18)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="int8")

    def get_uint8_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint8_vector",19)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('B', self.B[b:b+i8step])[0])
            b+=i8step
        return intList      

    def get_uint8_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint8_vector",19)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="uint8")

    def get_int16_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int16_vector",20)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('h', self.B[b:b+i16step])[0])
            b+=i16step
        return intList   

    def get_int16_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int16_vector_np",20)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="uint16")

    def get_uint16_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint16_vector",21)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('H', self.B[b:b+i16step])[0])
            b+=i16step
        return intList

    def get_uint16_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint16_vector",21)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="uint16")

    def get_int32_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int32_vector",22)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('i', self.B[b:b+i32step])[0])
            b+=i32step
        return intList
        
    def get_int32_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int32_vector",22)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="int32")

    def get_uint32_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int32_vector",23)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('I', self.B[b:b+i32step])[0])
            b+=i32step
        return intList

    def get_uint32_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int32_vector",23)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="uint32")

    def get_int64_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int64_vector",24)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('q', self.B[b:b+i64step])[0])
            b+=i64step
        return intList

    def get_int64_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int64_vector_np",24)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="int64")

    def get_uint64_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int64_vector",25)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        return intList

    def get_uint64_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int64_vector_np",25)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="uint64")

    def get_float_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_float_vector",26)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('f', self.B[b:b+i32step])[0])
            b+=i32step
        return intList

    def get_float_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_float_vector_np",26)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="float32")

    def get_double_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_double_vector",27)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        intList = []
        for s in range(iCount):
            intList.append(struct.unpack('d', self.B[b:b+i64step])[0])
            b+=i64step
        return intList

    def get_double_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_double_vector_np",27)
        if(kInd==-1):return
        buf = self.B[self.EL[kInd][0]+i64step:self.EL[kInd][1]]
        return np.frombuffer(buf, dtype="float64")

    def get_string_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_string_vector",28)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        sIndList = []
        for s in range(iCount+1):
            sIndList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        sList = []
        for s in range(iCount):sList.append(str(self.B[sIndList[s]+b:sIndList[s+1]+b],'ascii'))
        return sList

    def get_string_vector_np(self, inKey):
        kInd = self.get_key_ind(inKey,"get_string_vector_np",28)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        sIndList = []
        for s in range(iCount+1):
            sIndList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        sList = []
        for s in range(iCount):sList.append(str(self.B[sIndList[s]+b:sIndList[s+1]+b],'ascii'))
        return np.array(sList)

    def get_stream_vector(self, inKey):
        kInd = self.get_key_ind(inKey,"get_stream_vector",54)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        sIndList = []
        for s in range(iCount+1):
            sIndList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        sList = []
        for s in range(iCount):sList.append(self.B[sIndList[s]+b:sIndList[s+1]+b])
        return sList


    ####################################### GET 2D VECTORS #######################################

    def get_int8_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int8_vector2d",35)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('b', self.B[b:b+i8step])[0])
                b+=i8step
            valList.append(subList)
        return valList

    def get_uint8_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint8_vector2d",36)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('B', self.B[b:b+i8step])[0])
                b+=i8step
            valList.append(subList)
        return valList

    def get_int16_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int16_vector2d",37)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('h', self.B[b:b+i16step])[0])
                b+=i16step
            valList.append(subList)
        return valList

    def get_uint16_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint16_vector2d",38)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('H', self.B[b:b+i16step])[0])
                b+=i16step
            valList.append(subList)
        return valList

    def get_int32_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int32_vector2d",39)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('i', self.B[b:b+i32step])[0])
                b+=i32step
            valList.append(subList)
        return valList

    def get_uint32_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint32_vector2d",40)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('I', self.B[b:b+i32step])[0])
                b+=i32step
            valList.append(subList)
        return valList

    def get_int64_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_int64_vector2d",41)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('q', self.B[b:b+i64step])[0])
                b+=i64step
            valList.append(subList)
        return valList

    def get_uint64_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_uint64_vector2d",42)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
                b+=i64step
            valList.append(subList)
        return valList

    def get_float_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_float_vector2d",43)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('f', self.B[b:b+i32step])[0])
                b+=i32step
            valList.append(subList)
        return valList

    def get_double_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_double_vector2d",44)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        for s in range(iCount):
            countList.append(struct.unpack('Q', self.B[b:b+i64step])[0])
            b+=i64step
        valList = []
        for subCount in countList:
            subList=[]
            for ind in range(subCount):
                subList.append(struct.unpack('d', self.B[b:b+i64step])[0])
                b+=i64step
            valList.append(subList)
        return valList

    def get_string_vector2d(self, inKey):
        kInd = self.get_key_ind(inKey,"get_string_vector2d",45)
        if(kInd==-1):return
        b = self.EL[kInd][0]
        iCount = struct.unpack('Q', self.B[b:b+i64step])[0]
        b+=i64step
        countList = []
        extraOffset = 0
        for s in range(iCount):
            count = struct.unpack('Q', self.B[b:b+i64step])[0] # next the counts for each list
            countList.append(count)
            extraOffset=extraOffset+count*i64step 
            b+=i64step
        tIndex = b + extraOffset + i64step # extra offset at the end for end pos
        sList = []
        for subCount in countList:
            posList=[]
            for ind in range(subCount+1): #add on the End Pos over the length 
                posList.append(struct.unpack('Q', self.B[b:b+i64step])[0]) # positions for each string
                if ind < subCount:b+=i64step
            subList=[]
            for s in range(subCount):
                subList.append(str(self.B[posList[s]+tIndex:posList[s+1]+tIndex],'ascii'))
            sList.append(subList)
        return sList


    ####################################### ADD NUMPY #######################################

    def add_numpy_array(self, inKey, inArr):
        if(inArr.dtype == "int8"):self.add_int8_vector(inKey, inArr)
        elif(inArr.dtype == "int16"):self.add_int16_vector(inKey, inArr)
        elif(inArr.dtype == "int32"):self.add_int32_vector(inKey, inArr)
        elif(inArr.dtype == "int64"):self.add_int64_vector(inKey, inArr)
        elif(inArr.dtype == "uint8"):self.add_uint8_vector(inKey, inArr)
        elif(inArr.dtype == "uint16"):self.add_uint16_vector(inKey, inArr)
        elif(inArr.dtype == "uint32"):self.add_uint32_vector(inKey, inArr)
        elif(inArr.dtype == "uint64"):self.add_uint64_vector(inKey, inArr)
        elif(inArr.dtype == "float16"):self.add_float_vector(inKey, inArr) 
        elif(inArr.dtype == "float32"):self.add_float_vector(inKey, inArr)            
        elif(inArr.dtype == "float64"):self.add_double_vector(inKey, inArr)
        elif(inArr.dtype == "bool"):self.add_int8_vector(inKey, inArr)
        elif(str(inArr.dtype)[:10] == "datetime64" ):
            dtArr = inArr.astype("datetime64[ns]")
            dtArr = dtArr.astype(np.int64)
            self.add_int64_vector(inKey, dtArr)
        elif(str(inArr.dtype)[:11] == "timedelta64" ):
            dtArr = inArr.astype("timedelta64[ns]")
            dtArr = dtArr.astype(np.int64)
            self.add_int64_vector(inKey, dtArr)
        else: # handle all the numpy edge case types using encoding or conversion to string
            encList=[]
            for item in inArr:
                enc = ""
                try:enc = json.dumps(item)
                except (TypeError, OverflowError):enc = str(item)
                if enc.startswith('"') and enc.endswith('"'):enc = enc[1:-1]
                print("enc: ", enc)
                encList.append(enc)
            self.add_string_vector(inKey,encList)

    #################################### ADD SINGLE VALUE ######################################

    def add_bool(self, inKey, inBool):
        bar = bytearray()
        boolVal = 0
        if(inBool):boolVal = 1
        bType = bytearray(struct.pack('B', 2)) #uint8
        bInt = bytearray(struct.pack('B', boolVal))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_char(self, inKey, inChar):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 2)) #uint8
        bInt = bytearray(struct.pack('B', ord(inChar)))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_int8(self, inKey, inInt8):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 1)) #int8
        bInt = bytearray(struct.pack('b', inInt8))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint8(self, inKey, add_int8):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 2)) #uint8
        bInt = bytearray(struct.pack('B', add_int8))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_int16(self, inKey, inInt16):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 3)) #int16
        bInt = bytearray(struct.pack('h', inInt16))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint16(self, inKey, inUInt16):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 4)) #uint16
        bInt = bytearray(struct.pack('H', inUInt16))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_int32(self, inKey, inInt32):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 5)) #int32
        bInt = bytearray(struct.pack('i', inInt32))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint32(self, inKey, inUInt32):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 6)) #uint32
        bInt = bytearray(struct.pack('I', inUInt32))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_int64(self, inKey, inInt64):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 7)) #int64
        bInt = bytearray(struct.pack('q', inInt64))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint64(self, inKey, inUInt64):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 8)) 
        bInt = bytearray(struct.pack('Q', inUInt64)) #uint64
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_float(self, inKey, inFloat):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 9)) #float
        bInt = bytearray(struct.pack('f', inFloat))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_double(self, inKey, inDouble):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 10)) #double
        bInt = bytearray(struct.pack('d', inDouble))
        bar += bType + bytearray(struct.pack('Q', len(inKey))) + inKey.encode('ascii') + bInt
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_string(self, inKey, inStr):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 11)) #string
        bar += bType + keySize + inKey.encode('ascii') + inStr.encode('ascii')
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_buffer(self, inKey, inBuffer):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 52)) #buffer
        bar += bType + keySize + inKey.encode('ascii') + inBuffer
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_stream(self, inKey, inStreamBuf):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 53)) #stream
        bar += bType + keySize + inKey.encode('ascii')
        if(inStreamBuf==""):pass
        if isinstance(inStreamBuf, str):
            bar += inStreamBuf.encode('ascii')
        else:
            bar += inStreamBuf
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    ####################################### ADD VECTOR 1D #######################################

    def add_int8_vector(self, inKey, inInt8List):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 18)) #int8 vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inInt8List))) # count
        for item in inInt8List:bar += bytearray(struct.pack('b', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint8_vector(self, inKey, inUInt8List):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 19)) #uint8 vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inUInt8List))) # count
        for item in inUInt8List:bar += bytearray(struct.pack('B', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_int16_vector(self, inKey, inInt16List):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 20)) #int16 vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inInt16List))) # count
        for item in inInt16List:bar += bytearray(struct.pack('h', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint16_vector(self, inKey, inUInt16List):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 21)) #uint16 vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inUInt16List))) # count
        for item in inUInt16List:bar += bytearray(struct.pack('H', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_int32_vector(self, inKey, inInt32List):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 22)) #int32 vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inInt32List))) # count
        for item in inInt32List:bar += bytearray(struct.pack('i', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint32_vector(self, inKey, inUInt32List):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 23)) #uint32 vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inUInt32List))) # count
        for item in inUInt32List:bar += bytearray(struct.pack('I', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_int64_vector(self, inKey, inInt64List):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 24)) #int64 vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inInt64List))) # count
        for item in inInt64List:bar += bytearray(struct.pack('q', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint64_vector(self, inKey, inUInt64List):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 24)) #uint64 vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inUInt64List))) # count
        for item in inUInt64List:bar += bytearray(struct.pack('Q', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_float_vector(self, inKey, inFloatList):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 26)) #float vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inFloatList))) # count
        for item in inFloatList:bar += bytearray(struct.pack('f', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_double_vector(self, inKey, inDoubleList):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 27)) #double vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inDoubleList))) # count
        for item in inDoubleList:bar += bytearray(struct.pack('d', item))
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_string_vector(self, inKey, inStrList):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 28)) #string vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inStrList))) # count
        endBuf = bytearray()
        sPos = 0
        for item in inStrList:
            bar += bytearray(struct.pack('Q', sPos)) # sub count 
            sPos += len(item)
            endBuf+=item.encode('ascii')
        bar += bytearray(struct.pack('Q', sPos))
        bar += endBuf
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_stream_vector(self, inKey, inStreamList):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 54)) #stream vector
        bar += bType + keySize + inKey.encode('ascii')
        bar += bytearray(struct.pack('Q', len(inStreamList))) # count
        endBuf = bytearray()
        sPos = 0
        for item in inStreamList:
            bar += bytearray(struct.pack('Q', sPos)) # sub count 
            sPos += len(item)
            if isinstance(item, str):endBuf+=item.encode('ascii')
            else:endBuf+=item
        bar += bytearray(struct.pack('Q', sPos))
        bar += endBuf
        self.bufList.append(bar)
        self.lenList.append(len(bar))
    
    ####################################### ADD VECTOR 2D #######################################

    def add_int8_vector2d(self, inKey, inInt8List2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 35)) #int8 vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inInt8List2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inInt8List2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('b', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint8_vector2d(self, inKey, inUInt8List2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 36)) #int8 vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inUInt8List2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inUInt8List2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('B', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_int16_vector2d(self, inKey, inInt16List2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 37)) #int16 vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inInt16List2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inInt16List2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('h', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint16_vector2d(self, inKey, inUInt16List2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 38)) #uint16 vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inUInt16List2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inUInt16List2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('H', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_int32_vector2d(self, inKey, inInt32List2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 39)) #int32 vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inInt32List2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inInt32List2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('i', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar))    

    def add_uint32_vector2d(self, inKey, inUInt32List2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 40)) #uint32 vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inUInt32List2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inUInt32List2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('I', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar)) 

    def add_int64_vector2d(self, inKey, inInt64List2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 41)) #int64 vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inInt64List2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inInt64List2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('q', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_uint64_vector2d(self, inKey, inUInt64List2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 42)) #uint64 vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inUInt64List2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inUInt64List2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('Q', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_float_vector2d(self, inKey, inFloatList2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 43)) #float vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inFloatList2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inFloatList2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('f', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_double_vector2d(self, inKey, inDoubleList2D):
        bar = bytearray()
        bType = bytearray(struct.pack('B', 44)) #double vector2d
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inDoubleList2D)))
        bar += oCount
        valBar = bytearray()
        for iList in inDoubleList2D:
            bar += bytearray(struct.pack('Q', len(iList)))
            for item in iList:
                valBar += bytearray(struct.pack('d', item))
        bar += valBar
        self.bufList.append(bar)
        self.lenList.append(len(bar))

    def add_string_vector2d(self, inKey, inStrList2D):
        bar = bytearray()
        keySize = bytearray(struct.pack('Q', len(inKey))) 
        bType = bytearray(struct.pack('B', 45)) #string vector
        bar += bType + keySize + inKey.encode('ascii')
        oCount = bytearray(struct.pack('Q', len(inStrList2D)))
        bar += oCount
        endBuf = bytearray()
        posBuf = bytearray()
        sPos = 0
        for sList in inStrList2D:
            bar += bytearray(struct.pack('Q', len(sList))) # sub count
            for item in sList:
                posBuf += bytearray(struct.pack('Q', sPos)) # sub pos 
                sPos += len(item)
                endBuf += item.encode('ascii')
        posBuf += bytearray(struct.pack('Q', sPos)) # sub pos 
        bar += posBuf
        bar += endBuf
        self.bufList.append(bar)
        self.lenList.append(len(bar))


bytestream_types = [
    "none",
    "int8", "uint8",
    "int16", "uint16",
    "int32", "uint32",
    "int64", "uint64",
    "float", "double",
    "string",
    "vec2", "vec3", "vec4",
    "mat2", "mat3", "mat4",
    "int8_vector", "uint8_vector",
    "int16_vector", "uint16_vector",
    "int32_vector", "uint32_vector",
    "int64_vector", "uint64_vector",
    "float_vector", "double_vector",
    "string_vector",
    "vec2_vector", "vec3_vector", "vec4_vector",
    "mat2_vector", "mat3_vector", "mat4_vector",
    "int8_vector2d", "uint8_vector2d",
    "int16_vector2d", "uint16_vector2d",
    "int32_vector2d", "uint32_vector2d",
    "int64_vector2d", "uint64_vector2d",
    "float_vector2d", "double_vector2d",
    "string_vector2d",
    "vec2_vector2d", "vec3_vector2d", "vec4_vector2d",
    "mat2_vector2d", "mat3_vector2d", "mat4_vector2d",
    "buffer",
    "stream", "stream_vector",
    "table",
    "json",
    "last"
]

# Quick lookup if you get a type error code
# 0 =  none
# 1 =  int8
# 2 =  uint8
# 3 =  int16
# 4 =  uint16
# 5 =  int32
# 6 =  uint32
# 7 =  int64
# 8 =  uint64
# 9 =  float
# 10 = double
# 11 = string
# 12 = vec2
# 13 = vec3
# 14 = vec4
# 15 = mat2
# 16 = mat3
# 17 = mat4
# 18 = int8_vector
# 19 = uint8_vector
# 20 = int16_vector
# 21 = uint16_vector
# 22 = int32_vector
# 23 = uint32_vector
# 24 = int64_vector
# 25 = uint64_vector
# 26 = float_vector
# 27 = double_vector
# 28 = string_vector
# 29 = vec2_vector
# 30 = vec3_vector
# 31 = vec4_vector
# 32 = mat2_vector
# 33 = mat3_vector
# 34 = mat4_vector
# 35 = int8_vector2d
# 36 = uint8_vector2d
# 37 = int16_vector2d
# 38 = uint16_vector2d
# 39 = int32_vector2d
# 40 = uint32_vector2d
# 41 = int64_vector2d
# 42 = uint64_vector2d
# 43 = float_vector2d
# 44 = double_vector2d
# 45 = string_vector2d
# 46 = vec2_vector2d
# 47 = vec3_vector2d
# 48 = vec4_vector2d
# 49 = mat2_vector2d
# 50 = mat3_vector2d
# 51 = mat4_vector2d
# 52 = buffer
# 53 = stream
# 54 = stream_vector
# 55 = table
# 56 = json
# 57 = last

