import chess
from chess import Board, pgn
from chess.engine import Score


def sign(a):
    return (a > 0) - (a < 0)


def material_value(board):
    return sum(v * (len(board.pieces(pt, True)) + len(board.pieces(pt, False))) for v, pt in
               zip([0, 3, 3, 5.5, 9], chess.PIECE_TYPES))


def material_count(board):
    return chess.popcount(board.occupied)


def investigate(a: Score, b: Score, board: Board, checkmate_only: bool):
    """
    determine if the difference between position A and B
    is worth investigating for a puzzle.
    """
    a_cp, a_mate = a.score(), a.mate()
    b_cp, b_mate = b.score(), b.mate()
    if a_cp is not None and b_cp is not None and not checkmate_only:
        if (((-110 < a_cp < 850 and 200 < b_cp < 850)
             or (-850 < a_cp < 110 and -200 > b_cp > -850))
                and material_value(board) > 3
                and material_count(board) > 6):
            return True
    elif a_cp is not None and b_mate is not None and material_value(board) > 3:
        if (a_cp < 110 and sign(b_mate) == -1) or (a_cp > -110 and sign(b_mate) == 1):
            # from an even position, walking int a checkmate
            return True
    elif a_mate is not None and b_mate is not None:
        if sign(a_mate) == sign(b_mate):  # actually means that they're opposite
            return True
    return False


def filter_game(opening: pgn, game_pgn: pgn):
    if game_pgn is None or opening is None:
        return True

    moveIndex = 0

    for (move, game_move) in zip(opening.mainline_moves(), game_pgn.mainline_moves()):
        print("OPENINGMOVE: " + str(move))
        print("GAMEMOVE: " + str(game_move))
        if game_move is None or game_move != move:
            return False

    return True
