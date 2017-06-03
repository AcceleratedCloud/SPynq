from pyspark import SparkContext
from pyspark.mllib_accel.classification import LogisticRegression
from sys import argv

if __name__ == "__main__":
    
    if len(argv) != 8:
        print("Usage: LogisticRegressionApp <train_file> <chunkSize> <alpha> <iterations> <test_file> <numPartitions> <accel>")
        exit(-1)

    train_file = "inputs/" + argv[1]
    chunkSize = int(argv[2])
    alpha = float(argv[3])
    iterations = int(argv[4])
    test_file = "inputs/" + argv[5]
    numPartitions = int(argv[6])
    accel = int(argv[7])

    sc = SparkContext(appName = "Python Logistic Regression")

    print("* LogisticRegression Application *")
    print(" # train file:               " + train_file)
    print(" # test file:                " + test_file)
    print(" # numPartitions:            " + str(numPartitions))
        
    trainRDD = sc.textFile(train_file, numPartitions)
    testRDD = sc.textFile(test_file, numPartitions)

    # Exact Partitioning
    trainRDD = trainRDD.zipWithIndex().map(lambda line: (line[1], line[0])).partitionBy(numPartitions).map(lambda line: line[1]) 
    testRDD = testRDD.zipWithIndex().map(lambda line: (line[1], line[0])).partitionBy(numPartitions).map(lambda line: line[1])

    numClasses = 10
    numFeatures = 784
    LR = LogisticRegression(numClasses, numFeatures)    
    
    weights = LR.train(trainRDD, chunkSize, alpha, iterations, accel)
    
    with open("outputs/weights.out", "w") as weights_file:
        for k in range(0, numClasses):
            for j in range(0, numFeatures):
                if j == 0:
                    weights_file.write(str(round(weights[k * numFeatures + j], 5)))
                else:
                    weights_file.write("," + str(round(weights[k * numFeatures + j], 5)))
            weights_file.write("\n")
    weights_file.close()
 
    LR.test(testRDD)

    sc.stop()
