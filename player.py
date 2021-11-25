class player:
    T = 1
    rank = 1
    score = 0.0
    name = ''
    sc = 0
    acc = 0.0

    def __init__(self, T: int, rank: int, name: str, sc: int, acc: float):
        self.T = T
        self.rank = rank
        self.name = name
        self.sc = sc
        self.acc = acc
        self.score = 0.0
