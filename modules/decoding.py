import chess
from chess import Move, Board
from chess.uci import Score

#
# def move_from_dict(d: dict) -> Move:
#     return m.uci() if m else None


def score_from_dict(d) -> Score:
    return Score(d[0], d[1]) if d else None


def board_from_dict(d: dict) -> Board:
    board = chess.Board(d['fen'])
    return board
