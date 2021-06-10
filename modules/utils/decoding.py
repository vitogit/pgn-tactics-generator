from typing import Optional

import chess
from chess import Move, Board
from chess.engine import Cp, Mate, BestMove, Score

from modules.puzzle.analysed import analysed
from modules.puzzle.position_list import position_list
from modules.puzzle.puzzle import puzzle


def score_from_dict(d) -> Optional[Score]:
    if not d:
        return None
    if d[0] is not None:
        return Cp(d[0])
    else:
        return Mate(d[1])


def board_from_dict(d: dict) -> Board:
    board = chess.Board(d['fen'])
    return board


def move_from_str(s: str) -> Move:
    return Move.from_uci(s) if s else None


def bestmove_from_dict(d: dict) -> BestMove:
    return BestMove(move_from_str(d['move']), move_from_str(d['ponder'])) if d else None


def analyzed_from_dict(d: dict) -> analysed:
    return analysed(move_from_str(d['move']), score_from_dict(d['evaluation']))


def positionlist_from_dict(d: dict) -> position_list:
    result = position_list(position=board_from_dict(d['position']),
                           engine=None,
                           info_handler=None,
                           player_turn=d['player_turn'],
                           best_move=bestmove_from_dict(d['best_move']),
                           evaluation=score_from_dict(d['evaluation']),
                           strict=d['strict'])

    result.next_position = positionlist_from_dict(d['next_position']) if d['next_position'] else None
    result.analysed_legals = [analyzed_from_dict(al) for al in d['analysed_legals']]

    return result


def puzzle_from_dict(d: dict) -> puzzle:
    result = puzzle(
        last_pos=board_from_dict(d['last_pos']),
        last_move=move_from_str(d['last_move']),
        game_id=d['last_move'],
        engine=None,
        info_handler=None,
        game=None,
        strict=True
    )

    result.positions = positionlist_from_dict(d['positions'])
    return result
