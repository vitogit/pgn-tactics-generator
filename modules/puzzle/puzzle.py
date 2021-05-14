import logging

from modules.bcolors.bcolors import bcolors
from modules.puzzle.position_list import position_list


class puzzle:
    def __init__(self, last_pos, last_move, game_id, engine, info_handler, game, strict):
        self.last_pos = last_pos.copy()
        self.last_move = last_move
        self.game_id = game_id
        last_pos.push(last_move)
        self.positions = position_list(last_pos, engine, info_handler, strict=strict)
        self.game = game

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
        return (self.positions.is_complete(
            self.positions.category(),
            self.color(),
            True,
            self.positions.material_difference()
        )
                and not self.positions.ambiguous()
                and len(self.positions.move_list()) > 2)

    def generate(self, depth):
        self.positions.generate(depth)
        if self.is_complete():
            logging.debug(bcolors.OKGREEN + "Puzzle is complete" + bcolors.ENDC)
        else:
            logging.debug(bcolors.FAIL + "Puzzle incomplete" + bcolors.ENDC)

    def category(self):
        return self.positions.category()
