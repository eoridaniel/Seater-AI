#from Algorithm import Algorithm
import numpy as np
#from BestFit import BestFit
from numba import cuda

'''def simulate(simulations: list):
    for i in Algorithm.create_groups(1000,4):
        simulations[cuda.blockDim*cuda.blockIdx+cuda.threadIdx].search(i)
'''
if __name__ == '__main__':
    cuda.get_current_device()
    #a = [BestFit(4, np.empty((100,100), dtype=np.bool_),np.empty((1,100), dtype=np.bool_)) for _ in range (10000)]
    #simulate[10,512](a)


    