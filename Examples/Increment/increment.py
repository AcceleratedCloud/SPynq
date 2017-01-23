from __future__ import print_function
from pyspark import SparkContext

import sys
sys.path.append('/home/xilinx')

from pynq import PL
from pynq import Overlay
from pynq import MMIO

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: Increment <IP (.bit file)> <input data>", file=sys.stderr)
        exit(-1)

    #download the bitstream to fpga
    ol = Overlay(sys.argv[1])
    ol.download()
    math_ip = MMIO(0x43C40000,0x10000)

    #initialize SparkContext   
    sc = SparkContext(appName="Python Increment")
    testFile = sc.textFile(sys.argv[2])
    oldRDD = testFile.flatMap(lambda x: x.split())
    arr = [x for x in oldRDD.toLocalIterator()] #used spark_2.1.1 because of a spark bug with toLocalIterator() timeout error
    print(arr[0])
    print(arr[1])

    #The RDD is converted to array and we perform the increment function (fpga side) 
    math_ip.write(0x18,int(arr[0]))
    math_ip.write(0x20,int(arr[1]))
    op1=math_ip.read(0x18)
    print(hex(op1))
    op2=math_ip.read(0x20)
    print(hex(op2))
    result=math_ip.read(0x10)
    print(hex(result))

    #A new RDD is created from the values of op1 and op2
    result = str(op1)+" "+str(op2)
    print(result) 
    newRDD = sc.parallelize(list(result))
    newRDD.collect()
    sc.stop()

