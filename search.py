import numba
import numpy as np
import math
from FreeSeats import FreeSeats
import numba as nb

__IS_NOT_FREE = [np.True_, None]


@nb.cuda.jit
def isin(a, b):
    out = nb.typed.List([1])
    for _ in range(len(a)):
        out.append(1)
    for i in nb.prange(len(a)):
        if a[i] in b:
            out[i] = True
        else:
            out[i] = False
    return out


@nb.cuda.jit
def __reserve(seats: np.ndarray, row: float, first_seat: float, required_seats: int) -> bool:
    seats[row, first_seat:first_seat + required_seats] = np.True_
    return True


@nb.cuda.jit
def __is_free(seats: np.ndarray, shifting: np.array, row: int, first_seat: int, required_seats: int) -> bool:
    col_len: int = len(seats)
    row_len: int = len(seats[0])
    seat_max_pos: int = first_seat + required_seats
    if not (row < col_len and seat_max_pos <= row_len):
        return False
    previous_row: bool = False
    next_row: bool = False
    current_row: bool = isin(seats[row, first_seat:seat_max_pos], __IS_NOT_FREE).any()
    if row > 0:
        previous_row = seats[row - 1, ((first_seat - 1 if first_seat > 0 else first_seat) if
                                       shifting[row - 1] == True and shifting[row] == False else first_seat):(
                                          (seat_max_pos + 1) if shifting[row] == True and shifting[
                                              row - 1] == False else seat_max_pos)].any()
    if row < col_len - 1:
        next_row = seats[row + 1, ((first_seat - 1 if first_seat > 0 else first_seat) if
                                   shifting[row + 1] == True and shifting[row] == False else first_seat):(
                                      (seat_max_pos + 1) if shifting[row] == True and shifting[
                                          row + 1] == False else seat_max_pos)].any()
    if current_row or previous_row or next_row:
        return False
    if (first_seat == 0 or seats[row, first_seat - 1] != np.True_) and (
            seat_max_pos == row_len or seats[row, seat_max_pos] != np.True_):
        return True


@nb.cuda.jit
def __search_free_seat_groups(seats: np.ndarray, shifting: np.array) -> np.array:
    free_seat_groups: np.array = np.array([])
    row_len: int = len([seats[0]])
    col_len: int = len(seats)
    for row in range(col_len):
        first_free: int = 0
        free_count: int = 0
        for seat in range(row_len):
            if __is_free(seats, shifting, row, seat, 1):
                free_count += 1
                continue
            elif free_count > 0:
                # FreeSeats
                free_seat_groups = np.append(free_seat_groups, [[row, first_free, free_count]])
            first_free = seat + 1
            free_count = 0
        if first_free < row_len:
            free_seat_groups = np.append(free_seat_groups, [[row, first_free, free_count]])
    return free_seat_groups


@nb.cuda.jit
def best_fit(seats: np.ndarray, shifting: np.array, max_group_size: int, required_seats: int) -> bool:
    while required_seats > 0:
        free_seat_groups: np.array = __search_free_seat_groups(seats, shifting)
        if required_seats <= max_group_size:
            best_seats: FreeSeats = __search_best_seats(required_seats, free_seat_groups)
            if best_seats.free_count != math.inf:
                return __reserve(seats, best_seats.row, best_seats.first_seat, required_seats)
            return False

        best_seats: FreeSeats = __search_best_seats(max_group_size, free_seat_groups)
        if best_seats.free_count != math.inf:
            required_seats -= max_group_size
            __reserve(seats, best_seats.row, best_seats.first_seat, max_group_size)
            continue
        return False


@nb.cuda.jit
def __search_best_seats(required_seats: int, free_seat_groups: np.array) -> FreeSeats:
    best_seats: FreeSeats = FreeSeats(math.inf, math.inf, math.inf)
    if len(free_seat_groups) > 0:
        for seats in free_seat_groups:
            if 0 <= seats.free_count - required_seats < best_seats.free_count - required_seats:
                best_seats = seats
    return best_seats


@nb.cuda.jit
def worst_fit(seats: np.ndarray, shifting: np.array, max_group_size: int, required_seats: int) -> bool:
    while required_seats > 0:
        free_seat_groups: np.array = __search_free_seat_groups(seats, shifting)
        if required_seats <= max_group_size:
            worst_seats: FreeSeats = __search_worst_seats(required_seats, free_seat_groups)
            if worst_seats.free_count != 0:
                return __reserve(seats, worst_seats.row, worst_seats.first_seat, required_seats)
            return False

        worst_seats: FreeSeats = __search_worst_seats(max_group_size, free_seat_groups)
        if worst_seats.free_count != 0:
            required_seats -= max_group_size
            __reserve(seats, worst_seats.row, worst_seats.first_seat, max_group_size)
            continue
        return False


@nb.cuda.jit
def __search_worst_seats(required_seats: int, free_seat_groups: np.array) -> FreeSeats:
    worst_seats: FreeSeats = FreeSeats(0, 0, 0)
    if len(free_seat_groups) > 0:
        for seats in free_seat_groups:
            if 0 <= seats.free_count - required_seats > worst_seats.free_count - required_seats:
                worst_seats = seats
    return worst_seats


@nb.cuda.jit
def first_fit(seats: np.ndarray, shifting: np.array, max_group_size: int, required_seats: int) -> bool:
    row_len: int = len([seats[0]])
    col_len: int = len(seats)
    for row in range(col_len):
        for seat in range(row_len):
            if max_group_size >= required_seats and __is_free(seats, shifting, row, seat, required_seats):
                return __reserve(seats, row, seat, required_seats)
            elif required_seats > max_group_size and __is_free(seats, shifting, row, seat, max_group_size):
                __reserve(seats, row, seat, max_group_size)
                return first_fit(required_seats - max_group_size)
    return False
