class analysed:
    def __init__(self, move, evaluation):
        self.move = move
        self.evaluation = evaluation

    def sign(self, val):
        return -1 if val <= 0 else 1

    def sort_val(self):
        if self.evaluation.score() is not None:
            return self.evaluation.score()
        elif self.evaluation.is_mate():
            return self.sign(self.evaluation.mate()) * (abs(100 + self.evaluation.mate())) * 10000
        else:
            return 0
