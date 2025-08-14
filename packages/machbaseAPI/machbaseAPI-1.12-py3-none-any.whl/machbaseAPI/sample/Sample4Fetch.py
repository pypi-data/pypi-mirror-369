#******************************************************************************
# Copyright of this product 2013-2023,
# MACHBASE Corporation(or Inc.) or its subsidiaries.
# All Rights reserved.
#******************************************************************************

import re
import json, sys, os
import time
from machbaseAPI.machbaseAPI import machbase

def sample():
    port = int(os.environ['MACHBASE_PORT_NO'])
    records = 500000
    tablename = 'sample_table'

    db = machbase()
    if db.open('127.0.0.1','SYS','MANAGER',port) == 0 :
        return db.result()

    db.execute('drop table ' + tablename)
    db.result()
    if db.execute('create table ' + tablename + '(idx integer, d1 short, d2 integer, d3 long, f1 float, f2 double, name varchar(20), text text, bin binary, v4 ipv4, v6 ipv6, dt datetime)') == 0:
        return db.result()
    db.result()

    db.columns(tablename)
    result = db.result()

    if db.close() == 0:
        return db.result()

# append start
    db2 = machbase()

    types = []
    for item in re.findall('{[^}]+}',result):
        types.append(json.loads(item).get('type'))

    sStart = time.time()
    if db2.open('127.0.0.1','SYS','MANAGER',port) == 0 :
        return db2.result()

    if db2.appendOpen(tablename, types) == 0:
        return db2.result()
    print("append open")

    print("append ", end=" ")
    sys.stdout.flush()
    values = []
    for i in range(0, records):
        v = []
        v.append(i-1)
        v.append(i%32768)
        v.append(i+i)
        v.append(int(i+i+i)*10000)
        v.append(float((i+2)/(i+i+i+1))*10000)
        v.append(float((i+1)/(i+i+i+1))*10000)
        v.append("char-"+str(i))
        v.append("text log-"+str(i))
        v.append("binary image-"+str(i))
        v.append("192.168.9."+str(i%256))
        v.append("2001:0DB8:0000:0000:0000:0000:1428:"+str(i%8999+1000))
        v.append("2015-05-18 15:26:"+str(i%40+10))

        values.append(v)
        if (i % 100000) == 0:
            print(str(i), end=" ")
            sys.stdout.flush()
        if (i % 10000) == 0:
            continue
        if db2.appendData(tablename, types, values) == 0:
            return db2.result()
        values = []
    print("")
    if len(values) > 0:
        if db2.appendData(tablename, types, values) == 0:
            return db2.result()

    if db2.appendClose() == 0:
        return db2.result()

    if db2.close() == 0 :
        return db2.result()
    sEnd = time.time()
    print("append Close (" + str(i+1) + " records)")
    print('elapsed time : ' + str(sEnd - sStart) + " sec\n")
# append end

    db = machbase()
    if db.open('127.0.0.1','SYS','MANAGER',port) == 0 :
        return db.result()

    query = "SELECT idx, d1, d2, d3, f1, f2, name, text, bin, to_hex(bin), v4, v6, to_char(dt,'YYYY-MM-DD') as dt from " + tablename

    print("==================================================")
    print("Using select() -> fetch() -> selectClose()")

    sStart = time.time()
    if db.select(query) == 0:
        return db.result()

    sIdx = -1
    while True:
        is_success, result = db.fetch()
        if is_success == 0:
            break;

        res = json.loads(result)
        sIdx += 1
        if sIdx % 100000 > 0:
            continue
        print("idx  : "+res.get('idx'))
        print("d1   : "+res.get('d1'))
        print("d2   : "+res.get('d2'))
        print("d3   : "+res.get('d3'))
        print("f1   : "+res.get('f1'))
        print("f2   : "+res.get('f2'))
        print("name : "+res.get('name'))
        print("text : "+res.get('text'))
        print("bin  : "+res.get('bin'))
        print("v4   : "+res.get('v4'))
        print("v6   : "+res.get('v6'))
        print("dt   : "+res.get('dt'))
        print("")

    db.selectClose()
    sEnd = time.time()
    print("elapsed time : " + str(sEnd - sStart) + " sec\n")

    if db.close() == 0 :
        return db.result()

    return "successfully executed."

if __name__=="__main__":
    print(sample())
