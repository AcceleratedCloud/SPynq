## Increment overlay

In this example we test the integration of Spark and Zynq, Pynq's PL with a simple increment IP.
The IP was created using Vivado_HLS. 
Then, using Pynq's github project, we created two new files (base_with_ip.bit and base_with_ip.tcl). 
These files containt Pynq's default data plus the increment IP.

The two files mentioned above can be found in this directory.
_(Please note that they must be placed in the the bitstream direcotry under the Pynq directory of the SD card.)_

####Increment IP usage
Two integer numbers are given as input to the IP and their sum increased by one is returned.  
_(Please note that there is a bug with the ceated IP and the results are not as expected. Will be fixed soon.)_

####Running the increment application
Please note that submitting increment.py to Spark, requires version 2.1.0 and above, 
otherwise the 'toLocalIterator()' method may result in a timeout error!
