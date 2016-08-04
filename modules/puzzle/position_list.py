import chess
import chess.uci
import os
from modules.bcolors.bcolors import bcolors
from modules.puzzle.analysed import analysed
from modules.fishnet.fishnet import stockfish_filename
from operator import methodcaller

class position_list:
    def __init__(self, position, engine, info_handler, player_turn=True, best_move=None, evaluation=None):
        self.position = position.copy()
        self.engine = engine
        self.info_handler = info_handler
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
        print(bcolors.OKBLUE + 'Material Value: ' + str(self.material_difference()) + bcolors.ENDC)
        has_best = self.evaluate_best()
        if self.player_turn:
            self.evaluate_legals()
        if has_best and not self.ambiguous() and not self.game_over():
            print(bcolors.OKGREEN + "Going Deeper:")
            print("   Ambiguous: " + str(self.ambiguous()))
            print("   Game Over: " + str(self.game_over()))
            print("   Has Best Move: " + str(has_best) + bcolors.ENDC)
            self.next_position.generate()
        else:
            print(bcolors.WARNING + "Not Going Deeper:")
            print("   Ambiguous: " + str(self.ambiguous()))
            print("   Game Over: " + str(self.game_over()))
            print("   Has Best Move: " + str(has_best) + bcolors.ENDC)

    def evaluate_best(self, nodes=6000000):
        print(bcolors.OKGREEN + "Evaluating Best Move...")
        self.engine.position(self.position)
        self.best_move = self.engine.go(nodes=nodes)
        if self.best_move.bestmove is not None:
            self.evaluation = self.info_handler.info["score"][1]
            self.next_position = position_list(self.position.copy(),
                self.engine,
                self.info_handler,
                not self.player_turn)
            self.next_position.position.push(self.best_move.bestmove)
            print("Best Move: " + self.best_move.bestmove.uci() + bcolors.ENDC)
            print(bcolors.OKBLUE + "   CP: " + str(self.evaluation.cp))
            print("   Mate: " + str(self.evaluation.mate) + bcolors.ENDC)
            return True
        else:
            print(bcolors.FAIL + "No best move!" + bcolors.ENDC)
            return False

    def evaluate_legals(self, nodes=6000000):
        print(bcolors.OKGREEN + "Evaluating Legal Moves..." + bcolors.ENDC)
        for i in self.position.legal_moves:
            position_copy = self.position.copy()
            position_copy.push(i)
            self.engine.position(position_copy)
            self.engine.go(nodes=nodes)
            self.analysed_legals.append(analysed(i, self.info_handler.info["score"][1]))
        self.analysed_legals = sorted(self.analysed_legals, key=methodcaller('sort_val'))
        for i in self.analysed_legals[:3]:
            print(bcolors.OKGREEN + "Move: " + str(i.move.uci()) + bcolors.ENDC)
            print(bcolors.OKBLUE + "   CP: " + str(i.evaluation.cp))
            print("   Mate: " + str(i.evaluation.mate))
        print("... and " + str(max(0, len(self.analysed_legals) - 3)) + " more moves" + bcolors.ENDC)

    def material_difference(self):
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

    def is_complete(self, category, color, first_node, first_val):
        if self.next_position is not None:
            if ((category == 'Mate' and not self.ambiguous())
                or (category == 'Material' and self.next_position.next_position is not None)):
                return self.next_position.is_complete(category, color, False, first_val)
        
        if category == 'Material':
            if color:
                if (self.material_difference() > 0.2 
                    and abs(self.material_difference() - first_val) > 0.1 
                    and first_val < 2
                    and self.evaluation.mate is None):
                    return True
                else:
                    return False
            else:
                if (self.material_difference() < -0.2 
                    and abs(self.material_difference() - first_val) > 0.1
                    and first_val > -2
                    and self.evaluation.mate is None):
                    return True
                else:
                    return False
        else:
            if self.position.is_game_over():
                return True
            else:
                return False

    def ambiguous(self):
        if len(self.analysed_legals) > 1:
            if (self.analysed_legals[0].evaluation.cp is not None
                and self.analysed_legals[1].evaluation.cp is not None):
                if (self.analysed_legals[0].evaluation.cp > -200
                    or self.analysed_legals[1].evaluation.cp < -100):
                    return True
            if (self.analysed_legals[0].evaluation.mate is not None
                and self.analysed_legals[1].evaluation.mate is not None):
                if (self.analysed_legals[0].evaluation.mate < 1
                    and self.analysed_legals[1].evaluation.mate < 1):
                    return True
            if (self.analysed_legals[0].evaluation.mate is not None
                and self.analysed_legals[1].evaluation.cp is not None):
                if (self.analysed_legals[1].evaluation.cp < -100):
                    return True
        return False

    def game_over(self):
        return self.next_position.position.is_game_over()
