from pynq import MMIO, Overlay, PL
from .drivers import DMA

DMA_TO_DEV = 0    # DMA sends data to PL.
DMA_FROM_DEV = 1  # DMA receives data from PL.

def gradients_kernel_accel(data, weights):
    numClasses = 10
    numFeatures = 784
    chunkSize = int(len(data) / (numClasses + (1 + numFeatures)))

    # -------------------------
    #   Download Overlay.
    # -------------------------    

    ol = Overlay("LogisticRegression.bit")
    ol.download()

    # -------------------------
    #   Physical address of the Accelerator Adapter IP.
    # -------------------------
    
    ADDR_Accelerator_Adapter_BASE = int(PL.ip_dict["SEG_LR_gradients_kernel_accel_0_if_Reg"][0], 16)
    ADDR_Accelerator_Adapter_RANGE = int(PL.ip_dict["SEG_LR_gradients_kernel_accel_0_if_Reg"][1], 16)

    # -------------------------
    #    Initialize new MMIO object. 
    # -------------------------

    bus = MMIO(ADDR_Accelerator_Adapter_BASE, ADDR_Accelerator_Adapter_RANGE)

    # -------------------------
    #   Physical addresses of the DMA IPs.
    # -------------------------

    ADDR_DMA0_BASE = int(PL.ip_dict["SEG_dm_0_Reg"][0], 16)
    ADDR_DMA1_BASE = int(PL.ip_dict["SEG_dm_1_Reg"][0], 16)
    ADDR_DMA2_BASE = int(PL.ip_dict["SEG_dm_2_Reg"][0], 16)
    ADDR_DMA3_BASE = int(PL.ip_dict["SEG_dm_3_Reg"][0], 16)

    # -------------------------
    #    Initialize new DMA objects. 
    # -------------------------


    dma0 = DMA(ADDR_DMA0_BASE, direction = DMA_TO_DEV)    # data1 DMA
    dma1 = DMA(ADDR_DMA1_BASE, direction = DMA_TO_DEV)    # data2 DMA
    dma2 = DMA(ADDR_DMA2_BASE, direction = DMA_TO_DEV)    # weights DMA
    dma3 = DMA(ADDR_DMA3_BASE, direction = DMA_FROM_DEV)  # gradients DMA

    # -------------------------
    #    Allocate physically contiguous memory buffers.
    # -------------------------

    dma0.create_buf(int(chunkSize * (numClasses + (1 + numFeatures)) / 2) * 4)
    dma1.create_buf(int(chunkSize * (numClasses + (1 + numFeatures)) / 2) * 4)
    dma2.create_buf((numClasses * (1 + numFeatures)) * 4)
    dma3.create_buf((numClasses * (1 + numFeatures)) * 4)
    
    # -------------------------
    #    Get CFFI pointers to objects' internal buffers.
    # -------------------------

    data1_buf = dma0.get_buf(data_type = "float")
    data2_buf = dma1.get_buf(data_type = "float")
    weights_buf = dma2.get_buf(data_type = "float")
    gradients_buf = dma3.get_buf(data_type = "float")

    for i in range (0, int(chunkSize * (numClasses + (1 + numFeatures)) / 2)):
        data1_buf[i] = float(data[i])
        data2_buf[i] = float(data[int(chunkSize * (numClasses + (1 + numFeatures)) / 2) + i])
    for kj in range (0, numClasses * (1 + numFeatures)):
        weights_buf[kj] = float(weights[kj])

    # -------------------------
    #   Write data to MMIO.
    # -------------------------

    CMD = 0x0028            # Command.
    ISCALAR0_DATA = 0x0080  # Input Scalar-0 Write Data FIFO.

    bus.write(ISCALAR0_DATA, int(chunkSize))
    bus.write(CMD, 0x00010001)
    bus.write(CMD, 0x00020000)
    bus.write(CMD, 0x00000107)

    # -------------------------
    #   Transfer data using DMAs (Non-blocking).
    #   Block while DMAs are busy.
    # -------------------------
   
    dma0.transfer(int(chunkSize * (numClasses + (1 + numFeatures)) / 2) * 4, direction = DMA_TO_DEV)
    dma1.transfer(int(chunkSize * (numClasses + (1 + numFeatures)) / 2) * 4, direction = DMA_TO_DEV)
    dma2.transfer((numClasses * (1 + numFeatures)) * 4, direction = DMA_TO_DEV)
    
    dma0.wait()
    dma1.wait()
    dma2.wait()

    dma3.transfer((numClasses * (1 + numFeatures)) * 4, direction = DMA_FROM_DEV)
    
    dma3.wait()

    gradients = []
    for kj in range (0, numClasses * (1 + numFeatures)):
        gradients.append(float(gradients_buf[kj]))
    

    # -------------------------
    #   Destructors for DMA objects.
    # -------------------------

    dma0.__del__()
    dma1.__del__()
    dma2.__del__()
    dma3.__del__()     

    return gradients
