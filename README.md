# SPynq: Spark on Pynq

## Description

SPynq is a framework for the efficient deployment of Spark data analytics applications on the heterogeneous MPSoC FPGA called Zynq on the Xilinx [Pynq](http://www.pynq.io/) platform. The mapping of [Spark](http://spark.apache.org/) on Pynq allows the acceleration of Spark application by utlizing seamlessly the programmable logic of the FPGAs. Below we will describe the configuration steps for the deployment of Spark on Pynq as well as the actions needed to access the built-in Xilinx libraries from PySpark.

In this project we have developed a library of hardware accelerators that can be used to speedup Spark applications such as Machine learning. SPecifically, we have developed a hardware accelerator that can speedup Logistic regression application up to 22x as it is described in [SPynq](http://vineyard-h2020.eu/download.php?f=81&lang=en&key=6453050166fa5731bfbd16364f5fe97d) paper ([bibtex](http://kachris.weebly.com/uploads/1/3/6/6/13662069/spynq_bibtex.txt)).

## Publications

If you use any part of this work, we would love to hear about it and would very much appreciate a citation:

* Spark acceleration on FPGAs: A use case on machine learning in Pynq, Elias Koromilas, Ioannis Stamelos, Christoforos Kachris, Dimitrios Soudris. International Conference on Modern Circuits and Systems Technologies (MOCAST), 2017.
* SPynq: Acceleration of machine learning applications over Spark on Pynq, Christoforos Kachris, Elias Koromilas, Ioannis Stamelos, Dimitrios Soudris. International Conference on Embedded Computer Systems: Architectures, Modeling, and Simulation (SAMOS), 2017.
* FPGA acceleration of spark applications in a Pynq cluster, Christoforos Kachris, Elias Koromilas, Ioannis Stamelos, Dimitrios Soudris. 27th International Conference on Field Programmable Logic and Applications (FPL), 2017.

```
@misc{
  author =       "Elias Koromilas, Ioannis Stamelos, Christoforos Kachris, Dimitrios Soudris",
  title =        "Spark acceleration on FPGAs: A use case on machine learning in Pynq",
  conference =   "International Conference on Modern Circuits and Systems Technologies(MOCAST)",
  year =         "2017",
  month =        "May",
}

@misc{
  author =       "Christoforos Kachris, Elias Koromilas, Ioannis Stamelos, Dimitrios Soudris",
  title =        "SPynq: Acceleration of machine learning applications over Spark on Pynq",
  conference =   "International Conference on Embedded Computer Systems: Architectures, Modeling, and Simulation (SAMOS)",
  year =         "2017",
}

@misc{
  author =       "Christoforos Kachris, Elias Koromilas, Ioannis Stamelos, Dimitrios Soudris",
  title =        "FPGA acceleration of spark applications in a Pynq cluster",
  conference =   "27th International Conference on Field Programmable Logic and Applications (FPL)",
  year =         "2017",
}
```


## Deploying Apache Spark

The Zynq FPGA, hosts a dual-core ARM Cortex-A9 32-bit processor and programmable logic. The Pynq platform hosts the Zynq SoC and 512MB of DDR3 memory. It is obvious that building Spark from source on Pynq could take too long or even end up failing since its resources are limited enough. For that reason, a pre-built version of Spark is used for the deployment. After connecting with Pynq through ssh protocol and extracting Spark to the directory of your choice, we need to follow certain steps in order for it to work.

First of all, we need to edit the following three files under the conf/ dir of Spark. 

1. **spark-defaults.conf**  _(Add or edit the following lines)_

  ```shell
  spark.eventLog.enabled           true  
  spark.eventLog.dir               {path/to/the/dir/where/log/files/will/be/stored}  
  spark.driver.memory              505M  
  spark.executor.memory            505M 
  spark.executor.cores             1
  spark.executor.instances         1
  ```
  
2. **spark-env.sh**  _(Add or edit the following lines)_  

  ```shell
  export PYSPARK_PYTHON           = python3
  export PYTHONHASHSEED           = 0
  export SPARK_DAEMON_MEMORY      = 505m
  export SPARK_DRIVER_MEMORY      = 505m
  export SPARK_EXECUTOR_MEMORY    = 505m
  export SPARK_WORKER_MEMORY      = 505m
  export SPARK_WORKER_CORES       = 1
  export SPARK_EXECUTOR_INSTANCES = 1
  export SPARK_EXECUTOR_CORES     = 1
 
  ```
  
  Xilinx libraries for accessing Pynq's modules, are built using python3. Not adding the first line to the configuration, would prevent applciations using those libraries from running.

3. **log4j.properties**  
Should look something like the file uploaded to the current project. (this one is optional and doesn't affect Spark execution, is used in order to hide unwanted log lines from the console)

After these configurations are made, Spark is ready to be run on Pynq. Of course, before running a Spark application, jdk has to be present and JAVA_HOME to be set properly.

 _(Under the project's conf dir you can find all of the three files mentioned above.)_
 
## Xilinx libraries for python applications
In order to use Pynq's board peripherals or the PL, always remember to append the path to Xilinx's pre-built libraries. Every python application should include the following two lines:
  ```python
  import sys
  sys.path.append('/home/xilinx')
  ```

**Contact Details:**
> Christoforos Kachris
Microprocessors and Digital Systems Lab (Microlab)
School of Electrical & Computer Engineering 
National Technical University of Athens (NTUA)
Athens, Greece

**Contributions:**
>Ioannis Stamelos
Elias Koromilas


[VINEYARD H2020](http://vineyard-h2020.eu)



