from modules.puzzle.position_list import position_list
import json
import os
from operator import methodcaller

class puzzle:
    def __init__(self, last_pos, last_move, game_id):
        self.last_pos = last_pos.copy()
        self.last_move = last_move
        self.game_id = game_id
        last_pos.push(last_move)
        self.positions = position_list(last_pos)

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'category': self.positions.category(),
            'last_pos': self.last_pos.fen(),
            'last_move': self.last_move.uci(),
            'move_list': self.positions.move_list()
            }

    def color(self):
        return self.positions.position.turn

    def is_complete(self):
        return self.positions.is_complete(
            self.positions.category(), 
            self.color(), 
            True, 
            self.positions.board_value()) and not self.positions.ambiguous()

    def generate(self):
        self.positions.generate()
        if self.is_complete():
            print(bcolors.OKGREEN + "Puzzle is complete" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "Puzzle incomplete" + bcolors.ENDC)

    def category(self):
        return self.positions.category()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
