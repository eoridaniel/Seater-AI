import numba
import numpy as np
from Database import Database
import random
from numba import cuda




if __name__ == '__main__':
    print(cuda.gpus)
    groups = [[random.randint(1, 5) for _ in range(100)] for _ in range(100)]

    print(numba.typeof(np.full((10, 10), np.False_, dtype=np.bool_)))
    Database.generate_data_bf[len(groups), 10]("Test", np.full((10, 10), np.False_, dtype=np.bool_), [np.False_ for _ in range(10)],
                                                   groups, 4)
