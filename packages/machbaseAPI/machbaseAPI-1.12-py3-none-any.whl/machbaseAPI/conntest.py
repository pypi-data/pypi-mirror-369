#******************************************************************************
# Copyright of this product 2013-2023,
# MACHBASE Corporation(or Inc.) or its subsidiaries.
# All Rights reserved.
#******************************************************************************

import os
from machbaseAPI.machbaseAPI import machbase

def connect():
    port = int(os.environ['MACHBASE_PORT_NO'])
    db = machbase()
    if db.open('192.168.0.148','SYS','MANAGER',port) == 0 :
        return db.result()

    if db.execute('select count(*) from m$tables') == 0 :
        return db.result()

    result = db.result()

    if db.close() == 0 :
        return db.result()

    return result

if __name__=="__main__":
    print(connect())
