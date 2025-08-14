#******************************************************************************
# Copyright of this product 2013-2023,
# MACHBASE Corporation(or Inc.) or its subsidiaries.
# All Rights reserved.
#******************************************************************************

def makeData():
    with open('data.txt','w') as f:
        for i in range(1,100):
            text = str(i%32768)+","+str(i+i)+","+str((int)(i+i+i)*10000)+","+str((float)(i+2)/(i+i+i)*10000)+","+str((float)(i+1)/(i+i+i)*10000)+",char-"+str(i)+",text log-"+str(i)+",binary image-"+str(i)+",192.168.9."+str(i%256)+",2001:0DB8:0000:0000:0000:0000:1428:"+str(i%8999+1000)+",2015-05-18 15:26:"+str(i%40+10)+"\n";
            f.write(text)

if __name__=="__main__":
    makeData()
