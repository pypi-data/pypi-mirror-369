#-*- coding: utf-8 -*-
"""
 * Copyright of this product 2013-2023,
 * MACHBASE Corporation(or Inc.) or its subsidiaries.
 * All Rights reserved.
"""

import ctypes,os,platform

def get_library_path():
    # 현재 스크립트의 경로
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    lib_dir = os.path.join(script_dir, 'lib')
    system = platform.system()
    architecture = platform.machine()

    if system == 'Linux':
        # if distro:  # Check if distro is available
        #     distro_name = distro.id()
        #     distro_version = distro.version()
        #     distro_major_version = int(distro_version.split('.')[0])
        #     distro_combined = f"{distro_name}{distro_major_version}"
        #     print(f"Detected Linux distribution and version: {distro_combined}")

        if architecture in ['x86_64', 'AMD64']:
            arch = "x64"
        elif architecture in ['arm64', 'aarch64']:
            arch = "arm64"
        else:
            raise OSError(f"Unsupported CPU architecture on Linux: {architecture}")

        lib_name = f"libmachbaseAPI_{arch}.so"

        # 우분투와 레드헷 계열 구분 및 조건 처리
        # if distro_name == 'ubuntu':
        #     if distro_major_version >= 20:
        #         lib_name = f"libmachbaseAPI_{arch}_ubuntu.so"
        #     else:
        #         raise OSError(f"Unsupported Ubuntu OS system:  {distro_major_version}")
        # elif distro_name in ['rhel', 'centos', 'rocky', 'almalinux']:
        #     if distro_major_version == 6 or distro_major_version == 7:
        #         lib_name = f"libmachbaseAPI_{arch}_rhel6.so"
        #     elif distro_major_version >= 8:
        #         lib_name = f"libmachbaseAPI_{arch}_rhel8.so"
        #     else:
        #         raise OSError(f"Unsupported RHEL OS Version : RHEL {distro_major_version}")
        # else: #Unknown linux pkg
        #     raise OSError(f"Unsupported  OS Package :  {distro_name}")

        return os.path.join(lib_dir, lib_name)

    elif system == 'Windows':
        if architecture in ['x86_64', 'AMD64']:
            return os.path.join(lib_dir, 'machbaseAPI_x64.dll')
        elif architecture in ['ARM64']:
            return os.path.join(lib_dir, 'machbaseAPI_arm64.dll')
        else:
            raise OSError(f"Unsupported CPU architecture on Windows: {architecture}")

    elif system == 'Darwin':  # macOS
        if architecture in ['x86_64', 'AMD64']:
            return os.path.join(lib_dir, 'libmachbaseAPI_x64.dylib')
        elif architecture in ['arm64']:
            return os.path.join(lib_dir, 'libmachbaseAPI_arm64.dylib')
        else:
            raise OSError(f"Unsupported CPU architecture on macOS: {architecture}")

    else:
        raise OSError(f"Unsupported operating system: {system}")

gCharset = 'UTF-8'

