import chess
import chess.uci
import os
from modules.bcolors.bcolors import bcolors
from modules.puzzle.analysed import analysed
from modules.fishnet.fishnet import stockfish_filename
from operator import methodcaller

engine = chess.uci.popen_engine(os.path.join(os.getcwd(),stockfish_filename()))
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

class position_list:
    def __init__(self, position, player_turn=True, best_move=None, evaluation=None):
        self.position = position.copy()
        self.player_turn = player_turn
        self.best_move = best_move
        self.evaluation = evaluation
        self.next_position = None
        self.analysed_legals = []

    def move_list(self):
        if self.next_position is None or self.next_position.ambiguous() or self.next_position.position.is_game_over():
            if self.best_move is not None:
                return [self.best_move.bestmove.uci()]
            else:
                return []
        else:
            return [self.best_move.bestmove.uci()] + self.next_position.move_list()

    def category(self):
        if self.next_position is None:
            if self.position.is_game_over():
                return 'Mate'
            else:
                return 'Material'
        else:
            return self.next_position.category()

    def generate(self):
        print(bcolors.WARNING + str(self.position) + bcolors.ENDC)
        print(bcolors.OKBLUE + 'Material Value: ' + str(self.board_value()) + bcolors.ENDC)
        self.evaluate_best()      
        if self.player_turn:
            self.evaluate_legals()
        if not self.player_turn or (not self.ambiguous() and not self.game_over()):
            print(bcolors.OKGREEN + 
                "Going Deeper: PT " + str(self.player_turn) + 
                " A " + str(self.ambiguous()) + 
                " GO " + str(self.game_over()) + bcolors.ENDC)
            self.next_position.generate()
        else:
            print(bcolors.WARNING + 
                "Not Going Deeper: PT " + str(self.player_turn) + 
                " A " + str(self.ambiguous()) + 
                " GO " + str(self.game_over()) + bcolors.ENDC)

    def is_complete(self, category, color, first_node, first_val):
        if self.next_position is not None:
            if category == 'Mate' or (category == 'Material' and self.next_position.next_position is not None):
                return self.next_position.is_complete(category, color, False, first_val)
        
        if category == 'Material':
            if color:
                if (self.board_value() > 2 
                    and abs(self.board_value() - first_val) > 0.1 
                    and first_val < 2):
                    return True
                else:
                    return False
            else:
                if (self.board_value() < -2 
                    and abs(self.board_value() - first_val) > 0.1
                    and first_val > -2):
                    return True
                else:
                    return False
        else:
            if self.position.is_game_over():
                return True
            else:
                return False

    def evaluate_best(self, nodes=4500000):
        print(bcolors.OKGREEN + "Evaluating Best Move...")
        engine.position(self.position)
        self.best_move = engine.go(nodes=nodes)
        self.evaluation = info_handler.info["score"][1]
        self.next_position = position_list(self.position.copy(), not self.player_turn)
        self.next_position.position.push(self.best_move.bestmove)
        print("Best Move: " + self.best_move.bestmove.uci() + bcolors.ENDC)
        print(bcolors.OKBLUE + "   CP: " + str(self.evaluation.cp))
        print("   Mate: " + str(self.evaluation.mate) + bcolors.ENDC)

    def evaluate_legals(self, nodes=2500000):
        print(bcolors.OKGREEN + "Evaluating Legal Moves..." + bcolors.ENDC)
        for i in self.position.legal_moves:
            position_copy = self.position.copy()
            position_copy.push(i)
            engine.position(position_copy)
            engine.go(nodes=nodes)
            self.analysed_legals.append(analysed(i, info_handler.info["score"][1]))
        self.analysed_legals = sorted(self.analysed_legals, key=methodcaller('sort_val'))
        for i in self.analysed_legals[:3]:
            print(bcolors.OKGREEN + "Move: " + str(i.move.uci()) + bcolors.ENDC)
            print(bcolors.OKBLUE + "   CP: " + str(i.evaluation.cp))
            print("   Mate: " + str(i.evaluation.mate))
        print("... and " + str(max(0, len(self.analysed_legals) - 3)) + " more moves" + bcolors.ENDC)

    def board_value(self):
        total = 0
        for i in chess.SQUARES:
            square = self.position.piece_at(i)
            base_val = 0
            if square is not None:
                if square.piece_type == chess.KNIGHT:
                    base_val = 3
                elif square.piece_type == chess.BISHOP:
                    base_val = 3
                elif square.piece_type == chess.ROOK:
                    base_val = 5.5
                elif square.piece_type == chess.QUEEN:
                    base_val = 9

                if square.color:
                    sign = 1
                else:
                    sign = -1

                total += sign * base_val
        return total

    def ambiguous(self):
        if len(self.analysed_legals) <= 1:
            return False
        elif len(self.analysed_legals) > 1:
            if (self.analysed_legals[0].evaluation.cp is not None
                and self.analysed_legals[1].evaluation.cp is not None):
                if (abs(self.analysed_legals[0].evaluation.cp - self.analysed_legals[1].evaluation.cp) < 160
                    or self.analysed_legals[1].evaluation.cp < -280):
                    return True
                else:
                    return False
            else:
                return False
            if (self.analysed_legals[0].evaluation.mate is not None
                and self.analysed_legals[1].evaluation.mate is not None):
                if (self.analysed_legals[0].evaluation.mate < 0
                    and self.analysed_legals[1].evaluation.mate < 0):
                    return True
                else:
                    return False
        return False

    def game_over(self):
        return self.next_position.position.is_game_over()
