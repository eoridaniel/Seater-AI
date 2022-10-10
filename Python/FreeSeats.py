class FreeSeats:
    row: float = None
    first_seat: float = None
    free_count: float = None
    score: float = None

    def __init__(self, row: float, first_seat: float, free_count: float, score: float = None):
        self.row = row
        self.first_seat = first_seat
        self.free_count = free_count
        self.score = score

    def __gt__(self, other) -> float:
        return self.score > other.score