class machbaseAPI(object):
    sofile = get_library_path()
    clib = ctypes.CDLL(sofile)
    clib.openDB.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32]
    clib.openDB.restype = ctypes.c_void_p
    clib.openDBEx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_char_p]
    clib.openDBEx.restype = ctypes.c_void_p
    clib.closeDB.argtypes = [ctypes.c_void_p,]
    clib.closeDB.restypes = ctypes.c_int
    clib.execDirect.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    clib.execDirect.restypes = ctypes.c_int
    clib.execSelect.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int] #ctypes.c_int
    clib.execSelect.restypes = ctypes.c_int
    clib.execStatistics.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    clib.execStatistics.restypes = ctypes.c_int
    clib.execSchema.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    clib.execSchema.restypes = ctypes.c_int

    clib.execAppendOpen.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    clib.execAppendOpen.restypes = ctypes.c_int
    clib.execAppendClose.argtypes = [ctypes.c_void_p,]
    clib.execAppendClose.restypes = ctypes.c_int
    clib.execAppendData.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p), ctypes.c_int, ctypes.c_char_p]
    clib.execAppendData.restypes = ctypes.c_int
    clib.execAppendDataByTime.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p), ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    clib.execAppendDataByTime.restypes = ctypes.c_int
    clib.execAppendFlush.argtypes = [ctypes.c_void_p,]
    clib.execAppendFlush.restypes = ctypes.c_int

    clib.getColumns.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    clib.getColumns.restypes = ctypes.c_int
    clib.getIsConnected.argtypes = [ctypes.c_void_p,]
    clib.getIsConnected.restypes = ctypes.c_int
    clib.getDataCount.argtypes = [ctypes.c_void_p,]
    clib.getDataCount.restypes = ctypes.c_ulong
    clib.getlAddr.argtypes = [ctypes.c_void_p,]
    clib.getlAddr.restypes = ctypes.c_int
    clib.getrAddr.argtypes = [ctypes.c_void_p,]
    clib.getrAddr.restypes = ctypes.c_int
    clib.getData.argtypes = [ctypes.c_void_p,]
    clib.getData.restypes = ctypes.POINTER(ctypes.c_char)

    clib.getSessionId.argtypes = (ctypes.c_void_p,)
    clib.getSessionId.restypes = ctypes.c_ulong
    clib.fetchRow.argtypes = (ctypes.c_void_p,)
    clib.fetchRow.restypes = ctypes.c_ulong
    clib.selectClose.argtypes = (ctypes.c_void_p,)
    clib.selectClose.restypes = ctypes.c_ulong


    def __init__(self):
        pass
    def openDB(self, aHost='127.0.0.1', aUser='SYS', aPw='MANAGER', aPort=5656):
        return self.clib.openDB(aHost, aUser, aPw, aPort)
    def openDBEx(self, aHost='127.0.0.1', aUser='SYS', aPw='MANAGER', aPort=5656, aConnStr=''):
        return self.clib.openDBEx(aHost, aUser, aPw, aPort, aConnStr)
    def closeDB(self, aObj):
        return self.clib.closeDB(aObj)
    def execDirect(self, aObj, aSql):
        return self.clib.execDirect(aObj, aSql)
    def execSelect(self, aObj, aSql, aType=0):
        return self.clib.execSelect(aObj, aSql, aType)
    def execStatistics(self, aObj, aTable, aUser):
        return self.clib.execStatistics(aObj, aTable, aUser)
    def execSchema(self, aObj, aSql):
        return self.clib.execSchema(aObj, aSql)
    def execAppendOpen(self, aObj, aTable, aNum):
        return self.clib.execAppendOpen(aObj, aTable, aNum)
    def execAppendClose(self, aObj):
        return self.clib.execAppendClose(aObj)
    def execAppendData(self, aObj, aType, aValue, aNum, aFormat):
        return self.clib.execAppendData(aObj, aType, aValue, aNum, aFormat)
    def execAppendDataByTime(self, aObj, aType, aValue, aNum, aFormat, aTime):
        return self.clib.execAppendDataByTime(aObj, aType, aValue, aNum, aFormat, aTime)
    def execAppendFlush(self, aObj):
        return self.clib.execAppendFlush(aObj)

    def getColumns(self, aObj, aTable):
        return self.clib.getColumns(aObj, aTable)
    def getIsConnected(self, aObj):
        return self.clib.getIsConnected(aObj)
    def getDataCount(self, aObj):
        return self.clib.getDataCount(aObj)&0xFFFFFFFFFFFFFFFF
    def getlAddr(self, aObj):
        return self.clib.getlAddr(aObj)&0x00000000FFFFFFFF
    def getrAddr(self, aObj):
        return self.clib.getrAddr(aObj)&0x00000000FFFFFFFF
    def getData(self, aObj):
        return self.clib.getData(aObj)
    def getSessionId(self, aObj):
        return self.clib.getSessionId(aObj)
    def fetchRow(self, aObj):
        return self.clib.fetchRow(aObj)
    def selectClose(self, aObj):
        return self.clib.selectClose(aObj)

class machbase(object):
    def __init__(self):
        self.so = machbaseAPI()
        self.mObj = None
        self.mIs_connected = False
        self.mIs_opened = False
        self.mIs_appendopend = False
    def isConnected(self):
        if not self.mIs_connected:
            return 0
        return 1
    def isOpened(self):
        if not self.mIs_opened:
            return 0
        return 1
    def open(self, aHost='127.0.0.1', aUser='SYS', aPw='MANAGER', aPort=5656):
        self.mIs_opened = True
        self.mObj = self.so.openDB(aHost.encode('utf-8'), aUser.upper().encode('utf-8'), aPw.encode('utf-8'), int(aPort))
        if self.mObj is None:
            sRC = 0
        else:
            sRC = self.so.getIsConnected(self.mObj)
        self.mIs_connected = bool( sRC )
        return sRC
    def openEx(self, aHost='127.0.0.1', aUser='SYS', aPw='MANAGER', aPort=5656, aConnStr=""):
        self.mIs_opened = True
        self.mObj = self.so.openDBEx(aHost.encode('utf-8'),
                                     aUser.upper().encode('utf-8'),
                                     aPw.encode('utf-8'),
                                     int(aPort),
                                     aConnStr.encode('utf-8'))
        if self.mObj is None:
            sRC = 0
        else:
            sRC = self.so.getIsConnected(self.mObj)
        self.mIs_connected = bool( sRC )
        return sRC
    def close(self):
        if not self.mIs_opened:
            return 0
        if self.mIs_connected:
            sRC = self.so.closeDB(self.mObj)
            if sRC == 0:
                return 0
        else:
            sRC = 1
        self.mIs_connected = False
        self.mIs_opened = False
        return sRC
    def column(self, aTableName):
        if not self.mIs_connected:
            return 0
        sRC = self.so.getColumns(self.mObj, aTableName.encode(gCharset))
        return sRC
    def statistics(self, aTableName, aUser='SYS'):
        if not self.mIs_connected:
            return 0
        sRC = self.so.execStatistics(self.mObj, aTableName.encode(gCharset), aUser.upper().encode(gCharset))
        return sRC
    def schema(self, aSql):
        if not self.mIs_connected:
            return 0
        sRC = self.so.execSchema(self.mObj, aSql.encode(gCharset))
        return sRC
    def tables(self):
        if not self.mIs_connected:
            return 0
        sSql = "select t.NAME as name, u.NAME as username, t.COLCOUNT as colcount from m$sys_tables t, m$sys_users u where u.user_id=t.user_id"
        sRC = self.so.execSelect(self.mObj, sSql.encode(gCharset))
        return sRC
    def columns(self, aTableName):
        if not self.mIs_connected:
            return 0
        sSql = None
        if aTableName == None:
