import mysql.connector as db
import numpy as np
import time
from numba import cuda, jit


@cuda.jit
def write_seats_into_database(seats: np.ndarray, test_id, table_name) -> None:
    try:
        col_len: int = len(seats)
        row_len: int = len(seats[0])
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

        while row_idx < col_len:
            group_size: int = __how_many(seats, row_idx, seat_idx)
            for seat in range(group_size if (group_size > 0 and seat_idx < row_len) else 1):
                params.append([test_id, seat_idx + seat, row_idx, group_size, np.count_nonzero(seats)])
            seat_idx += (group_size if group_size > 0 else 1)
            if seat_idx >= row_len:
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
        write_seats_into_database(seats, test_id, table_name)


@cuda.jit
def __how_many(seats: np.ndarray, row, seat) -> int:
    reserved_count: int = 0
    row_len: int = len(seats[0])
    while seat < row_len and seats[row, seat]:
        reserved_count += 1
        seat += 1
    return reserved_count
