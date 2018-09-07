import chess

def sign(a):
    if a > 0:
        return 1
    elif a < 0:
        return -1
    else:
        return 0

def material_value(board):
    return sum(v * (len(board.pieces(pt, True)) + len(board.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

def material_count(board):
    return chess.popcount(board.occupied)

def investigate(a, b, board):
    # determine if the difference between position A and B 
    # is worth investigating for a puzzle.
    if a.cp is not None and b.cp is not None:
        if (a.cp > -110 and a.cp < 850 and b.cp > 200 and b.cp < 850
            and material_value(board) > 3
            and material_count(board) > 6):
            return True
    elif (a.cp is not None
        and b.mate is not None
        and material_value(board) > 3):
        if (a.cp > -110 and sign(b.mate) == 1):
            return True
    elif (a.mate is not None
        and b.mate is not None):
        if sign(a.mate) == sign(b.mate) and sign(b.mate) == 1: #actually means that they're opposite
            return True
    return False