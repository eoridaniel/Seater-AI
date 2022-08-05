import numpy as np
from Algorithm import Algorithm



class FirstFit(Algorithm):

    def __init__(self, max_group_size: int, seats: np.ndarray, shifting: np.array):
        super(FirstFit, self).__init__(max_group_size, seats, shifting)

    def search(self, required_seats: int) -> bool:
        for row in range(self._col_len):
            for seat in range(self._row_len):
                if self._max_group_size >= required_seats and self._is_free(row, seat, required_seats):
                    return self._reserve(row, seat, required_seats)
                elif required_seats > self._max_group_size and self._is_free(row, seat, self._max_group_size):
                    self._reserve(row, seat, self._max_group_size)
                    return self.search(required_seats - self._max_group_size)
        return False
