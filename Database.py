import copy
import mysql.connector as db
import numpy as np
from BestFit import BestFit
from Algorithm import Algorithm
from WorstFit import WorstFit
from FirstFit import FirstFit
from numba import cuda, jit
from search import best_fit
from write_seats_into_database import write_seats_into_database



def generate_data_bf_one_thread(table_name: str, seats: np.ndarray, groups: np.array, max_group_size: int,
                                test_id: int, test_count: int, block_size: int, shifting: list) -> None:
    data: Algorithm = BestFit(max_group_size, copy.deepcopy(seats), shifting)
    for group in range(test_id, test_id + block_size):
        data.set_seats(copy.deepcopy(seats))
        for gr in groups[group]:
            data.search(gr)
        data.write_seats_into_database(test_id, table_name)
        print(f"{test_id + 1}/{test_count}")
        test_id += 1


def generate_data_wf_one_thread(table_name: str, seats: np.ndarray, groups: np.array, max_group_size: int,
                                test_id: int, test_count: int, block_size: int, test_id_plus: int,
                                shifting: list) -> None:
    data: Algorithm = WorstFit(max_group_size, copy.deepcopy(seats), shifting)
    for group in range(test_id, test_id + block_size):
        data.set_seats(copy.deepcopy(seats))
        for gr in groups[group]:
            data.search(gr)
        data.write_seats_into_database(test_id + test_id_plus, table_name)
        print(f"{test_id + 1 + test_id_plus}/{test_count}")
        test_id += 1


def generate_data_ff_one_thread(table_name: str, seats: np.ndarray, groups: np.array, max_group_size: int,
                                test_id: int, test_count: int, block_size: int, test_id_plus: int,
                                shifting: list) -> None:
    data: Algorithm = FirstFit(max_group_size, copy.deepcopy(seats), shifting)
    for group in range(test_id, test_id + block_size):
        data.set_seats(copy.deepcopy(seats))
        for gr in groups[group]:
            data.search(gr)
        data.write_seats_into_database(test_id + test_id_plus, table_name)
        print(f"{test_id + 1 + test_id_plus}/{test_count}")
        test_id += 1


class Database:

    @staticmethod
    def query_avg_scores_from_database(table_name: str, group_size: int, size: tuple,
                                       simulation_count: int) -> np.ndarray:
        database_connection = db.connect(host="192.168.1.2", user="dani", passwd="Rengar12", database="Seating")
        cursor = database_connection.cursor()
        cursor.execute(f"SELECT test_id, NEWID() AS 'new_id' INTO temp_table FROM {table_name} GROUP BY test_id;")
        cursor.execute("SELECT a.y_coord, a.x_coord, avg(a.score + 0.0) AS 'avg_score' FROM ("
                       f"SELECT TOP {simulation_count * size[0] * size[1]} r.id, r.test_id, r.x_coord, r.y_coord, r.group_size, r.score "
                       f"FROM {table_name} r "
                       "INNER JOIN temp_table t ON r.test_id = t.test_id "
                       "ORDER BY t.new_id, y_coord, x_coord) a "
                       f"WHERE a.group_size = {group_size} "
                       "GROUP BY a.y_coord, a.x_coord "
                       "ORDER BY a.y_coord, a.x_coord;")
        avg_scores: np.ndarray = np.zeros((16, 20), dtype='float')
        for row in cursor.fetchall():
            avg_scores[row.y_coord, row.x_coord] = round(row.avg_score, 5) if row.avg_score != 0 else np.NAN
        cursor.execute("DROP TABLE IF EXISTS temp_table;")
        cursor.commit()
        database_connection.commit()
        cursor.close()
        database_connection.close()
        return avg_scores

    @staticmethod
    def query_avg_scores_from_database_all(table_name: str, group_size: int, size: tuple) -> np.ndarray:
        database_connection = db.connect(host="192.168.1.2", user="dani", passwd="Rengar12", database="Seating")
        cursor: db.Cursor = database_connection.cursor()
        cursor.execute(f"select y_coord, x_coord, avg(score + 0.0) as 'avg_score' from {table_name} "
                       f"where group_size = {group_size}"
                       f"group by y_coord, x_coord order by y_coord, x_coord")
        avg_scores: np.ndarray = np.zeros(size, dtype='float')
        for row in cursor.fetchall():
            avg_scores[row.y_coord, row.x_coord] = round(row.avg_score, 5) if row.avg_score != 0 else np.NAN
        cursor.commit()
        database_connection.commit()
        cursor.close()
        database_connection.close()
        return avg_scores

    @staticmethod
    @cuda.jit
    def generate_data_fits(table_name: str, seats: np.ndarray, groups: np.array, max_group_size: int,
                           shifting: list) -> None:
        groups_1 = groups[:int(len(groups) / 3)]
        groups_2 = groups[int(len(groups) / 3):int(len(groups) / 3) * 2]
        groups_3 = groups[int(len(groups) / 3) * 2:]

        pos = cuda.grid(1)
        if pos < len(groups_1):
            data: Algorithm = BestFit(max_group_size, copy.deepcopy(seats), shifting)
            data.set_seats(copy.deepcopy(seats))
            for gr in groups_1[pos]:
                data.search(gr)
            data.write_seats_into_database(pos, table_name)
            print(f"{pos}/{len(groups)}")

        if pos < len(groups_2):
            data: Algorithm = WorstFit(max_group_size, copy.deepcopy(seats), shifting)
            data.set_seats(copy.deepcopy(seats))
            for gr in groups_2[pos]:
                data.search(gr)
            data.write_seats_into_database(pos + len(groups_1), table_name)
            print(f"{pos + len(groups_1)}/{len(groups)}")

        if pos < len(groups_3):
            data: Algorithm = FirstFit(max_group_size, copy.deepcopy(seats), shifting)
            data.set_seats(copy.deepcopy(seats))
            for gr in groups_3[pos]:
                data.search(gr)
            data.write_seats_into_database(pos + len(groups_1) + len(groups_2), table_name)
            print(f"{pos + len(groups_1) + len(groups_2)}/{len(groups)}")

    @staticmethod
    @cuda.jit
    def generate_data_bf(table_name: str, seats: np.ndarray, shifting: np.array, groups: np.array,
                         max_group_size: int):
        pos = cuda.grid(1)
        if pos < (len(groups)):
            seats_cpy = seats.copy()
            for gr in groups[pos]:
                best_fit(seats_cpy, shifting, max_group_size, gr)
            write_seats_into_database(seats, pos, table_name)
        print(f"{pos}/{len(groups)}")
