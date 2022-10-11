import numpy as np
from Algorithm import Algorithm
from FreeSeats import FreeSeats


class WorstFit(Algorithm):

    def __inti__(self, max_group_size: int, seats: np.ndarray, shifting: np.array):
        super(WorstFit, self).__init__(max_group_size, seats, shifting)

    def __search_worst_seats(self, required_seats: int, free_seat_groups: list) -> FreeSeats:
        worst_seats: FreeSeats = FreeSeats(0, 0, 0)
        if len(free_seat_groups) > 0:
            for seats in free_seat_groups:
                if 0 <= seats.free_count - required_seats > worst_seats.free_count - required_seats:
                    worst_seats = seats
        return worst_seats

    def search(self, required_seats: int) -> bool:
        while required_seats > 0:
            free_seat_groups: np.array = self._search_free_seat_groups()
            if required_seats <= self._max_group_size:
                worst_seats: FreeSeats = self.__search_worst_seats(required_seats, free_seat_groups)
                if worst_seats.free_count != 0:
                    return self._reserve(worst_seats.row, worst_seats.first_seat, required_seats)
                return False

            worst_seats: FreeSeats = self.__search_worst_seats(self._max_group_size, free_seat_groups)
            if worst_seats.free_count != 0:
                required_seats -= self._max_group_size
                self._reserve(worst_seats.row, worst_seats.first_seat, self._max_group_size)
                continue
            return False
