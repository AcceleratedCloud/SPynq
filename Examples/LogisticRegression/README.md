# Logistic Regression  

In this example we have implemented a hardware accelerator used for the computation of gradients for the Logistic Regression machine learning algorithm. The hardware accelerator is Spark independent, meaning that it can be used for any typical python application using the Pynq-Z1 board, thus we have implemented a new MLlib_accel package (beta version) for Spark that takes advantage of our hardware accelerator. In the next few lines we are going through the configuration steps needed to make use of the accelerated library as well as running a Logistic Regression application example.

## Configurations

### Apache Spark

1. In this repository you can find a folder named "MLlib_accel". Copy it under *\$SPARK_HOME/python/pyspark*. Make sure to rename **pyspark.zip** under *\$SPARK_HOME/python/lib* directory to something else (eg. pyspark1.zip), or else importing modules from MLlib_accel will raise errors because of the non existing modules in pyspark.zip.
2. Optionally you can set **\$SPARK_HOME** variable under */etc/environment* file, and add to *\$PATH $SPARK_HOME/bin* and *\$SPARK_HOME/sbin* directories. In that way, you can access them either being logged in as xilinx or root user and you will be able to run our application using the proposed scripts.

### Pynq-Z1

1. Copy **LogisticRegression.bit** and **LogisticRegression.tcl** files that can be found under the *bitstream* folder of this example, under the */home/xilinx/pynq/bitstream* folder on PYNQ-Z1 board.

> Congratulations! You are all set and ready to run your first accelerated Logistic Regression application.

## Application Execution Instructions

We have written a bash script which basically invokes spark-submit and runs the Logistic Regression application with our default input parameters.
- Running the ***lr*** bash script with only one argument (the iterations), will execute the Logistic Regression application and its algorithm using only the Zynq's CPU cores,  
- while running the ***lr *** script  followed by the ***accel*** option and the number of the iterations, will execute the same algorithm using the hardware accelerator. 
### Execution examples:
#### Software only
> **./lr 5**
#### Hardware accelerated
> **./lr accel 5**

## Running Logistic Regression Over a  Spark Cluster

Of course Spark can be run over a cluster. You will need a master node other than PYNQ-Z1 (eg. server or laptop) since Pynq has very limited resources and can't host both a Spark master and a Spark worker node. Furthermore, you can have several PYNQ-Z1 nodes as worker nodes were the application is going to be executed and accelerated. Make sure  that you have set-up properly your cluster by modifying slaves, spark-defaults.conf and spark-env.sh files accordingly. If you have any questions don't hesitate to ask them. Finally, it is well suggested that you have a Hadoop node installed and configured for the Spark cluster, otherwise you will have to copy the application's input files to each node.

In our evaluation, we used an Intel PC as the Spark master node and several PYNQ-Z1 worker nodes. Spark's *standalone* cluster manager was used in *client* mode. The master node also hosted the Hadoop distributed file-system.  


## Running Logistic Regression notebook

You can also find our Logistic Regression notebook under the "***notebook***" folder. The instructions for its execution are very simple:

1. Copy the ***LogisticRegression.ipynb*** notebook under the "***/home/xilinx/jupyter_notebooks/Examples***" directory of your Pynq board. 
2. Copy the input files ( ***MNIST_train.dat *** and ***MNIST_test.dat*** ) under the "***/home/xilinx/jupyter_notebooks/Examples/data***" directory of your Pynq board. 

You are all set to run an interactive PySpark shell through Jupyter and execute our Logistic Regression application.
 

For any further questions, discussion on the topic or our latest libraries, don't hesitate to contact the authors:
>Christoforos Kachris: kachris@microlab.ntua.gr
>Ioannis Stamelos: jgstamelos@gmail.com
>Elias Koromilas: el11059@central.ntua.gr


