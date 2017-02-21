from __future__ import print_function
from pyspark import SparkContext

import datetime
import time
from math import exp
#from joblib import Parallel, delayed
import multiprocessing
import sys
sys.path.append('/home/xilinx')

from pynq import PL
from pynq import Overlay
from pynq import MMIO

def training_accel(data, weights):
    # design parameters
    NUM_OF_LABELS = 10
    NUM_OF_FEATURES = 784
    CHUNK_SIZE = 50

	# Offset Adress, Range
    training_accel_ip = MMIO(0x43C00000, 0x80000)
	
	# Address Info (BUS_A_s_axi)
    data1_BASE = 0x20000
    data2_BASE = 0x40000
    weights_BASE = 0x60000
    gradients_BASE = 0x68000
	
	# Memory 'data1'/'data2'
    for index in range (0, int(CHUNK_SIZE * (NUM_OF_LABELS + NUM_OF_FEATURES)/2)):
	    training_accel_ip.write(data1_BASE + index * 4, float(data[index]))
   
    for index in range (0, int(CHUNK_SIZE * (NUM_OF_LABELS + NUM_OF_FEATURES)/2)):
	    training_accel_ip.write(data2_BASE + index * 4, float(data[int(CHUNK_SIZE * (NUM_OF_LABELS + NUM_OF_FEATURES)/2)+index]))
    
    # Memory 'weights'
    for index in range (0, NUM_OF_LABELS * NUM_OF_FEATURES):
	    training_accel_ip.write(weights_BASE + index * 4, float(weights[index]))
	
    # Control signals (ap_start) 
    training_accel_ip.write(0x0, 1)
	# ACK is set to check for 0x0 in the ACK offset
    while (training_accel_ip.read(0x0) & 0b10) != 0b10:
        pass
        # Ack has been received
	# Memory 'gradients'
    gradients = []
    for index in range (0, NUM_OF_LABELS * NUM_OF_FEATURES):
        gradients.append(training_accel_ip.fread(gradients_BASE + index * 4))
    return gradients	

def training(data, weights):
	# design parameters
    NUM_OF_LABELS = 10
    NUM_OF_FEATURES = 784
    CHUNK_SIZE = 50	

    gradients = []
    for k in range (0, NUM_OF_LABELS):
        for j in range (0, NUM_OF_FEATURES):
            gradients.append(0.0)

    for i in range (0, CHUNK_SIZE):	
        labels = []
        for k in range (0, NUM_OF_LABELS):
            labels.append(float(data[i * (NUM_OF_LABELS + NUM_OF_FEATURES) + k]))
        features = []
        for j in range (0, NUM_OF_FEATURES):
    	    features.append(float(data[i * (NUM_OF_LABELS + NUM_OF_FEATURES) + NUM_OF_LABELS + j]))
			
        for k in range (0, NUM_OF_LABELS):
            dot = 0.0
            for j in range (0, NUM_OF_FEATURES):
                dot = dot + float(weights[k * NUM_OF_FEATURES + j]) * float(features[j])

            dif = 1.0 / (1.0 + exp(-dot)) - float(labels[k])

            for j in range (0, NUM_OF_FEATURES):
        	    gradients[k * NUM_OF_FEATURES + j] += dif * float(features[j])
	
    return gradients	

if __name__ == "__main__":
    
    accel = 0
    
    if len(sys.argv) == 4:
        accel = 1
    elif len (sys.argv) != 3:
        print("Usage: Logistic_regression <IP <data file> <weights file> <.bit file>", file=sys.stderr)
        exit(-1)

    NUM_OF_LABELS = 10
    NUM_OF_FEATURES = 784
    CHUNK_SIZE = 50
    
    #download the bitstream to fpga
    if accel:
        ol = Overlay(sys.argv[3])
        ol.download()
    
    #initialize SparkContext   
    sc = SparkContext(appName="Python Logistic Regression")
    dataFile = sc.textFile(sys.argv[1])
    weightsFile = sc.textFile(sys.argv[2])    
   
    dataRDD = dataFile.flatMap(lambda line: line.split(','))
    #dataRDD = dataFile.flatMap(lambda line: map_func)
    weightsRDD = weightsFile.flatMap(lambda line: line.split(','))    
    data = [x for x in dataRDD.toLocalIterator()]
    weights = [x for x in weightsRDD.toLocalIterator()]
 
    #num_cores = multiprocessing.cpu_count()
    #Parallel(n_jobs=num_cores)(delayed(paral_write)(l_baddr,labels,i) for i in range (num_of_labels))
    #Parallel(n_jobs=num_cores)(delayed(paral_write)(f_baddr,features,i) for i in range (num_of_features))
    #Parallel(n_jobs=num_cores)(delayed(paral_write)(w_baddr,weights,i) for i in range (num_of_labels*num_of_features))
    #write data 	
    
    grads = []
    
    time1 = datetime.datetime.now().time()  
 
    if accel:
        grads = training_accel(data, weights)
    else:
        grads = training(data, weights)

    time2 = datetime.datetime.now().time()
     
    print(time1)    
    print(time2)
    
    with open("/home/xilinx/spark-2.1.1-SNAPSHOT-bin-jstam_final/gradients.txt", "a") as myfile:
        for k in range (0, NUM_OF_LABELS * NUM_OF_FEATURES):
            myfile.write(str(grads[k])+"\n")

    gradientsRDD = sc.parallelize(list(grads))
    gradientsRDD.collect()
    sc.stop()
