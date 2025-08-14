#******************************************************************************
# Copyright of this product 2013-2023,
# MACHBASE Corporation(or Inc.) or its subsidiaries.
# All Rights reserved.
#******************************************************************************

import re
import json
import os
from machbaseAPI.machbaseAPI import machbase

def insert():
    port = int(os.environ['MACHBASE_PORT_NO'])
    db = machbase()
    # Extention conection with additional param (_ARRIVAL_TIME will be shown)
    if db.openEx('127.0.0.1','SYS','MANAGER',port, 'SHOW_HIDDEN_COLS=1;CONNECTION_TIMEOUT=30') == 0 : 
        return db.result()

    db.execute('drop table sample_table')
    db.result()
    if db.execute('create table sample_table(id integer)') == 0:
        return db.result()
    db.result()

    for i in range(1,10):
        sql = "INSERT INTO SAMPLE_TABLE VALUES ("
        sql += str(i)
        sql += ")";

        if db.execute(sql) == 0 :
            return db.result()
        else:
            print(db.result())

        print(str(i)+" record inserted.")

    query = "SELECT * from SAMPLE_TABLE";

    if db.select(query) == 0:
        return db.result()

    while True:
        is_success, result = db.fetch()
        if is_success == 0:
            break;

        res = json.loads(result)
        print( "Arrival_time : "+res.get('_ARRIVAL_TIME')) # hidden column 

    db.selectClose()
    if db.close() == 0 :
        return db.result()

    return "successfully executed."

if __name__=="__main__":
    print(insert())
