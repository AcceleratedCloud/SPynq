from math import exp
from .accelerators.LogisticRegression import gradients_kernel_accel
from pyspark import RDD
from pyspark.storagelevel import StorageLevel
from time import time

class LogisticRegression(object):
    """
    Multiclass Logistic Regression
    
    One versus rest: The algorithm compares every class with all the remaining classes, 
                     building a model for every class.
    """

    def __init__(self, numClasses, numFeatures, weights = None):
        """
            :param numClasses:     Number of possible outcomes.

            :param numFeatures:    Dimension of the features.

            :param weights:        Weights computed for every feature.
        """

        self.numClasses = numClasses
        self.numFeatures = numFeatures
        self.weights = weights

    def train(self, trainRDD, chunkSize, alpha = 0.25, iterations = 5, _accel_ = 0):  
        """ 
        Train a logistic regression model on the given data.
   
            :param trainRDD:      The training data RDD.
            
            :param chunkSize:     Size of each data chunk. 

            :param alpha:         The learning rate (default: 0.25).

            :param iterations:    The number of iterations (default: 5).
            
            :param _accel_:       0: SW-only, 1: HW accelerated (deafult: 0).
        """

        def process_trainRDD(lines):
            data = []
            tmp = []

            for i, line in enumerate(lines):
                line = line.split(",")

                for k in range(0, self.numClasses):
                    if k == int(line[0]):
                        tmp.append(1.0)
                    else:
                        tmp.append(0.0)
                tmp.append(1)
                for j in range(0, self.numFeatures):
                    tmp.append(float(line[j + 1]))

                if (i + 1) % chunkSize == 0:
                    data.append(tmp)
                    tmp = []

            return data

        def gradients_kernel(data, weights):
            chunkSize = int(len(data) / (self.numClasses + (1 + self.numFeatures)))

            gradients = []
            for k in range (0, self.numClasses):
                for j in range (0, (1 + self.numFeatures)):
                    gradients.append(0.0)

            for i in range (0, chunkSize):
                labels = []
                for k in range (0, self.numClasses):
                    labels.append(float(data[i * (self.numClasses + (1 + self.numFeatures)) + k]))
                features = []
                for j in range (0, (1 + self.numFeatures)):
                    features.append(float(data[i * (self.numClasses + (1 + self.numFeatures)) + self.numClasses + j]))

                for k in range (0, self.numClasses):
                    dot = 0.0
                    for j in range (0, (1 + self.numFeatures)):
                        dot += float(weights[k * (1 + self.numFeatures) + j]) * features[j]

                    dif = 1.0 / (1.0 + exp(-dot)) - labels[k]

                    for j in range (0, (1 + self.numFeatures)):
                        gradients[k * (1 + self.numFeatures) + j] += dif * features[j]

            return gradients

        print("    * LogisticRegression Training *")

        trainRDD = trainRDD.mapPartitions(lambda lines: process_trainRDD(lines)).persist(StorageLevel.MEMORY_AND_DISK)
        numSamples = trainRDD.count() * chunkSize        

        print("     # numSamples:               " + str(numSamples))
        print("     # chunkSize:                " + str(chunkSize))
        print("     # numClasses:               " + str(self.numClasses))
        print("     # numFeatures:              " + str(self.numFeatures))
        print("     # alpha:                    " + str(alpha))
        print("     # iterations:               " + str(iterations))       

        start = time()

        # Batch Gradient Descent Algorithm
        if self.weights is None:
            self.weights = []
            for k in range(0, self.numClasses):
                for j in range(0, (1 + self.numFeatures)):
                    self.weights.append(0.0)

        for t in range(0, iterations):
            print("{:3d}% |{:40s}| {:d}/{:d}".format(int((t / iterations) * 100), u"\u25A5" * int((t / iterations) * 40), t, iterations), end = "\r")
            if _accel_ == 0:
                gradients = trainRDD.map(lambda data: gradients_kernel(data, self.weights))
            else:
                gradients = trainRDD.map(lambda data: gradients_kernel_accel(data, self.weights))
            gradients = gradients.reduce(lambda A, B: [a + b for a, b in zip(A, B)])

            for k in range(0, self.numClasses):
                for j in range(0, (1 + self.numFeatures)):
                    self.weights[k * self.numFeatures + j] -= (alpha / numSamples) * gradients[k * self.numFeatures + j]

        end = time()
        print("{:3d}% |{:40s}| {:d}/{:d} Time: {:.3f} sec".format(100, u"\u25A5" * 40, iterations, iterations, end - start))

        return self.weights      

    def test(self, testRDD):
        """
        Test a logistic regression model on the given data.

            :param testRDD:    The testing data RDD.
        """

        def process_testRDD(lines):
            data = []

            for line in lines:
                line = line.split(",")

                tmp = []
                tmp.append(int(line[0]))
                tmp.append(1)
                for j in range(0, self.numFeatures):
                    tmp.append(float(line[j + 1]))

                data.append(tmp)

            return data

        print("    * LogisticRegression Testing *")

        testRDD = testRDD.mapPartitions(lambda lines: process_testRDD(lines))

        true = testRDD.map(lambda data: 1 if data[0] == self.predict(data[1:]) else 0)
        true = true.reduce(lambda a, b: a + b)
        false = testRDD.count() - true

        print("     # accuracy:                 " + str(float(true) / float(true + false)) + "(" + str(true) + "/" + str(true + false) + ")")
        print("     # true:                     " + str(true))
        print("     # false:                    " + str(false))
      
    def predict(self, features):
        """
        Predict values for a single data point using the model trained.

            :param features:    Features to be labeled.
        """

        max_probability = -1.0
        prediction = -1

        for k in range (0, self.numClasses):
            dot = 0.0
            for j in range (0, (1 + self.numFeatures)):
                dot += float(features[j]) * float(self.weights[k * (1 + self.numFeatures) + j])
        
            probability = 1.0 / (1.0 + exp(-dot))

            if probability > max_probability:
                max_probability = probability
                prediction = k
   
        return prediction
