class analysed:
    def __init__(self, move, evaluation):
        self.move = move
        self.evaluation = evaluation

    def sign(self, val):
        return -1 if val <= 0 else 1

    def sort_val(self):
        if self.evaluation.cp is not None:
            return self.evaluation.cp
        elif self.evaluation.mate is not None:
            return self.sign(self.evaluation.mate) * (abs(100 + self.evaluation.mate)) * 10000
        else:
            return 0
