import time
import numpy as np
import cupy as cp
import mysql.connector as db
from abc import abstractmethod
from numba import cuda
from FreeSeats import FreeSeats


class Algorithm:

    def __init__(self, max_group_size: int, seats: np.ndarray, shifting: np.array):
        self._max_group_size = max_group_size
        self._seats = seats
        self._set_row_and_col_len()
        self._shifting = shifting
        self._seats_gpu = cp.ndarray(self._seats)
        self._shifting_gpu = cp.ndarray(self._shifting)
        self.__IS_NOT_FREE = cp.array([cp.True_, None])

    @cuda.jit
    def _is_free(self, row: int, first_seat: int, required_seats: int) -> bool:
        seat_max_pos: int = first_seat + required_seats
        if row < self._col_len and seat_max_pos <= self._row_len:
            previous_row: bool = False
            next_row: bool = False
            current_row: bool = cp.isin(self._seats_gpu[row, first_seat:seat_max_pos], self.__IS_NOT_FREE).any()
            if row > 0:
                previous_row = self._seats_gpu[row - 1, ((first_seat - 1 if first_seat > 0 else first_seat) if
                                                     self._shifting_gpu[row - 1] == True and self._shifting_gpu[
                                                         row] == False else first_seat):(
                                                        (seat_max_pos + 1) if self._shifting_gpu[row] == True and
                                                                              self._shifting_gpu[
                                                                                  row - 1] == False else seat_max_pos)].any()
            if row < self._col_len - 1:
                next_row = self._seats_gpu[row + 1, ((first_seat - 1 if first_seat > 0 else first_seat) if self._shifting_gpu[
                                                                                                           row + 1] == True and
                                                                                                       self._shifting_gpu[
                                                                                                           row] == False else first_seat):(
                                                    (seat_max_pos + 1) if self._shifting_gpu[row] == True and
                                                                          self._shifting_gpu[
                                                                              row + 1] == False else seat_max_pos)].any()
            if current_row or previous_row or next_row:
                return False
            if (first_seat == 0 or self._seats_gpu[row, first_seat - 1] != cp.True_) and (
                    seat_max_pos == self._row_len or self._seats_gpu[row, seat_max_pos] != cp.True_):
                return True
        return False

    @cuda.jit
    def _search_free_seat_groups(self) -> cp.array:
        free_seat_groups: cp.array = cp.array([], dtype=FreeSeats)
        for row in range(self._col_len):
            first_free: int = 0
            free_count: int = 0
            for seat in range(self._row_len):
                if self._is_free(row, seat, 1):
                    free_count += 1
                    continue
                elif free_count > 0:
                    free_seat_groups = cp.append(free_seat_groups, [FreeSeats(row, first_free, free_count)])
                first_free = seat + 1
                free_count = 0
            if first_free < self._row_len:
                free_seat_groups = cp.append(free_seat_groups, [FreeSeats(row, first_free, free_count)])
        return free_seat_groups

    @abstractmethod
    @cuda.jit
    def search(self, required_seats: int):
        pass

    def set_to_zero_last_visited(self) -> None:
        pass
    
    @cuda.jit
    def _reserve(self, row: float, first_seat: float, required_seats: int) -> bool:
        self._seats_gpu[row, first_seat:first_seat + required_seats] = cp.True_
        return True

    def print_seats(self) -> None:
        print(self._seats)

    def count_of_reserved_seats(self) -> int:
        return cp.count_nonzero(self._seats)

    def _set_row_and_col_len(self):
        self._row_len = len(self._seats[0])
        self._col_len = len(self._seats)

    def set_seats(self, seats: cp.ndarray) -> None:
        self._seats = seats
        self._set_row_and_col_len()

    def __how_many(self, row, seat) -> int:
        reserved_count: int = 0
        while seat < self._row_len and self._seats[row, seat]:
            reserved_count += 1
            seat += 1
        return reserved_count

    def write_seats_into_database(self, test_id, table_name) -> None:
        try:
            database_connection = db.connect(
                host="192.168.1.2", user="dani", passwd="Rengar12", database="Seating")
            cursor = database_connection.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ( id int NOT NULL AUTO_INCREMENT,"
                           "test_id int NOT NULL, x_coord int NOT NULL, y_coord int NOT NULL, group_size int,"
                           "score float, PRIMARY KEY(id));")
            cursor.execute(f"create index if not exists {table_name}_group_index on {table_name}(group_size)")
            row_idx: int = 0
            seat_idx: int = 0
            cursor.fast_executemany = True
            params = list()

            while row_idx < self._col_len:
                group_size: int = self.__how_many(row_idx, seat_idx)
                for seat in range(group_size if (group_size > 0 and seat_idx < self._row_len) else 1):
                    params.append([test_id, seat_idx + seat, row_idx, group_size, self.count_of_reserved_seats()])
                seat_idx += (group_size if group_size > 0 else 1)
                if seat_idx >= self._row_len:
                    seat_idx = 0
                    row_idx += 1

            cursor.executemany(
                f"INSERT INTO {table_name} (test_id, x_coord, y_coord, group_size, score) values(%s,%s,%s,%s,%s)",
                params)
            database_connection.commit()
            cursor.close()
            database_connection.close()
        except db.Error as ex:
            print(f"{ex}\n")
            time.sleep(600)
            self.write_seats_into_database(test_id, table_name)

    @staticmethod
    @cuda.jit
    def create_groups(size: int, max_value: int) -> cp.array:
        return cp.random.randint(1, max_value + 1, size)
