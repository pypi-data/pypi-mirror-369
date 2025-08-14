#-*- coding: utf-8 -*-
import pdslib
import time

def ReadExcel():
    l=pdslib.pglibreadexcel("222222.xlsx")
    print(l.__len__())

def WriteExcel():
    l=[]
    for i in range(1000000):
        l.append((1.111,2,"2","2","2","2","2","2","2","2","2","2","2","2","2","2","2","2","2","2","2","2","2"))
    pdslib.pgWriteExcel("222222.xlsx",("a","b"),l,'hhhhh')


if __name__ ==  '__main__':
    print(pdslib.register("300bf8f6f91a83b3731c99203acdbe492821347967e86b1f571be06f64ed97c002084b362bea25670577a88a72711f376c137bd0e914a77d1a6a4eab2f6196b0"))
    t1=time.time()
    WriteExcel()
    t2=time.time()
    print(t2-t1)
    ReadExcel()
    t3=time.time()
    print(t3-t2)