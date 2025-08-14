#******************************************************************************
# Copyright of this product 2013-2023,
# MACHBASE Corporation(or Inc.) or its subsidiaries.
# All Rights reserved.
#******************************************************************************

import re
import json
import os
import time
from machbaseAPI.machbaseAPI import machbase

def append():
#init,columns start
    port = int(os.environ['MACHBASE_PORT_NO'])
    db = machbase()
    if db.open('127.0.0.1','SYS','MANAGER',port) == 0 :
        return db.result()

    db.execute('drop table sample_table')
    db.result()
    if db.execute('create table sample_table(d1 short, d2 integer, d3 long, f1 float, f2 double, name varchar(20), text text, bin binary, v4 ipv4, v6 ipv6, dt datetime)') == 0:
        return db.result()
    db.result()

    tableName = 'sample_table'
    db.columns(tableName)
    result = db.result()

    if db.close() == 0 :
        return db.result()
#init, colums end

#appendByTime start
    db2 = machbase()
    if db2.open('127.0.0.1','SYS','MANAGER',port) == 0 :
        return db2.result()

    types = []
    for item in re.findall('{[^}]+}',result):
        types.append(json.loads(item).get('type'))

    values = []

    datesec = int(time.time())
    sStartTimeNs = datesec*1000000*1000;

    times = []
    with open('data.txt','r') as f:
        for line in f.readlines():
            v = []
            i = 0
            linenum = 0
            for l in line[:-1].split(','):
                t = int(types[i])
                if (t == 4 or t == 8 or t == 12 or t == 104 or t == 108 or t == 112) and (l != ''):
                    #short   integer    long       ushort      uinteger     ulong
                    v.append(int(l))
                elif (t == 16 or t == 20) and (l != ''):
                    #float      double
                    v.append(float(l))
                else:
                    v.append(str(l))
                i += 1
            values.append(v)

            timeNs = sStartTimeNs + (1000000 * linenum * 1000);
            times.append(timeNs)
            linenum += 1

    db2.appendByTime(tableName, types, values, 'YYYY-MM-DD HH24:MI:SS', times)
    result = db2.result()

    if db2.close() == 0 :
        return db2.result()
#appendByTime end

    return result

if __name__=="__main__":
    print (append())
