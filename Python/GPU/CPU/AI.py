import copy
import numpy as np
from FreeSeats import FreeSeats
from Database import Database
from Algorithm import Algorithm
from scipy.ndimage.interpolation import rotate


class AI(Algorithm):

    def __init__(self, name: str, max_group_size: int, seats: np.ndarray, shifting: np.array) -> None:
        super(AI, self).__init__(max_group_size, seats, shifting)
        self.__name = name
        self.__scores = np.full((max_group_size, self._col_len, self._row_len), 0.0)
        self.__original_room = copy.deepcopy(self._seats)

    @property
    def get_name(self) -> str:
        return self.__name

    def read_data_all(self) -> None:
        for group_size in range(self._max_group_size):
            self.__scores[group_size] = Database.query_avg_scores_from_database_all(self.__name, group_size + 1,
                                                                                    tuple(
                                                                                        [self._col_len, self._row_len]))
        print('Training is completed!')

    def read_data(self, simulation_count: int) -> None:
        for group_size in range(self._max_group_size):
            self.__scores[group_size] = Database.query_avg_scores_from_database(self.__name, group_size + 1,
                                                                                tuple([self._col_len, self._row_len]),
                                                                                simulation_count * self._col_len * self._row_len)
        print('Training is completed!')

    def vertical_corr(self) -> None:
        for k in range(len(self.__scores)):
            for i in range(self._col_len):
                for j in range(int(self._row_len / 2)):
                    self.__scores[k, i, self._row_len - j - 1] = (self.__scores[k, i, self._row_len - j - 1] +
                                                                  self.__scores[k, i, j]) / 2.0

    def horizontal_corr(self) -> None:
        for k in range(len(self.__scores)):
            for i in range(self._row_len):
                for j in range(int(self._col_len / 2)):
                    self.__scores[k, self._col_len - j - 1, i] = (self.__scores[k, self._col_len - j - 1, i] +
                                                                  self.__scores[k, j, i]) / 2.0

    def horizontal_vertical_corr(self) -> None:
        for k in range(len(self.__scores)):
            for i in range(self._col_len):
                for j in range(int(self._row_len / 2)):
                    self.__scores[k, i, self._row_len - j - 1] = (self.__scores[k, i, self._row_len - j - 1] +
                                                                  self.__scores[k, i, j]) / 2.0
            for i in range(self._row_len):
                for j in range(int(self._col_len / 2)):
                    self.__scores[k, self._col_len - j - 1, i] = (self.__scores[k, self._col_len - j - 1, i] +
                                                                  self.__scores[k, j, i]) / 2.0

    def central_corr(self) -> None:
        for k in range(len(self.__scores)):
            lower_triangle = np.matrix.round(rotate(self.__scores[k], angle=180), decimals=5)
            for i in range(self._col_len):
                for j in range(self._row_len):
                    if self.__scores[k][i][j] == lower_triangle[self._col_len - 1 - i][self._row_len - 1 - j]:
                        self.__scores[k][self._col_len - 1 - i][self._row_len - 1 - j] = \
                            lower_triangle[self._col_len - 1 - i][self._row_len - 1 - j]

    def reset_seats(self) -> None:
        self._seats = copy.deepcopy(self.__original_room)

    def search(self, required_seats: int):
        pass

    def train_fits(self, groups: np.array) -> None:
        Database.generate_data_fits(self.__name, copy.deepcopy(self._seats), groups, self._max_group_size,
                                    self._shifting)
        for group_size in range(self._max_group_size):
            self.__scores[group_size] = Database.query_avg_scores_from_database_all(self.__name, group_size + 1,
                                                                                    tuple(
                                                                                        [self._col_len, self._row_len]))
        print('Training is completed!')

    def train_bf(self, groups):
        
        print("Training is completed!")

    def score(self) -> int:
        return np.count_nonzero(self._seats)

    def insert_group_no_heuristic(self, group_size) -> bool:
        free_seat_groups: np.array = np.array([], dtype=FreeSeats)
        seat_idx: int = 0

        for row_idx in range(0, self._col_len):
            while seat_idx + group_size - 1 <= self._row_len:
                if self._is_free(row_idx, seat_idx, group_size):
                    free_seat_groups = np.append(free_seat_groups, FreeSeats(row_idx, seat_idx, group_size,
                                                                             sum(self.__scores[group_size - 1, row_idx,
                                                                                 seat_idx:seat_idx + group_size])))
                seat_idx += 1
            seat_idx = 0

        best_seats: FreeSeats = FreeSeats(0, 0, 0, score=0)
        for free_groups in free_seat_groups:
            if free_groups > best_seats:
                best_seats = free_groups
        if best_seats.free_count != 0:
            return self._reserve(best_seats.row, best_seats.first_seat, group_size)

    def insert_group_with_heuristic(self, group_size) -> bool:
        free_seat_groups: np.array = self._search_free_seat_groups()
        for group in free_seat_groups:
            if group.free_count != group_size:
                free_seat_groups = free_seat_groups[free_seat_groups != group]

        if free_seat_groups.size != 0:
            free_seat_groups_score: np.array = np.array([], dtype=FreeSeats)
            for group in free_seat_groups:
                free_seat_groups_score = np.append(free_seat_groups_score,
                                                   [FreeSeats(group.row, group.first_seat, group.free_count,
                                                              sum(self.__scores[group_size - 1, group.row,
                                                                  group.first_seat:group.first_seat + group_size]))])
            free_seat_groups = free_seat_groups_score

        else:
            free_seat_groups: np.array = np.array([], dtype=FreeSeats)
            seat_idx: int = 0

            for row_idx in range(0, self._col_len):
                while seat_idx + group_size - 1 <= self._row_len:
                    if self._is_free(row_idx, seat_idx, group_size):
                        free_seat_groups = np.append(free_seat_groups, FreeSeats(row_idx, seat_idx, group_size,
                                                                                 sum(self.__scores[group_size - 1,
                                                                                     row_idx,
                                                                                     seat_idx:seat_idx + group_size])))
                    seat_idx += 1
                seat_idx = 0

        best_seats: FreeSeats = FreeSeats(0, 0, 0, score=0)
        for free_groups in free_seat_groups:
            if free_groups > best_seats:
                best_seats = free_groups
        if best_seats.free_count != 0:
            return self._reserve(best_seats.row, best_seats.first_seat, group_size)