#            sSql = "select name,type,length from m$sys_columns where table_id = (select id from m$sys_tables) and id not in(0,65534) order by id"
            sSql = "select c.name name, c.type type, c.length length from m$sys_columns c, m$sys_tables t where c.table_id = t.id and c.id not in(0,65534) order by c.id"
        else:
            aTableName = aTableName.upper()
            if aTableName[0] == 'M' and aTableName[1] == '$':
                sSql = "select name,type,length from m$columns where table_id = (select id from m$tables where name = '"+aTableName+"') and id not in(0,65534) order by id"
            elif aTableName[0] == 'V' and aTableName[1] == '$':
                sSql = "select name,type,length from v$columns where table_id = (select id from v$tables where name = '"+aTableName+"') and id not in(0,65534) order by id"
            else:
                #sSql = "select name,type,length from m$sys_columns where table_id = (select id from m$sys_tables where name = '"+aTableName+"') and id not in(0,65534) order by id"
                sSql = "select name,type,length from m$sys_columns where table_id = (select id from m$sys_tables where name = '"+aTableName+"') and name not in('_RID','_ARRIVAL_TIME') order by id"
        sRC = self.so.execSelect(self.mObj, sSql.encode(gCharset))
        return sRC

    def appendOpen(self, aTableName, aTypes):
        if not self.mIs_connected:
            return 0
        sTout = ctypes.c_char_p*(len(aTypes)+1)
        sType = eval('sTout(%s,None)' % ','.join([ "'%s'" % x for x in aTypes]).encode(gCharset))
        sRC = self.so.execAppendOpen(self.mObj, aTableName.encode(gCharset), len(sType)-1)
        if sRC == 0:
            return sRC
        self.mIs_appendopend = True
        return sRC

    def appendClose(self):
        if not self.mIs_connected:
            return 0
        if not self.mIs_appendopend:
            return 0
        sRC = self.so.execAppendClose(self.mObj)
        if sRC == 0:
            return sRC
        self.mIs_appendopend = False
        return sRC

    def appendData(self, aTableName, aTypes, aValues, aFormat='YYYY-MM-DD HH24:MI:SS'):
        if not self.mIs_connected:
            return 0
        if not self.mIs_appendopend:
            return 0
        sTout = ctypes.c_char_p*(len(aTypes)+1)
        sTemp = 'sTout(%s,None)' % ','.join([ "%s" % (x.encode(gCharset) if type(x) is str else x) for x in aTypes])
        #sType = eval('sTout(%s,None)' % ','.join([ "'%s'" % x for x in aTypes]))
        sType = eval(sTemp)
        sRC = 1
        for sItem in aValues :
            sVout = ctypes.c_char_p*(len(sItem)+1)
            sTemp = 'sVout(%s,None)' % ','.join([ "%s" % (x.encode(gCharset) if type(x) is str else str(x).encode()) for x in sItem])
            #sValue = eval('sVout(%s,None)' % ','.join([ "'%s'" % x for x in sItem]))
            sValue = eval(sTemp)
            if len(sValue) != len(sType):
                return 0
            sRC = self.so.execAppendData(self.mObj, sType, sValue, len(sType)-1, aFormat.encode(gCharset))
            if sRC == 0:
                return sRC
        return sRC

    def appendDataByTime(self, aTableName, aTypes, aValues, aFormat='YYYY-MM-DD HH24:MI:SS', aTimes=None):
        if not self.mIs_connected:
            return 0
        if not self.mIs_appendopend:
            return 0
        sTout = ctypes.c_char_p*(len(aTypes)+1)
        sTemp = 'sTout(%s,None)' % ','.join([ "%s" % (x.encode(gCharset) if type(x) is str else x) for x in aTypes])
        sType = eval(sTemp)
        sRC = 1
        for sItem in aValues :
            sVout = ctypes.c_char_p*(len(sItem)+1)
            sTemp = 'sVout(%s,None)' % ','.join([ "%s" % (x.encode(gCharset) if type(x) is str else str(x).encode()) for x in sItem])
            sValue = eval(sTemp)
            if len(sValue) != len(sType):
                return 0
            if len(aTimes) > 0 :
                sTime = aTimes[aValues.index(sItem)]
            else :
                sTime = None
            sRC = self.so.execAppendDataByTime(self.mObj, sType, sValue, len(sType)-1, aFormat.encode(gCharset), sTime)
            if sRC == 0:
                return sRC
        return sRC

    def appendFlush(self):
        if not self.mIs_connected:
            return 0
        if not self.mIs_appendopend:
            return 0
        sRC = self.so.execAppendFlush(self.mObj)
        if sRC == 0:
            return sRC
        return sRC

    def append(self, aTableName, aTypes, aValues, aFormat='YYYY-MM-DD HH24:MI:SS'):
        if not self.mIs_connected:
            return 0
        sRC = self.appendOpen(aTableName, aTypes)
        if sRC == 0:
            return sRC
        sRC = self.appendData(aTableName, aTypes, aValues, aFormat)
        if sRC == 0:
            return sRC
        sRC = self.appendClose()
        return sRC
    def appendByTime(self, aTableName, aTypes, aValues, aFormat='YYYY-MM-DD HH24:MI:SS', aTimes=None):
        if not self.mIs_connected:
            return 0
        sRC = self.appendOpen(aTableName, aTypes)
        if sRC == 0:
            return sRC
        sRC = self.appendDataByTime(aTableName, aTypes, aValues, aFormat, aTimes)
        if sRC == 0:
            return sRC
        sRC = self.appendClose()
        return sRC
    def execute(self, aSql, aType=0):
        if not self.mIs_connected:
            return 0
        aSql = aSql.strip()
        sCmd = aSql.split()[0].lower()
        if sCmd == 'select':
            sRC = self.so.execSelect(self.mObj, aSql.encode(gCharset), int(aType))
            return sRC
        elif sCmd == 'update':
            raise Exception('MachbaseBase does not support UPDATE')
        else:
            sRC = self.so.execDirect(self.mObj, aSql.encode(gCharset))
            return sRC
    def result(self):
        if not self.mIs_connected:
            return '{"EXECUTE ERROR":"SQLConnection error!!"}'
        if self.checkBit() == 32:
            sAdd = self.so.getData(self.mObj)
        elif self.checkBit() == 64:
            sL = self.so.getlAddr(self.mObj) << 32
            sR = self.so.getrAddr(self.mObj)
            sAdd = sL+sR
        return ctypes.cast(sAdd, ctypes.c_char_p).value.decode(gCharset)
    def count(self):
        return self.so.getDataCount(self.mObj)
    def checkBit(self):
        sBit = ctypes.sizeof(ctypes.c_void_p)
        if sBit == 4:
            return 32
        elif sBit == 8:
            return 64
    def getSessionId(self):
        return self.so.getSessionId(self.mObj)
    def select(self, aSql):
        if not self.mIs_connected:
            return 0
        aSql = aSql.strip()
        sCmd = aSql.split()[0].lower()
        if sCmd == 'select':
            sRC = self.so.execSelect(self.mObj, aSql.encode(gCharset), 2)
            return sRC
        else:
            raise Exception('select function supports only SELECT statements.')
    def fetch(self):
        if not self.mIs_connected:
            return 0
        sRC = self.so.fetchRow(self.mObj)
        if self.checkBit() == 32:
            sAdd = self.so.getData(self.mObj)
        elif self.checkBit() == 64:
            sL = self.so.getlAddr(self.mObj) << 32
            sR = self.so.getrAddr(self.mObj)
            sAdd = sL+sR
        sRet = ctypes.cast(sAdd, ctypes.c_char_p).value.decode(gCharset)
        return sRC, sRet
    def selectClose(self):
        if not self.mIs_connected:
            return 0
        sRC = self.so.selectClose(self.mObj)
        return sRC

# Example usage
if __name__ == "__main__":
    try:
        library_path = get_library_path()
        print(f"Library path: {library_path}")
    except OSError as e:
        print(e)
