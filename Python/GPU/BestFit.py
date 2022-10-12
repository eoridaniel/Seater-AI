import math
import numpy as np
from FreeSeats import FreeSeats
from Algorithm import Algorithm
import cupy as cp
from numba import cuda

class BestFit(Algorithm):

    def __init__(self, max_group_size: int, seats: np.ndarray, shifting: np.array):
        super(BestFit, self).__init__(max_group_size, seats, shifting)

    @cuda.jit
    def search(self, required_seats: int) -> bool:
        while required_seats > 0:
            free_seat_groups: cp.array = self._search_free_seat_groups()
            if required_seats <= self._max_group_size:
                best_seats: FreeSeats = self.__search_best_seats(required_seats, free_seat_groups)
                if best_seats.free_count != math.inf:
                    return self._reserve(best_seats.row, best_seats.first_seat, required_seats)
                return False

            best_seats: FreeSeats = self.__search_best_seats(self._max_group_size, free_seat_groups)
            if best_seats.free_count != math.inf:
                required_seats -= self._max_group_size
                self._reserve(best_seats.row, best_seats.first_seat, self._max_group_size)
                continue
            return False

    @cuda.jit
    def __search_best_seats(self, required_seats: int, free_seat_groups: list) -> FreeSeats:
        best_seats: FreeSeats = FreeSeats(math.inf, math.inf, math.inf)
        if len(free_seat_groups) > 0:
            for seats in free_seat_groups:
                if 0 <= seats.free_count - required_seats < best_seats.free_count - required_seats:
                    best_seats = seats
        return best_seats
